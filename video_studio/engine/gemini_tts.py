"""Google AI Studio (Gemini TTS) narration.

The whole script is generated in ONE request (one consistent performance, and the free tier rate limit is low).
The audio is then split back into the episode's segments at the longest pauses, and word times inside each
segment are estimated from character lengths (Gemini does not return word timestamps).

API key: env GEMINI_API_KEY or the file named by env GEMINI_KEY_FILE. It is never stored in the repo.
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

import numpy as np

CACHE = os.path.join(os.path.dirname(__file__), "..", "output", "tts_cache")
SR = 24000


def _key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k and os.environ.get("GEMINI_KEY_FILE"):
        k = open(os.environ["GEMINI_KEY_FILE"]).read().strip()
    if not k:
        raise SystemExit("Gemini TTS needs GEMINI_API_KEY (or GEMINI_KEY_FILE)")
    return k


def _request(text, voice, model):
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for attempt in range(6):
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"x-goog-api-key": _key(), "Content-Type": "application/json"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=300))
            return np.frombuffer(base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]),
                                 np.int16).astype(np.float32) / 32768
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode(errors="ignore")
            if e.code in (429, 500, 503) and attempt < 5:
                wait = 20 * (attempt + 1)
                print(f"  gemini {e.code}, retry in {wait}s")
                time.sleep(wait)
                continue
            raise SystemExit(f"Gemini TTS error {e.code}: {msg}")


def _silences(x):
    hop = int(0.01 * SR)
    frames = len(x) // hop
    env = np.sqrt(np.convolve((x[: frames * hop].reshape(frames, hop) ** 2).mean(1), np.ones(5) / 5, "same"))
    silent = env < max(env.max() * 0.02, 1e-4)
    runs, start = [], None
    for k, s_ in enumerate(silent):
        if s_ and start is None:
            start = k
        elif not s_ and start is not None:
            runs.append((start * hop, k * hop))
            start = None
    speech = np.where(~silent)[0]
    return runs, speech[0] * hop, speech[-1] * hop


def _split(x, ref_durs):
    """Split one long take into len(ref_durs) lines. Dynamic programming over the pauses: every line's
    length should match its expected length (from the reference voice), and long pauses are preferred."""
    n = len(ref_durs)
    runs, first, last = _silences(x)
    cands = [((a + b) / 2, (b - a) / SR) for a, b in runs if first < a and b < last and (b - a) > 0.08 * SR]
    pos = [first] + [c[0] for c in cands] + [last]
    plen = [0.0] + [c[1] for c in cands] + [0.0]
    scale = (last - first) / sum(ref_durs)
    exp_ = [d * scale for d in ref_durs]
    M = len(pos)
    INF = 1e18
    cost = [[INF] * M for _ in range(n + 1)]
    back = [[-1] * M for _ in range(n + 1)]
    cost[0][0] = 0.0
    for k in range(1, n + 1):
        for j in range(1, M):
            if k == n and j != M - 1:
                continue
            bonus = 0.0 if j == M - 1 else 1.2 * min(plen[j], 0.8)
            for i2 in range(j):
                if cost[k - 1][i2] >= INF:
                    continue
                seg = pos[j] - pos[i2]
                c = cost[k - 1][i2] + float(np.log(seg / exp_[k - 1])) ** 2 * 4 - bonus
                if c < cost[k][j]:
                    cost[k][j], back[k][j] = c, i2
    cuts, j = [], M - 1
    for k in range(n, 0, -1):
        cuts.append(j)
        j = back[k][j]
    cuts = [0] + cuts[::-1]
    edges = [int(pos[c]) for c in cuts]
    edges[0] = max(0, edges[0] - int(0.05 * SR))
    edges[-1] = min(len(x), edges[-1] + int(0.15 * SR))
    return [x[edges[k]: edges[k + 1]] for k in range(n)]


def _strip_spoken_style(x, window=16.0, min_pause=0.35, min_lead=2.0):
    """Gemini sometimes reads the style instruction aloud before the script. It ends with the longest pause
    in the first `window` seconds -> drop everything before that pause (only if it is clearly long)."""
    runs, first, last = _silences(x[: int(window * SR)])
    runs = [r for r in runs if r[0] > first + min_lead * SR]
    if not runs:
        return x
    a, b = max(runs, key=lambda r: r[1] - r[0])
    if (b - a) / SR < min_pause:
        return x
    return x[(a + b) // 2:]


def _trim(x, thr_ratio=0.02):
    env = np.abs(x)
    idx = np.where(env > env.max() * thr_ratio)[0]
    return x[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.1 * SR)]


def _estimate_words(text, dur):
    """Rough word timings: time proportional to letters, extra weight after punctuation."""
    words = text.split()
    w = []
    for t in words:
        core = re.sub(r"[^\wऀ-ॿ]", "", t)
        weight = max(1, len(core)) + (4 if re.search(r"[।?!]$", t) else 2 if re.search(r"[,]$", t) else 0)
        w.append(weight)
    total = sum(w)
    out, acc = [], 0.0
    speak = dur * 0.97
    for t, k in zip(words, w):
        out.append({"t": speak * acc / total, "d": speak * k / total, "w": t})
        acc += k
    return out


def narrate(ep):
    """Returns [(wav_path, duration, words)] per segment."""
    if ep["tts"].get("per_segment", True):
        return narrate_per_segment(ep)
    tts = ep["tts"]
    voice, model = tts.get("voice", "Puck"), tts.get("model", "gemini-3.8-flash-tts")
    style = tts.get("style", "Read in a fun, energetic, excited Hindi YouTuber style, fast pace, "
                             "with a short pause between paragraphs:")
    texts = [s["text"] for s in ep["segments"]]
    # "take_texts": the script the cached one-take was recorded with. Lines edited since then are re-voiced
    # one by one (with "patch_model"), so the rest of the take can be reused without a new request.
    take_texts = tts.get("take_texts") or texts
    script = style + "\n\n" + "\n\n".join(take_texts)
    key = hashlib.sha1(f"{model}|{voice}|{script}".encode()).hexdigest()[:16]
    os.makedirs(CACHE, exist_ok=True)
    raw = os.path.join(CACHE, f"gemini_{key}.npy")
    if not os.path.exists(raw):
        print(f"  Gemini TTS ({model}, {voice}) ...")
        np.save(raw, _request(script, voice, model))
    x = np.load(raw)
    if tts.get("strip_spoken_style", True):
        x = _strip_spoken_style(x)
    # reference timing from the edge-tts voice (cached, free) -> where each line should end + word positions
    from . import tts as edge
    take_refs = [edge.synth(t, "hi-IN-MadhurNeural", "+22%") for t in take_texts]
    parts = _split(x, [r[1] for r in take_refs])
    refs = [edge.synth(t, "hi-IN-MadhurNeural", "+22%") for t in texts]
    out = []
    for i, (p, t) in enumerate(zip(parts, texts)):
        if t != take_texts[i]:
            pm = tts.get("patch_model", "gemini-3.8-flash-lite-tts")
            pkey = hashlib.sha1(f"{pm}|{voice}|{t}".encode()).hexdigest()[:16]
            raw_p = os.path.join(CACHE, f"gempatch_{pkey}.npy")
            if not os.path.exists(raw_p):
                print(f"  re-voicing edited line {i + 1} with {pm}")
                np.save(raw_p, _request(t, voice, pm))  # no instruction text: it tends to get read aloud
                time.sleep(6)
            p = _strip_spoken_style(np.load(raw_p), window=5.0, min_pause=0.15, min_lead=1.5)
        p = _trim(p)
        wav = os.path.join(CACHE, f"gemini_{key}_{i:02d}_{hashlib.sha1(t.encode()).hexdigest()[:6]}.wav")
        if not os.path.exists(wav):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                            "-ar", "48000", wav], input=p.astype(np.float32).tobytes(), check=True)
        dur = len(p) / SR
        rdur, rwords = refs[i][1], refs[i][2]
        words = [{"t": w["t"] * dur / rdur, "d": w["d"] * dur / rdur, "w": w["w"]} for w in rwords] \
            if rwords else _estimate_words(t, dur)
        out.append((wav, dur, words))
    return out


def narrate_per_segment(ep):
    """One request per segment: exact sync (slower on the free tier, so requests are spaced out)."""
    from . import tts as edge
    tts = ep["tts"]
    voice, model = tts.get("voice", "Hali"), tts.get("model", "gemini-3.8-flash-tts")
    style = tts.get("style", "Read in a fun, energetic, excited Hindi YouTuber style, fast pace:")
    os.makedirs(CACHE, exist_ok=True)
    out = []
    for i, seg in enumerate(ep["segments"]):
        t = seg["text"]
        key = hashlib.sha1(f"{model}|{voice}|{style}|{t}".encode()).hexdigest()[:16]
        wav = os.path.join(CACHE, f"gemseg_{key}.wav")
        if not os.path.exists(wav):
            print(f"  Gemini TTS {i + 1}/{len(ep['segments'])} ({voice})")
            x = _trim(_request(style + "\n\n" + t, voice, model))
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                            "-ar", "48000", wav], input=x.astype(np.float32).tobytes(), check=True)
            time.sleep(7)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                             "-of", "csv=p=0", wav]).strip())
        _, rdur, rwords = edge.synth(t, "hi-IN-MadhurNeural", "+22%")
        words = [{"t": w["t"] * dur / rdur, "d": w["d"] * dur / rdur, "w": w["w"]} for w in rwords] \
            if rwords else _estimate_words(t, dur)
        out.append((wav, dur, words))
    return out
