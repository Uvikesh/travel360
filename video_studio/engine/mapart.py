"""Big pre-rendered map rasters (with mip-maps) in the style of the reference:
  * black sea, grey "plaster" textured neighbour land with a thin white coastline
  * India filled with a vertical gradient (blue -> purple -> red), same texture, faint white state borders
  * a label raster (state index per pixel) + a shading raster so any state can be re-coloured per frame

World window is in SVG units (see geo.py). Raster scale K px per SVG unit at mip level 0.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

from . import geo

WX0, WY0, WX1, WY1 = -200.0, -300.0, 820.0, 1000.0
K = 8
CACHE = os.path.join(os.path.dirname(__file__), "..", "output", "map_cache")

SEA = (16, 16, 18)
LAND = (150, 150, 152)
GRAD = [(0.00, (40, 50, 250)), (0.38, (60, 45, 240)), (0.58, (125, 35, 205)), (0.74, (200, 25, 140)), (0.88, (232, 22, 64)), (1.00, (238, 20, 50))]


def to_px(x, y, k=K):
    return ((x - WX0) * k, (y - WY0) * k)


def plaster(h, w, seed=7, strength=0.32):
    """Screen-space embossed 'plaster' texture -> uint8 shading image (128 == x1.0)."""
    rng = np.random.default_rng(seed)
    hs, ws = h // 2, w // 2
    n = np.zeros((hs, ws), np.float32)
    for sigma, amp in [(14, 1.0), (6, 0.35), (2.5, 0.06)]:
        n += amp * gaussian_filter(rng.standard_normal((hs, ws)).astype(np.float32), sigma)
    n /= n.std()
    gy, gx = np.gradient(n)
    light = -(gx * 0.7 + gy * 0.7)
    light = light / (np.abs(light).max() + 1e-6)
    shade = 1.0 + strength * light + 0.03 * n
    img = Image.fromarray(np.clip(shade * 128, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return img


def build(force=False):
    os.makedirs(CACHE, exist_ok=True)
    marker = os.path.join(CACHE, f"built_K{K}_v2.ok")
    if os.path.exists(marker) and not force:
        return
    W = int((WX1 - WX0) * K)
    H = int((WY1 - WY0) * K)
    print(f"  building map raster (one-time, cached) {W}x{H} ...")
    states = geo.india_states()
    ids = sorted(states)


    # --- land / sea
    land = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(land)
    for poly in geo.world_land():
        d.polygon([to_px(*p) for p in poly[0]], fill=255)
        for hole in poly[1:]:
            d.polygon([to_px(*p) for p in hole], fill=0)
    # --- india label map
    label = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(label)
    for i, sid in enumerate(ids, start=1):
        for r in states[sid]["rings"]:
            d.polygon([to_px(*p) for p in r], fill=i)
    lab = np.asarray(label)
    india = (lab > 0)

    # gradient colour by svg y
    ys = (np.arange(H) / K + WY0)
    t = np.clip(ys / 696.0, 0, 1)
    col = np.zeros((H, 3), np.float32)
    for c in range(3):
        col[:, c] = np.interp(t, [g[0] for g in GRAD], [g[1][c] for g in GRAD])

    lm = np.asarray(land, np.float32)[..., None] / 255.0
    rgb = np.empty((H, W, 3), np.float32)
    rgb[:] = np.array(SEA, np.float32)
    rgb = rgb * (1 - lm) + np.array(LAND, np.float32) * lm
    rgb = np.where(india[..., None], col[:, None, :], rgb)
    base = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))

    # --- lines: coastline (thin), state borders (faint), India outline (bold)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for poly in geo.world_land():
        d.line([to_px(*p) for p in poly[0]] + [to_px(*poly[0][0])], fill=(255, 255, 255, 120), width=max(1, K // 3))
    for sid in ids:
        for r in states[sid]["rings"]:
            d.line([to_px(*p) for p in r] + [to_px(*r[0])], fill=(255, 255, 255, 70), width=max(1, K // 4))
    base = Image.alpha_composite(base.convert("RGBA"), ov)
    # bold outline = edge of the india mask
    im = Image.fromarray((india * 255).astype(np.uint8))
    edge = np.asarray(im.filter(ImageFilter.MaxFilter(5)), np.int16) - np.asarray(
        im.filter(ImageFilter.MinFilter(3)), np.int16)
    edge = Image.fromarray(np.clip(edge, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    white.putalpha(edge)
    base = Image.alpha_composite(base, white).convert("RGB")

    # --- save mip levels
    for lvl in range(4):
        s = 2 ** lvl
        size = (W // s, H // s)
        (base if lvl == 0 else base.resize(size, Image.BOX)).save(os.path.join(CACHE, f"base_L{lvl}_K{K}.png"))
        (label if lvl == 0 else label.resize(size, Image.NEAREST)).save(os.path.join(CACHE, f"label_L{lvl}_K{K}.png"))
    with open(os.path.join(CACHE, "ids.txt"), "w") as f:
        f.write("\n".join(ids))
    open(marker, "w").write("ok")


class MapRasters:
    def __init__(self):
        build()
        Image.MAX_IMAGE_PIXELS = None
        self.ids = open(os.path.join(CACHE, "ids.txt")).read().split()
        self.index = {sid: i + 1 for i, sid in enumerate(self.ids)}
        self.base, self.label = [], []
        for lvl in range(4):
            self.base.append(Image.open(os.path.join(CACHE, f"base_L{lvl}_K{K}.png")).convert("RGB"))
            lab = Image.open(os.path.join(CACHE, f"label_L{lvl}_K{K}.png"))
            lab.load()
            self.label.append(lab)

    def view(self, cx, cy, zoom, W, H, highlight=None):
        """Render the map for camera centred at svg (cx,cy), `zoom` frame-px per svg unit.
        highlight: iterable of state ids -> returns (rgb Image, {sid: antialiased mask Image L})."""
        # choose mip level: the coarsest level that still has >= zoom px per unit
        lvl = 0
        while lvl < 3 and K / 2 ** (lvl + 1) >= zoom:
            lvl += 1
        k = K / 2 ** lvl
        x0 = (cx - W / 2 / zoom - WX0) * k
        y0 = (cy - H / 2 / zoom - WY0) * k
        x1 = (cx + W / 2 / zoom - WX0) * k
        y1 = (cy + H / 2 / zoom - WY0) * k
        box = (x0, y0, x1, y1)
        frame = _sample(self.base[lvl], box, W, H, Image.BILINEAR, SEA)
        masks = {}
        if highlight:
            lab = np.asarray(_sample(self.label[lvl], box, W, H, Image.NEAREST, 0))
            for sid in highlight:
                m = (lab == self.index[sid]).astype(np.uint8) * 255
                # soften edges a little (label raster is nearest-sampled)
                masks[sid] = Image.fromarray(m).filter(ImageFilter.GaussianBlur(0.8))
        return frame, masks


def _sample(img, box, W, H, resample, fill):
    """img.resize((W,H), box=box) that also works when the box leaves the raster (fills with `fill`)."""
    x0, y0, x1, y1 = box
    iw, ih = img.size
    if x0 >= 0 and y0 >= 0 and x1 <= iw and y1 <= ih:
        return img.resize((W, H), resample, box=box)
    sx, sy = W / (x1 - x0), H / (y1 - y0)
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(iw, x1), min(ih, y1)
    out = Image.new(img.mode, (W, H), fill)
    if cx1 <= cx0 or cy1 <= cy0:
        return out
    dx0, dy0 = int(round((cx0 - x0) * sx)), int(round((cy0 - y0) * sy))
    dw, dh = int(round((cx1 - cx0) * sx)), int(round((cy1 - cy0) * sy))
    if dw > 0 and dh > 0:
        out.paste(img.resize((dw, dh), resample, box=(cx0, cy0, cx1, cy1)), (dx0, dy0))
    return out
