# Crazy Arcade Web Clone — Generation Prompts

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

---

## Asset 0: char — 캐릭터 Atlas (bazzi variant)

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a sprite sheet for a top-down cartoon water-balloon battle game (Crazy Arcade clone style).

Sheet: **char-bazzi** — Player character "Bazzi type" (speed archetype)
Canvas: 384×672 pixels, 4 columns × 7 rows, each cell 96×96 pixels.
Background: fully transparent PNG-32 RGBA, straight alpha.

Character design (Bazzi):
- Bright cartoon style, big round eyes with shine, chubby cheeks with blush marks
- Color palette: warm yellow skin, orange-tinted hair/top-knot, blue clothing accent, white trim
- Top-down 0.75 isometric view — slightly above-and-behind perspective, not perfectly overhead
- Foot contact point is always at pixel (48, 84) within each 96×96 cell (baseline y=84)
- Character silhouette fits within a roughly 60×80px area centered in the cell, leaving transparent margin

Row layout (7 rows × 4 frames each):
- Row 0 (y=0..95): `idle` — standing still, subtle breathing or gentle sway animation (frames 0-3)
- Row 1 (y=96..191): `walk_down` — walking toward viewer/south (frames 0-3, smooth walk cycle)
- Row 2 (y=192..287): `walk_up` — walking away from viewer/north (frames 0-3)
- Row 3 (y=288..383): `walk_left` — walking left (frames 0-3)
- Row 4 (y=384..479): `walk_right` — walking right (frames 0-3)
- Row 5 (y=480..575): `trapped` — character inside a water bubble, bouncing/struggling (frames 0-3)
- Row 6 (y=576..671): `dead` — character falling or fading out (frames 0-3)

Requirements:
- Pixel boundaries between cells must be sharp (no bleed/overlap)
- Contact anchor pixel (48, 84) must be consistent across ALL rows and frames
- Straight alpha edges (no pre-multiplied alpha, no fringe)
- Readable and charming at 48×48 display size (2x downscale)

---

## Asset 0b: char-dao — 캐릭터 Dao palette variant

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a sprite sheet for a top-down cartoon water-balloon battle game (Crazy Arcade clone style).

Sheet: **char-dao** — Player character "Dao type" (balanced archetype)
Canvas: 384×672 pixels, 4 columns × 7 rows, each cell 96×96 pixels.
Background: fully transparent PNG-32 RGBA, straight alpha.

Character design (Dao):
- Bright cartoon style, big round eyes with shine, chubby cheeks with blush marks
- Color palette: cool blue theme (#4f8df7 range) — blue skin tone/clothing, white and light blue accents, silver-blue hair, blue eyes with white shine
- Slightly stockier build than the speed archetype, conveying "balanced" archetype
- Top-down 0.75 isometric view — slightly above-and-behind perspective, not perfectly overhead
- Foot contact point is always at pixel (48, 84) within each 96×96 cell (baseline y=84)
- Character silhouette fits within a roughly 60×80px area centered in the cell, leaving transparent margin

Row layout (7 rows × 4 frames each):
- Row 0 (y=0..95): `idle` — standing still, subtle breathing or gentle sway animation (frames 0-3)
- Row 1 (y=96..191): `walk_down` — walking toward viewer/south (frames 0-3, smooth walk cycle)
- Row 2 (y=192..287): `walk_up` — walking away from viewer/north (frames 0-3)
- Row 3 (y=288..383): `walk_left` — walking left (frames 0-3)
- Row 4 (y=384..479): `walk_right` — walking right (frames 0-3)
- Row 5 (y=480..575): `trapped` — character inside a water bubble, bouncing/struggling (frames 0-3)
- Row 6 (y=576..671): `dead` — character falling or fading out (frames 0-3)

Requirements:
- Pixel boundaries between cells must be sharp (no bleed/overlap)
- Contact anchor pixel (48, 84) must be consistent across ALL rows and frames
- Straight alpha edges (no pre-multiplied alpha, no fringe)
- Readable and charming at 48×48 display size (2x downscale)
- Same grid, anchor, and row layout as the other character sheets — palette variant differs only in colors and build

---

## Asset 0c: char-marid — 캐릭터 Marid palette variant

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a sprite sheet for a top-down cartoon water-balloon battle game (Crazy Arcade clone style).

Sheet: **char-marid** — Player character "Marid type" (power archetype)
Canvas: 384×672 pixels, 4 columns × 7 rows, each cell 96×96 pixels.
Background: fully transparent PNG-32 RGBA, straight alpha.

Character design (Marid):
- Bright cartoon style, big round eyes with shine, chubby cheeks with blush marks
- Color palette: deep purple theme (#b06ef7 range) — purple/teal skin, dark green or deep purple clothing accents
- Heavier build than the other archetypes — slightly wider silhouette, conveying "power" archetype (slower but impactful feeling)
- Top-down 0.75 isometric view — slightly above-and-behind perspective, not perfectly overhead
- Foot contact point is always at pixel (48, 84) within each 96×96 cell (baseline y=84)
- Character silhouette fits within a roughly 60×80px area centered in the cell (Marid may read slightly wider but must keep transparent margin, no cell overflow)

Row layout (7 rows × 4 frames each):
- Row 0 (y=0..95): `idle` — standing still, subtle breathing or gentle sway animation (frames 0-3)
- Row 1 (y=96..191): `walk_down` — walking toward viewer/south (frames 0-3, smooth walk cycle)
- Row 2 (y=192..287): `walk_up` — walking away from viewer/north (frames 0-3)
- Row 3 (y=288..383): `walk_left` — walking left (frames 0-3)
- Row 4 (y=384..479): `walk_right` — walking right (frames 0-3)
- Row 5 (y=480..575): `trapped` — character inside a water bubble, bouncing/struggling (frames 0-3)
- Row 6 (y=576..671): `dead` — character falling or fading out (frames 0-3)

Requirements:
- Pixel boundaries between cells must be sharp (no bleed/overlap)
- Contact anchor pixel (48, 84) must be consistent across ALL rows and frames
- Straight alpha edges (no pre-multiplied alpha, no fringe)
- Readable and charming at 48×48 display size (2x downscale)
- Same grid, anchor, and row layout as the other character sheets — palette variant differs only in colors and build

---

## Asset 1: balloon — 물풍선 Atlas

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a sprite sheet for a water balloon in a top-down cartoon battle game.

Sheet: **balloon** — Water balloon prop
Canvas: 192×96 pixels, 2 columns × 1 row, each cell 96×96 pixels.
Background: fully transparent PNG-32 RGBA, straight alpha.

Cell layout:
- Cell (0,0) — `inflate_small`: Small water balloon just placed, about 40×50px visible area, pale blue translucent with water inside, cartoon style, slightly wobbling shape
- Cell (1,0) — `inflate_big`: Same balloon fully inflated before explosion, about 70×80px visible area, deeper blue, more spherical, glowing slightly to indicate imminent explosion

Design requirements:
- Top-down 0.75 view — slightly above and behind
- Contact anchor at (48, 84) — bottom of balloon touches tile ground
- Baseline y=84 across both cells
- Bright cartoon style matching Crazy Arcade aesthetic
- Water visible through translucent skin
- Readable at 48×48 display size

---

## Asset 2: stream — 물줄기 Atlas

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a sprite sheet for water stream explosions in a top-down cartoon water-balloon battle game.

Sheet: **stream** — Water stream tiles
Canvas: 192×384 pixels, 2 columns × 4 rows, each cell 96×96 pixels.
Background: fully transparent PNG-32 RGBA, straight alpha.

Cell layout (one stream part per row; animation frames advance left-to-right):
- Row 0: `center` — cross-shaped water splash at explosion origin, 4-directional burst
- Row 1: `arm_h` — horizontal water stream segment (left-right direction), fills cell width
- Row 2: `arm_v` — vertical water stream segment (up-down direction), fills cell height
- Row 3: `end` — rounded water stream terminus (generic end cap, works in any direction)

Column 0 (frame 0 — static), Column 1 (frame 1 — flowing):
- Column 1 repeats the same part as column 0 in each row, with flowing water animation (slight wave/ripple variation)

Design:
- Bright blue water streams, cartoon style
- Streams are roughly 20-30px wide within the 96px cell, leaving transparent margin
- Consistent water color: bright blue (#4AA8E8 range), white foam highlights
- Contact anchor center at (48, 48) — streams are centered on tiles
- Readable as "dangerous water" at 48px display size

---

## Asset 3: tiles — 타일 Atlas

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a tile sprite sheet for a top-down cartoon water-balloon battle game (Crazy Arcade style).

Sheet: **tiles** — Map tiles
Canvas: 384×192 pixels, 4 columns × 2 rows, each cell 96×96 pixels.
Background: PNG-32 RGBA; floor tiles are fully opaque, blocks have transparent edges.

Cell layout:
Row 0:
- (0,0): `floor_a` — bright grass-green floor tile, cartoon checkerboard pattern (light variant), tile border subtle
- (1,0): `floor_b` — same floor but slightly darker green (dark variant for checkerboard pairing)
- (2,0): `soft_block` — destructible wooden/crate block, brown warm tones, visible grain/cracks, sits on one tile, isometric-ish top face visible, rounded corners
- (3,0): `hard_block` — indestructible stone/concrete block, grey cool tones, solid and heavy appearance, clear visual difference from soft block

Row 1 (soft block destruction animation):
- (0,1): `soft_break_0` — block starts cracking (hairline cracks appear)
- (1,1): `soft_break_1` — cracks deepen, pieces beginning to separate
- (2,1): `soft_break_2` — block exploding into pieces, water splash visible
- (3,1): `soft_break_3` — final debris/residue, nearly transparent

Design:
- Top-down 0.75 view consistent with character sheets
- Blocks should visually "sit" on the floor tile — slight depth/height impression
- Readable at 48×48 display size

---

## Asset 4: items — 아이템 Atlas

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a sprite sheet for collectible power-up items in a top-down cartoon water-balloon battle game (Crazy Arcade clone).

Sheet: **items** — Power-up items
Canvas: 192×480 pixels, 2 columns × 5 rows, each cell 96×96 pixels.
Background: fully transparent PNG-32 RGBA, straight alpha.

Cell layout (2-frame sparkle animation per item):
Row 0 — `potion` (water stream length up potion):
- (0,0): frame0 — blue potion bottle, liquid visible, cartoon style, warm glow
- (1,0): frame1 — same with subtle sparkle/glow effect added

Row 1 — `balloon` (extra balloon capacity):
- (0,1): frame0 — small bright yellow/red water balloon icon
- (1,1): frame1 — with sparkle

Row 2 — `roller` (speed roller / boost shoes):
- (0,2): frame0 — roller skate or speed shoe icon, cartoon style
- (1,2): frame1 — with speed lines or sparkle

Row 3 — `needle` (needle/pin — pops own bubble):
- (0,3): frame0 — shiny silver needle/pin with pointed tip clearly visible
- (1,3): frame1 — with glint sparkle

Row 4 — `iron` (ultra iron — instant-explode balloon):
- (0,4): frame0 — iron/bomb icon, warm orange/red tones, slightly scary-cute expression
- (1,4): frame1 — with glow/spark effect

Design:
- Each item must have a unique, immediately recognizable silhouette at 48px
- Bright, saturated colors on transparent background
- Contact anchor at (48, 84), baseline y=84
- Cartoon style matching the rest of the game's aesthetic

---

## Asset 5: fx — 이펙트 Atlas

### Prompt

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.

Create a sprite sheet for visual effects in a top-down cartoon water-balloon battle game (Crazy Arcade clone).

Sheet: **fx** — Visual effects
Canvas: 384×576 pixels, 4 columns × 6 rows, each cell 96×96 pixels.
Background: fully transparent PNG-32 RGBA, straight alpha.

Cell layout (4-frame animations):
Row 0 — `pop` (water bubble pop — character is caught/dies):
- 4 frames: small bubble → expanding water burst → splash scatter → dissipate
- Blue water, circular burst pattern

Row 1 — `needle` (needle escape — character uses needle to pop own bubble):
- 4 frames: needle appears → sharp pierce point flash → bright radial sparkle → clear
- Silver needle glint, radial star flash

Row 2 — `splash` (water stream hit):
- 4 frames: water contact flash → water scatter → drops → clear
- Blue water droplets, impact star shape initial frame

Row 3 — `pickup` (item collected):
- 4 frames: star/sparkle appears → expands → twinkle → clear
- Yellow/white stars, cheerful pickup feel

Row 4 — `crumb` (soft block destroyed — debris burst):
- 4 frames: brown square wood chips burst from center → scatter outward with a slight upward toss → drift apart → fade out
- Warm brown wooden fragments (#9a6a30 range), chunky square pieces matching the soft block's brown tones

Row 5 — `itemPop` (item destroyed by water stream):
- 4 frames: small white water droplets appear at center → burst outward in 4 directions → spread and thin out → vanish
- White/pale water droplets, light and quick dissipate feel

Design:
- All effects centered at (48, 48) within 96×96 cell
- Effects should extend to cell boundaries for visual impact but NOT bleed into adjacent cells
- Readable at 48px+ display size
- Cartoon style — not realistic, not overly complex
- Each frame should be visually distinct (clear animation progression)
