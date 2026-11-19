"""Find monetization-safe photos on Wikimedia Commons (CC0 / PD / CC BY / CC BY-SA only), with attribution.

    python -m engine.commons candidates "<search>" <key>   -> output/commons/<key>/cand_*.jpg + meta.json
    python -m engine.commons pick <key> <n>                -> assets/stickers/<key>.png (round photo) + credit

Credits are collected in assets/stickers/credits.json; the renderer writes output/<ep>/credits.txt for the
YouTube description (required by CC BY / BY-SA).
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UA = "MapVideoTool/0.1 (educational map video generator)"
API = "https://commons.wikimedia.org/w/api.php"
OK_LICENSES = re.compile(r"^(cc0|public domain|pd|cc by(-sa)? ?[\d.]*|cc-by(-sa)?-[\d.]+)", re.I)
BAD = re.compile(r"\bnc\b|non-?commercial|\bnd\b|no-?deriv", re.I)


def _get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(5 * (k + 1))


def _strip(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def search(query, limit=8, width=500):
    q = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"filetype:bitmap {query}",
         "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
         "iiprop": "url|extmetadata|size|mime", "iiurlwidth": width}
    d = json.loads(_get(API + "?" + urllib.parse.urlencode(q)))
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        lic = _strip(m.get("LicenseShortName", {}).get("value", ""))
        if not OK_LICENSES.match(lic) or BAD.search(lic) or ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        if ii.get("width", 0) < 500:
            continue
        out.append({"title": p["title"], "thumb": ii.get("thumburl", ii["url"]), "page": ii["descriptionurl"], "license": lic,
                    "artist": _strip(m.get("Artist", {}).get("value", ""))[:120] or "unknown"})
    return out


def candidates(query, key, limit=8):
    d = os.path.join(ROOT, "output", "commons", key)
    os.makedirs(d, exist_ok=True)
    res = search(query, limit)
    for i, r in enumerate(res):
        path = os.path.join(d, f"cand_{i}.jpg")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            try:
                data = _get(r["thumb"])
            except Exception as e:
                print("   skip", r["title"], e)
                continue
            from PIL import Image
            import io
            im = Image.open(io.BytesIO(data)).convert("RGB")
            im.thumbnail((1000, 1000))
            im.save(path, quality=92)
            time.sleep(4.0)
        r["file"] = path
    res = [r for r in res if r.get("file") and os.path.exists(r["file"]) and os.path.getsize(r["file"]) > 0]
    json.dump(res, open(os.path.join(d, "meta.json"), "w"), ensure_ascii=False, indent=1)
    return res


def pick(key, n, crop=None):
    """Make a round photo sticker from candidate n. crop = (cx, cy, size) as fractions of the image."""
    from PIL import Image, ImageDraw
    d = os.path.join(ROOT, "output", "commons", key)
    meta = json.load(open(os.path.join(d, "meta.json")))[n]
    im = Image.open(meta["file"]).convert("RGB")
    w, h = im.size
    cx, cy, s = crop or (0.5, 0.5, 1.0)
    side = int(min(w, h) * s)
    x0 = int(min(max(cx * w - side / 2, 0), w - side))
    y0 = int(min(max(cy * h - side / 2, 0), h - side))
    im = im.crop((x0, y0, x0 + side, y0 + side)).resize((720, 720), Image.LANCZOS)
    mask = Image.new("L", (720 * 4, 720 * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 720 * 4 - 1, 720 * 4 - 1), fill=255)
    im.putalpha(mask.resize((720, 720), Image.LANCZOS))
    out = os.path.join(ROOT, "assets", "stickers", f"{key}.png")
    im.save(out)
    cred_path = os.path.join(ROOT, "assets", "stickers", "credits.json")
    creds = json.load(open(cred_path)) if os.path.exists(cred_path) else {}
    creds[f"{key}.png"] = {k: meta[k] for k in ("title", "page", "license", "artist")}
    json.dump(creds, open(cred_path, "w"), ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "candidates":
        for r in candidates(sys.argv[2], sys.argv[3]):
            print(r["license"], "|", r["title"])
    elif sys.argv[1] == "pick":
        crop = tuple(map(float, sys.argv[4].split(","))) if len(sys.argv) > 4 else None
        print(pick(sys.argv[2], int(sys.argv[3]), crop))
