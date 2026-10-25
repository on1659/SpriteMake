# 반입 요청: LAMDiceBot 데구리 야식 7종 (marble_balloon)

원본 의뢰서는 다른 저장소(`/Users/radar/Work/LAMDiceBot/docs/spritemake-request/2026-09-23-marble-balloon-yasik.md`)에
있어서 SpriteMake 워크스페이스에서는 안 보인다. 그래서 여기로 복사해 뒀다.

## 여기서 할 일 (SpriteMake)

1. **`BRIEF.md` 를 끝까지 읽는다.** §계약(캔버스 96×128, 매듭 (48,106), 외곽선 #5A3D52 4px, 하드 에지 알파,
   가장자리 여백 5px)과 §7종의 괄호 안 함정이 핵심이다.
2. **`references/` 두 장을 배치의 `source/references/` 로 넣고 프롬프트에서 style reference 로 지목한다.**
   - `style-creatures.png` — 맞춰야 할 화풍
   - `current-placeholder.png` — 교체 대상(현재 임시본). 실루엣 구성은 유지하고 그림 질만 올린다
   텍스트 설명만으로는 화풍이 안 맞는다. edit target 은 없다(새로 그리는 것) — style reference 둘만.
3. 배치를 만든다:
   ```bash
   cd /Users/radar/Work/SpriteMake
   node tools/runner/request-batch.js "<BRIEF.md 의 §7종 + §계약을 풀어 쓴 요청문>"
   ```
4. 결과 PNG 7장을 `output/<batch>/final/` 에 `balloon-{chicken,pizza,tteokbokki,jokbal,gimbap,burger,tangsuyuk}.png`
   이름으로 둔다.

## 여기서 하지 않는 일

`BRIEF.md` 의 **§인수** 절(webp 변환·매니페스트·ASSET_VER·QA 실행)은 **LAMDiceBot 저장소 세션에서** 한다.
이 워크스페이스에는 그 경로도 스크립트도 없다. `final/` 까지만 만들고 넘기면 된다.

## 시작 전에 사용자에게 확인할 것

**음식 모양 풍선이냐, 실제 음식이냐.** BRIEF.md 는 "음식 모양 호일 풍선"(줄에 매달린 게 말이 되는 쪽) 기준으로
쓰여 있다. 실제 음식을 원하면 화풍과 7종 설명을 다시 써야 하므로 **그림을 만들기 전에 묻는다.**

## 넘겨받는 쪽(LAMDiceBot)에서 하는 검사

받은 PNG 는 아래 검사를 **7/7 통과해야** 인수된다. 계약을 어기면 그냥 반려된다.

```bash
python3 AutoTest/spritemake/make-balloons.py --verify <final 폴더>
```

캔버스 크기 / 반투명 픽셀 0 / 매듭 (48,106) 불투명 / 가장자리 여백 5px / 실루엣 경계가 외곽선 색(±40).
임시본 3장이 외곽선 잘린 채 통과한 적이 있어 외곽선 검사가 추가됐다.
