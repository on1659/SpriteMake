# Asset Request: dragon-rider

## Strict atlas contract

- Canvas: `512×256` RGBA PNG
- Grid: 4 columns × 2 rows; fixed `128×128` cells
- Column boundaries: `0, 128, 256, 384, 512`
- Row boundaries: `0, 128, 256`
- Row 0: fire idle, frames 0–3
- Row 1: ice idle, frames 0–3
- No gutters or outer canvas padding
- One intended frame in every cell; no frame bleed
- Final path after promotion: `final/dragon-rider.png`

## Placement contract

- Contact anchor: `(64, 110)`, meaning `ground/mount contact`
- Y-axis source plane: `110`
- The anchor and source plane are separate requirements and must both remain
  stable across every frame and both elemental variants.
