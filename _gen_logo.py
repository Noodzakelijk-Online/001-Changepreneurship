"""Generate Changepreneurship logo — 512×512 dark-themed PNG."""
from PIL import Image, ImageDraw
import math

SIZE    = 512
CORNER  = 80
OUT_512 = "e:/GIT/001-Changepreneurship/changepreneurship-enhanced/public/logo.png"
OUT_192 = "e:/GIT/001-Changepreneurship/changepreneurship-enhanced/public/logo-192.png"

# Brand colours
CYAN   = (6,  182, 212)
PURPLE = (168,  85, 247)

# ── Helpers ─────────────────────────────────────────────────────────────────

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_canvas(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # vertical gradient background: very dark navy → deep indigo
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    for y in range(size):
        t  = y / (size - 1)
        r  = int(10 + 14 * t)
        g  = int(9  +  4 * t)
        b  = int(20 + 24 * t)
        bd.line([(0, y), (size - 1, y)], fill=(r, g, b, 255))

    # round-rect mask
    msk = Image.new("L", (size, size), 0)
    ImageDraw.Draw(msk).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=CORNER, fill=255
    )
    bg.putalpha(msk)
    img.paste(bg, mask=bg)
    return img


def draw_bars(img, size):
    """Three ascending gradient bars."""
    BAR_W   = int(size * 0.140)   # ≈72 px at 512
    GAP     = int(size * 0.043)   # ≈22 px
    HEIGHTS = [
        int(size * 0.230),       # left  (short)
        int(size * 0.336),       # mid
        int(size * 0.469),       # right (tall)
    ]
    BOTTOM  = int(size * 0.655)
    BRADIUS = int(size * 0.024)  # rounded bar corners

    total_w = 3 * BAR_W + 2 * GAP
    sx = (size - total_w) // 2

    bars = []
    for i, h in enumerate(HEIGHTS):
        x0 = sx + i * (BAR_W + GAP)
        bars.append((x0, BOTTOM - h, x0 + BAR_W, BOTTOM))

    # ── Horizontal gradient layer (cyan → purple across bar span) ────────
    gx0   = bars[0][0]
    gx1   = bars[2][2]
    gspan = gx1 - gx0

    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for x in range(gx0, gx1 + 1):
        t   = (x - gx0) / max(1, gspan)
        col = lerp_color(CYAN, PURPLE, t)
        gd.line([(x, 0), (x, size - 1)], fill=(*col, 255))

    # ── Bar mask ─────────────────────────────────────────────────────────
    bar_mask = Image.new("L", (size, size), 0)
    bmd      = ImageDraw.Draw(bar_mask)
    for (x0, y0, x1, y1) in bars:
        bmd.rounded_rectangle([x0, y0, x1, y1], radius=BRADIUS, fill=255)

    grad.putalpha(bar_mask)
    result = Image.alpha_composite(img, grad)

    # ── White highlight stripe on top of each bar ────────────────────────
    hd  = ImageDraw.Draw(result)
    for (x0, y0, x1, y1) in bars:
        pad = max(4, BAR_W // 9)
        hd.rounded_rectangle(
            [x0 + pad, y0 + pad, x1 - pad, y0 + pad + max(3, BAR_W // 14)],
            radius=2,
            fill=(255, 255, 255, 80),
        )

    return result, bars


def draw_arrow(img, bars, size):
    """Upward arrow above the tallest (right-most) bar."""
    bar   = bars[2]
    cx    = (bar[0] + bar[2]) // 2
    tip_y = bar[1] - int(size * 0.055)
    base_y = bar[1] - int(size * 0.008)
    hw    = int(size * 0.050)     # arrowhead half-width
    sw    = int(size * 0.016)     # shaft half-width
    neck_y = tip_y + int(size * 0.052)

    poly = [
        (cx,          tip_y),
        (cx - hw,     neck_y),
        (cx - sw,     neck_y),
        (cx - sw,     base_y),
        (cx + sw,     base_y),
        (cx + sw,     neck_y),
        (cx + hw,     neck_y),
    ]
    draw = ImageDraw.Draw(img)
    draw.polygon(poly, fill=(220, 160, 255, 235))
    return img


def draw_connector_dots(img, bars, size):
    """Small dots at the top-centre of each bar linking the growth line."""
    draw = ImageDraw.Draw(img)
    r    = max(4, int(size * 0.009))
    for (x0, y0, x1, y1) in bars:
        cx = (x0 + x1) // 2
        draw.ellipse([cx - r, y0 - r, cx + r, y0 + r],
                     fill=(255, 255, 255, 180))


def draw_glow_border(img, size):
    """Thin faint gradient ring around the rounded square edge."""
    for offset, alpha in [(3, 55), (6, 35), (9, 20)]:
        layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle(
            [offset, offset, size - 1 - offset, size - 1 - offset],
            radius=CORNER - offset // 2,
            outline=(*CYAN, alpha),
            width=2,
        )
        img = Image.alpha_composite(img, layer)
    return img


def draw_inner_glow(img, bars, size):
    """Soft glow bloom under the bars (bar shadow/reflection)."""
    bar_bottom = bars[0][3]
    tx0 = bars[0][0] - int(size * 0.02)
    tx1 = bars[2][2] + int(size * 0.02)
    for i in range(20):
        alpha = max(0, 60 - i * 4)
        layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(
            [tx0 - i * 2, bar_bottom - 6 + i,
             tx1 + i * 2, bar_bottom + 14 + i],
            fill=(*CYAN, alpha),
        )
        img = Image.alpha_composite(img, layer)
    return img


# ── Build logo ───────────────────────────────────────────────────────────────

canvas, bars     = draw_bars(make_canvas(SIZE), SIZE)
canvas           = draw_arrow(canvas, bars, SIZE)
draw_connector_dots(canvas, bars, SIZE)
canvas           = draw_inner_glow(canvas, bars, SIZE)
canvas           = draw_glow_border(canvas, SIZE)

canvas.save(OUT_512, "PNG")

# 192-px variant for PWA manifest
canvas.resize((192, 192), Image.LANCZOS).save(OUT_192, "PNG")

print(f"✓  {OUT_512}")
print(f"✓  {OUT_192}")
