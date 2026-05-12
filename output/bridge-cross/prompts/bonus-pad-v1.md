# Prompt: Bridge Cross Bonus Jump Pad V1

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is for the external generation step.

Create a transparent PNG-32 RGBA sprite atlas for a game prop animation.

Game context:
- Bridge Cross is a dimetric pixel-art neon glass bridge game.
- New rule (2026-05-05): instead of falling, players race across an 8-tile bridge.
- Each tile has two sides (left/right). The server secretly picks a "bonus side" each tile.
- If the player picks the bonus side, a **jump pad** spawns on that tile and launches the player **+2 or +3 tiles forward** (super jump).
- If the player picks the normal side, no pad — they jump only +1 tile.
- The bonus pad is the visual feedback that says "you got the bonus".

Gameplay purpose:
- The pad must clearly read as "spring/trampoline/launcher" — something that propels the character upward and forward.
- It appears briefly on the glass tile, the character lands on it, it compresses, then launches them.
- It should feel exciting, energetic, and rewarding (not dangerous, not a trap).

Style reference:
- Match the existing LAMDiceBot Bridge Cross assets — neon glass bridge stage.
- Crisp dimetric/isometric pixel art (same projection as the player and tile sprites).
- Palette: deep navy/black shadow base, electric cyan (#42edff) primary glow, magenta/violet (#a78bfa, #ec4899) accent, white-yellow (#fef08a) energy highlights for the launch burst.
- Strong silhouette at small size (the pad will be drawn at roughly tile width = ~180-220 px on screen).
- No photorealism, no painterly blur, no text, no labels, no watermark, no gridlines.

Canvas:
- Final image size: exactly 1024x256 px
- Grid: exactly 4 columns x 1 row
- Cell size: exactly 256x256 px
- Column boundaries: x=0, 256, 512, 768, 1024
- Row boundary: y=0, 256
- No gutters, no outer padding, no guide grid

Anchor (used by game code):
- anchor.x = 0.5
- anchor.y = 1.0  (bottom-center of cell sits on the glass tile surface)
- The pad object should be drawn so its **base** rests at the bottom edge of the cell, centered horizontally.

Frame breakdown (left → right):

Frame 0 — IDLE / SPAWN-IN (col 0, x=0..256)
- The pad has just appeared on the glass tile. Compact spring/trampoline shape.
- A neon ring or platform disc sits on the tile, with a subtle glow pulse.
- Slight upward energy (small particle hint) but nothing released yet.
- Read as "ready / armed."

Frame 1 — CHARGE / READY (col 1, x=256..512)
- Same pad shape but with a brighter ring, more glow, and a small tension hint.
- This is the "the player is about to land on me" anticipation frame.
- Maybe 1-2 small electric arcs or sparkles around the spring.
- Same base position as frame 0 (no vertical movement of the pad itself).

Frame 2 — COMPRESS / IMPACT (col 2, x=512..768)
- The spring/trampoline is **squished down**, compressed by the impact.
- Pad height is roughly 60-70% of frame 0.
- Glow flares brightly outward (radial impact ring around the base).
- A few yellow-white energy lines bursting outward at the base.
- Read as "stored energy."

Frame 3 — LAUNCH / RELEASE (col 3, x=768..1024)
- The spring extends fully, even slightly **taller** than frame 0 (overshoot).
- A vertical energy beam / arrow / "shoom" effect points upward to indicate "you are launched."
- Sparkles and motion lines streaking upward, fading at the top of the cell.
- Pad itself starts to dissolve/fade (this is the last visible frame; after this it disappears).
- Read as "BOING — launched!"

Important rules for the artist / generator:
- All 4 frames share the **exact same horizontal center and base line** so the pad doesn't appear to slide between frames.
- The pad is the focus — no character art, no tile art (the game already draws the glass tile and the character separately on top).
- Transparent background. Each cell must be fully transparent except the pad / its effects.
- Effects (sparkles, energy lines) should stay inside the cell bounds. No bleed across cell columns.
- Avoid solid floor / tile surface in the sprite — the pad floats on the existing tile drawn by the game.

Output expectations:
- File name: `bonus-pad-v1.png`
- Place in: `D:\Work\vibe\SpriteMake\output\bridge-cross\final\bonus-pad-v1.png`
- Then copied to game at: `D:\Work\LAMDiceBot\assets\bridge-cross\sprites\bonus-pad-v1.png`

Manifest entry (to be added in `bridge-cross-sprites.manifest.json`):
```json
{
  "key": "bonusPad",
  "src": "bonus-pad-v1.png",
  "atlas": { "columns": 4, "rows": 1, "cellW": 256, "cellH": 256 },
  "anchor": { "x": 0.5, "y": 1.0 },
  "animations": {
    "spawn":    { "row": 0, "frames": [0],       "fps": 1,  "loop": false },
    "ready":    { "row": 0, "frames": [1],       "fps": 1,  "loop": false },
    "compress": { "row": 0, "frames": [2],       "fps": 1,  "loop": false },
    "launch":   { "row": 0, "frames": [3],       "fps": 1,  "loop": false },
    "full":     { "row": 0, "frames": [0,1,2,3], "fps": 14, "loop": false }
  }
}
```

Game code usage (for reference, not to render):
- Game spawns the pad on the bonus tile when a player's choice matches the secret bonus row.
- Sequence: spawn(0) shown for ~150ms → ready(1) for ~120ms → compress(2) for ~100ms (sync with character landing) → launch(3) for ~250ms (sync with character super jump) → pad fades.
- Pad sprite is drawn **above the tile sprite, below the character sprite** (z-order: tile < pad < character).
- Drawn at scale ~0.8 of cell (approx 200x200 px on screen).

Regenerate-on-fail:
- If the result is unclear or has more than one trampoline / pad / floor in a single cell, regenerate.
- If frames don't share the same base line, regenerate.
- If text / numbers / labels appear, regenerate.

Done.
