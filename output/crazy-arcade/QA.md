# Crazy Arcade Sprite Batch — QA 판정 기록

## 상태 요약

| Sheet | 생성 | QA | final 승격 | 게임 통합 |
|-------|------|-----|------------|----------|
| char-bazzi | BLOCKED(사용자) | - | - | - |
| char-dao | BLOCKED(사용자) | - | - | - |
| char-marid | BLOCKED(사용자) | - | - | - |
| balloon | BLOCKED(사용자) | - | - | - |
| stream | BLOCKED(사용자) | - | - | - |
| tiles | BLOCKED(사용자) | - | - | - |
| items | BLOCKED(사용자) | - | - | - |
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

(시트 수령 후 기록 예정)
