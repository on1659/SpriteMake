# QA: dragon-rider

## Current state

No candidate PNG is included in this repository demo. Therefore this asset is
**not QA-passed** and `final/` must stay empty.

## Required before promotion

- Verify `512×256`, RGBA, transparent expected corners, and exact 4×2 grid.
- Inspect full and per-cell alpha bounding boxes.
- Check exactly one dragon frame per cell with no cell bleed.
- Check anchor `(64, 110)` and source plane `110` across every frame.
- Play the atlas in the local preview tool and confirm no fire/ice Y drift.
- Record approved filename/content and style reviews in a structured status
  file, then use the local promotion gate to populate `final/`.
