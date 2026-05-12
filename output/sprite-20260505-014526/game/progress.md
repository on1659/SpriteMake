Original prompt: 이제 이거가지고 간단하게 게임만들어줘 / 햄스터들이 자유롭게 움직이다가 시간되면 밥주고 이런거

## Notes

- Building a small canvas-based hamster raising game demo using the generated 2D sheet as source art.
- Source sheet copied to assets/hamster_2d_sheet_source.png.
- The source image is RGB with a checkerboard background, so the game preprocesses each cell with edge flood-fill transparency cleanup at runtime.

## TODO

- Implement wandering hamsters, scheduled feeding, care buttons, state text hook, and deterministic time stepping.

## Implementation

- Added index.html canvas game with wandering hamsters, scheduled meal timer, feed/water/play/clean actions, sprite-sheet preprocessing, render_game_to_text, and advanceTime.

- Fixed source row extraction to avoid non-strict-sheet frame bleed and moved the bed prop inside the habitat area.

- Switched source column extraction to centered narrow crops to remove neighboring-frame artifacts from the non-strict generated sheet.

## Verification

- Inline script parse passed with Node.
- web_game_playwright_client smoke test passed; screenshots and state JSON written under game/qa/smoke2.
- Meal-flow browser check passed: mealDue became true after time advance, Space fed hamsters, mealDue became false, food/fullness recovered.
- Final browser console check: 0 errors, 0 warnings.
- Local server started; see server.txt.

## Animation Fix

- Confirmed the animation problem came from reading the non-strict generated sheet directly at runtime.
- Added tools/repack_hamster_sheet.py to build assets/hamster_game_atlas.png as a strict 4x5 atlas, 256x256 cells, anchor x=128 y=226.
- Updated index.html to load hamster_game_atlas.png with cache busting and slice exact grid cells only.

- Added frame and spriteRow to render_game_to_text so animation frame changes can be verified from tests.

## Animation Fix Verification

- Strict smoke screenshots written under game/qa/strict-smoke; no neighboring-frame artifacts visible.
- Meal-flow check passed again with strict atlas; screenshot written to game/qa/strict-meal-flow.png.
- Frame-check verified frame values cycle 0-3 and spriteRow maps to state rows correctly.
- Browser console check after fixes: 0 errors, 0 warnings.
