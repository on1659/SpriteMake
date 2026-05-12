# QA: hamster-care-20260505

Use templates/asset-qa-checklist.md.

## Summary

- Asset count: 2
- Automated geometry checks ok: 2
- Regeneration required: 0
- Repack required: 0
- Ready for game: no, keep generated attempts out of final/ until visual review passes

## Reports

| Asset | Size | Grid | Alpha BBox | Preview Tool | Status |
| --- | --- | --- | --- | --- | --- |
| hamster_care_atlas | 1024x1024 | 4 x 4, 256 x 256 cell | full bbox (46, 48, 977, 1000); see qa/hamster_care_bbox_report.txt | loaded in tools/hamster-care-preview.html | qa-needed |
| hamster_care_items | 1024x256 | 4 x 1, 256 x 256 cell | full bbox (52, 32, 973, 231); see qa/hamster_care_bbox_report.txt | loaded and sheet-switched in tools/hamster-care-preview.html | qa-needed |

## Required Checks

- Final size must exactly match the manifest.
- Width and height must divide cleanly by the grid.
- Each cell must contain exactly one intended frame or prop.
- No frame may bleed into neighboring cells.
- Corners must be transparent.
- Full alpha bbox and per-cell alpha bbox must be recorded.
- Contact anchor x=128, y=220 must place the hamster and props on the habitat floor.
- Y-axis baseline y=220 must not drift between frames.
- Animation playback must be checked in tools/hamster-care-preview.html.

## Current Notes

- PNGs were generated locally as a first usable attempt, without API keys.
- These files are not verified gpt-image-2 outputs.
- Keep them in generated/ until human visual review approves them.
- Size, grid divisibility, transparent corners, and per-cell alpha bbox were recorded in qa/hamster_care_bbox_report.txt.
- Preview tool check screenshot: qa/hamster_care_preview_check.png.
- Playwright preview check: manifest loaded, hamster_care_atlas and hamster_care_items appeared, item sheet switching worked, console errors 0.
- Visual review still needs to confirm the walk/eat/sleep motion reads well in-game.
