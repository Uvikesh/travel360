"""Hindi neural voice-over via edge-tts, with word-level timings (cached on disk)."""
import asyncio
import hashlib
import json
import os
import subprocess
import time

import edge_tts

CACHE = os.path.join(os.path.dirname(__file__), "..", "output", "tts_cache")


async def _synth(text, voice, rate, pitch, mp3_path):
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, proxy=proxy, boundary="WordBoundary")
    words = []
    with open(mp3_path, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
    return words


def synth(text, voice="hi-IN-MadhurNeural", rate="+18%", pitch="+0Hz"):
    """Returns (wav_path, duration_sec, words). Output is 48 kHz mono WAV."""
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(f"{voice}|{rate}|{pitch}|{text}".encode()).hexdigest()[:16]
    mp3 = os.path.join(CACHE, key + ".mp3")
    wav = os.path.join(CACHE, key + ".wav")
    meta = os.path.join(CACHE, key + ".json")
    if not os.path.exists(meta):
        for attempt in range(7):
            try:
                words = asyncio.run(_synth(text, voice, rate, pitch, mp3))
                if not words:
                    raise RuntimeError("no word timings received")
                break
            except Exception as e:  # the free endpoint is occasionally flaky
                if attempt == 6:
                    raise
                print("  tts retry:", e)
                time.sleep(2 + 3 * attempt)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ar", "48000", "-ac", "1", wav], check=True)
        dur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).strip())
        json.dump({"words": words, "duration": dur}, open(meta, "w"), ensure_ascii=False)
    m = json.load(open(meta))
    return wav, m["duration"], m["words"]


def find_word_time(words, keyword, default=0.0):
    """Time (sec) at which `keyword` starts being spoken. Matches on prefix so 'वड़ा' finds 'वड़ा'."""
    if keyword is None:
        return default
    if isinstance(keyword, (int, float)):
        return float(keyword)
    kw = keyword.strip("।,.!? ")
    first = kw.split()[0]
    for w in words:
        if w["w"].strip("।,.!? ").startswith(first):
            return w["t"]
    print(f"  ! keyword '{keyword}' not found in narration, using {default:.2f}s")
    return default
