# SpriteMake Usage

SpriteMake는 직접 이미지 생성 API를 호출하는 앱이 아닙니다.

현재 기본 흐름은 키 없는 Codex 직접 생성입니다. Codex 이미지 생성 기능으로 바로 시도하되, 모델을 `gpt-image-2`로 강제하거나 검증하지는 않습니다.

역할은 이것입니다.

```text
게임에 쓸 수 있는 스프라이트가 나오도록
폴더, MD 요청서, copy-ready prompt, manifest, QA, animation preview tool을 세팅한다.
```

## Quick Start

사용자는 길게 형식을 맞춰 쓰지 않아도 됩니다.

예시:

```text
드래곤 스프라이트 그려줘. 드래곤은 불속성과 얼음속성 두 개가 있어야 하고, 사람이 탈 수 있을 정도로 커야 하고, 우리가 아는 보통의 드래곤과 흡사해야 해.
```

SpriteMake 쪽에서 자동으로 해야 할 일:

1. 요청문을 받아 `output/{적당한이름}-{날짜시간}/` batch 폴더를 만든다.
2. `BATCH.md`, `REQUESTS.md`, `PROMPT.md`, `MANIFEST.md`, `QA.md`를 만든다.
3. `PROMPT.md`에 output 경로와 `gpt-image-2` 생성 대상 블록을 자동으로 넣는다.
4. 기본값으로 Codex 직접 생성을 진행한다.
5. Codex 직접 생성 결과는 모델 미검증 시안으로 `generated/`에 둔다.
6. `gpt-image-2` 엄격 생성이 필요하면 `PROMPT.md`의 프롬프트를 ChatGPT 웹이나 외부 생성 화면에 직접 입력한다.
7. 받은 PNG를 `generated/`에 넣는다.
8. QA를 통과한 PNG만 `final/`에 둔다.
9. manifest와 animation preview tool로 실제 slicing/anchor/Y축 기준선을 확인한다.
10. 통과한 파일만 실제 게임 프로젝트의 `assets/...`로 옮긴다.

자동 intake hook:

```powershell
.\.agents\hooks\sprite-intake.ps1 -Request "드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 해."
```

그 다음 현재 batch들의 상태를 보려면 mini-Symphony hook을 실행합니다.

```powershell
.\.agents\hooks\symphony.ps1
```

리포트 파일까지 남기려면:

```powershell
.\.agents\hooks\symphony.ps1 -WriteReport
```

생성되는 파일:

```text
output/SYMPHONY.md
```

이 hook은 `output/*` 폴더를 작업 보드처럼 보고 `needs-refine`, `prompt-ready`, `qa-needed`, `final-candidate` 같은 상태와 다음 액션을 알려줍니다. 이미지 API를 호출하지 않고, PNG를 `final/`로 옮기지도 않습니다.

브라우저 GUI로 현재 진행도를 보려면:

```powershell
.\start-symphony-gui.bat
```

이 BAT는 빈 로컬 포트를 자동으로 선택해서 SpriteMake Mini-Symphony 대시보드를 띄웁니다.

```text
output/SYMPHONY-GUI.url
```

에도 마지막 GUI 주소가 저장됩니다.

실시간 로그와 현재 노드 진행도는 같은 화면의 `현재 진행 노드` / `실시간 로그` 패널에서 볼 수 있습니다. 원본 로그 파일은 다음 위치에 계속 append됩니다.

```text
output/SYMPHONY-GUI.log
```

## 1. 새 Batch 시작

추천 폴더 구조:

```text
output/{game-or-feature}/
  BATCH.md
  REQUESTS.md
  PROMPT.md
  MANIFEST.md
  QA.md
  prompts/
  generated/
  source/
  manifests/
  tools/
  qa/
  final/
```

기준 템플릿:

```text
templates/folder-md-setup-template.md
templates/batch-sprite-request-template.md
```

`BATCH.md`에는 batch 목적, 공통 스타일, 대상 게임 프로젝트, asset 목록, 진행 상태를 적습니다.

## 2. Asset 요청서 만들기

각 asset마다 먼저 사용처를 적습니다.

```text
- 어떤 게임/컨셉인가?
- 어떤 화면/상황에 나오나?
- 플레이에서 무슨 역할인가?
- 플레이어가 무엇을 읽어야 하나?
- 기존 리소스와 어떤 스타일을 맞춰야 하나?
- 실제 게임에서 어느 크기로 보이나?
- 최종 target path는 어디인가?
```

그 다음 `mockup.html`을 엽니다.

```text
D:\Work\vibe\SpriteMake\mockup.html
```

4단계를 순서대로 채웁니다.

```text
1. Brief
2. Paths
3. Atlas
4. Tool / Review
```

필수값이 빠지면 프롬프트 복사가 막히게 되어 있습니다.

## 3. 프롬프트 사용

`mockup.html`에서 복사한 프롬프트는 Codex 직접 생성, 외부 이미지 생성 도구, 작업자, 또는 별도 생성 워크플로우에 전달합니다.

SpriteMake에는 API key를 넣지 않습니다.

사용자가 “스프라이트/그림 만들어줘”라고만 말하면 기본은 Codex 직접 생성입니다. 엄격한 모델 보장이나 세팅 전용이 필요할 때만 생성 방식을 고릅니다.

```text
1. Codex로 바로 생성
   - API key 없이 Codex 이미지 생성 기능으로 바로 시도
   - gpt-image-2 강제/검증은 불가
   - 결과는 generated/의 QA 대상 시안으로 보관

2. gpt-image-2 엄격 생성
   - gpt-image-2용 프롬프트를 만듦
   - 실제 이미지는 ChatGPT 웹이나 외부 생성 화면에 직접 입력해야 함

3. Codex로 세팅만
   - 폴더/MD/프롬프트/manifest/QA/preview tool만 세팅
   - 실제 이미지는 생성하지 않음
```

표준 질문 문구는 로컬 hook으로 출력할 수 있습니다.

```powershell
.\.agents\hooks\generation-choice.ps1
```

짧은 자연어 요청에서 batch까지 자동으로 만들 때는 이 hook을 먼저 씁니다.

```powershell
.\.agents\hooks\sprite-intake.ps1 -Request "{사용자 요청 원문}"
```

`mockup.html`을 거치지 않고 직접 쓴 프롬프트는 보내기 전에 로컬 hook으로 `gpt-image-2` 블록을 붙입니다.

```powershell
"Create a sprite atlas..." | .\.agents\hooks\prompt-inject.ps1
```

이미지를 만들 때는 요청서에 다음 조건이 들어가야 합니다.

```text
Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
```

금지:

```text
- API key를 README, batch MD, HTML, JSON에 저장
- gpt-image-2 요구를 빼고 이미지 생성 요청
- gpt-image-2가 안 된다고 다른 모델로 몰래 대체
- 임시 로컬 source path를 reusable template에 하드코딩
- 생성 실패본을 final asset처럼 게임 프로젝트에 복사
```

## 4. 결과 파일 배치

받은 파일은 바로 게임 프로젝트에 넣지 않습니다.

```text
generated/
- 외부 생성 도구에서 받은 원본 결과

source/
- 참고 이미지, source sheet, cleanup 전 중간 파일

qa/
- 검수 로그, screenshot, bbox report

final/
- QA 통과 후 게임 프로젝트로 옮길 준비가 된 파일
```

## 5. Manifest 만들기

애니메이션이 있는 atlas는 manifest를 같이 만듭니다.

시작 템플릿:

```text
templates/animation-manifest-template.json
```

manifest에는 최소한 이것이 있어야 합니다.

```text
- image
- grid columns / rows
- anchor
- baselineY
- animations
- fps
- frame order
```

Anchor는 가능하면 pixel 좌표로 적습니다.

```json
"anchor": { "x": 192, "y": 252, "mode": "pixel" }
```

정규화 좌표를 쓸 때는 반드시 명시합니다.

```json
"anchor": { "x": 0.5, "y": 0.875, "mode": "normalized" }
```

## 6. Animation Preview Tool 만들기

애니메이션 sprite atlas는 HTML 프리뷰 툴로 재생 확인까지 합니다.

시작 템플릿:

```text
templates/animation-player-template.html
```

주의: 위 파일은 빈 템플릿입니다. 실제 스프라이트 확인은 batch별 adapted tool을 엽니다.

```text
output/{batch}/tools/animation-preview.html
```

사용 방식:

1. 이 HTML을 batch의 `tools/` 또는 게임 프로젝트의 도구 폴더로 복사한다.
2. `Manifest` 입력값을 manifest JSON 경로로 맞춘다.
3. 필요하면 `Project Root`를 채워 로컬 path 표시를 확인한다.
4. sheet, animation, palette, FPS, scale을 바꿔 본다.
5. full sheet grid, selected frame, contact anchor, Y baseline을 확인한다.

필수 실행 규칙:

- 사용자가 HTML을 더블클릭해 `file://`로 열어도 기본 sheet가 자동으로 떠야 한다.
- 로컬 서버가 없다는 이유만으로 preview가 비어 있으면 실패다.
- 브라우저가 `file://`에서 `fetch()` 또는 canvas pixel read를 막는 경우, manifest와 현재 PNG 후보를 HTML에 내장하거나 data URL fallback을 넣는다.
- 단, 로컬 HTTP 서버로 열 때는 실제 `generated/` 또는 `final/` 파일을 읽도록 project-relative path를 우선한다.
- `Load` 버튼은 수동 재로드/다른 manifest 선택용으로 남기되, 최초 확인에 필수이면 안 된다.

이 툴에서 봐야 하는 것:

```text
- 프레임이 정확한 셀에서 잘리는가?
- anchor가 발/접촉점/원본 평면에 맞는가?
- Y baseline이 row/frame마다 흔들리지 않는가?
- alpha bbox가 과하게 튀지 않는가?
- 게임에서 보이는 크기로 읽히는가?
```

## 7. QA

기준 체크리스트:

```text
templates/asset-qa-checklist.md
```

최소 QA:

```text
- final size가 요청과 같은가?
- width % columns === 0 인가?
- height % rows === 0 인가?
- 셀 크기가 manifest와 같은가?
- 각 셀에 프레임이 하나만 있는가?
- 인접 셀로 넘치지 않는가?
- anchor와 Y baseline이 맞는가?
- 투명 모서리가 깨끗한가?
- per-cell alpha bbox가 기록됐는가?
- animation preview tool에서 재생 확인했는가?
- animation preview tool을 file://로 직접 열었을 때 자동 로드되는가?
- file://에서도 alpha bbox가 `pixel read blocked`가 아니라 실제 bbox로 표시되는가?
- 브라우저 콘솔 에러가 0개인가?
```

## 8. 게임 프로젝트로 옮기기

`final/`에 있는 QA 통과 파일만 실제 게임 프로젝트로 옮깁니다.

옮길 때 같이 확인합니다.

```text
- target asset path
- manifest path
- 코드가 기대하는 grid/cell size
- 코드가 기대하는 anchor/baseline
- animation key 이름
- cache busting이나 asset revision 필요 여부
```

SpriteMake의 `output/.../final`은 준비 구역이고, 실제 production asset의 소유권은 각 게임 프로젝트에 있습니다.

## Codex에게 시킬 때

예시:

```text
드래곤 스프라이트 그려줘.
드래곤은 불속성과 얼음속성 두 종류가 있어야 하고, 사람이 탈 수 있을 정도로 커야 해.
```

이렇게만 말하면 Codex는 SpriteMake 기준으로 `sprite-intake`를 먼저 돌려 batch와 `PROMPT.md`를 만들고, 생성 방식을 한 번만 물어봐야 합니다.

이미 PNG를 받은 뒤:

```text
SpriteMake output에 받은 PNG를 넣어뒀어.
manifest 만들고 animation preview tool 복사해서 QA 기준으로 확인해줘.
게임 프로젝트로 옮길 수 있는 final 상태인지 알려줘.
```

전체 진행 상황을 정리하고 싶을 때:

```text
SpriteMake mini-Symphony 돌려서 output batch 상태랑 다음 액션 정리해줘.
```

웹 GUI를 켜고 싶을 때:

```text
SpriteMake 진행도 GUI 켜줘.
```


