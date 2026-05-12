# Prompt: Bridge Cross Player Parallel Readability Refresh

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is for the external generation step.

Create transparent PNG-32 RGBA sprite atlases for small runner tokens in a game.

Game context:
- Bridge Cross now shows several runner tokens moving across the glass bridge at the same time.
- Active runner scale is small, around 0.58 of a 350x187 cell.
- The player must still read color, run, jump, landing, fall, and winner/result states.

Create one atlas per color variant:
- red
- orange
- yellow
- green
- blue
- indigo
- violet optional for source/archive consistency

Canvas per atlas:
- Final image size: exactly 1400x1122px
- Grid: exactly 4 columns x 6 rows
- Cell size: exactly 350x187px
- Column boundaries: x=0, 350, 700, 1050, 1400
- Row boundaries: y=0, 187, 374, 561, 748, 935, 1122
- No gutters
- No outer padding outside the exact canvas
- No guide grid
- No labels
- No text
- Fully transparent background
- PNG-32 RGBA, straight alpha, sRGB

Runtime slicing rule:
- The game slices frames only by the exact grid boundaries above.
- Each cell must contain exactly one complete runner frame.
- No frame may bleed into another cell.
- No cell may be empty.
- Transparent padding may exist only inside each fixed cell.

Contact Anchor Contract:
- Contact anchor is x=175, y=165 inside every 350x187 cell.
- This anchor means the runner foot contact point.
- This anchor is not the visual center.
- Do not move the contact anchor to the visual center.

Rows:
- Row 0: idle
- Row 1: run
- Row 2: jump
- Row 3: land
- Row 4: fall
- Row 5: result

Columns:
- Column 0: frame 0
- Column 1: frame 1
- Column 2: frame 2
- Column 3: frame 3

Visual Requirements:
- Match the existing Bridge Cross compact neon pixel runner style.
- Keep the same silhouette, pose layout, outline thickness, shadow placement, and frame placement for all color variants.
- Change only the suit/body color between variants.
- Make run/jump/fall/result readable at small in-game scale.
- For idle, run, land, and result rows, the lowest foot contact pixel must touch y=165 in every frame.
- For jump row, keep the anchor as the landing reference point, but draw the body above it to show a jump arc.
- For fall row, draw one complete falling pose per cell; do not leave any fall cell empty.

Do Not:
- Do not change final size, grid, row order, or column order.
- Do not premultiply alpha.
- Do not crop body parts.
- Do not draw multiple unrelated poses in one cell.
- Do not change pose placement between color variants.

Output Report:
- Final image size for each atlas
- Alpha bbox for each atlas
- Alpha bbox per cell if possible
- Confirm PNG-32 RGBA straight alpha
- Confirm anchor x=175, y=165
- Confirm grounded foot baseline did not drift across grounded rows

