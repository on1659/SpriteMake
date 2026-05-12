# helicopter-lose gpt-image-2 Prompt

Use this prompt in a strict external generation environment that can explicitly select OpenAI gpt-image-2.

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

Resource Request Brief:
- Game / concept: LAMDiceBot horse-race finish/result sequence.
- Scene or screen where this appears: finish-line slow motion and result overlay for the selected penalty vehicle.
- Gameplay role: lose-state vehicle sprite shown after finish/victory resolution.
- Player-readable purpose: instantly communicate that this vehicle is disappointed and is the penalty/selected vehicle.
- Vehicle ID: helicopter
- Asset ID: helicopter-lose
- Vehicle Korean label: 헬리콥터
- Pose family: stopped and tilted / sinking posture
- Visual direction override: 노란/검정 헬리콥터, 프로펠러 회전 X(정지), 살짝 비스듬히(5도), 작은 검은 연기
- Existing asset/style reference: Do not use POWER_VEHICLE_VARIANT_OVERRIDES or booster/power art.  match D:\Work\LAMDiceBot\js\horse-race-sprites.js vehicle 'helicopter' base svgMap run.frame1 state around line 405. Match its chunky pixel silhouette, facing direction, and 1-2 px black outline.

- In-game display scale: 60x45 px.
- Target game file path after QA: assets/horse-race/sprites/lose/helicopter-lose.png
- Local generated file expected by preview manifest: output/horse-lose-poses-2026-05-05/generated/helicopter-lose.png
- Local final file after QA: output/horse-lose-poses-2026-05-05/final/helicopter-lose.png

Per-Asset Visual Direction:
- Base color family: yellow/black helicopter, keeping original hue with saturation reduced to about 75-80%.
- Frame 0: 프로펠러가 정지하고 5도 기울어짐.
- Frame 1: 검은 연기와 차체가 1px 움직임.
- Effect: small dark smoke puff, about 8x8 px, above the head/body and fully inside each 60x45 cell.
- Keep the feet, wheels, hull, body bottom, or contact point touching y=45 in both frames.
- Do not center the sprite visually if that would move the contact anchor or Y baseline.

Animation Preview Tool Request:
- Tool output path: output/horse-lose-poses-2026-05-05/tools/helicopter-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/helicopter-lose.json
- The preview must show the strict 2x1 grid, selected frame bounds, contact anchor x=30 y=45, Y baseline y=45, image size, cell size, and alpha bbox.

