# Prompt: Bridge Cross Finish Lottery Object V1

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is for the external generation step.

Create a transparent PNG-32 RGBA sprite atlas for a game prop animation.

Game context:
- Bridge Cross is a dimetric pixel-art glass bridge game.
- After runners reach the final platform, both arrived players and fallen players gather.
- They perform a random draw / 제비뽑기 to decide the next result.
- The needed asset is the animated lottery object itself: a small draw box, lottery urn, or cup/tube with lots/slips/sticks.

Gameplay purpose:
- The prop must clearly read as "random draw / drawing lots" without using text.
- It appears on or near the finish platform during the post-game result phase.
- It should feel playful, fair, and ceremonial, not like a treasure chest or weapon.

Style reference:
- Match the existing LAMDiceBot Bridge Cross assets.
- Crisp dimetric/isometric pixel art.
- Neon glass-bridge stage palette: deep navy shadow, cyan glass glow, small yellow celebration highlights.
- Cute compact prop with strong silhouette at small size.
- No photorealism, no painterly blur, no text, no labels, no watermark.

Canvas:
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
- Each cell must contain exactly one complete prop frame.
- Do not rely on visual spacing or manual cropping.
- No frame may bleed into another cell.
- No cell may be empty.
- Transparent padding may exist only inside each fixed cell.

Contact Anchor Contract:
- Contact anchor is x=175, y=165 inside every 350x187 cell.
- This anchor means the bottom center of the lottery object touching the finish platform.
- This anchor is not the visual center.
- Do not move the contact anchor to the visual center.

Y-Axis Source Plane Contract:
- The local prop base/source plane must stay at y=165 in every row and frame.
- The object may shake, glow, open, or eject a slip, but its implied floor contact must not drift upward or downward.
- Particles, paper slips, sticks, sparkles, and glow may move inside the cell.

Rows:
- Row 0: idle_closed. The lottery object waits closed on the finish platform. Calm, readable silhouette.
- Row 1: gather_prompt. Subtle cyan/yellow ring or glow around the object, inviting all players to gather.
- Row 2: mix_shake. The box/tube shakes while the lots are mixed. The base remains planted at y=165.
- Row 3: draw_lot. One stick/card/slip rises or pops out of the object. No readable text on it.
- Row 4: reveal_lot. The selected lot glows with a small celebratory burst. Use an icon/mark shape, not letters or words.
- Row 5: reset_settle. The object settles back toward idle, with a tiny leftover sparkle.

Columns:
- Column 0: frame 0
- Column 1: frame 1
- Column 2: frame 2
- Column 3: frame 3

Visual Requirements:
- Keep the prop centered around x=175 in every cell.
- Keep the base contact point at y=165 in every grounded frame.
- Make the object readable when drawn around 180-260px wide in-game.
- Use transparent empty space around the prop inside the fixed cell.
- The animation should feel like a post-game ceremony: gather, mix, draw, reveal, settle.
- It must be visually distinct from glass bridge break FX and from treasure chests.

Do Not:
- Do not change final size, grid, row order, or column order.
- Do not premultiply alpha.
- Do not crop the prop, slips, sticks, glow, or particles.
- Do not draw multiple unrelated props in one cell.
- Do not add UI, labels, text, numbers, Korean letters, English letters, or guide marks.
- Do not draw player characters in this asset.

Output Report:
- Final image size
- Alpha bbox
- Alpha bbox per cell if possible
- Confirm PNG-32 RGBA straight alpha
- Confirm anchor x=175, y=165
- Confirm the prop base/source plane did not drift across rows or frames

