# Sprite Batch: hamster-care-20260505

## Purpose

- Created at: 2026-05-05 01:45:26 +09:00
- Original user request:

```text
햄스터 키우기 게임만들고싶은데, 스프라이트 만들어줘
```

- Game / project: Hamster raising / virtual pet game
- Feature / scene: Main care screen and basic interaction UI
- Shared gameplay purpose: Let the player read the hamster's current state and trigger basic care actions.
- Shared visual direction: Cozy cute mobile-game style, soft rounded forms, readable at small scale, warm but not monochrome.
- Existing assets or style to match: None provided; use a clean standalone starter style.
- In-game scale reference: Hamster rendered around 96-160 px tall depending on zoom; care items rendered around 48-96 px.
- Game project root: TBD by user
- Strict generation provider: OpenAI Images API
- Required image model for strict generation: gpt-image-2
- Codex direct model guarantee: unverified when Generation mode is codex
- Generation mode: codex / local generated attempt
- Output folder: output/sprite-20260505-014526

## Assets

| ID | Role | Target Path | Status |
| --- | --- | --- | --- |
| hamster_care_atlas | Main animated hamster character atlas | assets/sprites/hamster/hamster_care_atlas.png | generated-qa-pending |
| hamster_care_items | Static care item icon atlas | assets/sprites/hamster/hamster_care_items.png | generated-qa-pending |

## Runtime Contract Summary

### hamster_care_atlas

- Final canvas: 1024x1024 px
- Grid: 4 columns x 4 rows
- Cell size: 256x256 px
- Column boundaries: x=0, 256, 512, 768, 1024
- Row boundaries: y=0, 256, 512, 768, 1024
- Contact anchor: x=128, y=220 inside every cell
- Anchor meaning: lower body / ground contact point used to place the hamster on the habitat floor
- Y-axis baseline/source plane: y=220 in every row and frame

Rows:

- Row 0: idle_breathe
- Row 1: walk
- Row 2: eat
- Row 3: sleep

Columns:

- Column 0: frame_0
- Column 1: frame_1
- Column 2: frame_2
- Column 3: frame_3

### hamster_care_items

- Final canvas: 1024x256 px
- Grid: 4 columns x 1 row
- Cell size: 256x256 px
- Column boundaries: x=0, 256, 512, 768, 1024
- Row boundaries: y=0, 256
- Contact anchor: x=128, y=220 inside every cell
- Anchor meaning: item floor contact point used to place props on the habitat floor
- Y-axis baseline/source plane: y=220

Columns:

- Column 0: food_bowl
- Column 1: water_bottle
- Column 2: exercise_wheel
- Column 3: bed

## Status

- Scaffold: complete
- Prompt: complete
- Manifest: complete
- Preview tool: complete
- Generated PNGs: complete
- QA: generated report written; human visual review still needed before moving assets to final/
