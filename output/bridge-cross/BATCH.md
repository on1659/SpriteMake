# Bridge Cross Parallel Run Sprite Batch

작성일: 2026-04-30
상태: sprite/runtime mixed; 10-column bridge map runtime QA updated
현재 수정 방향: Bridge Cross 10칸 맵, bonus-pad, walk/run/player atlas 정합성 유지

## Batch Overview

Batch Sprite Production Request:
- Original user request: 도착하고 떨어진 사람들이 모여서 제비뽑기를 하는 기능. 그 제비뽑기용 오브젝트 애니메이션이 필요.
- SpriteMake batch folder: `D:\Work\vibe\SpriteMake\output\bridge-cross`
- Game / project: LAMDiceBot Bridge Cross
- Game project root: `D:\Work\LAMDiceBot`
- Scene or feature: Bridge Cross finish/result phase lottery draw
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Shared gameplay purpose: 도착자와 추락자가 finish area에 모인 뒤 제비뽑기 절차를 읽기 쉽게 보여준다.
- Shared visual direction: 기존 `assets/bridge-cross`의 dimetric pixel-art, cyan/yellow glass glow, neon void stage와 일치.
- Existing assets or style to match: `players-*.png`, `glass-fx-v2.png`, `background-void-v2.png`, `start-stage-v3.png`, `finish-stage-v2.png`
- In-game scale reference: finish platform prop, around `180-260px` wide on screen depending on camera zoom.
- Output root: `D:\Work\vibe\SpriteMake\output\bridge-cross`
- Preview tool folder: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools`
- QA output folder: `D:\Work\vibe\SpriteMake\output\bridge-cross\qa`

## Code Context

기능 추가 기준 문서:
- `D:\Work\LAMDiceBot\docs\meeting\impl\2026-04-29-bridge-cross-parallel-run-impl.md`

현재 런타임 사용처:
- `D:\Work\LAMDiceBot\js\bridge-cross.js`
- sprite root: `/assets/bridge-cross/sprites/`
- stage root: `/assets/bridge-cross/stage/`
- current glass FX path: `/assets/bridge-cross/sprites/glass-fx-v2.png`
- current player paths: `/assets/bridge-cross/sprites/players-{color}.png`

현재 리소스는 기본 다리 진행을 커버한다. 새 batch의 핵심은 finish/result 단계의 제비뽑기 오브젝트다.

Current runtime map contract:
- Bridge length is now `10` columns.
- Server `gameStart` sends `totalCols: 10`, `maxWaves: 10`.
- Client `StageLayout` uses world `2800x1900`, start `{ x: -145, y: 1080 }`, finish `{ x: 1528, y: 1 }`.
- Existing `background-void-v2.png` remains the source image and is tiled at runtime to cover the expanded map.

## Required Assets

Asset:
- ID: `players_my_outline_v1`
- Asset role: 내 캐릭터 식별용 high-visibility outline overlay atlas
- Generation method: derived from current `players-{color}.png` alpha union per cell, no image API
- Target file path after integration: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\players-my-outline-v1.png`
- SpriteMake generated path: `D:\Work\vibe\SpriteMake\output\bridge-cross\generated\players-my-outline-v1.png`
- SpriteMake final path: `D:\Work\vibe\SpriteMake\output\bridge-cross\final\players-my-outline-v1.png`
- Preview path: `D:\Work\vibe\SpriteMake\output\bridge-cross\qa\players-my-outline-v1-comparison.png`
- Asset type: transparent high-visibility outline overlay atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: `1400x1309`
- Grid columns: `4`
- Grid rows: `7`
- Cell size: `350x187`
- Contact anchor: same as player, normalized `(0.5, 0.88)`, pixel guide `(175, 165)`
- Contact anchor meaning: same runner foot contact point as the player sheet
- Y-axis baseline/source plane: same as player baseline `y=165`
- QA priority: use only for local player's character, not every character

Asset:
- ID: `players_outline_v1`
- Asset role: all player color variants에 공통으로 깔 수 있는 readability outline overlay atlas
- Generation method: derived from current `players-{color}.png` alpha union, no image API
- Target file path after integration: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\players-outline-v1.png`
- SpriteMake generated path: `D:\Work\vibe\SpriteMake\output\bridge-cross\generated\players-outline-v1.png`
- SpriteMake final path: `D:\Work\vibe\SpriteMake\output\bridge-cross\final\players-outline-v1.png`
- Preview path: `D:\Work\vibe\SpriteMake\output\bridge-cross\qa\players-outline-v1-preview.png`
- Asset type: transparent outline overlay atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: `1400x1309`
- Grid columns: `4`
- Grid rows: `7`
- Cell size: `350x187`
- Contact anchor: same as player, normalized `(0.5, 0.88)`, pixel guide `(175, 165)`
- Contact anchor meaning: same runner foot contact point as the player sheet
- Y-axis baseline/source plane: same as player baseline `y=165`
- QA priority: passed basic grid/alpha QA

Asset:
- ID: `finish_lottery_object_v1`
- Asset role: 도착자와 추락자가 모인 뒤 사용하는 제비뽑기 오브젝트 애니메이션
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\finish-lottery-object-v1.png`
- SpriteMake generated path: `D:\Work\vibe\SpriteMake\output\bridge-cross\generated\finish-lottery-object-v1.png`
- Animation tool path: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\finish-lottery-preview.html`
- Preview manifest path: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bridge-cross-parallel-sprites.manifest.json`
- Asset type: transparent animated prop atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: `1400x1122`
- Grid columns: `4`
- Grid rows: `6`
- Cell size: `350x187`
- Contact anchor: normalized `(0.5, 0.88)`, pixel guide `(175, 165)`
- Contact anchor meaning: bottom center of the lottery object touching the finish platform
- Y-axis baseline/source plane: prop base/source plane `y=165` must remain stable across all rows
- QA priority: highest

Deferred Asset:
- ID: `glass_fx_parallel_v3`
- Asset role: 병렬 진행용 유리/발판/동시 추락/출발/도착 FX 확장 atlas
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\glass-fx-v3.png`
- SpriteMake generated path: `D:\Work\vibe\SpriteMake\output\bridge-cross\generated\glass-fx-v3.png`
- Animation tool path: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\bridge-cross-parallel-preview.html`
- Preview manifest path: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bridge-cross-parallel-sprites.manifest.json`
- Asset type: transparent animated FX atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: `1400x2057`
- Grid columns: `4`
- Grid rows: `11`
- Cell size: `350x187`
- Contact anchor: normalized `(0.5, 0.88)`, pixel guide `(175, 165)`
- Contact anchor meaning: character foot/tile contact point and source plane, not visual center
- Y-axis baseline/source plane: local source plane `y=165` must remain stable across tile-derived rows
- QA priority: highest

Deferred Asset:
- ID: `players_parallel_readability_refresh`
- Asset role: 병렬 진행에서 작게 보이는 runner의 run/jump/fall/result 가독성 개선용 player atlas replacement 후보
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path after QA: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\players-{color}.png`
- SpriteMake generated path: `D:\Work\vibe\SpriteMake\output\bridge-cross\generated\players-{color}-parallel-v3.png`
- Animation tool path: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\bridge-cross-parallel-preview.html`
- Preview manifest path: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bridge-cross-parallel-sprites.manifest.json`
- Asset type: transparent animated player atlas, 6 color variants used by runtime plus optional violet source
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: `1400x1309`
- Grid columns: `4`
- Grid rows: `7`
- Cell size: `350x187`
- Contact anchor: normalized `(0.5, 0.88)`, pixel guide `(175, 165)`
- Contact anchor meaning: runner foot contact point
- Y-axis baseline/source plane: grounded rows keep foot contact at `y=165`
- QA priority: medium; current sheets pass basic QA, replace only if visual readability is not enough

## Integration Notes

- Do not put generated attempts into `final/` or the LAMDiceBot production assets until QA passes.
- `glass-fx-v3.png` is a new target file. Game code must either load this file as `glassFx` or intentionally replace `glass-fx-v2.png` after QA.
- If `glass-fx-v3.png` replaces the current `glassFx` sheet, update the manifest/grid rows to `11` and add the new animation keys before drawing them.
- Player refresh is optional. Current `players-*.png` sheets are strict `4x7` atlases with row 6 reserved for `walk`; do not replace unless browser QA shows poor readability at scale `0.58`.

Asset:
- ID: `bonus_pad_v1`
- Asset role: bonus-side super-jump visual feedback pad
- Generation method: procedural SpriteMake source script for this pass; no image API call
- Source prompt: `D:\Work\vibe\SpriteMake\output\bridge-cross\prompts\bonus-pad-v1.md`
- Target file path after integration: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\bonus-pad-v1.png`
- SpriteMake generated path: `D:\Work\vibe\SpriteMake\output\bridge-cross\generated\bonus-pad-v1.png`
- SpriteMake final path: `D:\Work\vibe\SpriteMake\output\bridge-cross\final\bonus-pad-v1.png`
- Preview path: `D:\Work\vibe\SpriteMake\output\bridge-cross\qa\bonus-pad-v1-preview.png`
- Preview tool: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\bonus-pad-preview.html`
- Preview manifest: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bonus-pad-v1.manifest.json`
- Asset type: transparent animated prop atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: `1024x256`
- Grid columns: `4`
- Grid rows: `1`
- Cell size: `256x256`
- Contact anchor: normalized `(0.5, 1.0)`, pixel guide `(128, 256)`
- Contact anchor meaning: bottom center of the pad on the glass tile surface
- Y-axis baseline/source plane: bottom contact plane `y=256`
- QA priority: passed asset QA; runtime spawn/draw code is integrated for bonus jumps
