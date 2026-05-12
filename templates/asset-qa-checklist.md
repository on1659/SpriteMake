# Asset QA Checklist

Run this checklist after receiving or generating a game asset. The goal is to catch coordinate problems before they become code-side magic numbers.

## Request Brief Fit

- Asset matches the requested game/concept.
- Asset fits the intended scene or screen.
- Gameplay role is visually readable.
- Player-readable purpose is clear at the intended in-game scale.
- Visual direction matches the requested style family.
- Existing asset proportions, angle, outline weight, and lighting are respected.

## File And Format

- Final path matches the requested path.
- Final size is exactly the requested `{width}x{height}`.
- PNG has RGBA channels.
- Alpha is straight alpha, not premultiplied alpha.
- Background is transparent where expected.
- No guide grid, labels, text, watermark, or unrequested objects remain.

## Grid And Cell Slicing

- `width % columns === 0`.
- `height % rows === 0`.
- Cell size matches the manifest.
- Every cell contains exactly one intended frame.
- No frame crosses into a neighboring cell.
- No cell is empty.
- Row order and column order match the request.
- Any source/contact-sheet image was repacked into a strict atlas before use.

## Anchor And Baseline

- Contact anchor pixel is documented.
- Anchor meaning is documented: foot, bag bottom, tile contact, platform origin, impact center, etc.
- Anchor is not confused with visual center.
- Grounded frames touch the same local Y baseline.
- Horizontal drift is expected and intentional, not caused by loose spacing.
- If the asset has variants, all variants share the same anchor and baseline.

## Y-Axis Plane Alignment

Use this for tiles, platforms, FX rows, and anything derived from the same object.

- Related rows share the same implied source plane Y.
- `crack` and `break_shards` style rows line up when guide lines are overlaid.
- `warning_glow`, `landing_pulse`, and `restore` style rows expand around the same source plane instead of shifting upward.
- Particles, shards, dust, and trails may move, but the original object plane does not jump.
- Animation does not appear to float, drop, or snap because of row-to-row Y drift.

## Animation Preview Tool

Use this for sprite atlases with animation frames.

- A local HTML animation preview tool exists for the asset.
- The tool loads the intended manifest and target PNG.
- The tool can switch sheet, animation, palette/variant if applicable, FPS, and scale.
- The tool shows both a stage preview and the full sprite sheet.
- The full sheet view shows exact grid lines, selected frame bounds, contact anchors, and Y-axis baseline/source plane.
- The stage preview makes row-to-row drift, crop errors, and anchor mistakes visible.
- Tool paths are project-relative or user-configurable, not hardcoded to a temporary local source path.

## Alpha BBox

For each output:

- Report full-image alpha bbox.
- Report per-cell alpha bbox for sprite atlases when possible.
- Confirm transparent corners for transparent assets.
- Confirm no accidental colored key fringe remains.
- If the bbox changed, report whether code placement needs an offset update.

## Pixel/Visual Quality

- No blur from resizing.
- No antialias cleanup pass that softens pixel art.
- No unexpected cast shadow outside the cell/layer.
- Character/FX silhouette remains readable at in-game display size.
- Color variants change only intended color regions.
- Lighting and outline weight match neighboring assets.

## Quick Pillow Probe

```python
from pathlib import Path
from PIL import Image

path = Path("asset.png")
cols, rows = 4, 6
im = Image.open(path).convert("RGBA")
cw, ch = im.width // cols, im.height // rows

print("size", im.size, "cell", (cw, ch), "mod", (im.width % cols, im.height % rows))
print("full alpha bbox", im.getchannel("A").getbbox())
print("corner alpha", [
    im.getpixel((0, 0))[3],
    im.getpixel((im.width - 1, 0))[3],
    im.getpixel((0, im.height - 1))[3],
    im.getpixel((im.width - 1, im.height - 1))[3],
])

for r in range(rows):
    cells = []
    for c in range(cols):
        cell = im.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
        cells.append(f"{c}:{cell.getchannel('A').getbbox()}")
    print("row", r, " ".join(cells))
```

## QA Report Template

```text
Asset QA Report:
- File:
- Final size:
- Format:
- Full alpha bbox:
- Grid:
- Cell size:
- Contact anchor:
- Y baseline:
- Per-cell bbox summary:
- Plane alignment result:
- Issues found:
- Code offset required:
```


