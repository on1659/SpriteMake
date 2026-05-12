# Manifest Notes: hamster-care-20260505

## Manifest Files

- manifests/hamster_care_manifest.json

## Runtime Contracts

| Asset | Image | Grid | Cell | Anchor | Baseline |
| --- | --- | --- | --- | --- | --- |
| hamster_care_atlas | generated/hamster_care_atlas.png | 4 x 4 | 256 x 256 | x=128, y=220 | y=220 |
| hamster_care_items | generated/hamster_care_items.png | 4 x 1 | 256 x 256 | x=128, y=220 | y=220 |

## Animation Keys

### hamster_care_atlas

- idle_breathe: row 0, frames 0-3, 6 fps, loop
- walk: row 1, frames 0-3, 8 fps, loop
- eat: row 2, frames 0-3, 7 fps, loop
- sleep: row 3, frames 0-3, 4 fps, loop

### hamster_care_items

- food_bowl: row 0, frame 0
- water_bottle: row 0, frame 1
- exercise_wheel: row 0, frame 2
- bed: row 0, frame 3

## Placement Notes

- Contact Anchor and Y-axis baseline are intentionally separate.
- Anchor x=128, y=220 is the point the game should place on the habitat floor.
- Baseline y=220 should remain visually stable when animations are played.
- Generated attempts stay in generated/ until QA and visual review pass.
