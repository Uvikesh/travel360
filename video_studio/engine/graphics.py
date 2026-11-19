"""Overlay graphics: sticker cut-outs, label pills (Hindi, properly shaped via raqm), clouds, watermark."""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter

ROOT = os.path.join(os.path.dirname(__file__), "..")
FONTS = os.path.join(ROOT, "assets", "fonts")
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def font(size, hindi=True, weight="ExtraBold"):
    name = f"NotoSansDevanagari-{weight}.ttf" if hindi else f"Poppins-{weight}.ttf"
    return ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)


def _has_devanagari(s):
    return any("ऀ" <= ch <= "ॿ" for ch in s)


def outline_and_shadow(img, stroke=10, shadow=18, stroke_color=(255, 255, 255, 255)):
    """White sticker border + soft drop shadow around an RGBA cut-out (the reference 'portrait' look)."""
    pad = stroke + shadow * 2
    W, H = img.width + 2 * pad, img.height + 2 * pad
    a = Image.new("L", (W, H), 0)
    a.paste(img.getchannel("A"), (pad, pad))
    a = a.point(lambda v: 255 if v > 40 else 0)
    border = a.filter(ImageFilter.MaxFilter(2 * stroke + 1)).filter(ImageFilter.GaussianBlur(1))
    sh = border.filter(ImageFilter.GaussianBlur(shadow / 2)).point(lambda v: int(v * 0.55))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shadow_img.putalpha(sh)
    out.alpha_composite(shadow_img, (0, shadow // 2))
    b = Image.new("RGBA", (W, H), stroke_color)
    b.putalpha(border)
    out.alpha_composite(b)
    out.alpha_composite(img, (pad, pad))
    return out


def _remove_white_bg(im, tol=28):
    """Cut out an object shot on a plain white/light background (flood fill from the borders)."""
    from scipy.ndimage import label as cc_label, binary_dilation
    rgb = np.asarray(im.convert("RGB"), np.int16)
    light = (np.abs(rgb - 255).max(axis=2) <= tol)
    lab, _ = cc_label(light)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    if bg.mean() < 0.08:          # not really a white-background image -> keep as is
        return None
    alpha = (~bg).astype(np.uint8) * 255
    a = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA")
    out.putalpha(a)
    return out


def _round_badge(im):
    w, h = im.size
    s = min(w, h)
    im = im.convert("RGB").crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    m = Image.new("L", (s * 2, s * 2), 0)
    ImageDraw.Draw(m).ellipse((0, 0, s * 2 - 1, s * 2 - 1), fill=255)
    im.putalpha(m.resize((s, s), Image.LANCZOS))
    return im


def load_sticker(path, height):
    """User-supplied art: transparent PNG used as is; white-background AI images are cut out
    automatically; any other photo becomes a round badge."""
    im = Image.open(path).convert("RGBA")
    if im.getchannel("A").getextrema()[0] == 255:   # fully opaque
        cut = _remove_white_bg(im)
        im = cut if cut is not None else _round_badge(im)
    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    return outline_and_shadow(im)


def emoji_sticker(emoji, height, bg=(255, 236, 190)):
    """Placeholder sticker for practice runs: a round badge with a big colour emoji."""
    f = ImageFont.truetype(EMOJI_FONT, 109)
    e = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((80, 80), emoji, font=f, embedded_color=True, anchor="mm")
    bb = e.getbbox() or (0, 0, 160, 160)
    e = e.crop(bb)
    s = int(height * 0.72)
    e = e.resize((int(e.width * s / e.height), s), Image.LANCZOS)
    D = height
    badge = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    # radial gradient disc
    yy, xx = np.mgrid[0:D, 0:D]
    r = np.hypot(xx - D / 2, yy - D / 2) / (D / 2)
    col = np.array(bg, np.float32)
    rgb = np.clip(col[None, None] * (1.08 - 0.25 * r[..., None]), 0, 255).astype(np.uint8)
    alpha = (np.clip((1 - r) * D / 2, 0, 1) * 255).astype(np.uint8)
    badge = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    badge.alpha_composite(e, ((D - e.width) // 2, (D - e.height) // 2))
    return outline_and_shadow(badge, stroke=9)


def label_pill(text, size=46, fill=(255, 196, 30), fg=(20, 16, 10)):
    """Rounded yellow name tag like the reference (Hindi or English text)."""
    f = font(size, hindi=_has_devanagari(text))
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=f, anchor="ls")
    asc, desc = f.getmetrics()
    padx, pady = int(size * 0.55), int(size * 0.22)
    w = (r - l) + 2 * padx
    h = asc + desc + 2 * pady - int(size * 0.35)
    im = Image.new("RGBA", (w + 16, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 12, w + 8, h + 12), radius=h // 3, fill=(0, 0, 0, 110))  # shadow
    d.rounded_rectangle((8, 6, w + 8, h + 6), radius=h // 3, fill=fill + (255,), outline=(120, 70, 0, 255), width=3)
    d.text((8 + padx - l, 6 + pady + asc - int(size * 0.18)), text, font=f, fill=fg, anchor="ls")
    return im


def title_text(text, size, fill=(255, 255, 255), stroke=(0, 0, 0), stroke_w=None, hindi=None):
    hindi = _has_devanagari(text) if hindi is None else hindi
    f = font(size, hindi=hindi)
    stroke_w = stroke_w if stroke_w is not None else max(2, size // 12)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l, t, r, b = d.textbbox((0, 0), text, font=f, stroke_width=stroke_w)
    im = Image.new("RGBA", (r - l + 20, b - t + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((10 - l, 10 - t + 8), text, font=f, fill=(0, 0, 0, 120), stroke_width=stroke_w, stroke_fill=(0, 0, 0, 120))
    d.text((10 - l, 10 - t), text, font=f, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
    return im


def watermark(text, size=34):
    f = font(size, hindi=_has_devanagari(text), weight="Bold")
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    im = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), text, font=f, fill=(255, 255, 255, 150))
    return im


def clouds(W, H, seed=3, n_clouds=7):
    """Big soft white cumulus puffs near the frame edges (RGBA) for 'fly through the clouds' transitions."""
    rng = np.random.default_rng(seed)
    w, h = W // 2, H // 2
    a = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(a)
    anchors = [(0.05, 0.08), (0.95, 0.12), (0.0, 0.5), (1.0, 0.55), (0.1, 0.92), (0.9, 0.9), (0.5, 1.02), (0.5, -0.02)]
    for ax, ay in anchors[:n_clouds + 1]:
        cx, cy = ax * w, ay * h
        cw = w * rng.uniform(0.45, 0.7)
        for _ in range(9):
            r = cw * rng.uniform(0.16, 0.3)
            x = cx + rng.uniform(-0.5, 0.5) * cw
            y = cy + rng.uniform(-0.18, 0.12) * cw
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)
        d.rounded_rectangle((cx - cw * 0.55, cy, cx + cw * 0.55, cy + cw * 0.22), radius=int(cw * 0.1), fill=255)
    a = a.filter(ImageFilter.GaussianBlur(w / 140))
    al = np.asarray(a, np.float32) / 255
    # shading: lit from the top, greyish bellies
    sh = gaussian_filter(al, w / 60)
    gy = np.gradient(sh)[0]
    shade = np.clip(0.97 - 6.0 * np.maximum(-gy, 0) * w / 100 + 0.03, 0.72, 1.0)
    rgb = (np.dstack([shade * 255, shade * 255, shade * 258]).clip(0, 255)).astype(np.uint8)
    im = Image.fromarray(np.dstack([rgb, (al * 255).astype(np.uint8)]), "RGBA")
    return im.resize((W, H), Image.BICUBIC)


def icon_pill(emoji, text, size=52, fill=(255, 255, 255), fg=(20, 16, 10), outline=(255, 196, 30)):
    """Rounded button: colour emoji + Hindi text (e.g. 👍 लाइक)."""
    f = font(size, hindi=True)
    ef = ImageFont.truetype(EMOJI_FONT, 109)
    e = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((80, 80), emoji, font=ef, embedded_color=True, anchor="mm")
    e = e.crop(e.getbbox() or (0, 0, 160, 160))
    es = int(size * 1.15)
    e = e.resize((int(e.width * es / e.height), es), Image.LANCZOS)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l, t, r, b = d0.textbbox((0, 0), text, font=f, anchor="lm")
    pad = int(size * 0.5)
    w = pad + e.width + int(size * 0.3) + (r - l) + pad
    h = int(size * 1.9)
    im = Image.new("RGBA", (w + 12, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 12, w + 6, h + 12), radius=h // 2, fill=(0, 0, 0, 120))
    d.rounded_rectangle((6, 4, w + 6, h + 4), radius=h // 2, fill=fill + (255,), outline=outline + (255,), width=6)
    im.alpha_composite(e, (6 + pad, 4 + (h - e.height) // 2))
    d.text((6 + pad + e.width + int(size * 0.3) - l, 4 + h // 2), text, font=f, fill=fg, anchor="lm")
    return im
