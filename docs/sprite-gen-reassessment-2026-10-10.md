# sprite-gen 재검토 — 2026-10-10 KST

## 결론

SpriteMake에 활용 가능하다. 우선 도입 대상으로 **결정적 색상 변형(recolor)**, 다음으로 **알파 정리·프레임 추출과 고정 격자 변환**을 권장한다. 생성 도구 전체를 설치하거나 기존 제작 흐름을 교체할 필요는 없다.

이번 요청의 범위는 도입 가능성 조사다. 임시 경로에서 공개 코드를 확인하고 synthetic 입력으로 색상 변형을 검증했다. 이 문서만 추가했으며 SpriteMake 코드·스킬·배치·`final/`·게임 파일은 수정하지 않았다.

## 검토 기준

- 상류: [aldegad/sprite-gen](https://github.com/aldegad/sprite-gen)
- 확인 버전: `2.44.0`, 커밋 [`3dc080aa8faa8b5a6dfe865b1247c047761f8fd1`](https://github.com/aldegad/sprite-gen/tree/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1)
- 기존 평가: [2026-10-04 평가](sprite-gen-assessment.md), 당시 `2.20.0`
- 현재 로컬 작업 트리의 구현과 비교했다. 여기에는 미커밋 변경사항도 포함되며, 아래 로컬 구현 근거가 원격 `main`에 모두 반영되었다는 뜻은 아니다. 이 문서 제출에는 해당 코드 변경을 포함하지 않는다.

## 이미 SpriteMake에 반영된 부분

| 항목 | 현재 구현 근거 |
| --- | --- |
| 승인 기본 이미지 → 방향별 단일 reference → 상태 생성 | `.agents/skills/spritemake-batch/references/workflow.md:30` |
| 비대칭 특징·공통 배율·공중 프레임 보존 | 같은 문서 `:47`, `:64` |
| 크기/grid/alpha/bbox 검사 | `tools/runner/inspect_sprite.py:217` |
| 중복 프레임·인접 프레임 차이·루프 이음새 보고 | `tools/runner/inspect_sprite.py:252` |
| 계약/reference/curation/비교 이미지의 해시 연결 | `tools/runner/asset_gate.py:156`, `:187` |
| 기하 검사와 별도 placement/motion 승인 | `tools/runner/asset_gate.py:198`, `:205` |

기존 평가의 부족한 점을 그대로 재도입 과제로 삼으면 중복 작업이 된다. 특히 기존 문서의 “비교 이미지는 존재 여부만 검사”는 과거 평가 시점 설명이며 현재 구현에는 해시 검증이 있다.

## 새로 가져올 가치

| 우선순위 | 기능 | 효과와 조건 |
| --- | --- | --- |
| 1 | RGB recolor | 색만 다른 variant를 이미지 재생성 없이 제작. 좌표·alpha 보존. 같은 RGB를 공유하는 눈·장비까지 바뀔 수 있어 시각 검수 필요. 의상/실루엣 변경용은 아님 |
| 2 | chroma 정리·프레임 추출 | 배치마다 흩어진 후처리를 공통화. native alpha 우선, chroma 원본에 선택 적용. 붙은 신체·누락 자세를 복구하는 기능으로 오해하지 않기 |
| 2 | strict atlas/manifest adapter | 추출 결과를 우리 canvas/grid/anchor/source plane과 `sheets/grid/animations`로 변환. 도입에 필요한 로컬 연결 작업 |
| 3 | 비파괴 curation | 프레임 선택·순서·위치 조정을 recipe로 기록하고 재출력. 기존 입력 해시 및 재승인 절차와 연결 |
| 후순위 | idle 호흡·pixel lattice | 해당 스타일에서만 실험. 실제 접점과 외곽선 보존 확인 |

상류 구현: [recolor](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/sprite_gen/effects/recolor.py), [extract](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/sprite_gen/frames/extract.py), [compose-atlas](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/sprite_gen/compose/compose_atlas.py).

## 2.20 이후 변경의 의미

[변경 기록](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/CHANGELOG.md)에 따르면 주요 확장은 동영상에서 모션 루프를 추출·정렬·수정하는 경로에 집중되어 있다. 현재 PNG 중심 SpriteMake에 전부 필요한 것은 아니다.

- `2.22`의 비대칭 장비 방향 처리: 좌우 미러 대신 각 방향 reference를 따로 만드는 접근은 시라노와 잘 맞는다. 로컬 비대칭 보존 규칙은 이미 있다.
- `2.32/2.33`의 body-plan: 이족·사족·다리 없는 캐릭터에 맞는 프롬프트 구분은 드래곤·동물 작업 시 참고 가치가 있다.
- `2.42`의 방향별 loop sheet: 공통 접지선을 지원하지만 원본 크기·가변 열 수·빈 슬롯을 허용하므로 우리 고정 계약 변환을 대체하지 않는다.
- `2.44`의 ghost frame 검출·재촬영 표시 및 복원 보고서 변경: 향후 동영상 파이프라인을 도입할 때 검토할 사항이다.

## 권장 연결 방식

```text
보존된 원본 PNG
→ 버전 고정된 선택적 후처리
→ SpriteMake 고정 격자/manifest 변환
→ generated 후보 + 변환 recipe/입력 해시
→ inspect_sprite + file:// preview
→ placement/motion 검토 + 기존 asset_gate
```

상류의 manifest는 절대 frame rect 중심이다. SpriteMake preview는 고정 grid 중심이므로 PNG만 복사해서는 호환되지 않는다. 공통 배율, contact anchor, Y-axis baseline/source plane, 공중 프레임의 높이도 변환 계약에 포함해야 한다. 상류의 compose 성공을 최종 QA 승인으로 간주하지 않는다.

도입 방식은 버전 고정 패키지와 얇은 로컬 adapter가 기본 후보다. recolor만 필요하다면 해당 기능만 이식하는 방식도 가능하다. 복잡한 추출 엔진까지 복사하면 업데이트와 버그 수정 추적 비용이 커진다. provider·로그인·API 호출은 이 후처리 연결에 필요하지 않다. curation 서버는 선택적 편집 도구이며 더블클릭 `file://` preview는 유지한다.

## 라이선스와 실행 환경

[LICENSE](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/LICENSE)는 Apache-2.0이다. 라이선스 조건하에 수정·재사용·배포할 수 있다. 코드를 포함해 배포할 때 라이선스 사본, 관련 저작권/출처 고지, 수정 파일의 변경 표시와 해당 NOTICE 내용을 보존한다.

[NOTICE](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/NOTICE)에는 perfectpixel-studio의 MIT 기반 이식 부분도 명시되어 있다. 추출 관련 코드를 이식할 때 그 출처도 함께 관리한다.

[패키지 요구사항](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/pyproject.toml): Python ≥3.11, Pillow ≥12.3.0,<13, NumPy ≥2.2.6,<3. 도입 시 별도 가상환경과 버전 고정을 사용한다. 이번 머신 기본 Python은 3.9.6이고 Pillow가 없어 그대로 실행할 수 없었다. 검증은 Codex 번들 Python을 이용했다.

## 이번 검증 결과와 한계

Python 3.12.14 / Pillow 12.3.0 / NumPy 2.3.5에서 상류 [test_recolor_bake.py](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/tests/effects/test_recolor_bake.py)의 테스트 함수 8개를 각각 임시 폴더로 직접 호출했다. 모두 통과했다.

- 동일 입력의 PNG 바이트 재현성
- 정확한 색 치환과 alpha·좌표 보존
- 치환·미사용·통과 색 보고
- 근접 색 허용오차 처리 및 모순 설정 거부
- 팔레트 빈도 정렬과 제한 시 누락량 보고
- variant별 manifest 전달

pytest가 설치되어 있지 않아 pytest 실행 및 전체 suite 검증은 하지 않았다. API 호출·이미지 생성·사용자 에셋 수정은 하지 않았다. 실제 캐릭터 품질, 의도한 부위만 변색되는지, 추출 개선율, 모션 정확도와 재생성 비용 감소는 아직 검증하지 않았다. 10월 4일 문서의 extract/compose 실행 결과는 당시 버전 기록이며 이번 버전의 재실행 결과로 주장하지 않는다.

다음 구현 범위로는 **공용 recolor → 후보 저장 → 기존 QA 연결**이 가장 작고 검증 가능하다. 그 다음 실제 PNG 한 배치로 기존 후처리와 upstream 추출 결과를 비교해 adapter 범위를 정한다.
