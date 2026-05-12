# Bridge Cross Parallel Run Manifest Notes

## Proposed Preview Manifest

Preview manifest:
- `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bridge-cross-parallel-sprites.manifest.json`

Preview tool:
- `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\finish-lottery-preview.html`

## Runtime Integration Contract

Current game code loads:
- `/assets/bridge-cross/sprites/glass-fx-v2.png`
- `/assets/bridge-cross/sprites/bridge-cross-sprites.manifest.json`
- `/assets/bridge-cross/sprites/players-{color}.png`

## 10-Column Bridge Map Contract

Runtime files:
- Server: `D:\Work\LAMDiceBot\socket\bridge-cross.js`
- Client: `D:\Work\LAMDiceBot\js\bridge-cross.js`
- HTML debug panel: `D:\Work\LAMDiceBot\bridge-cross-multiplayer.html`

Map/play contract:
- Bridge length: `10` columns.
- Server `gameStart` payload: `totalCols: 10`, `maxWaves: 10`.
- Client `layout.columnCount`: `10`.
- Normal bridge column count is authoritative for tile draw loops, progress clamp, HUD total, result progress labels, and render-game-to-text diagnostics.

Map placement:
- World size: `2800x1900`.
- Start stage world origin: `{ x: -145, y: 1080 }`.
- Finish stage world origin: `{ x: 1528, y: 1 }`.
- Bridge entrance: `{ x: 435, y: 1089 }`.
- Bridge exit: `{ x: 1593.5, y: 412 }`.
- Column step: approximately `{ x: 128.722, y: -75.222 }`.
- First top tile center: `{ x: 435, y: 1089 }`.
- Last top tile center: `{ x: 1594, y: 412 }`.
- Last bottom tile center: `{ x: 1813, y: 526 }`.

Background:
- Existing `background-void-v2.png` remains the production source image.
- Runtime now tiles the 1.5x scaled background across the expanded world instead of drawing two fixed copies.

For `players-{color}.png`:
- Player sheets are now `1400x1309`, `4 cols x 7 rows`, cell `350x187`.
- Rows 0-5 preserve the original contract: `idle`, `run`, `jump`, `land`, `fall`, `result`.
- Row 6 is the true `walk` row, frames `[0, 1, 2, 3]`, `5fps`, loop `true`.
- Use `walk` for start-platform roaming only.
- Keep `run` playback at `8fps` for the 4-frame row `1` cycle.
- `40fps` is too fast for the current chibi run row and reads as jitter instead of walking.
- Production `D:\Work\LAMDiceBot\js\bridge-cross.js` was aligned to `8fps` on `2026-05-01`.
- Reset any waiting-platform animation speed multiplier to `1.0` when a runner starts crossing.
- Production `drawPlayer()` adds a small frame-synced run bob/sway for all player colors so the existing leg poses remain readable at active scale.

For `players-my-outline-v1.png`:
- Add a new image definition in `js/bridge-cross.js`, for example `playersMyOutline: spriteRoot + 'players-my-outline-v1.png'`.
- Use the same `playerSheet` grid and anchor as `players-{color}.png`.
- In `drawPlayer`, draw this outline atlas cell first at the exact same destination rectangle only when the player is the local user's character, then draw the color player sprite over it.
- The outline is an overlay/backplate atlas derived from all player alpha masks per cell, so one file covers all player colors.
- Because it is drawn under the colored sprite, the transparent center does not tint the player.

For `players-outline-v1.png`:
- Keep as a softer readability outline candidate if every player needs a light separation outline.

For `finish-lottery-object-v1.png`:
- Add a new image definition in `js/bridge-cross.js`, for example `finishLottery: spriteRoot + 'finish-lottery-object-v1.png'`.
- Add a sheet config with `4 cols x 6 rows`, cell `350x187`, anchor `(0.5, 0.88)`.
- Draw the prop on or near the finish platform when the post-game lottery phase starts.
- Place by the prop base/contact anchor, not by visual center.

For `glass-fx-v3.png`, choose one integration path after QA:

1. New file path:
   - Copy QA-passed file to `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\glass-fx-v3.png`
   - Update `js/bridge-cross.js` imageDefs from `glass-fx-v2.png` to `glass-fx-v3.png`
   - Update production manifest grid rows to `11`

2. Intentional replacement:
   - Archive current `glass-fx-v2.png`
   - Replace it with QA-passed expanded atlas only after updating manifest rows to `11`
   - Keep old row meanings 0-6 exactly unchanged

Do not silently replace production assets before QA passes.

## Anchor And Baseline

`finish-lottery-object-v1.png`:
- normalized anchor: `(0.5, 0.88)`
- pixel guide in each `350x187` cell: `(175, 165)`
- source plane: prop bottom/contact plane at `y=165`

`glass-fx-v3.png` is designed as a contact-anchor FX sheet:
- normalized anchor: `(0.5, 0.88)`
- pixel guide in each `350x187` cell: `(175, 165)`
- source plane: `y=165`

This is intentionally different from the current legacy visual pivot of `glass-fx-v2.png`:
- current legacy anchor: `(0.5, 0.62)`

The current code already has a contact-anchor switch:
- if `fxSheet.anchor` equals `playerSheet.anchor`, tile FX use the contact anchor path.

## Bonus Pad V1

`bonus-pad-v1.png`:
- SpriteMake generated path: `D:\Work\vibe\SpriteMake\output\bridge-cross\generated\bonus-pad-v1.png`
- SpriteMake final path: `D:\Work\vibe\SpriteMake\output\bridge-cross\final\bonus-pad-v1.png`
- SpriteMake packaged sprite path: `D:\Work\vibe\SpriteMake\output\bridge-cross\sprites\bonus-pad-v1.png`
- Game asset path: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\bonus-pad-v1.png`
- Preview manifest: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bonus-pad-v1.manifest.json`
- Preview tool: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\bonus-pad-preview.html`
- Generation path: procedural SpriteMake source script, not an image API call and not verified as `gpt-image-2`.

Runtime contract:
- Final canvas: `1024x256`
- Grid: `4 cols x 1 row`
- Cell: `256x256`
- Column boundaries: `x=0,256,512,768,1024`
- Row boundaries: `y=0,256`
- Anchor: normalized `(0.5, 1.0)`, pixel guide `(128, 256)`
- Y-axis baseline/source plane: bottom contact plane `y=256`
- Animation row `0`: `spawn`, `ready`, `compress`, `launch`
- Playback: `full` uses frames `[0, 1, 2, 3]` at `14fps`, no loop.

Manifest integration:
- Added `bonusPad` sheet to SpriteMake sprite manifest.
- Added `bonusPad` sheet to `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\bridge-cross-sprites.manifest.json`.
- The current `bridge-cross.js` now draws `bonusPad` effects for bonus jumps, synchronized to the character jump launch phase.
