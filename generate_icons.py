#!/usr/bin/env python3
"""Generate apple-touch-icon.png and favicon.ico for Chinook Web Co. (W-mountain design)."""

import math
from PIL import Image, ImageDraw

# Colours
BG        = (10,  10,  10,  255)   # #0a0a0a
MTN_TOP   = (147, 197, 253, 255)   # #93c5fd  peak colour
MTN_BOT   = ( 29,  78, 216, 255)   # #1d4ed8  base colour
ARC_MID   = ( 34, 211, 238, 255)   # #22d3ee  cyan arc centre
ARC_EDGE  = (  8, 145, 178, 255)   # #0891b2  cyan arc edges


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def cubic_bezier_pts(p0, p1, p2, p3, steps=300):
    pts = []
    for i in range(steps + 1):
        t  = i / steps
        mt = 1 - t
        x  = mt**3*p0[0] + 3*mt**2*t*p1[0] + 3*mt*t**2*p2[0] + t**3*p3[0]
        y  = mt**3*p0[1] + 3*mt**2*t*p1[1] + 3*mt*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


def polygon_scanfill_gradient(draw, size, pts_raw, s, y_top_norm, y_bot_norm, col_top, col_bot):
    """Scan-line fill a polygon with a vertical gradient."""
    pts = [(x * s, y * s) for x, y in pts_raw]
    y_min = int(math.floor(min(p[1] for p in pts)))
    y_max = int(math.ceil(max(p[1] for p in pts)))
    n = len(pts)

    for py in range(y_min, y_max + 1):
        xs = []
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            if (ay <= py < by) or (by <= py < ay):
                if abs(by - ay) < 1e-9:
                    continue
                t = (py - ay) / (by - ay)
                xs.append(ax + t * (bx - ax))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            x0, x1 = xs[k], xs[k + 1]
            span = (py / size - y_top_norm) / max(y_bot_norm - y_top_norm, 1e-9)
            color = lerp_color(col_top, col_bot, span)
            draw.line([(x0, py), (x1, py)], fill=color, width=1)


def draw_icon(size):
    s   = size / 64.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # ── Background (rounded rect) ────────────────────────────────
    bg_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw  = ImageDraw.Draw(bg_layer)
    radius   = round(13 * s)
    bg_draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BG)
    img = Image.alpha_composite(img, bg_layer)

    # ── W-mountain polygon ───────────────────────────────────────
    # Normalised points (64×64 space):
    # base-left, left-outer-peak, left-valley, centre-peak,
    # right-valley, right-outer-peak, base-right
    w_pts_norm = [
        (5,  57),
        (14, 19),
        (24, 37),
        (32, 23),
        (40, 37),
        (50, 19),
        (59, 57),
    ]

    mtn_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mtn_draw  = ImageDraw.Draw(mtn_layer)
    # y_top ≈ 19/64, y_bot ≈ 57/64 (normalised)
    polygon_scanfill_gradient(
        mtn_draw, size,
        w_pts_norm, s,
        19 / 64, 57 / 64,
        MTN_TOP, MTN_BOT,
    )
    img = Image.alpha_composite(img, mtn_layer)

    # ── Chinook arch (cubic bezier, cyan stroke) ─────────────────
    # SVG: M 5 43 C 5 4, 59 4, 59 43
    p0 = ( 5 * s, 43 * s)
    p1 = ( 5 * s,  4 * s)
    p2 = (59 * s,  4 * s)
    p3 = (59 * s, 43 * s)
    arc_pts = cubic_bezier_pts(p0, p1, p2, p3)

    arc_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    arc_draw  = ImageDraw.Draw(arc_layer)
    stroke    = max(2, round(4.5 * s))
    n_pts     = len(arc_pts)

    for i in range(n_pts - 1):
        t     = i / (n_pts - 1)
        # gradient: ARC_EDGE → ARC_MID → ARC_EDGE
        shade = 1 - abs(t - 0.5) * 2       # 0 at edges, 1 at centre
        color = lerp_color(ARC_EDGE, ARC_MID, shade)
        arc_draw.line([arc_pts[i], arc_pts[i + 1]], fill=color, width=stroke)

    img = Image.alpha_composite(img, arc_layer)
    return img


# ── apple-touch-icon.png (180×180) ───────────────────────────────
icon_180 = draw_icon(180)
icon_180.save("apple-touch-icon.png", "PNG")
print("✓ apple-touch-icon.png (180×180)")

# ── favicon.ico (16, 32, 48) ─────────────────────────────────────
frames = [draw_icon(s) for s in [16, 32, 48]]
frames[0].save(
    "favicon.ico",
    format="ICO",
    sizes=[(s, s) for s in [16, 32, 48]],
    append_images=frames[1:],
)
print("✓ favicon.ico (16×16, 32×32, 48×48)")
