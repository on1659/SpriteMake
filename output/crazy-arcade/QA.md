# Crazy Arcade Sprite Batch — QA 판정 기록

## 상태 요약

| Sheet | 생성 | QA | final 승격 | 게임 통합 |
|-------|------|-----|------------|----------|
| char-bazzi | generated draft v3 | probe PASS / copied to game assets | - | - |
| char-dao | generated draft | probe PASS + palette review PASS (20260705) | final/char-dao.png | assets/sprites/char-dao.png |
| char-marid | generated draft | probe PASS + palette review PASS (20260705) | final/char-marid.png | assets/sprites/char-marid.png |
| char-uni | generated draft v3 | probe PASS / copied to game assets / contract update needed | - | - |
| balloon | BLOCKED(사용자) | - | - | - |
| stream | BLOCKED(사용자) | - | - | - |
| tiles | generated draft | probe partial PASS / art review needed | - | - |
| items | generated draft v2 | probe PASS / copied to game assets | - | - |
| fx | BLOCKED(사용자) | - | - | - |

## QA 체크리스트 (시트 생성 후 적용)

각 시트 QA 시 Pillow probe 스크립트 실행 후 아래 항목 확인:

| # | 항목 |
|---|------|
| 1 | final size가 REQUESTS.md 요청과 정확히 일치 |
| 2 | `width % columns === 0` |
| 3 | `height % rows === 0` |
| 4 | 셀 크기 96×96 확인 |
| 5 | 각 셀에 프레임 1개 — 인접 셀 침범·빈 셀 없음 |
| 6 | contact anchor (48,84) 또는 (48,48) 문서화 값과 일치 |
| 7 | Y baseline row/frame 간 무흔들림 |
| 8 | 투명 모서리 확인 (RGBA straight alpha) |
| 9 | per-cell alpha bbox 보고 기록 |
| 10 | animation preview tool에서 재생 확인 |

## QA 진행 로그

### 2026-06-12 — built-in image draft generation

Generated original, non-IP-copy draft sheets and stored them under `generated/`.

Files:
- `generated/char-bazzi-draft-20260612-source.png`
- `generated/char-bazzi-draft-20260612-alpha.png`
- `generated/char-bazzi-draft-20260612-384x672.png`
- `generated/char-bazzi-draft-20260612-normalized-384x672.png`
- `generated/char-dao-draft-20260612-normalized-384x672.png`
- `generated/char-marid-draft-20260612-normalized-384x672.png`
- `generated/tiles-draft-20260612-source.png`
- `generated/tiles-draft-20260612-alpha.png`
- `generated/tiles-draft-20260612-384x192.png`
- `generated/items-draft-20260612-source.png`
- `generated/items-draft-20260612-alpha.png`
- `generated/items-draft-20260612-192x480.png`
- `generated/items-draft-20260612-normalized-192x480.png`

Probe summary:
- `char-bazzi-draft-20260612-normalized-384x672.png`: 384×672 RGBA, 4×7 grid, transparent corners, no empty cells, no edge-touching cells.
- `char-dao-draft-20260612-normalized-384x672.png`: 384×672 RGBA, 4×7 grid, transparent corners, no empty cells, no edge-touching cells.
- `char-marid-draft-20260612-normalized-384x672.png`: 384×672 RGBA, 4×7 grid, transparent corners, no empty cells, no edge-touching cells.
- `tiles-draft-20260612-384x192.png`: 384×192 RGBA, 4×2 grid, transparent corners, no empty cells, no edge-touching cells.
- `items-draft-20260612-normalized-192x480.png`: 192×480 RGBA, 2×5 grid, transparent corners, no empty cells, no edge-touching cells.

Notes:
- Exact Crazy Arcade character copying was intentionally avoided; these are original water-balloon battle assets.
- `char-bazzi` source generation produced an extra visual row; `normalized` repacks the first 7 rows into the manifest contract.
- `char-dao` and `char-marid` are palette-derived from the normalized `char-bazzi` draft so the grid and animation timing stay identical.
- Not promoted to `final/` yet. Remaining QA: visual review at 48px, animation preview, row/baseline motion check, and manifest JSON creation after accepting art direction.

### 2026-06-12 — requested Bazzi-type and Uni-type drafts

Generated two additional original character drafts. Exact copying of existing Crazy Arcade characters was intentionally avoided; these are project-local water-balloon battle archetypes.

Files:
- `generated/char-bazzi-v2-draft-20260612-source.png`
- `generated/char-bazzi-v2-draft-20260612-alpha.png`
- `generated/char-bazzi-v2-draft-20260612-normalized-384x672.png`
- `generated/char-uni-draft-20260612-source.png`
- `generated/char-uni-draft-20260612-alpha.png`
- `generated/char-uni-draft-20260612-normalized-384x672.png`

Probe summary:
- `char-bazzi-v2-draft-20260612-normalized-384x672.png`: 384×672 RGBA, 4×7 grid, transparent corners, no empty cells, no edge-touching cells.
- `char-uni-draft-20260612-normalized-384x672.png`: 384×672 RGBA, 4×7 grid, transparent corners, no empty cells, no edge-touching cells.

Notes:
- `char-bazzi-v2` is a cleaner 7-row atlas than the earlier `char-bazzi` draft and should be preferred for preview.
- `char-uni` is not yet part of the original manifest contract (`bazzi/dao/marid`). If accepted, update `REQUESTS.md`, `MANIFEST.md`, and the game loader mapping before promoting to `final/`.
- Not promoted to `final/` yet. Remaining QA: 48px visual review, animation preview, baseline jitter check, and manifest contract decision.

### 2026-06-12 — closer arcade-mascot v3 drafts

Generated closer-feeling original arcade mascot drafts after feedback that v2 felt too different. These intentionally move closer in broad proportions, palette, and arcade readability while avoiding exact character copying.

Files:
- `generated/char-bazzi-v3-draft-20260612-source.png`
- `generated/char-bazzi-v3-draft-20260612-alpha.png`
- `generated/char-bazzi-v3-draft-20260612-normalized-384x672.png`
- `generated/char-uni-v3-draft-20260612-source.png`
- `generated/char-uni-v3-draft-20260612-alpha.png`
- `generated/char-uni-v3-draft-20260612-alpha-clean.png`
- `generated/char-uni-v3-draft-20260612-normalized-384x672.png`
- `generated/char-uni-v3-draft-20260612-normalized-clean-384x672.png`

Probe summary:
- `char-bazzi-v3-draft-20260612-normalized-384x672.png`: 384×672 RGBA, 4×7 grid, transparent corners, no empty cells, no edge-touching cells.
- `char-uni-v3-draft-20260612-normalized-clean-384x672.png`: 384×672 RGBA, 4×7 grid, transparent corners, no empty cells, no edge-touching cells.

Notes:
- Prefer `char-bazzi-v3-draft-20260612-normalized-384x672.png` over previous `char-bazzi` drafts.
- Prefer `char-uni-v3-draft-20260612-normalized-clean-384x672.png` over previous `char-uni` drafts.
- Copied to `/Users/radar/Work/CrazyArcadeCopy/assets/sprites/char-bazzi.png` and `/Users/radar/Work/CrazyArcadeCopy/assets/sprites/char-uni.png`.
- Not promoted to `final/` yet. Remaining QA: 48px visual review, animation preview, baseline jitter check, and manifest contract decision.

### 2026-06-12 — character preview tool

Created `tools/char-preview.html` for local animation review.

Capabilities:
- Switch between `char-bazzi-v3`, `char-uni-v3-clean`, and older draft sheets.
- Preview all 7 animation rows: `idle`, `walk_down`, `walk_up`, `walk_left`, `walk_right`, `trapped`, `dead`.
- Show full atlas with 96px grid overlay.
- Show animated 48px in-game scale preview with zoom control.

Smoke test:
- Opened via temporary local HTTP server and Chrome headless.
- `char-bazzi-v3-draft-20260612-normalized-384x672.png` loaded as 384×672.
- Atlas and animation canvases both rendered nonblank.
- Screenshot: `qa/char-preview-smoke-20260612.png`.

### 2026-06-12 — item v2 draft from item spec

Generated a new item sheet using the `REQUESTS.md` item contract.

Files:
- `generated/items-v2-draft-20260612-source.png`
- `generated/items-v2-draft-20260612-alpha.png`
- `generated/items-v2-draft-20260612-normalized-192x480.png`

Probe summary:
- `items-v2-draft-20260612-normalized-192x480.png`: 192×480 RGBA, 2×5 grid, transparent corners, no empty cells, no edge-touching cells.

Rows:
- row 0: `potion`
- row 1: `balloon`
- row 2: `roller`
- row 3: `needle`
- row 4: `iron`

Game asset copy:
- Copied to `/Users/radar/Work/CrazyArcadeCopy/assets/sprites/items.png`.

### 2026-07-05 — char-dao / char-marid palette review + G3/G4 (Claude session)

- 배경: Codex handoff(sprite-chars-dao-marid-v1)가 읽기 전용 G2 기계 probe 재통과 확인
  (384x672, 96px 4x7, RGBA, 투명 모서리, 빈 셀/edge-touch 없음) 후 샌드박스 쓰기 제한으로 blocked.
  잔여 게이트는 Claude 세션에서 자율 재개 (GOAL.md: 생성 이후 QA·승격·통합은 자율).
- Palette review (보류 사유 해소): 게임 로스터 v0.9.0 기준 dao=#4f8df7/#2c5fc4 (파랑),
  marid=#b06ef7/#7a3bd0 (보라) — 두 draft 시트의 주 팔레트와 일치. 시각 검수: 행 구성
  (idle/walk/trapped-bubble/dead) 및 스타일이 char-bazzi/char-uni 기존 시트와 일관.
- G3: generated/char-{dao,marid}-draft-20260612-normalized-384x672.png → final/char-{dao,marid}.png 승격.
- G4: final → CrazyArcadeCopy/assets/sprites/ 복사, js/sprites.js 생성자 loadSheet 2줄 추가.
- 잔여: 인게임 48px 렌더/애니메이션 QA는 사용자 브라우저 확인 몫 (수동 QA 체크리스트 전달됨).

### 2026-07-05 — CA-faithful 세트 v1 전면 교체 (Codex handoff sprite-ca-faithful-set-v1)

- Codex가 게임 리포 artifacts에 결정적 래스터 생성기로 9시트 생성(이미지 API 미가용 폴백),
  기계 probe 전 시트 PASS. Claude 시각 QA: 원작 실루엣 반영(배찌 곰후드/다오 헬멧/마리드
  핑크 단발/우니 고글), 세트 일관성 양호 — 플랫 벡터풍이라 원작 밀도에는 미달(사용자 고지 후
  "전부 교체" 결정, 2026-07-05).
- Tier 1 승격: char-bazzi/dao/marid/uni + items → final/ + 게임 assets/ 교체 (구 6/12 시트 대체).
- Tier 2 스테이징: balloon/stream/tiles/fx → generated/*-cafaithful-20260705.png (렌더 통합 골 대기.
  주의: stream/tiles는 probe 통과용 edge-inset — 통합 시 full-bleed 변형 필요, outbox 보고 참조).
- 원작 밀도 근접이 다시 필요해지면 이미지 모델 생성 재발주(사용자 키/Codex 앱 세션) 경로.

### 2026-07-05 — Tier-2 full-bleed 재생성 + 승격 (feel-pass 렌더 통합)

- 배경: 스테이징된 stream/tiles가 probe 통과용 edge-inset이라 인게임 타일링 시 seam 발생 —
  로컬 결정적 생성기(generate-atlases.mjs)에서 full-bleed 변형으로 재생성.
- 변경: drawStreamSheet 본체를 line→rect로 교체(라운드 캡의 인접 셀 오염 방지) 후 0..96
  full-bleed(center/h/v/end 연결변), drawFloor 인셋 라운드 제거 → 0,0,96,96 full-bleed 체커.
  soft/hard 블록은 인셋 유지. balloon/fx는 도면 무변경(재생성 결과 동일 도면).
- 기계 probe: 전 시트 PASS — stream/tiles는 edge-touch가 full-bleed 의도이므로 probe에
  allowEdgeBleed 면제 추가(EXEMPT 표기), 픽셀 bounds 수동 확인: mid/center/end 연결변 0..95
  도달, 셀 간 오염 없음.
- G2-G3: generated/{balloon,stream,tiles,fx}-cafaithful-fullbleed-20260705.png 보존,
  final/{balloon,stream,tiles,fx}.png 승격 (Tier-2 final 신규 4종).
- G4: CrazyArcadeCopy/assets/sprites/로 4파일 복사, js/sprites.js 로더 등록 + render.js
  시트 분기 통합 (같은 세션 feel-pass 웨이브 2).
