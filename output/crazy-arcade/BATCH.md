# Crazy Arcade Web Clone — Sprite Batch

작성일: 2026-06-12
상태: prompt-ready

## Batch Overview

Batch Sprite Production Request:
- Original user request: 크레이지 아케이드 웹 클론용 스프라이트 전체 제작
- SpriteMake batch folder: `/Users/radar/Work/SpriteMake/output/crazy-arcade`
- Game / project: Crazy Arcade Web Clone (CrazyArcadeCopy)
- Game project root: `/Users/radar/Work/CrazyArcadeCopy`
- Scene or feature: 전 게임 플레이 화면 (캐릭터, 물풍선, 물줄기, 타일, 아이템, 이펙트)
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Shared gameplay purpose: 탑다운 2D 물풍선 배틀 게임의 캐릭터·오브젝트·이펙트를 카툰 스타일로 표현한다.
- Shared visual direction: 원작 크아 감성의 밝은 카툰 톤. 잔디 그린 바닥, 갈색 소프트 블록, 파란 물줄기. 48px 타일 그리드에 정렬되는 탑다운 0.75-뷰 (살짝 내려다보는 각).
- Existing assets or style to match: 없음 (신규 프로젝트 — Canvas 도형 렌더 폴백 현재 사용 중)
- In-game scale reference: 캐릭터 기준 48×48px 렌더 (원본 프레임 96×96, defaultScale 0.5)
- Output root: `/Users/radar/Work/SpriteMake/output/crazy-arcade`
- Preview tool folder: `/Users/radar/Work/SpriteMake/output/crazy-arcade/tools`
- QA output folder: `/Users/radar/Work/SpriteMake/output/crazy-arcade/qa`

## Code Context

현재 렌더러 상태:
- `js/render.js` (574줄): Image/drawImage/sprite/manifest 참조 0건 — 전부 Canvas 도형 렌더
- `assets/sprites/` 폴더 미존재 — 게임 통합은 `crazyarcade-sprite-loader` goal 에서 처리
- 아이템 5종: `potion`, `balloon`, `roller`, `needle`, `iron` (constants.js:52-58 ITEM_TABLE)
- 이펙트 6종: `pop`(game.js:134), `needle`(:163), `splash`(:211), `pickup`(:234), `crumb`(:112), `itemPop`(:122)
- 캐릭터 3 아키타입: 배찌형(스피드), 다오형(밸런스), 마리드형(파워) — GDD §5

현재 타일 규약:
- `TILE = 48` (constants.js:3)
- 맵: 13열 × 11행 = 143 타일 (Village 맵 기준, MAPS.md)

## Required Assets

1. `char` — 캐릭터 3종 palette atlas (bazzi / dao / marid)
2. `balloon` — 물풍선 + 팽창 애니메이션
3. `stream` — 물줄기 (중심/팔/끝 4방향)
4. `tiles` — 바닥·소프트블록·하드블록·파괴 이펙트
5. `items` — 아이템 5종
6. `fx` — 이펙트 (pop / needle / splash / pickup / crumb / itemPop)

## Integration Notes

- 생성 실패본을 `final/` 또는 게임 `assets/`에 올리지 않는다 (G1-G4 게이트 준수).
- 게임 통합(4단계)은 별도 goal `crazyarcade-sprite-loader`에서 진행.
- 이미지 생성은 사용자가 직접 수행 (BLOCKED 상태로 마킹).
