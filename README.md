# SpriteMake

Continuation memo:

- [HANDOFF.md](./HANDOFF.md)
- [WORKFLOW.md](./WORKFLOW.md)

Usage:

- [USAGE.md](./USAGE.md)

Agent instructions:

- [AGENTS.md](./AGENTS.md)
- [agent.md](./agent.md)
- [.agents/README.md](./.agents/README.md)

Prompt hook:

- [.agents/hooks/sprite-intake.ps1](./.agents/hooks/sprite-intake.ps1)
- [.agents/hooks/symphony.ps1](./.agents/hooks/symphony.ps1)
- [.agents/hooks/generation-choice.ps1](./.agents/hooks/generation-choice.ps1)
- [.agents/hooks/prompt-inject.ps1](./.agents/hooks/prompt-inject.ps1)

Related mockup:

- [mockup.html](./mockup.html)
- [symphony-concept.html](./symphony-concept.html)
- [symphony-usage.html](./symphony-usage.html)

GUI:

- [start-symphony-gui.bat](./start-symphony-gui.bat)
- [tools/symphony-gui/](./tools/symphony-gui/)

GUI runtime files:

- `output/SYMPHONY-GUI.url`: last opened local dashboard URL
- `output/SYMPHONY-GUI.json`: host/port/start metadata
- `output/SYMPHONY-GUI.log`: live JSONL scan/server log shown in the GUI

Related templates:

- [templates/batch-sprite-request-template.md](./templates/batch-sprite-request-template.md)
- [templates/folder-md-setup-template.md](./templates/folder-md-setup-template.md)
- [templates/resource-request-template.md](./templates/resource-request-template.md)
- [templates/asset-generation-template.md](./templates/asset-generation-template.md)
- [templates/sprite-atlas-template.md](./templates/sprite-atlas-template.md)
- [templates/animation-player-template.html](./templates/animation-player-template.html)
- [templates/animation-manifest-template.json](./templates/animation-manifest-template.json)
- [templates/asset-qa-checklist.md](./templates/asset-qa-checklist.md)
- [templates/sprite-atlas-notes.md](./templates/sprite-atlas-notes.md)

SpriteMake는 게임에 바로 넣을 수 있는 스프라이트를 일괄 생산하기 위한 생성 요청/세팅 프로젝트입니다.

목표는 단순한 이미지 생성이 아닙니다.

> API key를 저장하거나 이미지 API를 직접 호출하는 툴이 아니라, 사용 가능한 스프라이트가 나오도록 폴더, MD 요청서, manifest, QA, 프리뷰 툴을 세팅한다.

기본 운영은 키 없는 편의성을 우선합니다. Codex 세션의 이미지 생성 기능으로 바로 시도할 수 있지만, 이 경로는 `gpt-image-2`를 강제하거나 검증하지 않습니다.

여기서 “사용 가능하다”는 뜻은 다음 산출물이 같이 준비된다는 의미입니다.

- strict atlas PNG
- runtime slicing contract
- manifest
- contact anchor
- Y-axis baseline/source plane
- alpha/bbox QA 결과
- 애니메이션 프리뷰/제작 HTML 툴
- 실제 게임 프로젝트로 옮길 수 있는 target path

> 예쁜 그림이 아니라, 게임 코드가 정확히 자르고 정확히 배치할 수 있는 리소스를 만든다.

## What This Project Does

SpriteMake가 하는 일:

- 짧은 자연어 요청을 받아 적당한 batch 이름과 날짜시간이 들어간 `output/...` 폴더를 만든다.
- batch 단위 리소스 목록을 정리한다.
- 각 리소스의 사용처, 경로, grid, anchor, Y-axis baseline을 문서화한다.
- `gpt-image-2`로 생성하라고 명시된 copy-ready prompt를 만든다.
- 키 없는 Codex 직접 생성 시도를 `generated/` 검수 대상으로 다룬다.
- 생성된 PNG가 실제 게임에서 쓸 수 있는지 QA한다.
- manifest와 animation preview HTML tool 템플릿을 제공한다.
- QA 통과 후 실제 게임 프로젝트로 옮길 산출물을 정리한다.

SpriteMake가 하지 않는 일:

- API key를 저장하거나 사용하지 않는다.
- 이미지 생성 API를 직접 호출하지 않는다.
- Codex 직접 생성 결과를 검증된 `gpt-image-2` 결과라고 주장하지 않는다.
- 게임 프로젝트의 최종 production asset을 임의로 덮어쓰지 않는다.

이미지 생성 모델 정책:

- 엄격 생성의 기본/필수 이미지 생성 모델은 `gpt-image-2`입니다.
- SpriteMake는 이 모델명을 요청서와 프롬프트에 명시합니다.
- 키 없는 기본 경로는 Codex 직접 생성입니다. 이 경우 모델은 미검증이며, 결과는 `generated/`의 시안으로만 취급합니다.
- `gpt-image-2` 보장이 필요하면 ChatGPT 웹이나 API key가 있는 외부 생성 화면에서 `PROMPT.md`를 사용해야 합니다.
- `gpt-image-2`를 사용할 수 없으면 다른 모델로 만든 결과를 조용히 엄격 생성 결과로 취급하지 말고, 조건 미충족 또는 Codex-direct 시안으로 표시합니다.

즉, 이 프로젝트의 중심은 `폴더 세팅 + MD 요청서 + manifest + QA + preview tool`입니다.

사용자는 처음부터 긴 템플릿을 채우지 않아도 됩니다.

```text
드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 하고 사람이 탈 수 있을 정도로 커야 해.
```

이런 요청이 오면 SpriteMake는 먼저 `sprite-intake`로 원문 요청을 저장하고, `output/{적당한이름}-{날짜시간}/`에 `BATCH.md`, `REQUESTS.md`, `PROMPT.md`, `MANIFEST.md`, `QA.md`를 만든 뒤, 생성 방식을 한 번만 묻습니다.

```powershell
.\.agents\hooks\sprite-intake.ps1 -Request "드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 해."
```

그 다음 부족한 내용이 있으면 보강합니다.

> 어떤 게임/화면/플레이 상황에서 쓰는 리소스인지 알수록 더 정확하게 만들 수 있다.

## 0. Batch Production Flow

SpriteMake의 기본 흐름은 여러 리소스를 한 번에 정의하고, 각 리소스를 같은 기준으로 생성/검수/프리뷰하는 것입니다.

```text
Batch request -> per-asset brief -> runtime contract -> sprite PNG -> manifest -> animation preview tool -> QA -> game integration
```

batch 단위 요청서는 [templates/batch-sprite-request-template.md](./templates/batch-sprite-request-template.md)를 기준으로 씁니다.

batch별 폴더와 MD 파일은 [templates/folder-md-setup-template.md](./templates/folder-md-setup-template.md)를 기준으로 잡습니다.

## 0.5 Mini-Symphony Status Board

SpriteMake는 OpenAI Symphony 같은 큰 외부 orchestrator 대신, 로컬 `output/*` batch 폴더를 작업 보드처럼 씁니다.

```powershell
.\.agents\hooks\symphony.ps1
```

이 hook은 각 batch를 훑어 다음 상태를 판정합니다.

```text
needs-scaffold
needs-prompt
needs-prompt-inject
needs-refine
prompt-ready
qa-needed
needs-regeneration
mixed-review
final-review
final-candidate
```

상태 리포트를 파일로 남기려면:

```powershell
.\.agents\hooks\symphony.ps1 -WriteReport
```

생성되는 리포트:

```text
output/SYMPHONY.md
```

이 기능은 이미지를 생성하거나 파일을 `final/`로 옮기지 않습니다. SpriteMake의 control plane을 읽고 다음 작업을 알려주는 진단/정리 레이어입니다.

웹 GUI로 진행도를 보려면:

```powershell
.\start-symphony-gui.bat
```

이 BAT는 Node.js 서버를 시작하고 빈 로컬 포트를 자동으로 선택합니다. 실행 후 URL은 브라우저로 열리며, `output/SYMPHONY-GUI.url`에도 저장됩니다. 명령은 계속 Codex 채팅이나 PowerShell에서 내리고, GUI는 읽기 전용 진행도 확인 화면으로 사용합니다.

## 1. 리소스 요청 브리프부터 받는다

스프라이트 요청은 바로 프롬프트로 들어가지 말고, 먼저 사용처를 정리합니다.

`mockup.html`은 이 흐름을 4단계로 강제합니다.

```text
1. Brief: 게임/화면/역할/가독 목적/비주얼 방향
2. Paths: 게임 프로젝트 루트, 최종 asset path, 참고 source/reference path, generation model
3. Atlas: canvas, grid, cell, anchor, row/column 의미
4. Tool/Review: 애니메이션 프리뷰 툴 경로를 정하고 QA 상태 확인 후 프롬프트 복사
```

```text
Resource Request Brief:
- Game / concept:
- Scene or screen where this appears:
- Gameplay role:
- Player-readable purpose:
- Visual direction:
- Existing assets or style to match:
- In-game display scale:
- Target file path:
```

이 브리프가 있어야 이후의 grid, anchor, Y-axis baseline이 의미를 가집니다.

자세한 요청 플로우는 [templates/resource-request-template.md](./templates/resource-request-template.md)를 기준으로 씁니다.

애니메이션이 있는 sprite atlas는 최종 PNG만 만들지 않습니다. 로컬에서 재생, 크롭, anchor, Y-axis baseline을 확인할 수 있는 HTML 프리뷰 툴도 같이 만듭니다.

기본 방식:

```text
1. templates/animation-player-template.html 을 게임 프로젝트 쪽 도구 폴더로 복사한다.
2. preview manifest path를 해당 프로젝트의 manifest JSON으로 맞춘다.
3. `templates/animation-manifest-template.json`을 참고해서 image, grid, anchor, baselineY, animations를 적는다.
4. HTML 툴에서 sheet/animation/FPS/scale을 바꿔 보며 프레임 튐과 크롭 문제를 확인한다.
```

`templates/animation-player-template.html` 자체는 빈 원본입니다. 실제 리소스 검수용으로 사용자에게 열어주거나 안내할 파일은 batch별로 적용된 파일입니다.

```text
output/{batch}/tools/animation-preview.html
```

Preview tool은 더블클릭 실행을 기본 품질선으로 둡니다.

```text
Standalone Preview Rule:
- animation-preview.html은 file://로 직접 열어도 작동해야 한다.
- 로컬 HTTP 서버가 있어야만 manifest/image를 읽는 구조로 만들지 않는다.
- file://에서 fetch()나 canvas pixel read가 막히면 manifest와 현재 PNG 후보를 HTML 안에 내장하거나 data URL fallback을 둔다.
- HTTP 서버로 열 때는 내장본보다 실제 project-relative 파일 경로를 우선해서, regenerated PNG를 바로 확인할 수 있게 한다.
- 페이지가 열리면 기본 manifest를 자동 load하고 첫 sheet를 바로 보여준다.
- 최종 검증은 실제 브라우저에서 ready=true, canvas nonblank, console error 0, bbox가 pixel-read-blocked가 아닌 상태로 확인한다.
```

문서나 요청서에는 임시 참고 파일의 로컬 절대 경로를 쓰지 않습니다. 복사 가능한 템플릿과 제작 방식만 남깁니다.

## 2. Strict Atlas로 만든다

스프라이트는 보기 좋게 늘어놓은 contact sheet가 아니라, 코드가 고정 좌표로 자르는 strict atlas여야 합니다.

반드시 명시할 것:

- 최종 이미지 크기
- 열 개수
- 행 개수
- 셀 크기
- 열 경계 좌표
- 행 경계 좌표
- 행/열의 의미

예시:

```text
Final image size: exactly 1536x1728px
Grid: exactly 4 columns x 6 rows
Cell size: exactly 384x288px
Column boundaries: x=0, 384, 768, 1152, 1536
Row boundaries: y=0, 288, 576, 864, 1152, 1440, 1728
```

## 3. 셀 밖으로 삐져나가면 안 된다

게임은 사람이 보고 자르는 게 아니라 정해진 셀 좌표로 자릅니다.

규칙:

- 한 셀에는 한 프레임만 들어간다.
- 프레임이 옆 셀이나 위아래 셀로 넘어가면 안 된다.
- 셀 사이에 임의 여백이나 gutter를 넣지 않는다.
- 바깥쪽에 임의 padding을 넣지 않는다.
- 투명 여백은 고정 셀 내부에서만 허용한다.

금지 표현:

```text
Make it evenly spaced.
Arrange naturally.
Make it look like a sprite sheet.
```

좋은 표현:

```text
This must be a strict sprite atlas, not a loosely spaced contact sheet.
The game slices frames only by the exact grid boundaries.
No frame may bleed into adjacent cells.
Transparent padding may exist only inside each fixed cell.
```

## 4. Anchor는 visual center가 아니다

Anchor는 그림의 중심이 아니라 게임이 배치에 쓰는 기준점입니다.

예시:

```text
Contact anchor: x=192, y=252 inside every 384x288 cell.
This point is where the character foot touches the ground.
This anchor is not the visual center.
Do not move the contact anchor to make the sprite look centered.
```

캐릭터라면 보통 발바닥 기준점입니다.

타일이라면 플레이어 발이 닿는 접촉점입니다.

이펙트라면 충돌 중심점이나 원본 오브젝트 기준점입니다.

## 5. Y축 기준선을 따로 고정한다

Anchor와 Y축 정렬은 비슷하지만 다릅니다.

- Anchor: 코드가 배치하는 기준점
- Y-axis baseline: 애니메이션 중 흔들리면 안 되는 지면/발판/타일 평면의 기준선

반드시 따로 적습니다.

```text
Y-Axis Alignment Contract:
- The local Y baseline must not change between animation rows or frames.
- Grounded frames must share the same contact anchor Y: y=252.
- The sprite must not drift upward or downward during animation.
```

타일/FX의 경우:

```text
Y-Axis Plane Alignment:
- All FX rows derived from the same tile must preserve the same local tile plane Y.
- crack, break_shards, landing_pulse, warning_glow, and restore_glass must line up on the same plane.
- Shards and particles may move, but the original tile plane must not jump.
- When horizontal guide lines are overlaid, the main tile plane must match.
```

## 6. 행과 열의 의미를 고정한다

행/열 순서는 나중에 바꾸면 코드가 깨집니다.

예시:

```text
Columns:
- Column 0: idle
- Column 1: sneak
- Column 2: steal
- Column 3: stunned

Rows:
- Row 0: red
- Row 1: orange
- Row 2: yellow
- Row 3: green
- Row 4: blue
- Row 5: violet
```

규칙:

- 중간에 새 포즈를 끼워 넣지 않는다.
- 빈 셀을 만들지 않는다.
- 색상 variant는 포즈, 실루엣, 위치를 바꾸지 않는다.
- 색상만 바꾸는 variant는 anchor와 bbox가 최대한 같아야 한다.

## 7. Alpha와 파일 포맷

스프라이트는 기본적으로 투명 PNG입니다.

필수:

```text
PNG-32 RGBA
Straight alpha, not premultiplied alpha
sRGB color
Transparent background
No watermark
No labels
No guide grid
No text
```

주의:

- 배경 제거용 chroma-key 이미지는 source로만 보관한다.
- 게임에 쓰는 파일은 투명 PNG여야 한다.
- 키 컬러가 캐릭터 색과 겹치면 안 된다.
- 빨강/주황 캐릭터에는 magenta key가 번질 수 있으니 cyan key가 더 안전할 수 있다.
- 초록 오브젝트에는 green key를 피한다.

## 8. 프롬프트 기본형

```text
Resource Request Brief:
- Game / concept: {GAME_CONCEPT}
- Scene or screen where this appears: {SCENE_CONTEXT}
- Gameplay role: {GAMEPLAY_ROLE}
- Player-readable purpose: {PLAYER_READABLE_PURPOSE}
- Visual direction: {VISUAL_DIRECTION}
- Existing assets or style to match: {STYLE_REFERENCE}
- In-game display scale: {IN_GAME_SCALE}
- Target file path: {PATH}

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.

Create a transparent PNG-32 RGBA sprite atlas for a game.

This must be a strict sprite atlas, not a loosely spaced contact sheet.

Canvas:
- Final image size: exactly {WIDTH}x{HEIGHT}px
- Grid: exactly {COLS} columns x {ROWS} rows
- Cell size: exactly {CELL_W}x{CELL_H}px
- Column boundaries: x={COLUMN_BOUNDARIES}
- Row boundaries: y={ROW_BOUNDARIES}
- No gutters
- No outer padding outside the exact canvas
- No guide grid
- No labels
- No text
- Fully transparent background
- PNG-32 RGBA, straight alpha, sRGB

Runtime slicing rule:
- The game slices frames only by the exact grid boundaries above.
- Each cell must contain exactly one complete frame.
- Do not rely on visual spacing or manual cropping.
- No frame may bleed into another cell.
- No cell may be empty.
- Transparent padding may exist only inside each fixed cell.

Anchor Contract:
- Contact anchor is x={ANCHOR_X}, y={ANCHOR_Y} inside every {CELL_W}x{CELL_H} cell.
- This anchor means: {ANCHOR_MEANING}.
- This anchor is not the visual center.
- Do not move the contact anchor to the visual center.

Y-Axis Alignment Contract:
- The local Y baseline must not change between animation rows or frames.
- Grounded frames must share the same contact anchor Y: y={ANCHOR_Y}.
- Moving effects may animate, but the source plane must not jump.

Rows:
{ROWS_DESCRIPTION}

Columns:
{COLUMNS_DESCRIPTION}

Visual Requirements:
- {STYLE}
- Keep silhouette, angle, lighting, and scale consistent across frames.
- Effects may extend inside the cell, but must not bleed into adjacent cells.

Do Not:
- Do not change final size, grid, row order, or column order.
- Do not premultiply alpha.
- Do not crop body parts or important effects.
- Do not draw multiple unrelated poses in one cell.

Output Report:
- Final image size
- Alpha bbox
- Alpha bbox per cell if possible
- Confirm PNG-32 RGBA straight alpha
- Confirm anchor x={ANCHOR_X}, y={ANCHOR_Y}
- Confirm Y baseline did not drift across rows/frames

Animation Preview Tool:
- Create a local HTML animation preview tool by copying and adapting the generic SpriteMake animation player template.
- Tool output path: {ANIMATION_TOOL_PATH}
- Preview manifest path: {ANIMATION_MANIFEST_PATH}
- The tool must play each row/frame, show the full sheet grid, selected frame, contact anchor, Y-axis baseline/source plane, image size, cell size, alpha bbox, and path metadata.
- The tool must work by double-clicking the HTML file under `file://`; embed manifest/image data URL fallback when needed.
- The tool must auto-load the default manifest on page open.
- Verify in a real browser: ready=true, visible nonblank canvas, no console errors, and alpha bbox not blocked by file:// security.
- Use project-relative or user-configurable paths. Do not hardcode machine-specific source paths.
```

## 9. 검수 규칙

받은 뒤 반드시 확인합니다.

- 이미지 크기가 맞는가?
- `width % cols === 0` 인가?
- `height % rows === 0` 인가?
- 셀 크기가 manifest와 맞는가?
- 각 셀에 프레임이 하나씩만 있는가?
- 프레임이 인접 셀로 넘어가지 않는가?
- 발/타일/이펙트 기준 Y가 row마다 흔들리지 않는가?
- 투명 모서리가 깨끗한가?
- 키 컬러 fringe가 남지 않았는가?
- bbox 변화 때문에 코드 offset이 필요한가?

## 10. Pillow 검수 스니펫

```python
from pathlib import Path
from PIL import Image

path = Path("asset.png")
cols, rows = 4, 6
im = Image.open(path).convert("RGBA")
cw, ch = im.width // cols, im.height // rows

print("size", im.size)
print("cell", (cw, ch))
print("mod", (im.width % cols, im.height % rows))
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

## 11. 한 줄 요약

SpriteMake의 한 줄 목적은 이렇게 쓴다.

```text
Batch usable sprites: strict atlas + manifest + exact grid + contact anchor + Y-axis baseline + alpha QA + animation preview.
```


