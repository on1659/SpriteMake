# Crazy Arcade Manifest 작업 노트

상태: 미생성 — QA 통과 후 `manifests/crazy-arcade.manifest.json` 작성 예정

## 예정 manifest 구조

```json
{
  "version": 1,
  "baseStyle": "crazy-arcade-cartoon-v1",
  "sheets": {
    "char-bazzi": {
      "label": "Player Atlas (Bazzi)",
      "image": "char-bazzi.png",
      "grid": { "columns": 4, "rows": 7 },
      "anchor": { "x": 48, "y": 84, "mode": "pixel" },
      "baselineY": 84,
      "defaultScale": 0.5,
      "paletteOrder": ["bazzi", "dao", "marid"],
      "paletteImages": {
        "dao": "char-dao.png",
        "marid": "char-marid.png"
      },
      "animations": {
        "idle":        { "row": 0, "frames": [0,1,2,3], "fps": 4, "loop": true },
        "walk_down":   { "row": 1, "frames": [0,1,2,3], "fps": 8, "loop": true },
        "walk_up":     { "row": 2, "frames": [0,1,2,3], "fps": 8, "loop": true },
        "walk_left":   { "row": 3, "frames": [0,1,2,3], "fps": 8, "loop": true },
        "walk_right":  { "row": 4, "frames": [0,1,2,3], "fps": 8, "loop": true },
        "trapped":     { "row": 5, "frames": [0,1,2,3], "fps": 6, "loop": true },
        "dead":        { "row": 6, "frames": [0,1,2,3], "fps": 6, "loop": false }
      }
    },
    "balloon": {
      "label": "Water Balloon",
      "image": "balloon.png",
      "grid": { "columns": 2, "rows": 1 },
      "anchor": { "x": 48, "y": 84, "mode": "pixel" },
      "baselineY": 84,
      "defaultScale": 0.5,
      "animations": {
        "inflate": { "row": 0, "frames": [0,1], "fps": 2, "loop": false }
      }
    },
    "stream": {
      "label": "Water Stream",
      "image": "stream.png",
      "grid": { "columns": 2, "rows": 4 },
      "anchor": { "x": 48, "y": 48, "mode": "pixel" },
      "baselineY": 48,
      "defaultScale": 0.5,
      "animations": {
        "center": { "row": 0, "frames": [0,1], "fps": 6, "loop": true },
        "arm_h":  { "row": 1, "frames": [0,1], "fps": 6, "loop": true },
        "arm_v":  { "row": 2, "frames": [0,1], "fps": 6, "loop": true },
        "end":    { "row": 3, "frames": [0,1], "fps": 6, "loop": true }
      }
    },
    "tiles": {
      "label": "Map Tiles",
      "image": "tiles.png",
      "grid": { "columns": 4, "rows": 2 },
      "anchor": { "x": 48, "y": 48, "mode": "pixel" },
      "baselineY": 48,
      "defaultScale": 0.5,
      "animations": {
        "floor_a":     { "row": 0, "frames": [0], "fps": 0, "loop": false },
        "floor_b":     { "row": 0, "frames": [1], "fps": 0, "loop": false },
        "soft_block":  { "row": 0, "frames": [2], "fps": 0, "loop": false },
        "hard_block":  { "row": 0, "frames": [3], "fps": 0, "loop": false },
        "soft_break":  { "row": 1, "frames": [0,1,2,3], "fps": 8, "loop": false }
      }
    },
    "items": {
      "label": "Power-up Items",
      "image": "items.png",
      "grid": { "columns": 2, "rows": 5 },
      "anchor": { "x": 48, "y": 84, "mode": "pixel" },
      "baselineY": 84,
      "defaultScale": 0.5,
      "animations": {
        "potion":  { "row": 0, "frames": [0,1], "fps": 3, "loop": true },
        "balloon": { "row": 1, "frames": [0,1], "fps": 3, "loop": true },
        "roller":  { "row": 2, "frames": [0,1], "fps": 3, "loop": true },
        "needle":  { "row": 3, "frames": [0,1], "fps": 3, "loop": true },
        "iron":    { "row": 4, "frames": [0,1], "fps": 3, "loop": true }
      }
    },
    "fx": {
      "label": "Visual Effects",
      "image": "fx.png",
      "grid": { "columns": 4, "rows": 6 },
      "anchor": { "x": 48, "y": 48, "mode": "pixel" },
      "baselineY": 48,
      "defaultScale": 0.5,
      "animations": {
        "pop":     { "row": 0, "frames": [0,1,2,3], "fps": 12, "loop": false },
        "needle":  { "row": 1, "frames": [0,1,2,3], "fps": 12, "loop": false },
        "splash":  { "row": 2, "frames": [0,1,2,3], "fps": 12, "loop": false },
        "pickup":  { "row": 3, "frames": [0,1,2,3], "fps": 12, "loop": false },
        "crumb":   { "row": 4, "frames": [0,1,2,3], "fps": 12, "loop": false },
        "itemPop": { "row": 5, "frames": [0,1,2,3], "fps": 12, "loop": false }
      }
    }
  }
}
```

## 작업 순서

1. QA 통과 시트부터 manifest entry 추가
2. `manifests/crazy-arcade.manifest.json` 실제 파일로 작성
3. 게임 통합 전 grid math 검증 (width % columns === 0, height % rows === 0)
4. preview tool에서 모든 animation key 동작 확인
