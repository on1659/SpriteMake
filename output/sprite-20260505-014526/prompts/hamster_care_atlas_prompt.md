# Copy-Ready Prompt: Hamster Care Sprite Pack

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.

Create two transparent PNG-32 RGBA sprite atlases for a cozy hamster raising / virtual pet game. Use a cute readable mobile-game style with rounded forms, soft tan-and-cream fur, warm cheeks, clear silhouettes, and no background.

Asset 1: hamster_care_atlas
- Final image size: exactly 1024x1024 px
- Grid: exactly 4 columns x 4 rows
- Cell size: exactly 256x256 px
- Column boundaries: x=0, 256, 512, 768, 1024
- Row boundaries: y=0, 256, 512, 768, 1024
- No gutters
- No outer padding outside the exact canvas
- Fully transparent background
- No labels, no text, no guide grid, no watermark
- PNG-32 RGBA, straight alpha, sRGB

Runtime slicing rule:
- The game slices frames only by the exact grid boundaries above.
- Each cell contains exactly one complete hamster frame.
- No frame may bleed into adjacent cells.
- Transparent padding may exist only inside each fixed cell.

Anchor Contract:
- Contact anchor is x=128, y=220 inside every 256x256 cell.
- This anchor means the hamster lower body / floor contact point used to place it on the habitat floor.
- This anchor is not the visual center.

Y-Axis Alignment Contract:
- The local Y baseline must stay at y=220 in every row and frame.
- The hamster must not drift upward or downward during animation.

Rows:
- Row 0: idle_breathe, subtle breathing and blink
- Row 1: walk, tiny side-to-side steps
- Row 2: eat, holding and nibbling seed or pellet
- Row 3: sleep, curled/resting frames with closed eyes

Columns:
- Column 0: frame_0
- Column 1: frame_1
- Column 2: frame_2
- Column 3: frame_3

Asset 2: hamster_care_items
- Final image size: exactly 1024x256 px
- Grid: exactly 4 columns x 1 row
- Cell size: exactly 256x256 px
- Column boundaries: x=0, 256, 512, 768, 1024
- Row boundaries: y=0, 256
- No gutters
- No outer padding outside the exact canvas
- Fully transparent background
- No labels, no text, no guide grid, no watermark
- PNG-32 RGBA, straight alpha, sRGB

Item columns:
- Column 0: food_bowl
- Column 1: water_bottle
- Column 2: exercise_wheel
- Column 3: bed

Item Anchor Contract:
- Contact anchor is x=128, y=220 inside every 256x256 cell.
- This anchor means the prop floor contact point used to place the item on the habitat floor.

Output Report:
- Final image size for both assets.
- Grid and cell size for both assets.
- Contact anchor and Y baseline confirmation.
- Full alpha bbox and per-cell alpha bbox if possible.
- Confirm raw generated attempts should be saved first under output/sprite-20260505-014526/generated/.
