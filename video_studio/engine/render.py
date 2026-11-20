"""Map-explainer Shorts renderer.

    python -m engine.render episodes/<name>.json            # full 1080x1920 @30fps
    python -m engine.render episodes/<name>.json --preview  # fast 540x960 @15fps check
    python -m engine.render episodes/<name>.json --stills   # a few PNG frames only

The episode JSON is the whole "edit": narration text per segment and beats that are synced to spoken words
(camera moves, state highlights, sticker + label pops). See episodes/README.md for the format.
"""
import argparse
import json
import math
import multiprocessing as mp
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageFilter

from . import audio, geo, graphics, mapart, tts

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PALETTE = {
    "yellow": (246, 222, 40), "green": (60, 205, 70), "cyan": (40, 215, 235), "orange": (250, 150, 30),
    "magenta": (235, 70, 235), "lime": (170, 235, 40), "teal": (40, 190, 160), "pink": (255, 110, 170),
}
CYCLE = ["yellow", "green", "cyan", "orange", "lime", "teal"]


# ------------------------------------------------------------------ easing
def ease_io(x):
    x = min(1.0, max(0.0, x))
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x, s=1.9):
    x = min(1.0, max(0.0, x))
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ camera
def fit_camera(spec, W, H):
    if "point" in spec:   # {"point": [lon, lat], "span": svg units visible across the frame width}
        x, y = geo.project(*spec["point"])
        return (x + spec.get("dx", 0), y + spec.get("dy", 0), W / spec.get("span", 120))
    if spec.get("fit", "india") == "india":
        ids = [s for s in geo.india_states() if s not in ("an", "ld")]
    else:
        ids = spec["fit"]
    bbs = [geo.state_bbox(s) for s in ids]
    x0, y0 = min(b[0] for b in bbs), min(b[1] for b in bbs)
    x1, y1 = max(b[2] for b in bbs), max(b[3] for b in bbs)
    pad = spec.get("pad", 1.35 if len(ids) < 5 else 1.08)
    z = min(W / ((x1 - x0) * pad), H / ((y1 - y0) * pad))
    z = min(z, spec.get("max_zoom", 9.5) * W / 1080) * spec.get("zoom", 1.0)
    cx = (x0 + x1) / 2 + spec.get("dx", 0)
    cy = (y0 + y1) / 2 + spec.get("dy", 0)
    return (cx, cy, z)


class Timeline:
    def __init__(self, ep, W, H, fps):
        self.W, self.H, self.fps = W, H, fps
        self.cam_keys = []   # (t0, t1, from, to, kind)
        self.items = []      # dicts with t_in, t_out, state, sticker img, label img, color
        self.clouds = []     # (t0, t1)
        self.voice = []      # (t, wav_path)
        self.sfx = []        # (t, kind)
        self.captions = []   # (t0, t1, text)
        self.endcard_t = None
        self.build(ep)

    def add_move(self, t0, t1, to, kind):
        frm = self.camera(t0)
        self.cam_keys.append((t0, t1, frm, to, kind))
        if kind == "clouds":
            self.clouds.append((t0, t1))
        self.sfx.append((t0, "whoosh"))

    def camera(self, t):
        if not self.cam_keys:
            return (306, 348, 1.6)
        cur = self.cam_keys[0][3]
        cur_t = self.cam_keys[0][1]
        for t0, t1, frm, to, kind in self.cam_keys:
            if t < t0:
                break
            if t <= t1 and t1 > t0:
                s = (t - t0) / (t1 - t0)
                e = ease_io(s)
                lz = math.log(frm[2]) + (math.log(to[2]) - math.log(frm[2])) * e
                dist = math.hypot(to[0] - frm[0], to[1] - frm[1])
                view = self.W / min(frm[2], to[2])
                dip = min(0.55, 0.35 * dist / view) if kind != "cut" else 0
                if kind == "clouds":
                    dip = max(dip, 0.25)
                z = math.exp(lz) * (1 - dip * math.sin(math.pi * s))
                return (frm[0] + (to[0] - frm[0]) * e, frm[1] + (to[1] - frm[1]) * e, z)
            cur, cur_t = to, t1
        # gentle push-in while holding (Ken Burns)
        hold = max(0.0, t - cur_t)
        return (cur[0], cur[1], cur[2] * (1 + 0.012 * min(hold, 6)))

    def build(self, ep):
        W = self.W
        voice, rate = ep.get("voice", "hi-IN-MadhurNeural"), ep.get("rate", "+18%")
        gap = ep.get("gap", 0.12)
        sticker_h = int(ep.get("sticker_height", 480) * W / 1080)
        t = 0.0
        color_i = 0
        first = True
        pre = None
        if ep.get("tts", {}).get("engine") == "gemini":
            from . import gemini_tts
            pre = gemini_tts.narrate(ep)
        for si, seg in enumerate(ep["segments"]):
            if pre:
                wav, dur, words = pre[si]
            else:
                wav, dur, words = tts.synth(seg["text"], voice, rate, ep.get("pitch", "+0Hz"))
            beats = seg.get("beats", [])
            lead = 0.0
            b0 = beats[0] if beats else {}
            if "camera" in b0 and b0.get("at") is None and not first:
                lead = {"cut": 0.0, "fly": 0.55, "clouds": 1.1}[b0.get("transition", "fly")]
            seg_t = t + lead
            self.voice.append((seg_t, wav))
            self.captions.append((seg_t, seg_t + dur, seg["text"]))
            for b in beats:
                bt = seg_t + tts.find_word_time(words, b.get("at"), 0.0)
                if "camera" in b:
                    to = fit_camera(b["camera"], self.W, self.H)
                    kind = b.get("transition", "fly")
                    if first and b.get("at") is None:
                        self.cam_keys.append((0, 0, to, to, "cut"))
                    else:
                        t0 = (bt - lead) if b.get("at") is None else bt - 0.45
                        t1 = bt if b.get("at") is None else bt + 0.15
                        if kind == "cut":
                            t0 = t1 = bt
                        self.add_move(t0, max(t1, t0 + 0.01), to, kind)
                    if b.get("clear", True):
                        for it in self.items:
                            if it["t_out"] is None:
                                it["t_out"] = (bt - lead) if b.get("at") is None else bt - 0.45
                for sh in ([b["show"]] if "show" in b else []) + b.get("shows", []):
                    color = PALETTE.get(sh.get("color"), None) or PALETTE[CYCLE[color_i % len(CYCLE)]]
                    color_i += 1
                    self.items.append(self.make_item(sh, bt, color, sticker_h))
                    self.sfx.append((bt, "pop"))
                if b.get("endcard"):
                    self.endcard_t = bt
                    self.sfx.append((bt, "whoosh"))
                if b.get("collage"):
                    self.make_collage(bt, sticker_h, b.get("collage_scale", 0.3))
            t = seg_t + dur + gap
            first = False
        self.duration = t + ep.get("tail", 0.9)

    def make_item(self, sh, bt, color, sticker_h):
        sid = sh["state"]
        cx, cy = geo.project(*sh["lonlat"]) if sh.get("lonlat") else geo.state_centroid(sid)
        h = int(sticker_h * sh.get("scale", 1.0))
        art = sh.get("sticker")
        art_path = os.path.join(ROOT, "assets", "stickers", art) if art else None
        if art_path and os.path.exists(art_path):
            img = graphics.load_sticker(art_path, h)
        elif sh.get("emoji"):
            img = graphics.emoji_sticker(sh["emoji"], h)
        else:
            img = None
        lab = graphics.label_pill(sh["label"], size=int(46 * self.W / 1080)) if sh.get("label") else None
        return {"state": sid, "pos": (cx + sh.get("dx", 0), cy + sh.get("dy", 0)), "img": img, "label": lab,
                "color": color, "t_in": bt, "t_out": None, "highlight": sh.get("highlight", True),
                "src": sh, "scale": 1.0}

    def make_collage(self, bt, sticker_h, scale):
        seen, picks = set(), []
        for it in list(self.items):
            key = (it["state"], it["src"].get("sticker") or it["src"].get("emoji"), tuple(it["src"].get("lonlat") or ()))
            if it.get("collage") or key in seen:
                continue
            seen.add(key)
            picks.append(it)
        for k, src in enumerate(picks):
            it = dict(src)
            it.update(t_in=bt + 0.07 * k, t_out=None, collage=True, scale=scale, label=None)
            self.items.append(it)
        self.sfx.append((bt, "pop"))


# ------------------------------------------------------------------ frame rendering
G = {}


def _init_globals(ep, W, H, fps):
    G["tl"] = Timeline(ep, W, H, fps)
    G["map"] = mapart.MapRasters()
    G["shade"] = (np.asarray(mapart.plaster(H, W), np.float32) / 128.0)[..., None]
    G["clouds"] = graphics.clouds(W, H)
    G["wm"] = graphics.watermark(ep.get("watermark", ""), size=int(34 * W / 1080)) if ep.get("watermark") else None
    G["logo"] = None
    if ep.get("logo"):
        lg = Image.open(os.path.join(ROOT, ep["logo"])).convert("RGBA")
        G["logo_src"] = lg
        sz = int(ep.get("logo_size", 150) * W / 1080)
        lg = lg.resize((sz, sz), Image.LANCZOS)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.95)))
        G["logo"] = lg
    ec = ep.get("endcard")
    if ec:
        s_ = W / 1080
        G["ec"] = {
            "title": graphics.title_text(ec.get("title", "वीडियो पसंद आया?"), int(84 * s_), fill=(255, 205, 30)),
            "buttons": [graphics.icon_pill(e, t, size=int(62 * s_)) for e, t in
                        ec.get("buttons", [["👍", "लाइक"], ["🔁", "शेयर"], ["🔔", "सब्सक्राइब"]])],
            "ask": graphics.icon_pill("💬", ec.get("ask", "अगली वीडियो किस पर बनाएँ?"), size=int(56 * s_),
                                      fill=(255, 196, 30), outline=(255, 255, 255)),
            "ask2": graphics.title_text(ec.get("ask2", "कमेंट करके बताओ 👇").replace(" 👇", ""), int(64 * s_)),
        }
    G["W"], G["H"] = W, H


def _item_state(it, t):
    """(alpha, scale) of an item at time t; None if invisible."""
    if t < it["t_in"] - 0.15:
        return None
    a_in = smooth((t - it["t_in"] + 0.15) / 0.25)
    a_out = 1.0 if it["t_out"] is None else 1 - smooth((t - it["t_out"]) / 0.3)
    if a_out <= 0:
        return None
    pop = ease_out_back((t - it["t_in"]) / 0.38) if t >= it["t_in"] else 0.0
    return a_in * a_out, pop


def render_frame(i):
    tl, W, H = G["tl"], G["W"], G["H"]
    t = i / tl.fps
    cx, cy, z = tl.camera(t)

    def to_screen(x, y):
        return (W / 2 + (x - cx) * z, H / 2 + (y - cy) * z)

    vis = []
    for it in tl.items:
        st = _item_state(it, t)
        if st:
            vis.append((it, st))
    hl = {}
    for it, (a, pop) in vis:
        if it["highlight"]:
            hl[it["state"]] = (it, a, pop)
    frame, masks = G["map"].view(cx, cy, z, W, H, list(hl))
    frame = frame.convert("RGBA")

    # --- highlighted states pop up off the map
    for sid, (it, a, pop) in hl.items():
        m = masks[sid]
        bb = m.getbbox()
        if not bb:
            continue
        lift = 1.0 + 0.05 * math.sin(min(1.0, max(0.0, (t - it["t_in"] + 0.15) / 0.45)) * math.pi)
        lift = lift if not it.get("collage") else 1.0
        pad = 14
        bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(W, bb[2] + pad), min(H, bb[3] + pad))
        mc = m.crop(bb)
        border = mc.filter(ImageFilter.MaxFilter(5))
        layer = Image.new("RGBA", mc.size, (0, 0, 0, 0))
        white = Image.new("RGBA", mc.size, (255, 255, 255, 255))
        white.putalpha(border)
        layer.alpha_composite(white)
        colr = Image.new("RGBA", mc.size, it["color"] + (255,))
        colr.putalpha(mc)
        layer.alpha_composite(colr)
        if lift != 1.0:
            nw, nh = int(mc.width * lift), int(mc.height * lift)
            layer = layer.resize((nw, nh), Image.BILINEAR)
        ox = bb[0] - (layer.width - mc.width) // 2
        oy = bb[1] - (layer.height - mc.height) // 2
        sh = layer.getchannel("A").filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.55 * a))
        shadow = Image.new("RGBA", layer.size, (0, 0, 0, 255))
        shadow.putalpha(sh)
        _paste(frame, shadow, ox + 4, oy + 12)
        if a < 1:
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
        _paste(frame, layer, ox, oy)

    # --- screen-space plaster texture (applied to the map only)
    arr = np.asarray(frame.convert("RGB"), np.float32) * G["shade"]
    frame = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

    # --- stickers + labels
    for it, (a, pop) in vis:
        sx, sy = to_screen(*it["pos"])
        sc = it["scale"] * max(0.0, pop)
        if it["img"] is not None and sc > 0.02:
            img = it["img"]
            w, h = int(img.width * sc), int(img.height * sc)
            if w > 2 and h > 2:
                im2 = img.resize((w, h), Image.BILINEAR) if (w, h) != img.size else img
                # keep stickers inside the frame
                if it.get("collage"):
                    x, y = int(sx - w / 2), int(sy - h / 2)
                else:
                    x = int(min(max(sx - w / 2, 10 - w * 0.1), W - w * 0.9 - 10))
                    y = int(min(max(sy - h * 0.62, 150), H - h - 160))
                if a < 1:
                    im2 = im2.copy()
                    im2.putalpha(im2.getchannel("A").point(lambda v: int(v * a)))
                _paste(frame, im2, x, y)
                sx, sy = x + w / 2, y + h * 0.9
        if it["label"] is not None:
            lp = ease_out_back((t - it["t_in"] - 0.12) / 0.3)
            if lp > 0.02:
                lab = it["label"]
                lw, lh = max(2, int(lab.width * lp)), max(2, int(lab.height * lp))
                l2 = lab.resize((lw, lh), Image.BILINEAR)
                if a < 1:
                    l2.putalpha(l2.getchannel("A").point(lambda v: int(v * a)))
                x = int(min(max(sx - lw / 2, 16), W - lw - 16))
                _paste(frame, l2, x, int(sy - lh * 0.2))

    # --- clouds
    for t0, t1 in tl.clouds:
        if t0 <= t <= t1 + 0.3:
            s = (t - t0) / (t1 + 0.3 - t0)
            a = math.sin(math.pi * s) ** 0.6
            sc = 1.0 + 0.9 * s
            cl = G["clouds"]
            w, h = int(W * sc), int(H * sc)
            c2 = cl.resize((w, h), Image.BILINEAR).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
            c2.putalpha(c2.getchannel("A").point(lambda v: int(v * a)))
            frame.alpha_composite(c2)

    if G["wm"] is not None:
        frame.alpha_composite(G["wm"], (int(W * 0.025), int(H * 0.018)))
    if G["logo"] is not None:
        frame.alpha_composite(G["logo"], (int(W * 0.03), int(H * 0.02)))
        # big logo pops in over the final collage (end card)
        t_end = tl.duration - 2.2
        if tl.endcard_t is not None and t >= tl.endcard_t:
            _endcard(frame, t - tl.endcard_t, W, H)
        elif tl.endcard_t is None and t >= t_end:
            p = ease_out_back((t - t_end) / 0.5)
            sz = int(W * 0.34 * p)
            if sz > 4:
                big = G["logo_src"].resize((sz, sz), Image.LANCZOS)
                _paste(frame, big, (W - sz) // 2, int(H * 0.80) - sz // 2)
    return frame.convert("RGB").tobytes()


def _endcard(frame, dt, W, H):
    """Like / share / subscribe + 'next topic? comment' card with the big logo."""
    ec = G["ec"]
    dim = Image.new("RGBA", (W, H), (8, 6, 20, int(175 * smooth(dt / 0.4))))
    frame.alpha_composite(dim)

    def pop(img, cx, cy, t0, dur=0.45):
        p = ease_out_back((dt - t0) / dur)
        if p <= 0.02:
            return
        w, h = max(2, int(img.width * p)), max(2, int(img.height * p))
        _paste(frame, img.resize((w, h), Image.BILINEAR), int(cx - w / 2), int(cy - h / 2))

    sz = int(W * 0.46)
    pop(G["logo_src"].resize((sz, sz), Image.LANCZOS), W / 2, H * 0.25, 0.0, 0.55)
    pop(ec["title"], W / 2, H * 0.45, 0.35)
    for k, b in enumerate(ec["buttons"]):
        pulse = 1.0 + 0.04 * math.sin((dt - 0.6 - 0.15 * k) * 6) if dt > 1.2 else 1.0
        img = b if pulse == 1.0 else b.resize((int(b.width * pulse), int(b.height * pulse)), Image.BILINEAR)
        pop(img, W / 2, H * (0.55 + 0.08 * k), 0.55 + 0.15 * k)
    pop(ec["ask"], W / 2, H * 0.80, 1.1)
    pop(ec["ask2"], W / 2, H * 0.87, 1.3)


def _paste(dst, src, x, y):
    """alpha_composite that tolerates negative / out-of-frame offsets."""
    W, H = dst.size
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    w = min(src.width - sx0, W - dx0)
    h = min(src.height - sy0, H - dy0)
    if w <= 0 or h <= 0:
        return
    dst.alpha_composite(src.crop((sx0, sy0, sx0 + w, sy0 + h)), (dx0, dy0))


# ------------------------------------------------------------------ thumbnail
def thumbnail(ep, out):
    W, H = 1080, 1920
    tl, mp_ = G["tl"], G["map"]
    cx, cy, z = fit_camera({"fit": "india", "pad": 1.12}, W, H)
    cy -= 0.12 * H / z  # push the map down so the title sits above it
    items = [it for it in tl.items if not it.get("collage")]
    frame, masks = mp_.view(cx, cy, z, W, H, [it["state"] for it in items])
    frame = frame.convert("RGBA")
    for it in items:
        col = Image.new("RGBA", (W, H), it["color"] + (255,))
        col.putalpha(masks[it["state"]])
        frame.alpha_composite(col)
    arr = np.asarray(frame.convert("RGB"), np.float32) * G["shade"]
    frame = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    for it in items:
        if it["img"] is None:
            continue
        sx, sy = W / 2 + (it["pos"][0] - cx) * z, H / 2 + (it["pos"][1] - cy) * z
        im = it["img"].resize((int(it["img"].width * 0.3), int(it["img"].height * 0.3)), Image.LANCZOS)
        _paste(frame, im, int(sx - im.width / 2), int(sy - im.height / 2))
    th = ep.get("thumbnail", {})
    y = 90
    for line, col in zip(th.get("lines", [ep.get("title", "")]), th.get("colors", ["white", "yellow", "white"])):
        fill = (255, 205, 30) if col == "yellow" else (255, 255, 255)
        im = graphics.title_text(line, th.get("size", 120), fill=fill)
        frame.alpha_composite(im, ((W - im.width) // 2, y))
        y += im.height - 10
    if th.get("pill"):
        p = graphics.label_pill(th["pill"], size=60)
        frame.alpha_composite(p, ((W - p.width) // 2, H - 210))
    if G["wm"] is not None:
        frame.alpha_composite(G["wm"], (26, 34))
    if G.get("logo") is not None:
        lg = G["logo_src"].resize((230, 230), Image.LANCZOS)
        frame.alpha_composite(lg, (W - 250, H - 560))
    frame.convert("RGB").save(out, quality=92)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--preview", action="store_true", help="540x960 @15fps quick check")
    ap.add_argument("--stills", type=str, default=None, help="comma separated seconds -> PNGs only")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    args = ap.parse_args()

    ep = json.load(open(args.episode, encoding="utf-8"))
    name = os.path.splitext(os.path.basename(args.episode))[0]
    W, H = ep.get("size", [1080, 1920])
    fps = ep.get("fps", 30)
    if args.preview:
        W, H, fps = W // 2, H // 2, 15
    outdir = os.path.join(ROOT, "output", name)
    os.makedirs(outdir, exist_ok=True)

    t0 = time.time()
    print("[1/4] narration + timeline")
    _init_globals(ep, W, H, fps)
    tl = G["tl"]
    print(f"      duration {tl.duration:.1f}s, {len(tl.items)} items, {len(tl.cam_keys)} camera keys")

    if args.stills:
        for s in args.stills.split(","):
            fr = Image.frombytes("RGB", (W, H), render_frame(int(float(s) * fps)))
            fr.save(os.path.join(outdir, f"still_{float(s):05.1f}.png"))
        print("stills written to", outdir)
        return

    print("[2/4] audio mix")
    clips = [(t, audio.read_wav(p)) for t, p in tl.voice]
    sfx_lib = {"whoosh": audio.whoosh(), "pop": audio.pop()}
    sfx = [(t, sfx_lib[k]) for t, k in tl.sfx]
    music = None
    m = ep.get("music", "synth")
    if m == "synth":
        music = audio.music_bed(tl.duration)
    elif m:
        music = audio.read_wav(os.path.join(ROOT, m))
    wav = audio.mix(tl.duration, clips, sfx, music, ep.get("music_gain_db", -20), os.path.join(outdir, "mix.wav"),
                    ep.get("voice_fx", audio.VOICE_FX))

    print("[3/4] frames")
    n = int(tl.duration * fps)
    suffix = "_preview" if args.preview else ""
    out = os.path.join(outdir, f"{name}{suffix}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(fps), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset",
                           "veryfast" if args.preview else "medium", "-crf", "26" if args.preview else "17",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    ctx = mp.get_context("fork")
    with ctx.Pool(args.workers) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if k % (fps * 5) == 0:
                el = time.time() - t0
                print(f"      {k}/{n} frames  ({el:.0f}s)", flush=True)
    ff.stdin.close()
    ff.wait()

    print("[4/4] thumbnail + script")
    if not args.preview:
        thumbnail(ep, os.path.join(outdir, f"{name}_thumbnail.jpg"))
    with open(os.path.join(outdir, "captions.srt"), "w", encoding="utf-8") as f:
        for k, (a, b, txt) in enumerate(tl.captions, 1):
            f.write(f"{k}\n{_ts(a)} --> {_ts(b)}\n{txt}\n\n")
    # attribution for CC BY / BY-SA photos -> paste into the YouTube description
    cred_path = os.path.join(ROOT, "assets", "stickers", "credits.json")
    if os.path.exists(cred_path):
        creds = json.load(open(cred_path, encoding="utf-8"))
        used = {it["src"].get("sticker") for it in tl.items}
        lines = ["फ़ोटो क्रेडिट (Wikimedia Commons):"]
        for f, c in creds.items():
            if f in used:
                lines.append(f"- {c['title'][5:]} — {c['artist']} — {c['license']} — {c['page']}")
        lines += ["", "मैप: @svg-maps/india (CC BY 4.0), Natural Earth.", "आवाज़: AI (Google Gemini TTS)."]
        open(os.path.join(outdir, "credits.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"done in {time.time() - t0:.0f}s -> {out}")


def _ts(s):
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")


if __name__ == "__main__":
    sys.exit(main())
