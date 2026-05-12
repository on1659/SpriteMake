# Sprite Atlas Guide

## 핵심 문제

AI가 만든 sprite sheet는 종종 진짜 atlas가 아니라 "그림을 일정해 보이게 늘어놓은 contact sheet"가 된다.

예를 들어 30px짜리 frame 6개라면 전체 폭은 `30 * 6 = 180px`이어야 한다. 그런데 AI가 시작 여백 10px, 중간 간격 30px, 끝 여백 10px을 섞어 넣으면 전체는 200px처럼 보이고, 코드는 균등분할을 해도 원하는 frame을 자르지 못한다.

따라서 프롬프트에는 "보기 좋게 배치"가 아니라 **코드가 자르는 정확한 boundary**를 적어야 한다.

## 필수 프롬프트 구조

```text
Create a transparent PNG-32 RGBA sprite sheet for a pixel-art game.

This must be a strict sprite atlas, not a loosely spaced contact sheet.

Canvas:
- Final image size: exactly {WIDTH}x{HEIGHT} pixels
- Grid: exactly {COLS} columns x {ROWS} rows
- Cell size: exactly {CELL_W}x{CELL_H} pixels
- Column boundaries: x={X0}, {X1}, ... {WIDTH}
- Row boundaries: y={Y0}, {Y1}, ... {HEIGHT}
- No gutters
- No outer padding
- No guide grid
- No labels
- No text
- Fully transparent background
- sRGB color
- Crisp pixel-art edges, no blur

Important slicing rule:
The game will slice frames only by the exact grid boundaries above.
Each cell must contain exactly one complete frame.
Do not add arbitrary leading margins, trailing margins, or variable spacing between frames.
No frame may bleed into another cell.
No cell may be empty.
Transparent padding may exist only inside each fixed cell.
```

## Anchor 규칙

Anchor는 화면에 그릴 때 기준이 되는 점이다. 캐릭터의 경우 보통 발 접지점이 anchor가 된다.

프롬프트에는 normalized 값만 쓰지 말고 cell 내부 pixel coordinate도 같이 적는다.

예:

```text
Use a shared visual anchor point at x=175, y=165 inside every 350x187 cell.
For grounded rows, the lowest foot contact pixel must touch y=165 in every frame.
Keep the torso center near x=175, with at most 6 pixels of horizontal drift.
```

주의:

- `0.88 * 187 = 164.56`이므로 pixel guide는 보통 `165`로 반올림한다.
- 정확히 y=165를 코드 기준으로 쓰고 싶으면 normalized y는 `165 / 187 = 0.882352941`이다.

## 좋은 표현

AI 프롬프트에 쓰기 좋은 표현:

- `strict sprite atlas`
- `not a loosely spaced contact sheet`
- `exact cell boundaries`
- `the game will slice frames by these exact coordinates`
- `one complete frame per cell`
- `no frame bleeding into adjacent cells`
- `no arbitrary leading or trailing margins`
- `transparent padding only inside each fixed cell`
- `same foot contact pixel in every grounded frame`
- `same silhouette and cell placement across color variants`
- `PNG-32 RGBA, straight alpha, sRGB`
- `crisp pixel-art edges, nearest-neighbor friendly`

피해야 할 모호한 표현:

- `naturally aligned`
- `consistent spacing`
- `evenly arranged`
- `make it look like a sprite sheet`
- `similar size`
- `centered nicely`

위 표현들은 측정 기준이 없어서 AI가 여백을 임의로 넣기 쉽다.

## 검증 체크리스트

생성 후 반드시 확인한다.

- 이미지 크기가 정확한가?
- `width % columns === 0`인가?
- `height % rows === 0`인가?
- cell 크기가 의도와 같은가?
- 각 cell을 잘랐을 때 frame이 1개만 있는가?
- 빈 cell이 없는가?
- 옆 cell의 픽셀이 섞이지 않는가?
- 접지 row에서 발 위치가 흔들리지 않는가?
- jump/fall처럼 특수 row는 의도적으로만 움직이는가?

Python/Pillow로 빠르게 보는 예:

```python
from pathlib import Path
from PIL import Image

path = Path("players-blue.png")
cols, rows = 4, 6
im = Image.open(path).convert("RGBA")
cw, ch = im.width // cols, im.height // rows

print(im.size, "cell", cw, ch, "mod", im.width % cols, im.height % rows)
for r in range(rows):
    row = []
    for c in range(cols):
        cell = im.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
        row.append(f"{c}:{cell.getchannel('A').getbbox()}")
    print("row", r, " ".join(row))
```

## 기존 loose sheet를 고칠 때

AI 결과물이 loose contact sheet라면 두 가지 중 하나를 고른다.

- 재생성: 프롬프트를 strict atlas 기준으로 다시 작성한다.
- 재패킹: 기존 이미지에서 각 frame alpha bbox를 감지해서 새 atlas cell에 다시 붙인다.

재패킹은 빠르지만 원본 pose 자체가 깨진 frame은 고치지 못한다. fall row처럼 자세 자체가 이상하면 재생성이 더 낫다.


