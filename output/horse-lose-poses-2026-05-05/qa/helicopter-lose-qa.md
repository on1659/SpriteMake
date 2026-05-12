# helicopter-lose QA Report

Status: pending generated PNG from strict external gpt-image-2 generation.

## Expected File

- Generated PNG: output/horse-lose-poses-2026-05-05/generated/helicopter-lose.png
- Final PNG after QA: output/horse-lose-poses-2026-05-05/final/helicopter-lose.png
- Target game asset path after approval: assets/horse-race/sprites/lose/helicopter-lose.png
- Manifest: output/horse-lose-poses-2026-05-05/manifests/helicopter-lose.json
- Preview tool: output/horse-lose-poses-2026-05-05/tools/helicopter-lose.html
- Prompt: output/horse-lose-poses-2026-05-05/prompts/helicopter-lose-prompt.md

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
- Visual direction: 노란/검정 헬리콥터, 프로펠러 회전 X(정지), 살짝 비스듬히(5도), 작은 검은 연기

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
- [ ] Cell 0 contains exactly one complete frame: 프로펠러가 정지하고 5도 기울어짐.
- [ ] Cell 1 contains exactly one complete frame: 검은 연기와 차체가 1px 움직임.
- [ ] No frame crosses x=60.
- [ ] Contact anchor x=30 y=45 is visually correct.
- [ ] Y baseline y=45 does not drift between frames.
- [ ] 8x8 effect stays fully inside each cell.
- [ ] Preview tool loads manifest and PNG.
- [ ] Preview loop reads as subtle disappointed breathing, not a violent action.


## SVG Preview Status

- SVG atlas generated: output/horse-lose-poses-2026-05-05/generated/helicopter-lose.svg
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
