# Crazy Arcade Web Clone — Resource Requests

## 사용처 질문 답변 (전 asset 공통)

1. 어떤 게임/컨셉? → 크레이지 아케이드 웹 클론. 탑다운 물풍선 배틀.
2. 어떤 화면/상황? → 인게임 전투 화면 (타이틀/결과 화면 아님).
3. 플레이에서 무슨 역할? → 캐릭터/물풍선/물줄기/타일/아이템/이펙트를 구분 가능하게 표현.
4. 플레이어가 무엇을 읽어야? → 48px 렌더 크기에서 방향·상태·아이템 종류 즉시 식별 가능.
5. 기존 리소스와 스타일 맞춤? → 신규 일관 스타일 (원작 크아 감성 카툰).
6. 실제 게임에서 어느 크기? → 캐릭터/풍선/아이템: 48×48px. 타일: 48×48px.
7. 최종 target path? → `assets/sprites/{sheet}.png` (게임 프로젝트 루트 기준).

---

## Asset 0: char — 캐릭터 Atlas

Resource Request Brief:
- ID: `char`
- Asset role: 플레이어 및 봇 캐릭터 sprite atlas (3 palette 변형: bazzi / dao / marid)
- Game / concept: 탑다운 물풍선 배틀
- Scene or screen where this appears: 인게임 전투 화면
- Gameplay role: 캐릭터 이동 방향·상태(대기/이동/갇힘/탈락)를 실시간으로 표현
- Player-readable purpose: 48px 크기에서 방향·상태 즉시 식별. bazzi=밝은 노랑/주황, dao=파랑, marid=보라/딥그린
- Visual direction: 원작 크아 감성 밝은 카툰. 동그란 큰 눈, 볼터치. 탑다운 0.75-뷰 (정면보다 약간 위에서 내려다봄). 발 접지점 명확.
- Existing assets or style to match: 없음 (신규)
- In-game display scale: 48px (원본 96px, defaultScale 0.5)
- Target file path: `assets/sprites/char-bazzi.png` (+ `char-dao.png`, `char-marid.png` — 같은 grid, 색만 다름)
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- QA priority: high

Runtime Contract:
- Game project root: `/Users/radar/Work/CrazyArcadeCopy`
- Target asset path: `assets/sprites/char-bazzi.png`
- Asset type: transparent animated player atlas
- Static image or sprite atlas: strict sprite atlas
- Final canvas size: exactly `384x672`
- Grid columns: exactly `4`
- Grid rows: exactly `7`
- Cell size: exactly `96x96`
- Column boundaries: `x=0,96,192,288,384`
- Row boundaries: `y=0,96,192,288,384,480,576,672`
- Contact anchor: `x=48, y=84, mode=pixel` (발/타일 접지점, 셀 좌표계)
- Contact anchor meaning: 캐릭터 발이 타일 바닥에 닿는 지점
- Y-axis baseline/source plane: `baselineY: 84` (모든 row 공통, anchor와 별도 필드로 항상 분리)
- Alpha/background requirement: PNG-32 RGBA, straight alpha, transparent background
- Default scale: `0.5`

Rows:
- row 0: `idle` — 대기 (4프레임 호흡/살랑 애니메이션)
- row 1: `walk_down` — 아래쪽 이동 (4프레임)
- row 2: `walk_up` — 위쪽 이동 (4프레임)
- row 3: `walk_left` — 왼쪽 이동 (4프레임)
- row 4: `walk_right` — 오른쪽 이동 (4프레임)
- row 5: `trapped` — 물버블에 갇힘 (4프레임 흔들기)
- row 6: `dead` — 탈락/퇴장 (4프레임 페이드/쓰러짐)

Columns:
- column 0–3: frame 0–3 (왼쪽→오른쪽 재생 순서)

Palette variants (같은 grid, 색만 다른 PNG):
- `char-bazzi.png` — 배찌형: 밝은 노랑 피부, 주황 머리카락, 파란 옷 포인트
- `char-dao.png` — 다오형: 파란 피부/옷 계열, 흰 포인트
- `char-marid.png` — 마리드형: 보라/딥그린 계열, 파워풀한 체형 (약간 더 넓은 실루엣)

Animation Preview Tool Request:
- Tool output path: `/Users/radar/Work/SpriteMake/output/crazy-arcade/tools/char-preview.html`
- Preview manifest path: `/Users/radar/Work/SpriteMake/output/crazy-arcade/manifests/crazy-arcade.manifest.json`

---

## Asset 1: balloon — 물풍선 Atlas

Resource Request Brief:
- ID: `balloon`
- Asset role: 설치된 물풍선과 팽창 애니메이션
- Scene or screen where this appears: 인게임 전투 화면
- Gameplay role: 풍선 설치 후 퓨즈(3000ms) 동안 부풀어오르다 폭발 직전 최대 크기
- Player-readable purpose: 48px 크기에서 "풍선이 있다"는 것과 폭발 임박 여부 즉시 식별
- Visual direction: 파란 물이 든 반투명 카툰 풍선. 설치→팽창→최대 3단계.
- In-game display scale: 48px (defaultScale 0.5)
- Target file path: `assets/sprites/balloon.png`
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- QA priority: high

Runtime Contract:
- Final canvas size: exactly `192x96`
- Grid columns: exactly `2`
- Grid rows: exactly `1`
- Cell size: exactly `96x96`
- Column boundaries: `x=0,96,192`
- Row boundaries: `y=0,96`
- Contact anchor: `x=48, y=84, mode=pixel`
- Contact anchor meaning: 풍선 바닥이 타일 바닥에 닿는 접지점 (캐릭터와 같은 발밑 기준)
- Y-axis baseline/source plane: `baselineY: 84`
- Alpha/background requirement: PNG-32 RGBA, straight alpha

Rows:
- row 0: `inflate` — col0=작은 풍선(설치 직후), col1=부푼 풍선(폭발 임박)

Note: 폭발 자체는 `stream` + `fx` 시트에서 처리. 풍선 시트는 존재 상태만 표현.

---

## Asset 2: stream — 물줄기 Atlas

Resource Request Brief:
- ID: `stream`
- Asset role: 폭발 후 4방향으로 퍼지는 물줄기 (중심/팔/끝 구분)
- Scene or screen where this appears: 인게임 전투 화면
- Gameplay role: 물줄기 활성 타일 표시 (500ms 지속)
- Player-readable purpose: 48px 크기에서 "물줄기가 있다", 방향, 피격 범위 즉시 식별
- Visual direction: 파란 물 줄기. 중심=십자 방사형, 팔=직선, 끝=둥근 마무리. 모두 투명 배경.
- In-game display scale: 48px (defaultScale 0.5)
- Target file path: `assets/sprites/stream.png`
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- QA priority: high

Runtime Contract:
- Final canvas size: exactly `192x384`
- Grid columns: exactly `2`
- Grid rows: exactly `4`
- Cell size: exactly `96x96`
- Column boundaries: `x=0,96,192`
- Row boundaries: `y=0,96,192,288,384`
- Contact anchor: `x=48, y=48, mode=pixel` (타일 중심)
- Y-axis baseline/source plane: `baselineY: 48`
- Alpha/background requirement: PNG-32 RGBA, straight alpha

Rows (부위별 — 프레임은 column 방향 진행):
- row 0: `center` — 십자 방사형 중심. col0=frame0(정지), col1=frame1(출렁)
- row 1: `arm_h` — 좌우 방향 팔(직선). col0=frame0, col1=frame1
- row 2: `arm_v` — 상하 방향 팔(직선). col0=frame0, col1=frame1
- row 3: `end` — 둥근 끝 마무리(범용 end cap). col0=frame0, col1=frame1

Columns:
- column 0–1: frame 0–1 (왼쪽→오른쪽 재생 순서 — 정지→출렁)

Note: `end`는 4방향별로 다른 시트가 필요하면 별도 asset으로 분리 가능. 최소 구현은 row 3=범용 끝 처리.

---

## Asset 3: tiles — 타일 Atlas

Resource Request Brief:
- ID: `tiles`
- Asset role: 바닥·소프트블록·하드블록 타일 + 소프트블록 파괴 애니메이션
- Scene or screen where this appears: 인게임 맵 배경
- Gameplay role: 맵 시각화. 소프트블록은 파괴 가능, 하드블록은 불가.
- Player-readable purpose: 48px에서 "밟을 수 있는 바닥" / "부숴지는 블록" / "절대 못 뚫는 블록" 즉시 구분
- Visual direction: 잔디 그린 체커 바닥(2색), 갈색 나무 질감 소프트블록, 회색/돌 질감 하드블록. 탑다운 0.75-뷰.
- In-game display scale: 48px (원본 96px 셀을 defaultScale 0.5로 48px 타일에 렌더)
- Target file path: `assets/sprites/tiles.png`
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- QA priority: medium

Runtime Contract:
- Final canvas size: exactly `384x192`
- Grid columns: exactly `4`
- Grid rows: exactly `2`
- Cell size: exactly `96x96`
- Column boundaries: `x=0,96,192,288,384`
- Row boundaries: `y=0,96,192`
- Contact anchor: `x=48, y=48, mode=pixel` (타일 중심)
- Y-axis baseline/source plane: `baselineY: 48`
- Alpha/background requirement: PNG-32 RGBA, straight alpha (바닥 타일은 불투명 허용)

Rows:
- row 0: col0=floor_a(바닥 밝음), col1=floor_b(바닥 어둠 — 체커 패턴 짝), col2=soft_block(소프트블록 기본), col3=hard_block(하드블록)
- row 1: col0=soft_break_0(파괴 frame0), col1=soft_break_1(파괴 frame1), col2=soft_break_2(파괴 frame2), col3=soft_break_3(파괴 frame3/잔해)

---

## Asset 4: items — 아이템 Atlas

Resource Request Brief:
- ID: `items`
- Asset role: 필드에 드롭되는 5종 아이템 (물약/풍선/롤러/바늘/다리미)
- Scene or screen where this appears: 인게임 전투 화면 (소프트블록 파괴 후 드롭)
- Gameplay role: 아이템별 효과(물줄기UP/풍선UP/속도UP/바늘탈출/즉발다리미) 획득 유도
- Player-readable purpose: 48px에서 5종 아이템 즉시 구분. 아이콘적 실루엣 중요.
- Visual direction: 밝고 선명한 카툰 아이콘. 각 아이템이 한눈에 구분되는 고유 실루엣.
  - 물약(potion): 파란 물약 병
  - 풍선(balloon): 작은 노란/빨간 풍선
  - 롤러(roller): 롤러/속도 부스트 신발
  - 바늘(needle): 뾰족한 핀/바늘
  - 다리미(iron): 번쩍이는 다리미
- In-game display scale: 48px (defaultScale 0.5)
- Target file path: `assets/sprites/items.png`
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- QA priority: medium

Runtime Contract:
- Final canvas size: exactly `192x480`
- Grid columns: exactly `2`
- Grid rows: exactly `5`
- Cell size: exactly `96x96`
- Column boundaries: `x=0,96,192`
- Row boundaries: `y=0,96,192,288,384,480`
- Contact anchor: `x=48, y=84, mode=pixel`
- Contact anchor meaning: 드롭된 아이템이 타일 바닥에 놓이는 접지 기준점 (부유/바운스 연출은 이 기준점 위로 오프셋)
- Y-axis baseline/source plane: `baselineY: 84`
- Alpha/background requirement: PNG-32 RGBA, straight alpha

Rows (items.js 타입명과 1:1 대응):
- row 0: `potion` — 물약. col0=idle frame0, col1=idle frame1 (반짝임)
- row 1: `balloon` — 풍선 아이템. col0=idle frame0, col1=idle frame1
- row 2: `roller` — 롤러. col0=idle frame0, col1=idle frame1
- row 3: `needle` — 바늘. col0=idle frame0, col1=idle frame1
- row 4: `iron` — 다리미. col0=idle frame0, col1=idle frame1

---

## Asset 5: fx — 이펙트 Atlas

Resource Request Brief:
- ID: `fx`
- Asset role: 버블 터짐 / 바늘 사용 / 물 튀김 / 아이템 획득 / 블록 파편 / 아이템 소멸 이펙트
- Scene or screen where this appears: 인게임 전투 화면
- Gameplay role: 피격/탈출/획득/파괴 순간을 시각적으로 강조
- Player-readable purpose: 48px 이상에서 어떤 이벤트가 발생했는지 즉시 파악 (연출용 — 게임 판정에 영향 없음)
- Visual direction: 밝고 빠른 카툰 이펙트. pop=물방울 터짐 원형, needle=뾰족한 반짝임, splash=물 튀김, pickup=별/반짝임, crumb=갈색 블록 조각 비산, itemPop=흰 물방울 버스트.
- In-game display scale: 48~96px (이펙트는 타일을 조금 넘는 크기 허용)
- Target file path: `assets/sprites/fx.png`
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- QA priority: low

Runtime Contract:
- Final canvas size: exactly `384x576`
- Grid columns: exactly `4`
- Grid rows: exactly `6`
- Cell size: exactly `96x96`
- Column boundaries: `x=0,96,192,288,384`
- Row boundaries: `y=0,96,192,288,384,480,576`
- Contact anchor: `x=48, y=48, mode=pixel` (이펙트 중심)
- Y-axis baseline/source plane: `baselineY: 48`
- Alpha/background requirement: PNG-32 RGBA, straight alpha

Rows (game.js addEffect 타입과 1:1 대응):
- row 0: `pop` — 버블 터짐. 4프레임 (폭발→잔향 순서)
- row 1: `needle` — 바늘 사용(자기 버블 탈출). 4프레임 (찌르기→반짝임)
- row 2: `splash` — 물 튀김 피격. 4프레임 (충돌 순간→흩어짐)
- row 3: `pickup` — 아이템 획득. 4프레임 (별/빛 반짝임)
- row 4: `crumb` — 소프트블록 파괴 파편. 4프레임 (갈색 사각 나무 조각이 사방으로 튀어오르며 비산→소멸). 각 셀 빈 셀 금지
- row 5: `itemPop` — 물줄기에 맞은 아이템 소멸. 4프레임 (흰 물방울 4방향 버스트→흩어지며 소멸). 각 셀 빈 셀 금지
