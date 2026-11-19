"""Generate dish/character sticker art with Gemini image models (AI Studio key; never committed).

    python -m engine.gemini_image <episode.json> [--only mh,ct] [--model gemini-3.1-flash-image]

Prompts come from each show's "prompt" field, or "<label> (<state>)" + a fixed food-photo style.
Images land in assets/stickers/<file> (white background -> auto cut-out by graphics.load_sticker).
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STYLE = ("Appetizing professional food photography of a single serving, centered, 3/4 top angle, soft warm "
         "studio light, authentic Indian presentation, isolated on a plain pure white background, no text, "
         "no hands, no people, square 1:1.")


def _key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k and os.environ.get("GEMINI_KEY_FILE"):
        k = open(os.environ["GEMINI_KEY_FILE"]).read().strip()
    if not k:
        sys.exit("needs GEMINI_API_KEY or GEMINI_KEY_FILE")
    return k


def generate(prompt, out, model):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for attempt in range(4):
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"x-goog-api-key": _key(), "Content-Type": "application/json"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=300))
            for p in d["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    open(out, "wb").write(base64.b64decode(p["inlineData"]["data"]))
                    return True
            print("   no image returned")
            return False
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode(errors="ignore")
            if e.code in (429, 500, 503) and attempt < 3:
                if "per day" in msg or "PerDay" in msg:
                    print("   daily quota reached:", model)
                    return None
                time.sleep(20 * (attempt + 1))
                continue
            print("   error", e.code, msg[:200])
            return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--only", default="")
    ap.add_argument("--model", default="gemini-3.1-flash-image")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    ep = json.load(open(a.episode, encoding="utf-8"))
    only = set(filter(None, a.only.split(",")))
    seen = set()
    for seg in ep["segments"]:
        for b in seg.get("beats", []):
            for sh in ([b["show"]] if "show" in b else []) + b.get("shows", []):
                f = sh.get("sticker")
                if not f or f in seen or (only and sh["state"] not in only):
                    continue
                seen.add(f)
                out = os.path.join(ROOT, "assets", "stickers", f)
                if os.path.exists(out) and not a.force:
                    continue
                prompt = (sh.get("prompt") or sh["label"]) + ". " + STYLE
                print(f"{sh['state']}: {prompt[:70]}")
                r = generate(prompt, out, a.model)
                if r is None:
                    return
                time.sleep(4)


if __name__ == "__main__":
    main()
