# Asset QA Checklist

Run this checklist after receiving or generating a game asset. The goal is to catch coordinate problems before they become code-side magic numbers.

## Request Brief Fit

- Asset matches the requested game/concept.
- Asset fits the intended scene or screen.
- Gameplay role is visually readable.
- Player-readable purpose is clear at the intended in-game scale.
- Visual direction matches the requested style family.
- Existing asset proportions, angle, outline weight, and lighting are respected.
- When this extends an existing character, the reference image and its checksum
  are recorded, and a side-by-side comparison is attached for visual approval.
- Animated character states derive from an accepted base and one approved
  single-pose reference per actual direction. Identity, motion timing and layout
  geometry inputs have separate documented roles.
- Asymmetric features retain their physical side; any mirrored derivation was
  explicitly approved and its source/transform recorded.

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
- Related frames use a common documented scale and reproducible offsets, not
  independent bbox normalization to fill every cell.

## Anchor And Baseline

- Contact anchor pixel is documented.
- Anchor meaning is documented: foot, bag bottom, tile contact, platform origin, impact center, etc.
- Anchor is not confused with visual center.
- Grounded frames touch the same local Y baseline.
- Horizontal drift is expected and intentional, not caused by loose spacing.
- If the asset has variants, all variants share the same anchor and baseline.
- Intentional airborne displacement remains intact. Bbox ground alignment does
  not substitute for explicit placement review against the declared source plane.
- Direction reference images are not confused with runtime contact coordinates.

## Semantic Motion Review

- Animated assets declare sequences, FPS and loop intent in the contract and
  enable `reviews.motion.required`. Static assets leave animations empty.
- Motion is watched at intended game scale; identity, anatomy, contact phases
  and state readability are reviewed separately from geometric QA.
- Walk/run remain experimental until this review explicitly passes; static
  bobbing, broken joints, direction errors and unstable foot contacts fail.
- Looping states have a readable last-to-first transition. Non-loop actions have
  a readable start/middle/end and are not forced to loop.
- Duplicate-frame, frame-diff and seam measurements are recorded as evidence;
  they never automatically approve motion or placement.
- Playback slowdown does not conceal a failing motion verdict. Sequence edits,
  re-export, reference replacement and regeneration require fresh QA/reviews.

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
- The tool works when opened directly as `file://.../animation-preview.html`.
- The default manifest auto-loads on page open; the first sheet is visible without pressing `Load`.
- If `file://` blocks `fetch()` or canvas pixel reads, the adapted tool embeds the manifest and current PNG candidates as data URL fallback.
- When served over local HTTP, the tool reads project-relative manifest/image files so regenerated PNGs are reflected.
- Browser verification reports `ready: true`, nonblank canvases, console error count `0`, and alpha bbox is not `pixel read blocked on file://`.

## Alpha BBox

For each output:

- Report full-image alpha bbox.
- Report per-cell alpha bbox for sprite atlases when possible.
- Confirm transparent corners for transparent assets.
- Confirm no accidental colored key fringe remains.
- `maximumHaloPixels` requires custom/manual measurement; the common inspector
  cannot verify it, and alpha 1..7 counts do not measure halo.
- If the bbox changed, report whether code placement needs an offset update.

## Pixel/Visual Quality

- No blur from resizing.
- No antialias cleanup pass that softens pixel art.
- No unexpected cast shadow outside the cell/layer.
- Character/FX silhouette remains readable at in-game display size.
- Color variants change only intended color regions.
- Lighting and outline weight match neighboring assets.
- For progressive animation states, frame-to-frame diff meets the per-asset
  minimum visible-change threshold at game display scale.
- When only a declared region may change, the diff outside that allowed mask is
  measured and stays within its per-asset limit.

## Promotion Gate

- The candidate path and QA report checksum are recorded in a structured asset
  status file.
- The QA report was made with the current version of the asset contract.
- `qa.contractSha256` matches the current contract bytes; old approvals missing
  it require regenerated QA even when the version number is unchanged.
- Contract `references` and `qa.requiredInputs` include all base/direction
  references, selection recipes and runtime manifests used by the candidate.
- `qa.inputChecksums` lists their paths/SHA-256 values. Paths stay under batch
  `source/`, `generated/`, `manifests/` or `qa/`.
- Style reviews record `comparisonSha256` and `referenceSha256` when declared.
- Required filename/content and style reviews are explicitly `approved`, not
  inferred from a generated comparison image.
- Candidate, QA report, reference, and comparison inputs are unchanged since
  approval.
- `final/` was populated only by the local atomic promotion gate.
- Required placement review is `approved` when anchor/baseline checks are
  requested or `reviews.placement.required` is true; animated motion review is
  also explicitly `approved`.

The common offline inspector interface is:

```text
python3 tools/runner/inspect_sprite.py --batch-root <batch> --contract <contract> --image <candidate> --output <qa-report> [--status <asset-status>]
```

It writes geometric measurements, fingerprints and pending review statuses;
it never promotes or infers semantic approval. Unsupported required automatic
measurements need manual/custom QA before automated QA can be recorded as pass.
Geometric QA pass still leaves semantic placement/motion review pending.

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
- Preview file:// result:
- Preview console errors:
```


