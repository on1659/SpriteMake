# Prompt: Bridge Cross Glass FX Parallel V3

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is for the external generation step.

Create a transparent PNG-32 RGBA sprite atlas for a game.

Game context:
- Bridge Cross is a dimetric pixel-art glass bridge game.
- Multiple runner tokens now move across the bridge at the same time.
- Several runners may stand on the same glass tile.
- If a tile breaks, nearby runners on that same tile may fall together.
- The FX must make multi-runner tile pressure, cascade break, start launch, and finish arrival readable.

Style reference:
- Match the existing LAMDiceBot Bridge Cross assets.
- Crisp dimetric/isometric pixel art.
- Cyan glass, soft yellow highlights, neon void stage lighting.
- No soft painted blur, no photorealism, no text, no labels, no watermark.

Canvas:
- Final image size: exactly 1400x2057px
- Grid: exactly 4 columns x 11 rows
- Cell size: exactly 350x187px
- Column boundaries: x=0, 350, 700, 1050, 1400
- Row boundaries: y=0, 187, 374, 561, 748, 935, 1122, 1309, 1496, 1683, 1870, 2057
- No gutters
- No outer padding outside the exact canvas
- No guide grid
- No labels
- No text
- Fully transparent background
- PNG-32 RGBA, straight alpha, sRGB

Runtime slicing rule:
- The game slices frames only by the exact grid boundaries above.
- Each cell must contain exactly one complete FX frame.
- Do not rely on visual spacing or manual cropping.
- No frame may bleed into another cell.
- No cell may be empty.
- Transparent padding may exist only inside each fixed cell.

Contact Anchor Contract:
- Contact anchor is x=175, y=165 inside every 350x187 cell.
- This anchor means the runner foot contact point and glass source plane.
- This anchor is not the visual center.
- Do not move the contact anchor to the visual center.

Y-Axis Source Plane Contract:
- The local source plane must stay at y=165 in every tile-derived row.
- Glow, cracks, shards, pressure rings, landing pulses, restore glass, and arrival glow must line up on the same implied glass plane.
- Particles and trails may move, but the original tile plane must not jump.

Rows:
- Row 0: safe_sparkle. Existing safe tile shimmer, calm cyan/yellow sparkle.
- Row 1: warning_glow. Existing danger/choice glow, readable but not opaque.
- Row 2: crack. Glass crack spreading on the same tile plane.
- Row 3: break_shards. Broken glass burst, shards contained inside cell.
- Row 4: fall_trail. Vertical fall streak/trail for a runner falling below the tile.
- Row 5: landing_pulse. Soft impact ring centered around the contact plane.
- Row 6: restore_glass. Broken glass reforming back to a clean glass tile.
- Row 7: shared_tile_pressure. Subtle pressure rings under multiple feet on one tile, not a break, readable as "crowded tile".
- Row 8: cascade_break_burst. Stronger simultaneous break flash for cascade fall, more energetic than row 3 but still contained.
- Row 9: start_dash_dust. Small launch dust/spark kick that sits on the start platform contact plane.
- Row 10: finish_arrival_glow. Celebration/arrival shimmer for the finish platform contact plane.

Columns:
- Column 0: frame 0
- Column 1: frame 1
- Column 2: frame 2
- Column 3: frame 3

Visual Requirements:
- Preserve the same camera angle and tile plane across every row.
- Keep effects readable when drawn around 450x214px in-game.
- Keep all glow and particles within the current cell.
- Frame intensity should progress naturally from column 0 to column 3.
- Existing rows 0-6 should remain visually compatible with current glass-fx-v2 row meanings.
- New rows 7-10 should feel like the same asset family, not a different art pack.

Do Not:
- Do not change final size, grid, row order, or column order.
- Do not premultiply alpha.
- Do not crop important particles.
- Do not draw multiple unrelated effects in one cell.
- Do not add a visible guide grid.
- Do not include characters, UI, labels, or text.

Output Report:
- Final image size
- Alpha bbox
- Alpha bbox per cell if possible
- Confirm PNG-32 RGBA straight alpha
- Confirm anchor x=175, y=165
- Confirm Y source plane did not drift across rows

