from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "bonus-pad-v1.png"
QA_PREVIEW = ROOT / "qa" / "bonus-pad-v1-preview.png"

CELL = 256
COLS = 4
ROWS = 1
ANCHOR = (128, 256)
BASE_Y = 238


def rgba(hex_color, alpha=255):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


CYAN = "#42edff"
CYAN_DARK = "#087991"
VIOLET = "#a78bfa"
MAGENTA = "#ec4899"
GOLD = "#fef08a"
DEEP = "#071225"
INK = "#020712"


def draw_diamond(draw, ox, cx, cy, rx, ry, fill, outline=None, width=1):
    pts = [
        (ox + cx, cy - ry),
        (ox + cx + rx, cy),
        (ox + cx, cy + ry),
        (ox + cx - rx, cy),
    ]
    draw.polygon(pts, fill=fill)
    if outline:
        draw.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


def draw_ring(draw, ox, cx, cy, rx, ry, color, width=2, alpha=160):
    for i in range(width):
        draw.ellipse(
            [ox + cx - rx - i, cy - ry - i, ox + cx + rx + i, cy + ry + i],
            outline=rgba(color, max(0, alpha - i * 18)),
            width=1,
        )


def draw_glow(draw, ox, cx, cy, rx, ry, color, steps=5, alpha=56):
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        draw.ellipse(
            [ox + cx - rx * i / steps, cy - ry * i / steps,
             ox + cx + rx * i / steps, cy + ry * i / steps],
            fill=rgba(color, a),
        )


def draw_sparks(draw, ox, sparks, color=GOLD, alpha=210):
    for x, y, dx, dy in sparks:
        draw.line([ox + x - dx, y - dy, ox + x + dx, y + dy], fill=rgba(color, alpha), width=2)
        draw.line([ox + x - dy, y + dx, ox + x + dy, y - dx], fill=rgba(CYAN, alpha - 50), width=1)


def draw_motion_line(draw, ox, x, y1, y2, color, width=2, alpha=190):
    draw.line([ox + x, y1, ox + x, y2], fill=rgba(color, alpha), width=width)
    draw.point((ox + x, y1 - 2), fill=rgba(color, max(80, alpha - 60)))


def draw_spring(draw, ox, top_y, compressed=False, alpha=255):
    left = ox + 103
    right = ox + 153
    mid_left = ox + 111
    mid_right = ox + 145
    bottom = BASE_Y - 13
    coils = 4 if not compressed else 3
    span = bottom - (top_y + 24)
    points = []
    y = top_y + 24
    for i in range(coils * 2 + 1):
        t = i / (coils * 2)
        x = mid_left if i % 2 == 0 else mid_right
        points.append((x, int(y + span * t)))
    draw.line(points, fill=rgba(CYAN_DARK, int(alpha * 0.9)), width=9, joint="curve")
    draw.line(points, fill=rgba(CYAN, alpha), width=5, joint="curve")
    draw.line([(left, bottom + 3), (right, bottom + 3)], fill=rgba(VIOLET, int(alpha * 0.85)), width=5)
    draw.line([(left + 10, top_y + 18), (right - 10, top_y + 18)], fill=rgba(GOLD, int(alpha * 0.85)), width=3)


def draw_pad(draw, ox, frame):
    if frame == 0:
        top_y, glow_alpha, line_alpha = 151, 46, 155
    elif frame == 1:
        top_y, glow_alpha, line_alpha = 143, 72, 210
    elif frame == 2:
        top_y, glow_alpha, line_alpha = 176, 92, 240
    else:
        top_y, glow_alpha, line_alpha = 118, 72, 220

    fade = 225 if frame == 3 else 255

    # Tile-contact glow and base shadow.
    draw_glow(draw, ox, 128, BASE_Y - 1, 86, 21, CYAN, steps=5, alpha=glow_alpha)
    draw.ellipse([ox + 54, BASE_Y - 13, ox + 202, BASE_Y + 15], fill=rgba("#000615", 94))
    draw_ring(draw, ox, 128, BASE_Y - 3, 68, 18, CYAN, width=3, alpha=line_alpha)

    if frame == 2:
        draw_ring(draw, ox, 128, BASE_Y - 4, 88, 26, GOLD, width=4, alpha=220)
        for x1, y1, x2, y2 in [
            (52, 231, 24, 223), (204, 231, 232, 223),
            (72, 218, 39, 201), (184, 218, 217, 201),
            (88, 246, 55, 253), (168, 246, 201, 253),
        ]:
            draw.line([ox + x1, y1, ox + x2, y2], fill=rgba(GOLD, 218), width=3)
            draw.point((ox + x2, y2), fill=rgba("#ffffff", 230))

    # Base plate and spring.
    draw_diamond(draw, ox, 128, BASE_Y - 2, 74, 24, rgba(INK, 230), rgba(CYAN, 210), 3)
    draw_diamond(draw, ox, 128, BASE_Y - 6, 52, 16, rgba(DEEP, 230), rgba(VIOLET, 185), 2)
    draw_spring(draw, ox, top_y, compressed=(frame == 2), alpha=fade)

    # Top trampoline plate.
    draw_diamond(draw, ox, 128, top_y + 23, 67, 24, rgba(INK, 230), rgba(CYAN, fade), 4)
    draw_diamond(draw, ox, 128, top_y + 22, 49, 15, rgba("#0d2b4f", 235), rgba(VIOLET, 210), 2)
    draw.line([ox + 88, top_y + 22, ox + 168, top_y + 22], fill=rgba(GOLD, 205), width=2)
    draw.line([ox + 99, top_y + 13, ox + 157, top_y + 31], fill=rgba(MAGENTA, 145), width=2)

    if frame in (0, 1):
        draw_sparks(draw, ox, [(72, top_y + 7, 4, 7), (187, top_y + 4, 5, 5)], alpha=150 if frame == 0 else 215)
    if frame == 1:
        draw.line([ox + 68, 164, ox + 83, 153, ox + 76, 139], fill=rgba(CYAN, 210), width=3)
        draw.line([ox + 190, 164, ox + 174, 151, ox + 181, 137], fill=rgba(MAGENTA, 200), width=3)
        draw_sparks(draw, ox, [(52, 188, 5, 7), (205, 183, 6, 6), (128, 112, 4, 5)], alpha=205)
    if frame == 3:
        # Launch beam and upward motion. Kept inside the frame bounds.
        draw_glow(draw, ox, 128, 83, 34, 64, CYAN, steps=5, alpha=45)
        draw.polygon(
            [(ox + 117, 33), (ox + 128, 12), (ox + 139, 33), (ox + 134, 33),
             (ox + 134, 111), (ox + 122, 111), (ox + 122, 33)],
            fill=rgba(CYAN, 135),
        )
        draw.line([ox + 128, 22, ox + 128, 109], fill=rgba("#ffffff", 170), width=3)
        for x, y1, y2, color in [(92, 77, 39, VIOLET), (105, 96, 52, CYAN), (154, 99, 48, GOLD), (171, 80, 35, MAGENTA)]:
            draw_motion_line(draw, ox, x, y1, y2, color, width=2, alpha=190)
        draw_sparks(draw, ox, [(75, 108, 5, 6), (184, 94, 4, 8), (199, 138, 5, 5)], alpha=205)


def make_sheet():
    img = Image.new("RGBA", (CELL * COLS, CELL * ROWS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    for frame in range(COLS):
        ox = frame * CELL
        draw_pad(draw, ox, frame)
    return img


def make_preview(sheet):
    scale = 1
    pad = 22
    label_h = 36
    w = sheet.width + pad * 2
    h = sheet.height + pad * 2 + label_h
    preview = Image.new("RGBA", (w, h), rgba("#070915", 255))
    d = ImageDraw.Draw(preview, "RGBA")
    tile = 16
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            color = "#101944" if ((x // tile + y // tile) % 2) else "#0a1028"
            d.rectangle([x, y, x + tile - 1, y + tile - 1], fill=rgba(color, 255))
    preview.alpha_composite(sheet, (pad, pad + label_h))
    y0 = pad + label_h
    d.rectangle([pad, y0, pad + sheet.width - 1, y0 + sheet.height - 1], outline=rgba(CYAN, 220), width=2)
    for c in range(COLS + 1):
        x = pad + c * CELL * scale
        d.line([x, y0, x, y0 + sheet.height], fill=rgba("#ffffff", 80), width=1)
    d.line([pad, y0 + BASE_Y, pad + sheet.width, y0 + BASE_Y], fill=rgba(GOLD, 210), width=2)
    for c, label in enumerate(["spawn", "ready", "compress", "launch"]):
        x = pad + c * CELL + 12
        d.text((x, pad + 8), label, fill=rgba("#dffbff", 255))
        d.ellipse([pad + c * CELL + ANCHOR[0] - 3, y0 + ANCHOR[1] - 5,
                   pad + c * CELL + ANCHOR[0] + 3, y0 + ANCHOR[1] + 1], fill=rgba(CYAN, 230))
    return preview


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    QA_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    sheet = make_sheet()
    sheet.save(OUT)
    make_preview(sheet).save(QA_PREVIEW)
    print(f"wrote {OUT}")
    print(f"wrote {QA_PREVIEW}")


if __name__ == "__main__":
    main()
