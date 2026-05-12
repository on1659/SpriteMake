# Sprite Atlas Template

Use this for characters, item animations, UI tokens, particles, and FX sheets that the game slices by grid.

## Copy-Ready Prompt

```text
Resource Request Brief:
- Game / concept: {gameConcept}
- Scene or screen where this appears: {sceneContext}
- Gameplay role: {gameplayRole}
- Player-readable purpose: {playerReadablePurpose}
- Visual direction: {visualDirection}
- Existing assets or style to match: {styleReference}
- In-game display scale: {inGameScale}
- Target file path: {path}

Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.

Create a transparent PNG-32 RGBA sprite atlas for a game.

This must be a strict sprite atlas, not a loosely spaced contact sheet.

Canvas:
- Final image size: exactly {width}x{height}px
- Grid: exactly {cols} columns x {rows} rows
- Cell size: exactly {cellW}x{cellH}px
- Column boundaries: x={columnBoundaries}
- Row boundaries: y={rowBoundaries}
- No gutters
- No outer padding outside the exact canvas
- No guide grid
- No labels
- No text
- Fully transparent background
- PNG-32 RGBA, straight alpha, sRGB
- Crisp game-art edges, no blur or resample pass

Runtime slicing rule:
- The game slices frames only by the exact grid boundaries above.
- Each cell must contain exactly one complete frame.
- Do not rely on visual spacing or manual cropping.
- Do not add arbitrary leading margins, trailing margins, or variable spacing between frames.
- No frame may bleed into another cell.
- No cell may be empty.
- Transparent padding may exist only inside each fixed cell.

Rows:
{rowDefinitions}

Columns:
{columnDefinitions}

Anchor Contract:
- Contact anchor is x={anchorX}, y={anchorY} inside every {cellW}x{cellH} cell.
- This anchor means: {anchorMeaning}.
- This anchor is not the visual center unless explicitly stated.
- Do not move the contact anchor to the visual center.

Y-Axis Alignment Contract:
- The local Y baseline must not change between animation rows or frames.
- All grounded/resting frames must share the same contact anchor Y: y={anchorY}.
- For FX derived from the same object, the original object plane must stay on the same local Y line.
- Moving particles, shards, glow, dust, or trails may animate, but the source plane must not jump.

Visual Requirements:
- {visualStyle}
- Keep silhouette, angle, lighting, and scale consistent across frames.
- Effects may extend inside the cell, but must not bleed into adjacent cells.

Do Not:
- Do not change final size, grid, row order, or column order.
- Do not premultiply alpha.
- Do not add shadows outside the cell.
- Do not crop body parts or important effects.
- Do not draw multiple unrelated poses in one cell.

Output Report:
- Final image size
- Alpha bbox for the full image
- Alpha bbox per cell if possible
- Confirm PNG-32 RGBA straight alpha
- Confirm anchor x={anchorX}, y={anchorY}
- Confirm Y baseline did not drift across rows/frames

Animation Preview Tool:
- Create a local HTML animation preview tool by copying and adapting the generic SpriteMake animation player template.
- Tool output path: {animationToolPath}
- Preview manifest path: {animationManifestPath}
- The tool must play each animation row/frame, show the full sheet grid, selected frame, contact anchor, Y-axis baseline/source plane, image size, cell size, alpha bbox, and path metadata.
- Use project-relative or user-configurable paths. Do not hardcode machine-specific source paths.
```

## Tile FX Example

```text
Cell size is 350x187.
Contact anchor is x=175, y=165.
This is where the character foot anchor lands, not the diamond visual center.

Y-Axis Plane Alignment:
- safe_sparkle, warning_glow, crack, break_shards, fall_trail, landing_pulse, restore_glass must preserve the same local glass tile plane Y.
- Use crack row as the reference plane unless otherwise specified.
- break_shards must not be vertically higher than crack.
- Shards may fly, but the original broken tile reference line must remain fixed.
- When horizontal guide lines are drawn over crack and break_shards, the main glass plane must match.
```

## Side-View Character Example

```text
Final image size: exactly 1536x1728px
Grid: exactly 4 columns x 6 rows
Cell size: exactly 384x288px
Columns: idle, sneak, steal, stunned
Rows: red, orange, yellow, green, blue, violet

Contact anchor:
- x=192, y=252 inside every 384x288 cell
- This is the character foot/item ground contact baseline for placement on a side-view road or floor.

Y-Axis Alignment:
- idle, sneak, steal, and stunned frames must keep the same local ground baseline y=252.
- Sneak may lean forward, but feet must not drift vertically.
- Stunned may rotate/fall visually, but the implied impact ground line must remain at y=252.
```


