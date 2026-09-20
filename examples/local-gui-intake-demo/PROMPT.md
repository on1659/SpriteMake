# Original Request

> 불과 얼음 속성의 탑승 가능한 드래곤 스프라이트를 만들어줘.

## Copy-ready generation prompt

Generate a strict game sprite atlas for a mountable dragon with two readable
elemental variants: fire and ice. Use clean, game-usable fantasy sprite art;
keep the rider area visually clear but do not add a rider. Required generation
target: **gpt-image-2**.

Canvas must be exactly `512×256` pixels: 4 columns × 2 rows, each cell exactly
`128×128`; no gutters and no outer padding. Row 0 is fire idle frames 0–3.
Row 1 is ice idle frames 0–3. One dragon frame per cell. Transparent padding is
allowed only inside each fixed cell; background must otherwise be transparent.

Use contact anchor `(64, 110)` for every grounded frame. Keep the Y-axis source
plane at local `y=110` in both rows so the fire and ice variants never bob or
drift. Do not include labels, guides, text, watermarks, a contact sheet layout,
or objects crossing cell boundaries.

## Generation handling

- Codex direct generation may create an unverified candidate under `generated/`.
- Strict external generation uses this prompt in an external generation UI.
- Neither route stores an API key or account token in SpriteMake.
