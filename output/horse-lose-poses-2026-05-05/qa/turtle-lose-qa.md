# turtle-lose QA Report

Status: pending generated PNG from strict external gpt-image-2 generation.

## Expected File

- Generated PNG: output/horse-lose-poses-2026-05-05/generated/turtle-lose.png
- Final PNG after QA: output/horse-lose-poses-2026-05-05/final/turtle-lose.png
- Target game asset path after approval: assets/horse-race/sprites/lose/turtle-lose.png
- Manifest: output/horse-lose-poses-2026-05-05/manifests/turtle-lose.json
- Preview tool: output/horse-lose-poses-2026-05-05/tools/turtle-lose.html
- Prompt: output/horse-lose-poses-2026-05-05/prompts/turtle-lose-prompt.md

## Contract

- Required model: gpt-image-2 only
- Final size: 120x45
- Grid: 2 columns x 1 row
- Cell size: 60x45
- Column boundaries: x=0, 60, 120
- Row boundaries: y=0, 45
- Contact anchor: x=30, y=45
- Contact anchor meaning: track ground contact at bottom center
- Y baseline/source plane: y=45; vehicle feet/bottom touches cell bottom in both frames
- Animation: 2 frames, 0.6s loop total, subtle sad breathing only
- Visual direction: 초록색 거북이, 머리와 다리가 등껍질 안으로 절반쯤 들어감, 등껍질 위에 작은 구름

## Alpha BBox Report

- Full alpha bbox: PENDING - generated PNG is not present yet.
- Cell 0 bbox (x=0..59, y=0..44): PENDING.
- Cell 1 bbox (x=60..119, y=0..44): PENDING.
- Transparent corners: PENDING.

## Checklist

- [ ] PNG exists in generated/.
- [ ] File is exactly 120x45.
- [ ] PNG has RGBA channels, straight alpha, sRGB.
- [ ] Background is transparent; no labels, guide grid, watermark, or text.
- [ ] width % 2 == 0 and height % 1 == 0.
- [ ] Cell size is exactly 60x45.
- [ ] Cell 0 contains exactly one complete frame: 등껍질 안으로 움츠림.
- [ ] Cell 1 contains exactly one complete frame: 구름이 살짝 위로 움직이고 머리가 1px 더 들어감.
- [ ] No frame crosses x=60.
- [ ] Contact anchor x=30 y=45 is visually correct.
- [ ] Y baseline y=45 does not drift between frames.
- [ ] 8x8 effect stays fully inside each cell.
- [ ] Preview tool loads manifest and PNG.
- [ ] Preview loop reads as subtle disappointed breathing, not a violent action.


## SVG Preview Status

- SVG atlas generated: output/horse-lose-poses-2026-05-05/generated/turtle-lose.svg
- Source basis: D:\Work\LAMDiceBot\js\horse-race-sprites.js run.frame1 at the required line anchor in source/REFERENCE.md
- Batch preview: tools/all-lose-preview.html loaded this SVG in auto mode
- Note: final PNG QA remains pending only if the raster gpt-image-2 path is still required
## QA Result

- Passed: NO
- Needs generation: NO for SVG preview; YES only for original strict PNG path
- Needs regeneration: NO
- Needs repack: NO
- Needs manual cleanup: NO
- Code offset required: UNKNOWN until bbox is measured
- Ready for final/: NO
