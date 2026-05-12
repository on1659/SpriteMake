# Bridge Cross Parallel Run Resource Requests

## 0. Finish Lottery Object V1

Resource Request Brief:
- Original user request: 도착하고 떨어진 사람들이 모여서 제비뽑기를 하는 기능. 그 제비뽑기용 오브젝트 애니메이션이 필요.
- SpriteMake batch folder: `D:\Work\vibe\SpriteMake\output\bridge-cross`
- Game / concept: 유리다리건너기 finish/result phase
- Scene or screen where this appears: final platform / result staging area after runners finish or fall
- Gameplay role: gathered players perform a random draw / 제비뽑기
- Player-readable purpose: 지금 게임이 "통과 결과"에서 "제비뽑기 결과" 단계로 넘어갔음을 즉시 보여준다.
- Visual direction: 기존 neon dimetric pixel-art stage와 어울리는 작은 추첨함/제비통/lottery box prop. 귀엽고 선명하지만 UI 텍스트는 없음.
- Existing assets or style to match: `finish-stage-v2.png`, `players-*.png`, cyan/yellow glass FX
- In-game display scale: roughly `180-260px` wide on the finish platform, depending on camera zoom
- Target file path: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\finish-lottery-object-v1.png`
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2

Runtime Contract:
- Game project root: `D:\Work\LAMDiceBot`
- Target asset path: `assets/bridge-cross/sprites/finish-lottery-object-v1.png`
- Source/reference path: existing bridge-cross finish/platform/player assets
- Asset type: animated transparent prop atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: exactly `1400x1122`
- Grid columns: exactly `4`
- Grid rows: exactly `6`
- Cell size: exactly `350x187`
- Column boundaries: `x=0,350,700,1050,1400`
- Row boundaries: `y=0,187,374,561,748,935,1122`
- Contact anchor: `x=175, y=165` inside each `350x187` cell
- Contact anchor meaning: bottom center of the lottery object touching the finish platform
- Y-axis baseline or source plane: prop base/source plane remains at `y=165`
- Alpha/background requirement: PNG-32 RGBA, straight alpha, transparent background

Rows:
- row 0: `idle_closed` - object waits on the finish platform
- row 1: `gather_prompt` - subtle glow/ring inviting all players to gather
- row 2: `mix_shake` - box/tube shakes while lots are mixed
- row 3: `draw_lot` - one stick/card/slip rises or pops out
- row 4: `reveal_lot` - selected lot glows; no readable text
- row 5: `reset_settle` - object settles back to idle for the next round

Columns:
- column 0: frame 0
- column 1: frame 1
- column 2: frame 2
- column 3: frame 3

Animation Preview Tool Request:
- Tool output path: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\finish-lottery-preview.html`
- Preview manifest path: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bridge-cross-parallel-sprites.manifest.json`
- The tool must show exact cell grid, selected frame bounds, contact anchor, source plane baseline, image size, cell size, and alpha bbox.

## 1. Glass FX Parallel V3

Status: deferred; this was the previous interpretation before the user clarified the needed asset is a 제비뽑기 object.

Resource Request Brief:
- Original user request: 여기에 기능추가가되서 스프라이트가 필요해
- SpriteMake batch folder: `D:\Work\vibe\SpriteMake\output\bridge-cross`
- Game / concept: 유리다리건너기, 여러 runner가 동시에 다리를 건너는 실시간 시각화
- Scene or screen where this appears: Bridge Cross canvas, glass bridge tile layer and runner contact layer
- Gameplay role: 발판 상태, 다인 발판 압력, 동시 추락, 출발/도착 피드백을 보여주는 FX
- Player-readable purpose: 어느 발판이 위험한지, 누가 동시에 휩쓸렸는지, 누가 출발/도착했는지를 작은 화면에서도 빠르게 읽게 한다.
- Visual direction: 기존 cyan/yellow neon glass FX와 같은 dimetric pixel-art. 선명한 픽셀 edge, 투명 배경, 과한 blur 금지.
- Existing assets or style to match: `glass-fx-v2.png`, `start-stage-v3.png`, `finish-stage-v2.png`
- In-game display scale: tile visual size around `450x214`, source cell `350x187`
- Target file path: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\glass-fx-v3.png`
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2

Runtime Contract:
- Game project root: `D:\Work\LAMDiceBot`
- Target asset path: `assets/bridge-cross/sprites/glass-fx-v3.png`
- Source/reference path: `assets/bridge-cross/sprites/glass-fx-v2.png`
- Asset type: animated transparent FX atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: exactly `1400x2057`
- Grid columns: exactly `4`
- Grid rows: exactly `11`
- Cell size: exactly `350x187`
- Column boundaries: `x=0,350,700,1050,1400`
- Row boundaries: `y=0,187,374,561,748,935,1122,1309,1496,1683,1870,2057`
- Contact anchor: `x=175, y=165` inside each `350x187` cell
- Contact anchor meaning: runner foot contact point and glass source plane
- Y-axis baseline or source plane: every tile-derived row preserves source plane `y=165`
- Alpha/background requirement: PNG-32 RGBA, straight alpha, transparent background

Rows:
- row 0: `safe_sparkle`
- row 1: `warning_glow`
- row 2: `crack`
- row 3: `break_shards`
- row 4: `fall_trail`
- row 5: `landing_pulse`
- row 6: `restore_glass`
- row 7: `shared_tile_pressure`
- row 8: `cascade_break_burst`
- row 9: `start_dash_dust`
- row 10: `finish_arrival_glow`

Columns:
- column 0: frame 0
- column 1: frame 1
- column 2: frame 2
- column 3: frame 3

Animation Preview Tool Request:
- Tool output path: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\bridge-cross-parallel-preview.html`
- Preview manifest path: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bridge-cross-parallel-sprites.manifest.json`
- The tool must show exact cell grid, selected frame bounds, contact anchor, source plane baseline, image size, cell size, and alpha bbox.

## 2. Player Parallel Readability Refresh

Resource Request Brief:
- Original user request: 여기에 기능추가가되서 스프라이트가 필요해
- SpriteMake batch folder: `D:\Work\vibe\SpriteMake\output\bridge-cross`
- Game / concept: Bridge Cross parallel-run runner tokens
- Scene or screen where this appears: start platform walk roaming, bridge tiles, falling sequence, finish platform
- Gameplay role: 다리 위 여러 runner가 동시에 움직일 때 각 색상과 상태를 읽게 한다.
- Player-readable purpose: scale `0.58`에서도 run/jump/fall/result 상태와 색상을 구분한다.
- Visual direction: existing compact neon pixel runner. 같은 silhouette, 같은 anchor, 색상만 변경.
- Existing assets or style to match: current `players-red.png` through `players-indigo.png`; violet exists as source/optional
- In-game display scale: active `0.58`, waiting/finish `0.50`
- Target file path: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\players-{color}.png` after QA
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2

Runtime Contract:
- Asset type: animated player atlas, color variants
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: exactly `1400x1309`
- Grid columns: exactly `4`
- Grid rows: exactly `7`
- Cell size: exactly `350x187`
- Column boundaries: `x=0,350,700,1050,1400`
- Row boundaries: `y=0,187,374,561,748,935,1122,1309`
- Contact anchor: `x=175, y=165` inside each `350x187` cell
- Contact anchor meaning: runner foot contact point
- Y-axis baseline or source plane: grounded rows keep foot baseline `y=165`
- Alpha/background requirement: PNG-32 RGBA, straight alpha, transparent background

Rows:
- row 0: `idle`
- row 1: `run`
- row 2: `jump`
- row 3: `land`
- row 4: `fall`
- row 5: `result`
- row 6: `walk`

Columns:
- column 0: frame 0
- column 1: frame 1
- column 2: frame 2
- column 3: frame 3

Color variants:
- runtime required: red, orange, yellow, green, blue, indigo
- optional archive/source consistency: violet

QA note:
- This is not mandatory unless browser QA shows the current player sheets are too hard to read in parallel mode.

## 3. Bonus Pad V1

Resource Request Brief:
- Source prompt: `D:\Work\vibe\SpriteMake\output\bridge-cross\prompts\bonus-pad-v1.md`
- SpriteMake batch folder: `D:\Work\vibe\SpriteMake\output\bridge-cross`
- Game / concept: Bridge Cross bonus side super-jump feedback
- Scene or screen where this appears: glass bridge tile, immediately after a player chooses the secret bonus side
- Gameplay role: short-lived jump pad that communicates `+2` or `+3` forward launch reward
- Player-readable purpose: clearly show that the chosen side was the bonus side and that the player is being launched forward
- Visual direction: dimetric neon pixel-art spring/trampoline pad with cyan glow, violet/magenta accent, yellow-white launch energy
- Existing assets or style to match: `glass-fx-v2.png`, `players-*.png`, Bridge Cross neon glass stage
- Target file path: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\bonus-pad-v1.png`
- Generation provider: procedural SpriteMake script for this pass; no image API call
- Required image model for strict external regeneration: `gpt-image-2`

Runtime Contract:
- Asset type: animated transparent prop atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: exactly `1024x256`
- Grid columns: exactly `4`
- Grid rows: exactly `1`
- Cell size: exactly `256x256`
- Column boundaries: `x=0,256,512,768,1024`
- Row boundaries: `y=0,256`
- Contact anchor: normalized `(0.5, 1.0)`, pixel guide `(128, 256)`
- Contact anchor meaning: bottom center of the pad resting on the glass tile surface
- Y-axis baseline or source plane: pad base/source plane remains at bottom edge `y=256`
- Alpha/background requirement: PNG-32 RGBA, straight alpha, transparent background

Frames:
- column 0: `spawn`
- column 1: `ready`
- column 2: `compress`
- column 3: `launch`

Animation Preview Tool Request:
- Tool output path: `D:\Work\vibe\SpriteMake\output\bridge-cross\tools\bonus-pad-preview.html`
- Preview manifest path: `D:\Work\vibe\SpriteMake\output\bridge-cross\manifests\bonus-pad-v1.manifest.json`
- The tool must show exact cell grid, selected frame bounds, contact anchor, source plane baseline, image size, cell size, and alpha bbox.
