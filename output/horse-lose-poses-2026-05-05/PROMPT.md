# Strict gpt-image-2 Prompt Handoff

This batch explicitly requires gpt-image-2. SpriteMake does not call the image API and Codex direct image generation cannot satisfy this requirement, so use the per-asset prompt files below in a strict external gpt-image-2 generation environment.

Do not silently substitute another model. If gpt-image-2 is unavailable, stop and leave the asset pending.

## Per-Asset Prompts

- prompts/horse-lose-prompt.md
- prompts/rabbit-lose-prompt.md
- prompts/turtle-lose-prompt.md
- prompts/dinosaur-lose-prompt.md
- prompts/knight-lose-prompt.md
- prompts/car-lose-prompt.md
- prompts/rocket-lose-prompt.md
- prompts/bird-lose-prompt.md
- prompts/ninja-lose-prompt.md
- prompts/boat-lose-prompt.md
- prompts/bicycle-lose-prompt.md
- prompts/scooter-lose-prompt.md
- prompts/helicopter-lose-prompt.md
- prompts/eagle-lose-prompt.md
- prompts/crab-lose-prompt.md

## Common Generation Target Block

```text
Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- If gpt-image-2 is unavailable, stop and report the condition instead of using another model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation is not allowed for this batch because the source request explicitly requires gpt-image-2.

Strict Atlas Contract:
- Output format: PNG-32 RGBA, straight alpha, sRGB.
- Transparent background only; no guide grid, no labels, no watermark, no text.
- Final canvas size: exactly 120x45 px.
- Grid: exactly 2 columns x 1 row.
- Cell size: exactly 60x45 px.
- Column boundaries: x=0, 60, 120.
- Row boundaries: y=0, 45.
- No gutters and no outer padding outside the exact canvas.
- Transparent padding may exist only inside each fixed cell.
- Each cell must contain exactly one complete frame.
- No frame may bleed into the neighboring cell.
- Contact anchor: x=30, y=45 inside every 60x45 cell.
- Contact anchor meaning: track ground contact point at the bottom center of the vehicle/feet.
- Y-axis baseline/source plane: local y=45 is the track ground; the vehicle feet/bottom must touch this line in both frames.
- Row 0 meaning: lose pose.
- Column 0 meaning: pose A, sad base pose.
- Column 1 meaning: pose B, subtle sad-breath variant.
- Animation timing: 2 frames, 0.6s loop total, no violent motion.

Shared Visual Rules:
- Pixel art / chunky SVG-matched style, readable at 60x45 in-game scale.
- Side view facing the same direction as the existing run-state vehicle, mostly right-facing.
- 1-2 px black outline, crisp pixel edges, no blur.
- Keep each vehicle's base hue but reduce saturation to about 75-80% for a discouraged tone.
- Add one small 8x8 px effect above the head/body: gray sigh cloud, blue tear, tiny smoke, or bubble according to the asset notes.
- Character-like vehicles should have sad eyes: ㅠㅠ style or narrowed eyes in simple pixel marks.
- The tone is comic and disappointed, not dark tragedy.

Output Report Required From Generation Step:
- Confirm final image size 120x45.
- Confirm PNG-32 RGBA straight alpha, transparent background.
- Report full alpha bbox.
- Report per-cell alpha bbox for cell 0 (x=0..59) and cell 1 (x=60..119).
- Confirm contact anchor x=30, y=45.
- Confirm Y baseline did not drift between the two frames.
```