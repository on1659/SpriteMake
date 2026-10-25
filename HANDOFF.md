# SpriteMake Handoff

## 한국어 요약

`D:\Work\vibe\SpriteMake`는 게임에 바로 넣을 수 있는 스프라이트를 일괄 생산하기 위한 생성 요청/세팅 프로젝트다.

이 프로젝트는 API key를 저장하거나 이미지 생성 API를 직접 호출하는 앱이 아니다. 목적은 strict atlas PNG가 게임에서 쓸 수 있도록 폴더 구조, MD 요청서, manifest, anchor/Y-axis 계약, QA 결과, 애니메이션 프리뷰 툴을 세팅하는 것이다.

현재 기본 운영은 키 없는 Codex 직접 생성이다. Codex 이미지 생성 기능으로 바로 시도할 수 있지만, 이 경로는 `gpt-image-2`를 강제하거나 검증하지 않는다. 엄격한 `gpt-image-2` 보장이 필요하면 `PROMPT.md`를 ChatGPT 웹이나 API key가 있는 외부 생성 환경에 넣는다.

엄격한 `gpt-image-2`를 요청했지만 현재 도구가 모델을 선택하거나 검증할 수 없으면 자동으로 거절하거나 대체 생성하지 않는다. 제한을 알리고, 결과를 `unverified Codex direct generation`으로만 기록해 `generated/`에 보관하는 조건으로 계속할지 한 번 묻는다. 명시적 동의가 있어야만 직접 생성한다.

최종 목표는 예쁜 그림이 아니라 게임 코드가 정확히 자르고 정확히 배치할 수 있는 usable sprite batch다.

## 핵심 사용 방식

1. 사용자는 긴 템플릿 대신 “드래곤 스프라이트 그려줘...”처럼 자연어로 요청해도 된다.
2. 자연어 요청은 `.agents/hooks/sprite-intake.ps1`로 먼저 받아 `output/{적당한이름}-{날짜시간}/` batch를 만든다.
3. `sprite-intake`는 원문 요청, output 경로, `gpt-image-2` 생성 대상 블록을 `PROMPT.md`에 자동 저장한다.
4. 생성 방식이 애매하면 기본은 Codex 직접 생성이다. 엄격 생성/세팅 전용을 구분해야 할 때만 `.agents/hooks/generation-choice.ps1`의 표준 질문을 사용한다.
5. `templates/batch-sprite-request-template.md`와 `templates/resource-request-template.md` 기준으로 부족한 사용처/경로/atlas 정보를 보강한다.
6. `mockup.html`의 1/2/3/4 단계 플로우는 더 정밀한 브리프, 경로, 아틀라스 계약, 툴/검토가 필요할 때 쓴다.
7. `gpt-image-2` 프롬프트 블록이 빠진 직접 작성 프롬프트는 `.agents/hooks/prompt-inject.ps1`로 보강한다.
8. 생성된 PNG는 바로 게임 프로젝트에 넣지 말고 SpriteMake batch 폴더의 `generated/`에 둔다.
9. `templates/asset-qa-checklist.md` 기준으로 PNG를 검수한다.
10. QA 통과 파일만 `final/`에 두고 실제 게임 프로젝트의 `assets/...`로 옮긴다.
11. 생성 전용 작업을 끝내면 batch의 `HANDOFF-CLAUDE.md`를 작성하고, 최종 응답은 그 내용을 요약한다. 여기에는 완료 범위, 미수행 범위, provenance, 레퍼런스 복사 경로, 에셋별 모든 attempt/횟수/현재 최선 시도, 제외 에셋, QA 상태, 다음 담당자, `final/`·게임 경로 변경 여부를 반드시 넣는다.

## 중요 규칙

`Contact Anchor`와 `Y-Axis Alignment`는 분리해서 써야 한다.

- Contact Anchor: 게임 코드가 sprite를 배치할 때 붙잡는 좌표다. 예: 발 접점, 타일 접점, 충돌 중심, 손/가방 부착점.
- Y-Axis Baseline / Source Plane: 프레임이나 row 사이에서 위아래로 흔들리면 안 되는 기준선이다. 예: 발바닥 기준선, 타일 평면, crack/break source plane.

프롬프트와 manifest, QA 문서에는 둘 다 명시한다.

```text
Strict atlas + exact grid + cell boundaries + contact anchor + Y-axis baseline + alpha QA + animation preview.
```

Preview tool 운영 규칙:

- `templates/animation-player-template.html`은 빈 원본이다. 실제 리소스 확인 경로로 안내할 때는 `output/{batch}/tools/animation-preview.html` 같은 adapted batch tool을 안내한다.
- 새 animation/preview HTML tool은 더블클릭 `file://` 단독 실행을 지원해야 한다.
- 서버가 필요한 도구는 보조 경로로만 허용한다. 기본 QA 경로가 “서버 켜기”이면 실패다.
- `file://`에서 manifest `fetch()` 또는 canvas pixel read가 막히면 adapted tool에 manifest와 PNG data URL fallback을 내장한다.
- HTTP 서버로 열 때는 실제 project-relative 파일을 우선해서 regenerated PNG 확인이 가능해야 한다.
- 페이지 open 시 기본 manifest를 자동 load하고 첫 sheet를 보여준다.
- 검증은 실제 브라우저로 `ready=true`, nonblank canvas, console error 0, bbox 표시 정상까지 확인한다.

## 현재 파일 구조

```text
  SpriteMake/
    README.md
    USAGE.md
    AGENTS.md
    agent.md
    HANDOFF.md
    WORKFLOW.md
    mockup.html
    symphony-concept.html
    symphony-usage.html
    start-symphony-gui.bat
    sprite-make-mockup.png
  .agents/
    README.md
    skills/
      spritemake-batch/
        SKILL.md
        references/
          workflow.md
    hooks/
      README.md
      preflight.ps1
      sprite-intake.ps1
      sprite-intake.config.json
      new-batch.ps1
      symphony.ps1
      symphony.config.json
      generation-choice.ps1
      generation-choice.config.json
      prompt-inject.ps1
      prompt-hook.config.json
  templates/
    batch-sprite-request-template.md
    folder-md-setup-template.md
    resource-request-template.md
    asset-generation-template.md
    sprite-atlas-template.md
    animation-player-template.html
    animation-manifest-template.json
    sprite-atlas-notes.md
    asset-qa-checklist.md
  tools/
    symphony-gui/
      server.js
      public/
        index.html
  output/
    SYMPHONY.md
    SYMPHONY-GUI.url
    SYMPHONY-GUI.json
    SYMPHONY-GUI.log
```

## 주요 문서

- `README.md`: 프로젝트 목적과 핵심 규칙
- `USAGE.md`: 사람이 따라 하는 사용법
- `AGENTS.md`: 에이전트가 지켜야 할 작업 규칙
- `agent.md`: `AGENTS.md`로 가는 소문자 별칭
- `WORKFLOW.md`: SpriteMake mini-Symphony 상태/작업 흐름 정의
- `.agents/README.md`: 로컬 agent/skill/hook 구성 설명
- `.agents/skills/spritemake-batch/SKILL.md`: SpriteMake batch 작업용 로컬 skill

## 주요 훅

### sprite-intake

짧은 자연어 요청을 받았을 때 가장 먼저 쓰는 hook이다.

```powershell
.\.agents\hooks\sprite-intake.ps1 -Request "드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 해."
```

이 hook이 하는 일:

- 요청 원문 저장
- `output/{name}-{yyyyMMdd-HHmmss}/` batch 생성
- `BATCH.md`, `REQUESTS.md`, `PROMPT.md`, `MANIFEST.md`, `QA.md` 생성
- `PROMPT.md`에 SpriteMake output 경로와 `gpt-image-2` 블록 자동 삽입
- 생성 방식이 `pending`이면 Codex vs `gpt-image-2` 질문 출력

### generation-choice

사용자가 “스프라이트/그림 만들어줘”처럼 생성 방식을 명확히 말하지 않았고, 기본 Codex 직접 생성이 맞는지 확인해야 할 때 묻는 표준 질문이다.

```powershell
.\.agents\hooks\generation-choice.ps1
```

표준 질문:

```text
생성 방식부터 정할게요.

1. Codex로 바로 생성
   - API key 없이 이 Codex 세션의 이미지 생성 기능으로 바로 시도합니다.
   - 모델을 gpt-image-2로 강제하거나 검증하지는 못합니다.
   - 결과물은 generated/의 검수 대상 시안으로 보고, QA 통과 전에는 final/로 옮기지 않습니다.

2. gpt-image-2 엄격 생성
   - 제가 gpt-image-2용 프롬프트를 만들어드립니다.
   - 실제 이미지는 ChatGPT 웹이나 API key가 있는 외부 생성 화면에 직접 입력해야 합니다.
   - 이 프로젝트에는 API key를 저장하거나 사용하지 않습니다.

3. Codex로 세팅만
   - 폴더, MD 요청서, 프롬프트, manifest, QA, preview tool만 세팅합니다.
   - 실제 이미지는 생성하지 않습니다.

어느 쪽으로 할까요?
```

### prompt-inject

`mockup.html`을 거치지 않고 직접 쓴 프롬프트에 `gpt-image-2` 생성 대상 블록을 주입한다.

```powershell
"Create a sprite atlas..." | .\.agents\hooks\prompt-inject.ps1
```

주입되는 블록:

```text
Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.
```

### new-batch

새 batch 폴더와 기본 MD 파일을 만든다.

```powershell
.\.agents\hooks\new-batch.ps1 -BatchId demo-feature
```

생성 구조:

```text
output/{batch}/
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

### preflight

핵심 파일, JSON, HTML script syntax, prompt hook, encoding sanity를 검사한다.

```powershell
.\.agents\hooks\preflight.ps1
```

### symphony

`output/*` batch 폴더를 SpriteMake 작업 보드처럼 스캔한다.

```powershell
.\.agents\hooks\symphony.ps1
```

이 hook이 하는 일:

- 표준 batch docs/folders 존재 여부 확인
- `PROMPT.md`의 `gpt-image-2` generation target 확인
- target path, grid/cell, contact anchor, Y-axis baseline/source plane 누락 감지
- `generated/`, `final/`, `manifests/`, `tools/`, `qa/` 산출물 개수 확인
- batch 상태를 `needs-refine`, `prompt-ready`, `qa-needed`, `final-candidate` 등으로 분류
- 다음 액션을 제안

리포트를 파일로 남기려면:

```powershell
.\.agents\hooks\symphony.ps1 -WriteReport
```

출력 파일:

```text
output/SYMPHONY.md
```

### Mini-Symphony GUI

현재 진행도는 브라우저 GUI로 확인할 수 있다.

```powershell
.\start-symphony-gui.bat
```

이 BAT는 `tools/symphony-gui/server.js`를 실행한다. 서버는 Node.js 기본 모듈만 사용하고, 빈 로컬 포트를 자동 선택한다.

실행 중 생성/갱신되는 파일:

```text
output/SYMPHONY-GUI.url
output/SYMPHONY-GUI.json
```

GUI는 `/api/batch-intake`로 자연어 제작 요청을 접수해 batch, `PROMPT.md`, QA
뼈대를 만들고, `/api/status`를 통해 `.agents/hooks/symphony.ps1 -Json -WriteReport`
결과를 보여준다. 이미지 API 호출과 `final/` 승격은 GUI가 하지 않는다.

GUI에는 `현재 진행 노드`와 `실시간 로그` 패널이 있다. 서버/스캔/Batch 상태 변화는 `output/SYMPHONY-GUI.log`에 JSONL로 append되고, 브라우저는 `/api/events` SSE 스트림으로 즉시 갱신한다.

## mockup.html 사용 흐름

1. Brief: 게임/화면/역할/가독 목적/비주얼 방향
2. Paths: 게임 프로젝트 루트, 최종 asset path, 참고 path, `gpt-image-2` 모델 요구
3. Atlas: canvas, grid, cell, anchor, row/column 의미
4. Tool / Review: animation preview tool path, preview manifest path, QA 상태 확인, 프롬프트 복사

프롬프트 복사는 필수값이 모두 채워져야 가능하다.

## 현재 프리셋

### Character

```text
Canvas: 1536x1728
Grid: 4 columns x 6 rows
Cell: 384x288
Anchor: x=192, y=252
Rows: red, orange, yellow, green, blue, violet
Columns: idle, sneak, steal, stunned
Anchor meaning: side-view foot and item/bag ground contact baseline
```

### Tile FX

```text
Canvas: 1400x1309
Grid: 4 columns x 7 rows
Cell: 350x187
Anchor: x=175, y=165
Rows: safe_sparkle, warning_glow, crack, break_shards, fall_trail, landing_pulse, restore_glass
Columns: frame 0, frame 1, frame 2, frame 3
Anchor meaning: character foot contact point on the tile, not the tile visual center
```

## 이미지 생성 모델 정책

- 엄격 생성의 기본/필수 이미지 생성 모델은 `gpt-image-2`다.
- SpriteMake는 모델명을 요청서와 프롬프트에 명시한다.
- 키 없는 기본 경로는 Codex 직접 생성이며, 모델은 미검증이다.
- SpriteMake는 API key를 저장하거나 API를 직접 호출하지 않는다.
- `gpt-image-2`를 외부 생성 환경에서 사용할 수 없으면 다른 모델로 조용히 엄격 생성 결과로 대체하지 말고 조건 미충족 또는 Codex-direct 시안으로 표시한다.
- ChatGPT 웹 UI나 외부 생성 화면을 쓰는 경우, 사용자가 프롬프트를 직접 입력해야 한다.

## 최종 asset 소유권

SpriteMake에서 다루는 것:

- batch sprite production requests
- folder and markdown setup
- sprite prompt rules
- strict atlas mockups
- generated attempts before QA
- manifests and preview tools
- QA reports

각 게임 프로젝트에서 다루는 것:

- final PNG assets
- game-specific manifests
- actual game integration
- production-specific docs

QA 통과 전 파일은 실제 게임 프로젝트의 production asset으로 취급하지 않는다.

## 검증 상태

최근 확인한 항목:

- `mockup.html` script syntax check passed with Node.
- `templates/animation-player-template.html` script syntax check passed with Node.
- Adapted animation preview tools must also be browser-tested under `file://` for auto-load, nonblank canvas, clean console, and readable alpha bbox.
- `templates/animation-manifest-template.json` parses as JSON.
- `.agents/hooks/preflight.ps1` passed.
- `.agents/hooks/symphony.ps1` scans output batches and can write `output/SYMPHONY.md`.
- `start-symphony-gui.bat`, `.sh`, and `_mac.command` launch the local Mini-Symphony dashboard on a random local port; it includes batch intake but not image generation or final promotion.
- `.agents/skills/spritemake-batch` skill validation passed.
- `.agents/hooks/prompt-inject.ps1` injects the required `gpt-image-2` block.
- `.agents/hooks/generation-choice.ps1` prints the standard Codex-vs-gpt-image-2 question.
- `.agents/hooks/sprite-intake.ps1` creates a natural-request batch scaffold and `PROMPT.md`.
- `mockup.html` generated prompt includes the required `gpt-image-2` generation target.

Screenshot:

```text
D:\Work\vibe\SpriteMake\sprite-make-mockup.png
```

## 다음에 하면 좋은 작업

### 2026-10-04 sprite-gen 비교 후 반영

- 공용 `tools/runner/inspect_sprite.py`: PNG/grid/cell/alpha bbox와 프레임
  차이·중복·루프 이음새 보고. 원본 보존, `qa/` 출력, 승인은 pending.
- 승격 gate: 계약 전체와 선언된 reference/curation 입력, 스타일 reference,
  비교 이미지의 SHA-256을 확인. 접지·모션 리뷰를 분리해 요구한다.
- batch skill/요청 템플릿: 승인된 기본 이미지→방향별 단일 reference→
  동작 생성, 비대칭 보존, 공통 배율과 공중 프레임의 높이 보존.
- intake 및 상태 보드에도 placement/motion 검수 항목을 연결했다.
- 기하 검사 pass를 실제 걸음새나 발 접점의 승인으로 간주하지 않는다.
  후광·스타일 등 공용 검사 범위 밖의 요구는 배치별 QA가 필요하다.
- 이전 status는 다음 승격 전 계약·입력 체크섬과 필요한 리뷰를 다시 기록한다.
- 기존 batch 후보 및 final PNG는 이번 업데이트의 변경 대상이 아니다.
- 검증: Python 25개·Node 3개 테스트 통과. 실제 임시 PNG로 검사→승인→
  승격→reference 변경 차단 및 재검사 시 승인 초기화를 확인했다.
- 스킬 validator·계약/status JSON 스키마·정적 preflight 통과.
  이 Mac에는 PowerShell이 없어 `.ps1` 런타임 preflight는 미검증이다.

아래 PNG QA 제작 항목은 공용 검사기가 기본 구조 측정을 제공하므로
추가 작업에서는 배치별 의미·색 오염 검사를 확장하는 기준으로 사용한다.

1. 프리셋 추가
   - 아이템
   - UI 아이콘
   - 이펙트 단일행
   - 탑다운 캐릭터
   - 스테이지 레이어
2. PNG QA 스크립트 제작
   - size/grid/cell 확인
   - full alpha bbox
   - per-cell alpha bbox
   - transparent corners
3. output convention 강화
   - `output/generated/`
   - `output/qa/`
   - `output/manifests/`
   - `output/tools/`
   - `output/final/`
4. before/after 예시 이미지 추가
   - bad loose contact sheet
   - correct strict atlas
   - anchor vs visual center
   - Y-axis drift vs fixed baseline

## 미래 에이전트 지침

사용자가 “스프라이트는 여기서 만들자” 또는 `D:\Work\vibe\SpriteMake`를 언급하면 이 폴더에서 먼저 작업한다.

작업 전 읽을 것:

1. `AGENTS.md`
2. `USAGE.md`
3. `README.md`
4. 이 `HANDOFF.md`

생성 방식이 애매하면 키 없는 Codex 직접 생성을 기본값으로 둔다. 엄격한 `gpt-image-2` 보장이나 세팅 전용이 필요한지 확인해야 할 때만 `.agents/hooks/generation-choice.ps1`의 질문을 사용한다.

단, 사용자가 짧은 자연어로 “OO 이미지/스프라이트 그려줘”라고 하면 긴 템플릿을 요구하지 말고 `.agents/hooks/sprite-intake.ps1`로 batch와 `PROMPT.md`를 먼저 만든 뒤 Codex 직접 생성으로 진행한다.

## 2026-10-10 — offline sprite-gen processing integration

Implemented tools/sprite_pipeline: pinned upstream recolor helpers with full
LICENSE/NOTICE/provenance; local explicit chroma/component/rect processing;
shared-scale fixed-grid packing; upstream absolute-frame manifest adapter;
portable animation preview and non-destructive frame curation/recipe export.
Each attempt creates new candidates and derived contracts. Original contract,
recipe, sources, manifest and transform report are fingerprinted. Processing
never approves reviews or writes final/game assets. Existing QA foundation is
included in the integration branch, with contracts/ accepted as a QA input.

Validation: 46 Python unittest cases passed on Python3.12.14/Pillow12.3.0/
NumPy2.3.5. Real Chromium file:// checks reached ready:true with nonblank canvases,
working animation selection, no console errors or blocked alpha reads. Browser
1px recipe edits rebaked to the exact live alpha bbox. Existing Cyrano south-run
8-frame provisional PNG repacked with identical pixels. These are processing
checks, not an approval of Cyrano gait, anatomy, style or contact placement.
PowerShell preflight was not run because PowerShell is not installed here.

Start with tools/sprite_pipeline/README.md and
examples/sprite-pipeline/create_demo.py. Optional video/RIFE, automatic anatomy
repair and breathing animation are outside this PNG implementation. Chroma and
pixelGrid are conservative local tools rather than the complete upstream unmix
or lattice engines. Attempt statuses do not replace Symphony root status files.
