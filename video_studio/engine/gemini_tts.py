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
            msg = e.read()[:3000].decode(errors="ignore")
            if e.code == 429 and "per day" in msg.lower():
                raise SystemExit(f"Gemini TTS daily quota reached for {model}")
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


ASK_MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-3.1-flash-lite"]


def _ask(body):
    """Text/audio-understanding call (transcripts, checks). Falls back across models (separate free quotas)."""
    last = None
    for m in ASK_MODELS:
        for attempt in range(3):
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                data=json.dumps(body).encode(), headers={"x-goog-api-key": _key(), "Content-Type": "application/json"})
            try:
                return json.load(urllib.request.urlopen(req, timeout=400))
            except urllib.error.HTTPError as e:
                last = f"{m}: {e.code}"
                if e.code == 429 and attempt < 2 and "per day" not in e.read().decode(errors="ignore").lower():
                    time.sleep(30)
                    continue
                break
            except Exception as e:  # timeouts
                last = f"{m}: {e}"
                time.sleep(5)
    raise RuntimeError(f"all analysis models failed ({last})")


def _request_any(text, voice, models):
    """Try the models in order (each has its own free daily quota)."""
    last = None
    for m in models:
        print(f"  Gemini TTS ({m}, {voice}) ...")
        try:
            return _request(text, voice, m)
        except SystemExit as e:
            last = e
            print("   ->", str(e)[:120])
    raise SystemExit(f"all TTS models failed: {last}")


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


def _split_by_transcript(x, texts, cache_path):
    """Get a timestamped transcript of the take (gemini-2.5-flash), find where each script line starts by
    matching its opening words in order, and cut in the pause just before each start."""
    import difflib
    meta = cache_path.replace(".npy", "_transcript.json")
    if not os.path.exists(meta):
        mp3 = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                              "-b:a", "48k", "-f", "mp3", "-"], input=x.astype(np.float32).tobytes(),
                             capture_output=True, check=True).stdout
        body = {"contents": [{"parts": [
            {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(mp3).decode()}},
            {"text": "Transcribe this Hindi audio in Devanagari as short phrases (split at every comma, pause and "
                     "sentence end). Answer only JSON: {\"phrases\": [{\"start\": seconds_with_2_decimals, "
                     "\"text\": \"...\"}, ...]}"}]}],
            "generationConfig": {"responseMimeType": "application/json"}}
        d = _ask(body)
        json.dump(json.loads(d["candidates"][0]["content"]["parts"][0]["text"]), open(meta, "w"), ensure_ascii=False)
    phrases = json.load(open(meta))["phrases"]
    dur = len(x) / SR
    # Gemini sometimes writes times as "m.sss" (0.057 = 0:05.7, 1.083 = 1:08.3), for the whole list or only
    # after the first minute -> repair to seconds
    if phrases and max(float(p["start"]) for p in phrases) < dur / 20:
        for p in phrases:
            v = float(p["start"])
            m = int(v)
            p["start"] = m * 60 + (v - m) * 100
    # after a minute Gemini either restarts at 0 (1.94 = 1:01.94) or writes "m.sss" (1.083 = 1:08.3):
    # on every drop pick the reading that continues closest after the previous phrase
    prev, offset = 0.0, 0.0
    for p in phrases:
        v = float(p["start"])
        cand = v + offset
        if cand + 1.0 < prev:
            m = int(v)
            options = [v + offset + 60 * k for k in (1, 2, 3)] + [m * 60 + (v - m) * 100]
            options = [o for o in options if o + 1.0 >= prev] or options
            cand = min(options, key=lambda o: abs(o - prev))
            if abs(cand - (v + offset + 60)) < 1e-6 or abs(cand - (v + offset + 120)) < 1e-6:
                offset = cand - v
        p["start"] = cand
        prev = cand
    NUM = {"एक": "1", "दो": "2", "तीन": "3", "चार": "4", "पांच": "5", "पाँच": "5", "दस": "10", "बीस": "20",
           "तीस": "30", "अट्ठाईस": "28", "छत्तीस": "36", "चौबीस": "24", "बारह": "12", "आठ": "8"}

    def norm(t):
        t = " ".join(NUM.get(w.strip("।,!?"), w) for w in t.split())
        return re.sub(r"[^\u0900-\u097F\w]", "", t.replace("ँ", "ं").replace("़", ""))
    starts, k = [0.0], 0
    for t in texts[1:]:
        head = norm(" ".join(t.split()[:3]))
        best, score = None, 0.0
        for idx in range(k + 1, len(phrases)):
            p = norm(phrases[idx]["text"])[: len(head) + 4]
            sc = difflib.SequenceMatcher(None, head, p).ratio()
            if sc > score + 0.05:
                best, score = idx, sc
            if sc > 0.85:
                break
        if best is None or score < 0.5:
            raise ValueError(f"line not found in transcript: {t[:30]} ({score:.2f})")
        k = best
        starts.append(float(phrases[best]["start"]))
    if any(b <= a for a, b in zip(starts, starts[1:])) or starts[-1] >= dur:
        raise ValueError(f"bad alignment {starts}")
    runs, first, last = _silences(x)
    cuts = [max(0, first - int(0.05 * SR))]
    for t in starts[1:]:
        target = int(t * SR)
        near = [r for r in runs if -0.7 * SR < (r[1] - target) < 0.35 * SR]
        c = (min(near, key=lambda r: abs(r[1] - target))[0] + min(near, key=lambda r: abs(r[1] - target))[1]) // 2 \
            if near else target - int(0.1 * SR)
        cuts.append(max(c, cuts[-1] + int(0.3 * SR)))
    cuts.append(min(len(x), last + int(0.15 * SR)))
    print("  aligned line starts:", [round(v, 1) for v in starts])
    return [x[cuts[m]: cuts[m + 1]] for m in range(len(texts))]


def _strip_spoken_prefix_checked(x, cache_path):
    """Ask gemini-2.5-flash whether the take starts with a spoken (English) instruction, and where the Hindi
    script starts. Cut only if it really was spoken. The answer is cached next to the take."""
    meta = cache_path.replace(".npy", "_prefix.json")
    if not os.path.exists(meta):
        mp3 = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                              "-b:a", "48k", "-f", "mp3", "-"], input=x[: 25 * SR].astype(np.float32).tobytes(),
                             capture_output=True, check=True).stdout
        body = {"contents": [{"parts": [
            {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(mp3).decode()}},
            {"text": "Does this audio START with someone reading an instruction/stage direction (usually English, "
                     "e.g. 'Read this in Hindi like...') before the actual Hindi content? Answer only JSON: "
                     '{"instruction_spoken": true|false, "hindi_start_sec": <seconds where the Hindi content starts>}'}]}],
            "generationConfig": {"responseMimeType": "application/json"}}
        d = _ask(body)
        ans = json.loads(d["candidates"][0]["content"]["parts"][0]["text"])
        json.dump(ans, open(meta, "w"))
    ans = json.load(open(meta))
    print("  spoken-instruction check:", ans)
    if not ans.get("instruction_spoken"):
        return x
    # cut in the pause closest to the reported Hindi start
    runs, first, last = _silences(x[: 30 * SR])
    target = float(ans.get("hindi_start_sec", 0)) * SR
    if not runs:
        return x[int(max(0, target - 0.1 * SR)):]
    a, b = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - target) - 0.3 * (r[1] - r[0]))
    return x[(a + b) // 2:]


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
        np.save(raw, _request_any(script, voice, tts.get("models") or [model]))
    x = np.load(raw)
    if tts.get("strip_spoken_style", True):
        x = _strip_spoken_prefix_checked(x, raw)
    # reference timing from the edge-tts voice (cached, free) -> where each line should end + word positions
    from . import tts as edge
    take_refs = [edge.synth(t, "hi-IN-MadhurNeural", "+22%") for t in take_texts]
    parts = None
    if tts.get("align", "transcript") == "transcript":
        try:
            parts = _split_by_transcript(x, take_texts, raw)
        except Exception as e:  # fall back to the pause-based DP split
            print("  transcript alignment failed, using pause DP:", e)
    if parts is None:
        parts = _split(x, [r[1] for r in take_refs])
    bad = [i for i, (p, r) in enumerate(zip(parts, take_refs)) if len(p) / SR > 1.8 * r[1] + 1.5]
    if bad and tts.get("_retry", 0) < 2:
        # the model repeated or added text (seen in practice) -> throw this take away and record a new one
        print(f"  narration lines {[b + 1 for b in bad]} are far too long (repeated text?) -> new take")
        os.rename(raw, raw.replace(".npy", f"_bad{tts.get('_retry', 0)}.npy"))
        for f in os.listdir(CACHE):
            if f.startswith(os.path.basename(raw)[:-4] + "_"):
                os.remove(os.path.join(CACHE, f))
        tts["_retry"] = tts.get("_retry", 0) + 1
        time.sleep(5)
        return narrate(ep)
    refs = [edge.synth(t, "hi-IN-MadhurNeural", "+22%") for t in texts]
    out = []
    for i, t in enumerate(texts):
        p = parts[i] if i < len(parts) else None
        if i >= len(take_texts) or t != take_texts[i]:
            # edited or appended line -> voice it on its own with the patch model
            pm = tts.get("patch_model", "gemini-3.8-flash-lite-tts")
            old_raw = os.path.join(CACHE, f"gempatch_{hashlib.sha1(f'{pm}|{voice}|{t}'.encode()).hexdigest()[:16]}.npy")
            if os.path.exists(old_raw):      # older patches were requested with a (spoken) instruction
                p = _strip_spoken_style(np.load(old_raw), window=5.0, min_pause=0.15, min_lead=1.5)
            else:
                raw_p = os.path.join(CACHE, f"gempatch_{hashlib.sha1(f'{pm}|{voice}|noinst|{t}'.encode()).hexdigest()[:16]}.npy")
                if not os.path.exists(raw_p):
                    print(f"  voicing line {i + 1} with {pm}")
                    np.save(raw_p, _request(t, voice, pm))  # no instruction text: it tends to get read aloud
                    time.sleep(6)
                p = np.load(raw_p)
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
