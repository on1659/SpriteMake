from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
QA = ROOT / "qa"
SOURCE = ASSETS / "hamster_2d_sheet_source.png"
OUT = ASSETS / "hamster_game_atlas.png"
REPORT = QA / "hamster_game_atlas_repack_report.txt"

CELL = 256
COLS = 4
ROWS = 5
ANCHOR_X = 128
BASELINE_Y = 226

SOURCE_W = 1402
SOURCE_H = 1122
ROW_BANDS = [
    (0, 260),
    (260, 486),
    (486, 704),
    (704, 886),
    (886, 1122),
]
COL_CENTERS = [175, 526, 876, 1227]
COL_WIDTHS = [340, 320, 320, 380]

CHAR_TARGETS = [
    (174, 192),
    (178, 180),
    (176, 190),
    (190, 132),
]
PROP_TARGETS = [
    (170, 112),
    (102, 172),
    (166, 180),
    (178, 142),
]


def is_background(pixel):
    r, g, b, _ = pixel
    hi = max(r, g, b)
    lo = min(r, g, b)
    return hi > 218 and hi - lo < 34


def remove_edge_background(img):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    seen = [[False] * w for _ in range(h)]
    q = deque()

    def push(x, y):
      if x < 0 or y < 0 or x >= w or y >= h or seen[y][x]:
          return
      if not is_background(px[x, y]):
          return
      seen[y][x] = True
      q.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while q:
        x, y = q.popleft()
        r, g, b, _ = px[x, y]
        px[x, y] = (r, g, b, 0)
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)

    return img


def alpha_bbox(img):
    return img.getchannel("A").getbbox()


def crop_source(src, row, col):
    sx_scale = src.width / SOURCE_W
    sy_scale = src.height / SOURCE_H
    top, bottom = ROW_BANDS[row]
    cx = COL_CENTERS[col]
    col_w = COL_WIDTHS[col]
    sx = int(round((cx - col_w / 2) * sx_scale))
    sw = int(round(col_w * sx_scale))
    sy = int(round(top * sy_scale))
    sh = int(round((bottom - top) * sy_scale))
    sx = max(0, min(src.width - sw, sx))
    crop = src.crop((sx, sy, sx + sw, sy + sh))
    crop = remove_edge_background(crop)
    bbox = alpha_bbox(crop)
    if not bbox:
        return crop, (0, 0, crop.width, crop.height)
    return crop.crop(bbox), bbox


def paste_centered(atlas, sprite, row, col, target_w, target_h):
    scale = min(target_w / sprite.width, target_h / sprite.height)
    new_w = max(1, int(round(sprite.width * scale)))
    new_h = max(1, int(round(sprite.height * scale)))
    resized = sprite.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = col * CELL + ANCHOR_X - new_w // 2
    y = row * CELL + BASELINE_Y - new_h
    atlas.alpha_composite(resized, (x, y))
    return {
        "paste": (x - col * CELL, y - row * CELL, x - col * CELL + new_w, y - row * CELL + new_h),
        "scale": round(scale, 4),
        "size": (new_w, new_h),
    }


def main():
    QA.mkdir(parents=True, exist_ok=True)
    src = Image.open(SOURCE).convert("RGBA")
    atlas = Image.new("RGBA", (COLS * CELL, ROWS * CELL), (0, 0, 0, 0))
    report = [
        "hamster_game_atlas.png",
        f"source: {SOURCE}",
        f"output: {OUT}",
        f"canvas: {COLS * CELL}x{ROWS * CELL}",
        f"grid: {COLS}x{ROWS}",
        f"cell: {CELL}x{CELL}",
        f"anchor: x={ANCHOR_X}, y={BASELINE_Y}",
        "",
    ]

    for row in range(ROWS):
        for col in range(COLS):
            sprite, source_bbox = crop_source(src, row, col)
            if row < 4:
                target_w, target_h = CHAR_TARGETS[row]
            else:
                target_w, target_h = PROP_TARGETS[col]
            info = paste_centered(atlas, sprite, row, col, target_w, target_h)
            report.append(
                f"row {row} col {col}: source_bbox={source_bbox} "
                f"paste_bbox={info['paste']} size={info['size']} scale={info['scale']}"
            )

    atlas.save(OUT)
    report.append("")
    report.append(f"full alpha bbox: {alpha_bbox(atlas)}")
    for row in range(ROWS):
        cells = []
        for col in range(COLS):
            cell = atlas.crop((col * CELL, row * CELL, (col + 1) * CELL, (row + 1) * CELL))
            cells.append(f"{col}:{alpha_bbox(cell)}")
        report.append(f"row {row}: " + " ".join(cells))

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
