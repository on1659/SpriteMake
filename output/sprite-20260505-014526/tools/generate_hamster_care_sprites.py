from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
QA = ROOT / "qa"

CELL = 256
ANCHOR = (128, 220)
BASELINE_Y = 220

FUR = (201, 145, 86, 255)
FUR_DARK = (151, 93, 49, 255)
CREAM = (252, 229, 185, 255)
PINK = (239, 135, 145, 255)
SHADOW = (133, 83, 48, 70)
LINE = (93, 58, 39, 255)
BLACK = (35, 28, 24, 255)
WHITE = (255, 250, 237, 255)


def aa_canvas(size):
    scale = 3
    return Image.new("RGBA", (size[0] * scale, size[1] * scale), (0, 0, 0, 0)), scale


def downsample(img, scale):
    return img.resize((img.width // scale, img.height // scale), Image.Resampling.LANCZOS)


def ellipse(draw, box, fill, outline=None, width=1, scale=1):
    box = tuple(int(v * scale) for v in box)
    draw.ellipse(box, fill=fill, outline=outline, width=max(1, int(width * scale)))


def rounded(draw, box, radius, fill, outline=None, width=1, scale=1):
    box = tuple(int(v * scale) for v in box)
    draw.rounded_rectangle(box, radius=int(radius * scale), fill=fill, outline=outline, width=max(1, int(width * scale)))


def polygon(draw, points, fill, outline=None, scale=1):
    points = [(int(x * scale), int(y * scale)) for x, y in points]
    draw.polygon(points, fill=fill, outline=outline)


def line(draw, points, fill, width=1, scale=1):
    points = [(int(x * scale), int(y * scale)) for x, y in points]
    draw.line(points, fill=fill, width=max(1, int(width * scale)), joint="curve")


def hamster_frame(row, col):
    img, s = aa_canvas((CELL, CELL))
    d = ImageDraw.Draw(img)

    bob = [0, -3, -1, 2][col] if row == 0 else 0
    step = [-6, 3, 7, -2][col] if row == 1 else 0
    chew = [0, 2, 0, -1][col] if row == 2 else 0
    sleep_squash = [0, 3, 4, 2][col] if row == 3 else 0

    # Soft contact shadow stays on the source plane.
    ellipse(d, (62, BASELINE_Y - 9, 194, BASELINE_Y + 9), SHADOW, scale=s)

    if row == 3:
        # Curled sleeping hamster, still anchored on the same baseline.
        ellipse(d, (55, 105 + sleep_squash, 202, 218), FUR, LINE, 3, s)
        ellipse(d, (92, 130 + sleep_squash, 184, 209), CREAM, None, 1, s)
        ellipse(d, (52, 118 + sleep_squash, 90, 154), FUR_DARK, LINE, 3, s)
        ellipse(d, (63, 129 + sleep_squash, 81, 147), PINK, None, 1, s)
        line(d, [(105, 152 + sleep_squash), (122, 150 + sleep_squash), (139, 153 + sleep_squash)], BLACK, 3, s)
        ellipse(d, (144, 174 + sleep_squash, 160, 190), PINK, None, 1, s)
        ellipse(d, (167, 174 + sleep_squash, 183, 190), PINK, None, 1, s)
        line(d, [(79, 181 + sleep_squash), (98, 188 + sleep_squash), (118, 187 + sleep_squash)], LINE, 3, s)
        return downsample(img, s)

    body_y = 92 + bob
    head_y = 54 + bob
    if row == 1:
        body_y += abs(step) // 4
        head_y += abs(step) // 5
    if row == 2:
        body_y += 1
        head_y += chew

    # Ears behind head.
    ellipse(d, (55 + step * 0.2, head_y + 10, 91 + step * 0.2, head_y + 48), FUR, LINE, 3, s)
    ellipse(d, (165 + step * 0.2, head_y + 10, 201 + step * 0.2, head_y + 48), FUR, LINE, 3, s)
    ellipse(d, (64 + step * 0.2, head_y + 20, 82 + step * 0.2, head_y + 39), PINK, None, 1, s)
    ellipse(d, (174 + step * 0.2, head_y + 20, 192 + step * 0.2, head_y + 39), PINK, None, 1, s)

    # Body and head.
    ellipse(d, (50 + step * 0.15, body_y, 206 + step * 0.15, 222), FUR, LINE, 4, s)
    ellipse(d, (72 + step * 0.2, head_y, 184 + step * 0.2, head_y + 109), FUR, LINE, 4, s)
    ellipse(d, (82 + step * 0.15, body_y + 41, 174 + step * 0.15, 214), CREAM, None, 1, s)
    ellipse(d, (95 + step * 0.2, head_y + 47, 161 + step * 0.2, head_y + 95), CREAM, None, 1, s)

    # Face.
    blink = row == 0 and col == 2
    if blink:
        line(d, [(98 + step * 0.2, head_y + 49), (111 + step * 0.2, head_y + 51)], BLACK, 3, s)
        line(d, [(145 + step * 0.2, head_y + 51), (158 + step * 0.2, head_y + 49)], BLACK, 3, s)
    else:
        ellipse(d, (98 + step * 0.2, head_y + 43, 111 + step * 0.2, head_y + 58), BLACK, scale=s)
        ellipse(d, (145 + step * 0.2, head_y + 43, 158 + step * 0.2, head_y + 58), BLACK, scale=s)
        ellipse(d, (102 + step * 0.2, head_y + 45, 106 + step * 0.2, head_y + 49), WHITE, scale=s)
        ellipse(d, (149 + step * 0.2, head_y + 45, 153 + step * 0.2, head_y + 49), WHITE, scale=s)

    ellipse(d, (122 + step * 0.2, head_y + 61, 134 + step * 0.2, head_y + 70), PINK, LINE, 1, s)
    line(d, [(128 + step * 0.2, head_y + 70), (128 + step * 0.2, head_y + 78)], LINE, 2, s)
    line(d, [(128 + step * 0.2, head_y + 78), (119 + step * 0.2, head_y + 84)], LINE, 2, s)
    line(d, [(128 + step * 0.2, head_y + 78), (137 + step * 0.2, head_y + 84)], LINE, 2, s)
    ellipse(d, (78 + step * 0.2, head_y + 63, 96 + step * 0.2, head_y + 79), PINK, scale=s)
    ellipse(d, (160 + step * 0.2, head_y + 63, 178 + step * 0.2, head_y + 79), PINK, scale=s)

    # Whiskers.
    line(d, [(99 + step * 0.2, head_y + 69), (72 + step * 0.2, head_y + 62)], LINE, 2, s)
    line(d, [(99 + step * 0.2, head_y + 76), (70 + step * 0.2, head_y + 77)], LINE, 2, s)
    line(d, [(157 + step * 0.2, head_y + 69), (184 + step * 0.2, head_y + 62)], LINE, 2, s)
    line(d, [(157 + step * 0.2, head_y + 76), (186 + step * 0.2, head_y + 77)], LINE, 2, s)

    if row == 2:
        # Seed and paws during eating.
        ellipse(d, (110, 152 + chew, 146, 187 + chew), (226, 177, 89, 255), LINE, 3, s)
        line(d, [(119, 163 + chew), (138, 175 + chew)], (154, 101, 39, 255), 2, s)
        ellipse(d, (87, 157 + chew, 115, 185 + chew), CREAM, LINE, 3, s)
        ellipse(d, (141, 157 + chew, 169, 185 + chew), CREAM, LINE, 3, s)
    else:
        # Paws and feet.
        paw_shift = step if row == 1 else 0
        ellipse(d, (82 + paw_shift * 0.3, 157, 113 + paw_shift * 0.3, 187), CREAM, LINE, 3, s)
        ellipse(d, (143 - paw_shift * 0.3, 157, 174 - paw_shift * 0.3, 187), CREAM, LINE, 3, s)
        ellipse(d, (75 + paw_shift, 207, 113 + paw_shift, 226), CREAM, LINE, 3, s)
        ellipse(d, (143 - paw_shift, 207, 181 - paw_shift, 226), CREAM, LINE, 3, s)

    return downsample(img, s)


def item_frame(kind):
    img, s = aa_canvas((CELL, CELL))
    d = ImageDraw.Draw(img)
    ellipse(d, (54, BASELINE_Y - 8, 202, BASELINE_Y + 8), SHADOW, scale=s)

    if kind == "food_bowl":
        rounded(d, (63, 150, 193, 220), 24, (108, 169, 200, 255), LINE, 4, s)
        ellipse(d, (60, 137, 196, 178), (143, 203, 229, 255), LINE, 4, s)
        ellipse(d, (84, 128, 112, 156), (221, 164, 82, 255), LINE, 2, s)
        ellipse(d, (113, 119, 144, 152), (234, 183, 101, 255), LINE, 2, s)
        ellipse(d, (144, 130, 172, 157), (209, 138, 70, 255), LINE, 2, s)
    elif kind == "water_bottle":
        rounded(d, (100, 50, 156, 178), 18, (154, 211, 236, 205), LINE, 4, s)
        rounded(d, (111, 35, 145, 62), 9, (92, 151, 186, 255), LINE, 3, s)
        polygon(d, [(128, 178), (153, 216), (139, 222), (116, 184)], (152, 152, 160, 255), LINE, s)
        ellipse(d, (147, 211, 159, 223), (93, 171, 220, 255), LINE, 2, s)
        ellipse(d, (116, 82, 142, 110), (232, 249, 255, 130), scale=s)
    elif kind == "exercise_wheel":
        ellipse(d, (55, 48, 201, 194), (217, 226, 232, 255), LINE, 5, s)
        ellipse(d, (78, 71, 178, 171), (245, 250, 250, 255), LINE, 3, s)
        line(d, [(128, 121), (128, 53)], (111, 139, 152, 255), 4, s)
        line(d, [(128, 121), (190, 88)], (111, 139, 152, 255), 4, s)
        line(d, [(128, 121), (182, 165)], (111, 139, 152, 255), 4, s)
        line(d, [(128, 121), (74, 165)], (111, 139, 152, 255), 4, s)
        line(d, [(128, 121), (66, 88)], (111, 139, 152, 255), 4, s)
        line(d, [(95, 220), (128, 180), (161, 220)], LINE, 6, s)
    elif kind == "bed":
        rounded(d, (54, 136, 202, 218), 26, (238, 155, 165, 255), LINE, 4, s)
        rounded(d, (70, 117, 129, 158), 15, (255, 222, 226, 255), LINE, 3, s)
        rounded(d, (123, 129, 188, 172), 15, (247, 184, 193, 255), LINE, 3, s)
        line(d, [(62, 183), (194, 183)], (205, 111, 126, 255), 4, s)
    return downsample(img, s)


def paste_grid(frames, cols, rows, out_path):
    atlas = Image.new("RGBA", (cols * CELL, rows * CELL), (0, 0, 0, 0))
    for r in range(rows):
        for c in range(cols):
            atlas.alpha_composite(frames[r][c], (c * CELL, r * CELL))
    atlas.save(out_path)
    return atlas


def alpha_bbox(im):
    return im.getchannel("A").getbbox()


def report_image(name, im, cols, rows):
    lines = [
        f"{name}",
        f"size: {im.width}x{im.height}",
        f"grid: {cols}x{rows}",
        f"cell: {im.width // cols}x{im.height // rows}",
        f"mod: width%cols={im.width % cols}, height%rows={im.height % rows}",
        f"full alpha bbox: {alpha_bbox(im)}",
        "corner alpha: "
        + str([
            im.getpixel((0, 0))[3],
            im.getpixel((im.width - 1, 0))[3],
            im.getpixel((0, im.height - 1))[3],
            im.getpixel((im.width - 1, im.height - 1))[3],
        ]),
    ]
    cw, ch = im.width // cols, im.height // rows
    for r in range(rows):
        cells = []
        for c in range(cols):
            cell = im.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
            cells.append(f"{c}:{alpha_bbox(cell)}")
        lines.append(f"row {r}: " + " ".join(cells))
    return "\n".join(lines)


def main():
    GENERATED.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)

    hamster_rows = [[hamster_frame(r, c) for c in range(4)] for r in range(4)]
    hamster = paste_grid(hamster_rows, 4, 4, GENERATED / "hamster_care_atlas.png")

    items = [[
        item_frame("food_bowl"),
        item_frame("water_bottle"),
        item_frame("exercise_wheel"),
        item_frame("bed"),
    ]]
    item_atlas = paste_grid(items, 4, 1, GENERATED / "hamster_care_items.png")

    report = "\n\n".join([
        report_image("hamster_care_atlas.png", hamster, 4, 4),
        report_image("hamster_care_items.png", item_atlas, 4, 1),
    ])
    (QA / "hamster_care_bbox_report.txt").write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
