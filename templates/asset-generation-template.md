# Asset Generation Template

Game assets should be requested as a runtime contract, not just as a pretty image prompt.

Use this as the common wrapper for every future AI/external asset request. Fill the `{placeholders}` before sending the request.

## Start With A Resource Brief

Before filling the runtime contract, define where and why the asset is used. Use `resource-request-template.md` for the full intake flow.

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
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
```

## Generation Target Block

```text
Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.
```

## Common Style Block

```text
Project:
- Game asset
- Game: {gameName}
- Asset role: {assetRole}
- Target file path: {path}

Style:
- {styleFamily}
- Readable at in-game scale
- Consistent silhouette, angle, and lighting family with existing assets
- Clean game-ready shapes
- No text, no labels, no guide grid, no watermark

Format:
- PNG-32 RGBA
- Straight alpha, not premultiplied alpha
- sRGB color
- Transparent background unless this is explicitly background art
- No blur, no resample, no antialias cleanup pass
```

## Runtime Contract Block

Use this when code depends on exact coordinates.

```text
Runtime Contract:
- File path must stay unchanged: {path}
- Final canvas size: exactly {width}x{height}px
- The game uses this asset by exact pixel coordinates.
- Do not change the frame count, row order, column order, or semantic meaning.
- Do not add gutters, labels, guide lines, or arbitrary outer padding.
- Transparent padding is allowed only inside the fixed canvas or fixed cells.
- Report final image size and alpha bbox after delivery.
```

## Anchor Contract Block

Use this for characters, items, tiles, FX, and platform contact points.

```text
Anchor Contract:
- Contact anchor is x={anchorX}, y={anchorY} in local asset/cell coordinates.
- This anchor means: {anchorMeaning}.
- This anchor is not the visual center unless explicitly stated.
- Do not move the contact anchor to make the image look centered.
- Visual mass may sit above, below, left, or right of the anchor as needed.
- All grounded/resting frames must preserve this same contact anchor.
```

## Y-Axis Alignment Contract

Use this whenever animation rows or related frames must not jump vertically.

```text
Y-Axis Alignment Contract:
- The local Y baseline must not change between animation rows or frames.
- Contact anchor Y must be identical across every related frame: y={anchorY}.
- Grounded/resting frames must not drift upward or downward during animation.
- If this is a tile, FX, platform, or impact effect, preserve the same implied plane Y.
- Moving debris, particles, glow, or motion trails may animate, but the original source plane must remain fixed.
- When guide lines are overlaid across related frames, the reference plane must line up.
```

## Output Block

```text
Output:
- Overwrite or deliver for this path: {path}
- Keep source backups untouched.
- Provide final image size.
- Provide alpha bbox.
- Confirm PNG-32 RGBA straight alpha.
- Confirm the anchor location and Y-axis baseline used.
- Mention any changed crop, offset, scale, or visual correction.
```

## When To Relax This Template

- Concept art: keep style and avoid rules, but skip exact grid/anchor blocks.
- Background art: keep canvas size and camera composition, but skip contact anchor unless code places objects on it.
- Production sprites, FX, tiles, and stage layers: use every relevant contract block.


