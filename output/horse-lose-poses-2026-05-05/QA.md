# Horse Lose Batch QA

Status: pending generated PNGs from strict gpt-image-2 external generation.

SVG review status: generated SVG atlases exist for all 15 vehicles under generated/. The all-in-one preview was browser-checked with 15 loaded, 0 missing, 0 size issues.

No file in final/ is production-ready yet. Do not copy phase-1 files into D:\Work\LAMDiceBot\assets\horse-race\sprites\lose\ until the corresponding QA reports pass and the user confirms the copy trigger.

## Batch QA Summary

- Batch ID: horse-lose-poses-2026-05-05
- Asset count: 15
- Passed: 0 final QA
- SVG preview loaded: 15/15
- Needs generation: 0 SVG visual attempts created; 15 PNG outputs still pending only if the original strict gpt-image-2 raster path is kept.
- Needs regeneration: 0
- Needs repack: 0
- Needs manual cleanup: 0
- Manifest updated: 15 prepared
- Preview tools updated: 15 per-asset prepared, plus tools/all-lose-preview.html for batch review
- Ready for game integration: no

## Per-Asset QA Reports

- qa/horse-lose-qa.md
- qa/rabbit-lose-qa.md
- qa/turtle-lose-qa.md
- qa/dinosaur-lose-qa.md
- qa/knight-lose-qa.md
- qa/car-lose-qa.md
- qa/rocket-lose-qa.md
- qa/bird-lose-qa.md
- qa/ninja-lose-qa.md
- qa/boat-lose-qa.md
- qa/bicycle-lose-qa.md
- qa/scooter-lose-qa.md
- qa/helicopter-lose-qa.md
- qa/eagle-lose-qa.md
- qa/crab-lose-qa.md

## Minimum Acceptance Gate

- PNG exists under generated/ and is exactly 120x45.
- width % 2 == 0 and height % 1 == 0.
- Cell size is exactly 60x45.
- Both cells contain one complete frame.
- No frame crosses x=60.
- All corners are transparent.
- Full alpha bbox and per-cell alpha bbox are recorded.
- Anchor x=30, y=45 and baseline y=45 are visually correct.
- Preview HTML loads the manifest and generated PNG and loops the lose animation.
