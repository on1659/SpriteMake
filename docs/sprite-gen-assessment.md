# sprite-gen의 SpriteMake 활용 평가

평가일: 2026-10-04 KST. 대상은 [aldegad/sprite-gen](https://github.com/aldegad/sprite-gen)의 `v2.20.0`, 커밋 `d993e5300b4255111e8ee0e29779caea1b3b97bd`이다. README 요약에 더해 실제 구현, 테스트 입력, SpriteMake의 공유 도구와 배치별 후처리 코드를 비교했다.

후속 업데이트(같은 날): 사용자의 적용 요청에 따라 로컬 스킬·요청/QA 템플릿,
공용 `tools/runner/inspect_sprite.py`, 계약/입력/비교 해시 및 placement/motion
승격 gate, intake·상태 보드를 수정했다. 아래 기존 코드의 부족한 점은
평가 시점 기록이다. 현재 사용 절차는 `tools/runner/README.md`를 따른다.
검증은 Python 25개·Node 3개 테스트와 스킬/JSON 스키마·정적 검사를 통과했다.
PowerShell이 없어 `.ps1` 실행 preflight는 미검증이다.

## 판단

도움이 된다. 우선순위는 **승인된 방향 reference를 이용한 생성 순서, 별도 모션 QA, 결정적 색상 변형, 배치별 후처리의 공통 도구화**다. 전체 스킬을 그대로 설치하는 방식보다 기존 `spritemake-batch`에 필요한 규칙을 추가하고, 후처리 도구의 출력을 SpriteMake 계약에 맞춰 검수하는 방식이 적합하다.

SpriteMake에는 이미 컴포넌트 배정, 알파 정리, 공통 배율, 접지선 검사, 프레임 비교, 체크섬 기반 승격이 있다. upstream의 이점은 이런 기능을 재사용 가능한 패키지와 명시적인 단계 계약으로 제공하는 데 있다. 설치나 제작 흐름 변경은 이번 평가에 포함하지 않았다.

## 기술별 효과와 적용 조건

| 기술 | 기대 효과 | 권장 적용 |
| --- | --- | --- |
| 승인된 기본 이미지 → 방향별 단일 포즈 reference → 상태별 생성 | 외형·방향·동작을 한 번에 해결할 때 생기는 혼선을 줄이고 잘못된 상태만 재생성 | 가장 먼저 로컬 스킬과 프롬프트 제작 규칙에 반영. reference의 파일·해시·역할 기록 |
| 모션 QA | 크기·알파가 정상이어도 정지 자세의 반복, 루프 튐, 잘못된 걸음새를 거부 | 공통 QA에 중복 프레임·실루엣 변화·루프 이음새 측정 추가. 발 교대와 동작 의미는 시각 판정 유지 |
| RGB 팔레트 치환 | 재생성 없이 색상 variant 제작; 좌표와 alpha 보존 | 색만 바뀌는 variant에 적합. 의상·장비·실루엣 변경 스킨에는 별도 생성 필요 |
| 결정적 idle 호흡 | 승인된 정지 그림으로 작은 반복 동작 제작 | 픽셀 캐릭터 idle에서 제한적으로 실험. 머리·장식·외곽선·접점 유지 확인 |
| chroma unmix / despill | 단색 배경과 가장자리 색 오염을 처리 | native alpha 보존 우선. 단색 chroma 원본에 선택 적용; 피사체와 key 색이 겹치면 재검토 |
| 컴포넌트 추출 | 격자를 넘친 완전한 포즈를 잘림 없이 회수 | 분리 가능한 원본의 복구 후보에 사용. 붙은 인물·잘린 신체·누락 자세를 복원하지 못함 |
| 픽셀 lattice·공통 팔레트 | 생성 이미지의 도트 크기·색상 편차 감소 | 픽셀아트에만 선택 적용. 원화풍 시라노에 강제하면 화풍 손실 |
| 비파괴 curation과 export | 선택·순서·수정 내용이 최종 파일에 반영 | 선택 기록의 세대·해시 관리와 함께 도입. 수정 후 후보 export·QA·승인 재실행 |

구현 근거:

- [생성 계획과 reference 역할](https://github.com/aldegad/sprite-gen/blob/d993e5300b4255111e8ee0e29779caea1b3b97bd/sprite_gen/gen/prepare.py#L753): `prepare.py:608,774–805`.
- [모션 측정](https://github.com/aldegad/sprite-gen/blob/d993e5300b4255111e8ee0e29779caea1b3b97bd/sprite_gen/qa/motion.py#L170): 사용자가 지정한 동일 발 접지 구간과 ROI를 검사한다. 픽셀만으로 발 접지나 보행 방향을 확정하지 않는다.
- [팔레트 치환](https://github.com/aldegad/sprite-gen/blob/d993e5300b4255111e8ee0e29779caea1b3b97bd/sprite_gen/effects/recolor.py#L204): RGB 정확 일치 치환; alpha·좌표 보존. 같은 색을 공유하는 눈과 장비도 함께 변할 수 있다.
- [호흡 변형](https://github.com/aldegad/sprite-gen/blob/d993e5300b4255111e8ee0e29779caea1b3b97bd/sprite_gen/effects/breathe.py#L262): 정수 좌표 사상과 bbox 하단 고정. bbox 하단은 실제 contact anchor와 다를 수 있다.
- [추출·키 색 처리](https://github.com/aldegad/sprite-gen/blob/d993e5300b4255111e8ee0e29779caea1b3b97bd/sprite_gen/frames/extract.py#L530): 여러 처리 경로와 경고·실패 보고가 있다. 모든 스타일에 동일한 정리 강도를 적용하면 안 된다.

## 우리 배치에 실제로 필요한 부분

### 시라노 8방향 캐릭터

`output/cyrano-8dir-2026-09-29/QA.md`에는 최신 기록상 원본 86장, 발 교대·동작·상하 흔들림·배율 문제와 미통과 상태가 남아 있다. 이 배치는 방향 reference를 먼저 확정하고 동작 행에 외형 reference와 모션 reference를 구분해 제공하는 실험 대상으로 적합하다.

다만 upstream도 [walk/run은 모션 검수를 통과하기 전 experimental](https://github.com/aldegad/sprite-gen/blob/d993e5300b4255111e8ee0e29779caea1b3b97bd/docs/qa-motion.md)로 다룬다. **추출 성공이 올바른 걸음새를 뜻하지 않는다.** 86회 시도 횟수나 재생성 비용이 줄어든다는 실측 근거는 아직 없다.

시라노의 칼 손잡이는 캐릭터 자신의 왼쪽 어깨 뒤에 고정되어 있다. 로컬 `REQUESTS.md:12`의 좌우 반전 금지 규칙을 적용해야 한다. upstream 방향 문서의 기본 미러 조항은 이 배치에 적용할 수 없다.

### 데구리와 스킨

현재 단일 idle reference에서 스킨 후보를 만드는 흐름과 방향·외형 reference 관리가 잘 맞는다. 단순 색상 variant에는 `recolor`가 특히 적합하다. 의상·장비·모양이 바뀌는 스킨은 RGB 치환만으로 만들 수 없다. 승인된 스킨 정지 그림에 작은 idle 호흡을 굽는 기술은 별도 후보로 실험할 가치가 있다.

로컬의 `output/marble-run-creatures-k-2026-09-21/tools/creatures_k_png.js:46–63,106–123`에는 컴포넌트·satellite 배정, sheet 공통 배율, 공중 프레임 예외가 이미 있다. 시라노의 `recover_walk_s.py:158–177`도 sheet 배율과 실제 접점 정렬을 수행한다. 공통 도구를 만들 때 이 규칙들을 보존해야 한다.

## 그대로 연결할 수 없는 부분

1. **최종 아틀라스 구성.** upstream `compose_atlas.py:106–110,138–142`는 고유한 baked 프레임 수에 따라 폭을 정하고 복제 프레임의 좌표를 공유한다. 짧은 행 뒤에는 빈 슬롯이 생길 수 있다. SpriteMake의 정확한 캔버스, 고정 열 의미, 한 셀 한 프레임 계약에는 재배치 adapter가 필요하다.
2. **manifest 형식.** upstream은 `frame_layout.rows`의 절대 rect와 `animation.rows`를 사용한다. 로컬 preview는 `sheets/grid/animations`에서 row·column으로 잘라낸다(`templates/animation-player-template.html:469–474`). PNG만 복사하면 manifest와 preview가 호환되지 않는다.
3. **배율·접지 기본값.** upstream 일반 `fit_to_cell`은 프레임별 contain 배율을 계산한다(`extract.py:1263–1327`). 픽셀 경로는 행 공통 배율이다(`:2204–2227`). 우리 sheet 전체 공통 배율을 자동 보장하지 않는다. bbox 하단이나 foot centroid 정렬은 명시적 contact anchor·source plane과 다르며 공중 프레임의 높낮이를 없앨 수 있다.
4. **anchor 용어.** upstream의 방향 anchor는 외형·방향 reference 이미지다. 로컬 contact anchor는 런타임 배치 좌표다. 도입 문서에서는 전자를 “방향 reference 이미지”로 명명한다.
5. **생성·인증 정책.** upstream은 Codex·Grok·명시적 OpenAI API 경로를 가진다. SpriteMake의 키 저장·이미지 API 호출 금지, Codex 생성 모델 미검증 표기를 유지해야 한다. 전체 provider·로그인·기본값 질문 흐름을 이식할 필요는 없다.
6. **검수 화면.** upstream curation 서버는 선택·편집 도구로 활용 가능하지만 SpriteMake의 더블클릭 `file://` 프리뷰를 대체하지 않는다.
7. **승격 범위.** upstream의 `ok`나 compose 성공은 SpriteMake 최종 승인으로 매핑하지 않는다. 로컬 geometry QA·시각 검토·승격 gate를 통과해야 한다.

로컬 `asset_gate.py:51–108`은 candidate·QA 보고서 해시와 승인 상태를 검사한다. 이미지 기하를 직접 측정하지 않고 QA 보고서에 의존한다. 또한 style 비교 이미지는 현재 존재 여부만 검사한다(`:101–105`). 방향 reference와 curation을 추가한다면 입력 해시·세대를 기록하고 변경 시 QA·승인을 무효화하는 연결이 필요하다.

## 실행 확인과 한계

API 호출·이미지 생성 없이 공개 synthetic 테스트 입력으로 다음을 확인했다.

| 확인 | 결과 |
| --- | --- |
| CLI `extract` | 종료 코드 0; 2개 행·7개 프레임이 기대 golden 픽셀과 일치 |
| CLI `compose-atlas` | 종료 코드 0; 384×192 RGBA와 기대 frame rect map 일치 |
| 필수 원본 행 누락 | 종료 코드 1; canonical `frames/`에 부분 결과를 게시하지 않음 |

입력과 기대값은 `tests/frames/test_extraction_golden.py:22–58`, `tests/packaging/test_pipeline_smoke.py:60–87`에서 가져와 CLI로 재현했다. 번들 Python 3.12.14 / Pillow 12.3.0 / NumPy 2.3.5를 사용했다. pytest가 없어 전체 테스트 스위트는 실행하지 않았다. 임시 테스트 데이터는 정리되었으며 upstream과 SpriteMake 소스는 수정하지 않았다.

이 확인은 작은 입력에서 후처리 경로와 실패 처리가 동작한다는 근거다. 우리 PNG에서의 알파 개선, 캐릭터 일관성, 모션 품질, 속도, 재시도 감소는 검증하지 않았다. 장기 동시 실행·프로세스 강제 종료에 대한 전체 보장도 아니다.

패키지 요구 사항은 Python ≥3.11, Pillow ≥12.3.0,<13, NumPy ≥2.2.6,<3이다. 동영상 경로의 ffmpeg·img2webp·RIFE는 이번 이미지 후처리 활용에 필요한 범위가 아니다. 라이선스는 Apache-2.0이며 코드를 배포물에 포함할 경우 LICENSE·NOTICE와 수정 표시를 관리한다.

## 권장 도입 순서

1. 로컬 `spritemake-batch`에 승인된 기본 이미지, 단일 방향 reference, 비대칭 특징, reference 세대, 별도 모션 판정을 명문화한다.
2. 공유 도구의 첫 범위는 **PNG 검사·색상 variant·후처리 보고 형식**으로 잡는다. 이미 있는 배치별 QA를 입력 계약으로 수용한다.
3. 작은 애니메이션 배치 한 개에서 upstream 추출 결과와 기존 처리 결과를 나란히 비교한다. 원본을 보존하고 결과는 `generated/` 후보로만 기록한다.
4. 정해진 canvas/grid/anchor/source plane으로 재배치하고 로컬 manifest와 `file://` preview를 만든다. 구조·색 오염·배율·모션·시각 판정이 기존 수준 이상일 때만 승격한다.
5. 이후 curation·호흡·픽셀 lattice를 필요에 따라 추가한다. 동영상 파이프라인과 전체 스킬 설치는 현재 우선순위가 낮다.

이번 작업으로 생성 후보, `final/`, 게임 프로젝트 파일, 기존 스킬·코드의 동작은 변경하지 않았다. 평가 문서만 추가했다.
