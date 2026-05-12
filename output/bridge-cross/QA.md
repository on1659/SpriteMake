# Bridge Cross Parallel Run QA

상태: asset QA mixed; runtime 10-column map QA updated `2026-05-06`

## Existing Asset Sanity

Previously checked production assets in `D:\Work\LAMDiceBot\assets\bridge-cross`:
- `players-*.png`: `1400x1309`, `4 cols x 7 rows`, cell `350x187`, no empty cells, transparent corners. Rows 0-5 preserve the original contract; row 6 is the new walk row.
- `glass-fx-v2.png`: `1400x1309`, `4 cols x 7 rows`, cell `350x187`, no empty cells, transparent corners.
- `background-void-v2.png`: `1536x1024`.
- `start-stage-v3.png`: `728x743`.
- `finish-stage-v2.png`: `559x794`.

## Runtime Map QA

### 10-column Bridge Cross map

Diagnostic:
- Date: `2026-05-06`
- Server file: `D:\Work\LAMDiceBot\socket\bridge-cross.js`
- Client file: `D:\Work\LAMDiceBot\js\bridge-cross.js`
- HTML debug panel: `D:\Work\LAMDiceBot\bridge-cross-multiplayer.html`
- Intended bridge length: PASS - `10` columns
- Server contract: PASS - `gameStart.totalCols=10`, `gameStart.maxWaves=10`
- Client contract: PASS - `layout.columnCount=10`
- Render diagnostic: PASS - `render_game_to_text().coordinateSystem = world 2800x1900, viewport 1024x683`
- Revealed/tile state array: PASS - 10 revealed columns emitted in browser diagnostic
- Canvas load: PASS - browser canvas `1024x683`, nonblank pixels `699392`
- Browser screenshot: `D:\Work\LAMDiceBot\output\playwright\bridge-cross-10-tile-map.png`
- Browser canvas screenshot: `D:\Work\LAMDiceBot\output\playwright\bridge-cross-10-tile-canvas.png`
- Canvas element diagnostic: PASS - displayed as `block`, viewport rect approximately `718x478px`
- Server payload smoke test: PASS - 2 QA clients received `totalCols=10`, `maxWaves=10`, and no `bonusRows` leak in `gameStart`

Layout values:
- World size: `2800x1900`
- Start world origin: `{ x: -145, y: 1080 }`
- Finish world origin: `{ x: 1528, y: 1 }`
- Bridge entrance: `{ x: 435, y: 1089 }`
- Bridge exit: `{ x: 1593.5, y: 412 }`
- Column step: `{ x: 128.722, y: -75.222 }`
- First top tile center: `{ x: 435, y: 1089 }`
- Last top tile center: `{ x: 1594, y: 412 }`
- Last bottom tile center: `{ x: 1813, y: 526 }`

Integration notes:
- Existing stage/background PNG files were not regenerated or replaced.
- `background-void-v2.png` is now tiled at runtime to cover the expanded world.
- The debug panel defaults are synchronized from `StageLayout`, including start/finish positions and offsets, so tweaking one debug field does not reset the map to the old 6-column coordinates.
- Browser console had only intentionally blocked external ad/font resource errors during the headless QA run; local bridge assets and layout diagnostics loaded.

## Runtime Animation QA

### `players-{color}.png` walk row

Diagnostic:
- Date: `2026-05-02`
- Files checked: `sprites/players-{red,orange,yellow,green,blue,indigo,violet}.png`
- Atlas contract: PASS - expanded to `1400x1309`, `4 cols x 7 rows`, cell `350x187`
- Walk row: row `6`, frames `[0, 1, 2, 3]`
- Expected runtime FPS: `5`
- Usage: start-platform roaming only; bridge crossing keeps `run`.
- Contact anchor: unchanged `(175, 165)` pixel, `(0.5, 0.88)` normalized
- Y baseline: unchanged `y=165`
- Integration fix: appended a true row 6 walk row to all player color atlases and outline atlases; updated production `playerSheet`, SpriteMake manifests, production sprite manifest, and preview tool. Waiting/start-platform characters now call `player.animator.set('walk')`.
- Visual result: row 6 uses upright walk-specific frames, slower playback, smaller frame-synced bob/sway, lower `_extraAdvance` range, and slower start-platform wander path for readable roaming.
- Backups:
  - `D:\Work\vibe\SpriteMake\output\bridge-cross\_unused\sprites\archive\walk-row-pre7-20260502-233757`
  - `D:\Work\LAMDiceBot\assets\bridge-cross\_unused\sprites\archive\walk-row-pre7-20260502-233757`
- Diagnostic previews:
  - `qa/players-walk-runtime-v1-diagnostic.png`
  - `qa/players-blue-walk-runtime-v1-5fps.gif`
  - `qa/players-walk-runtime-v2-diagnostic.png`
  - `qa/players-blue-walk-runtime-v2-5fps.gif`
  - `qa/players-walk-row-v3-true-row-diagnostic.png`
  - `qa/players-blue-walk-row-v3-true-row-5fps.gif`

### `players-{color}.png` run row

Diagnostic:
- Date: `2026-05-01`
- Files checked: `sprites/players-{red,orange,yellow,green,blue,indigo}.png`
- Atlas contract: PASS - now `1400x1309`, `4 cols x 7 rows`, cell `350x187`; original run row remains row `1`
- Run row: row `1`, frames `[0, 1, 2, 3]`
- Expected runtime FPS: `8`
- Contact anchor: `(175, 165)` pixel, `(0.5, 0.88)` normalized
- Y baseline: grounded foot baseline `y=165`
- Per-frame alpha bbox: consistent; all run frames remain grounded at or above baseline.
- Visual result: resource row has readable arm/leg pose changes when played at `8fps`.
- Issue found: production `D:\Work\LAMDiceBot\js\bridge-cross.js` had `run.fps = 40`, which makes 4-frame run motion too fast to read as walking.
- Secondary issue: waiting-platform `_extraAdvance` could carry into the bridge run if not reset on start.
- Integration fix: changed production `run.fps` to `8`, reset `_extraAdvance` to `1.0` in `resetForRun()`, and added a small frame-synced run bob/sway in `drawPlayer()` so the 4-frame leg poses read as walking at game scale.
- Diagnostic previews:
  - `qa/players-run-current-row-diagnostic.png`
  - `qa/players-blue-run-current-strip.png`
  - `qa/players-blue-run-current-8fps.gif`
  - `qa/players-blue-run-current-40fps.gif`
  - `qa/players-run-runtime-v2-diagnostic.png`
  - `qa/players-blue-run-runtime-v2-8fps.gif`

## New Asset QA Targets

### `players-my-outline-v1.png`

Asset QA Report:
- File: `generated/players-my-outline-v1.png`
- Final file: `final/players-my-outline-v1.png`
- Final size: `1400x1309`
- Format: PNG RGBA
- Full alpha bbox: `(108, 37, 1293, 1298)`
- Grid: `4 cols x 7 rows`
- Cell size: `350x187`
- Contact anchor: same as players, `(175, 165)` pixel, `(0.5, 0.88)` normalized
- Y baseline: same as players, `y=165`
- Per-cell bbox summary: no empty cells; generated per cell so no neighboring-cell bleed. Fall row outline reaches the bottom edge in some cells due to fall pose placement.
- Plane alignment result: derived from current player atlas alpha per cell, so frame placement matches player sheet.
- Issues found: high-contrast by design; use for local player only, not all players.
- Code offset required: none; draw at exact same destination rect as player sprites.
- Preview: `qa/players-my-outline-v1-high-contrast-scene-preview.png`

Integration note:
- Copy `final/players-my-outline-v1.png` to `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\players-my-outline-v1.png` only when ready to patch code.
- Draw order should be my-outline first, colored player second.

### `players-outline-v1.png`

Asset QA Report:
- File: `generated/players-outline-v1.png`
- Final file: `final/players-outline-v1.png`
- Final size: `1400x1309`
- Format: PNG RGBA
- Full alpha bbox: `(107, 35, 1294, 1296)`
- Grid: `4 cols x 7 rows`
- Cell size: `350x187`
- Contact anchor: same as players, `(175, 165)` pixel, `(0.5, 0.88)` normalized
- Y baseline: same as players, `y=165`
- Per-cell bbox summary: no empty cells; all cells stay inside fixed cell bounds; transparent corners confirmed.
- Plane alignment result: derived from current player atlas alpha, so frame placement matches player sheet.
- Issues found: none for basic slicing/alpha QA. Visual intensity may be tuned in code by globalAlpha if needed.
- Code offset required: none; draw at exact same destination rect as player sprites.
- Preview: `qa/players-outline-v1-preview.png`

Integration note:
- Copy `final/players-outline-v1.png` to `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\players-outline-v1.png` only when ready to patch code.
- Draw order should be outline first, colored player second.

### `finish-lottery-object-v1.png`

Asset QA Report:
- File: `generated/finish-lottery-object-v1.png`
- Actual generated size: `1401x1123`
- Expected final size: `1400x1122`
- Expected grid: `4 cols x 6 rows`
- Expected cell size: `350x187`
- Contact anchor: `(175, 165)` pixel, `(0.5, 0.88)` normalized
- Y baseline/source plane: prop base at `y=165`
- Format: PNG-32 RGBA, straight alpha, transparent background
- Issues found: FAIL - actual size is off by +1px in both dimensions; background is not transparent because the checkerboard is baked into the image with alpha 255 at all corners; every cell alpha bbox fills the full cell.
- Code offset required: do not integrate this PNG.
- Preview composite: `qa/finish-lottery-object-v1-on-finish-stage-preview.png`

Visual fit note:
- Concept reads as a lottery/draw object and the blue/gold/cyan palette is close enough to the Bridge Cross finish platform.
- Perspective is more front-facing than the finish platform's dimetric angle.
- The asset is too glossy/standalone-object-like for final integration unless regenerated or cleaned up.

Required checks:
- `width % 4 === 0`
- `height % 6 === 0`
- no empty cells
- no frame bleeds into neighboring cells
- transparent corners
- prop base/contact plane stays at `y=165`
- row 3/4 draw and reveal frames contain no readable text or labels
- preview tool loads manifest and can play every row

### `glass-fx-v3.png`

Status: deferred; not the current clarified need.

Asset QA Report:
- File: `generated/glass-fx-v3.png`
- Expected final size: `1400x2057`
- Expected grid: `4 cols x 11 rows`
- Expected cell size: `350x187`
- Contact anchor: `(175, 165)` pixel, `(0.5, 0.88)` normalized
- Y baseline/source plane: `y=165`
- Format: PNG-32 RGBA, straight alpha, transparent background
- Issues found: pending
- Code offset required: pending browser QA

Required checks:
- `width % 4 === 0`
- `height % 11 === 0`
- no empty cells
- no frame bleeds into neighboring cells
- transparent corners
- row 0-6 remain compatible with current row meanings
- rows 7-10 preserve source plane `y=165`
- preview tool loads manifest and can play every row

### `players-{color}-parallel-v3.png`

Asset QA Report:
- File: `generated/players-{color}-parallel-v3.png`
- Expected final size: `1400x1309`
- Expected grid: `4 cols x 7 rows`
- Expected cell size: `350x187`
- Contact anchor: `(175, 165)` pixel, `(0.5, 0.88)` normalized
- Y baseline/source plane: grounded foot baseline `y=165`
- Row 6: `walk`
- Format: PNG-32 RGBA, straight alpha, transparent background
- Issues found: pending
- Code offset required: should be none; replacement must preserve current anchor/grid

Replacement rule:
- Do not replace current production player sheets unless QA proves readability improves at active scale `0.58`.

### `bonus-pad-v1.png`

Asset QA Report:
- Date: `2026-05-05`
- Source prompt: `prompts/bonus-pad-v1.md`
- Generation path: procedural SpriteMake source script, no image API call, not verified as `gpt-image-2`.
- Source script: `source/make-bonus-pad-v1.py`
- Generated file: `generated/bonus-pad-v1.png`
- Final file: `final/bonus-pad-v1.png`
- Packaged SpriteMake sprite file: `sprites/bonus-pad-v1.png`
- Game asset file: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\bonus-pad-v1.png`
- Preview image: `qa/bonus-pad-v1-preview.png`
- Browser preview screenshot: `qa/bonus-pad-preview-browser.png`
- Preview manifest: `manifests/bonus-pad-v1.manifest.json`
- Preview tool: `tools/bonus-pad-preview.html`
- Final size: PASS - `1024x256`
- Format: PASS - PNG RGBA with transparent background
- Grid: PASS - `4 cols x 1 row`
- Cell size: PASS - `256x256`
- Width/height divisibility: PASS - `(0, 0)` remainder
- Transparent corners: PASS - corner alpha `[0, 0, 0, 0]`
- Contact anchor: normalized `(0.5, 1.0)`, pixel guide `(128, 256)`
- Y baseline/source plane: bottom contact plane `y=256`; every frame keeps the pad centered on the same base line
- Full alpha bbox: `(42, 12, 983, 256)`
- Per-cell alpha bbox:
  - frame 0 `spawn`: `(42, 149, 215, 256)`
  - frame 1 `ready`: `(42, 107, 215, 256)`
  - frame 2 `compress`: `(24, 174, 233, 256)`
  - frame 3 `launch`: `(42, 12, 215, 256)`
- Empty cells: PASS - none
- Neighbor bleed: PASS - all alpha bboxes remain inside their fixed `256x256` cells
- Game manifest: PASS - `bonusPad` sheet added to production sprite manifest
- SpriteMake manifest: PASS - `bonusPad` sheet added to SpriteMake sprite and preview manifests
- Preview tool browser load: PASS - loaded `bonusPad`, image `1024x256`, cell `256x256`, remainder `0x0`
- Code offset required: none for the asset; draw by bottom-center anchor when runtime integration is added
- Runtime note: current `bridge-cross.js` now spawns/draws bonus pad events for bonus jumps.
