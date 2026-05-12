# Resource Request Flow

Use this before writing a sprite prompt. A sprite request should explain what the asset is for before it explains how the atlas is sliced.

The user does not need to provide this whole form up front. If the user gives a short natural-language request, first capture it with `sprite-intake.ps1`, then fill missing fields with inferred defaults or placeholders.

The flow is:

```text
Resource brief -> runtime contract -> generated asset -> QA -> game integration
```

In `mockup.html`, this is enforced as four steps:

```text
1. Brief
2. Paths
3. Atlas
4. Tool / Review
```

Do not copy or send the generation prompt until all four steps pass.

## 1. Resource Brief

Fill this first.

```text
Resource Request Brief:
- Original user request:
- SpriteMake batch folder:
- Game / concept:
- Scene or screen where this appears:
- Gameplay role:
- Player-readable purpose:
- Visual direction:
- Existing assets or style to match:
- In-game display scale:
- Target file path:
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
```

Good answers are concrete:

```text
Game / concept:
- Side-view stealing game with small readable characters.

Scene or screen where this appears:
- Main play lane, drawn over a flat road/floor.

Gameplay role:
- Player and NPC bodies. The game places them by foot contact.

Player-readable purpose:
- The player must instantly read idle, sneak, stealing, and stunned states.

Visual direction:
- Cute, compact, crisp-edged, readable at small size.

Existing assets or style to match:
- Match existing side-view character proportions and outline weight.

In-game display scale:
- Around 96px tall on screen.

Target file path:
- assets/characters/player-atlas.png
```

## 2. Runtime Contract

After the brief is clear, define the technical contract.

```text
Runtime Contract:
- Game project root:
- Target asset path:
- Source/reference path:
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Asset type:
- Static image or sprite atlas:
- Final canvas size:
- Grid columns:
- Grid rows:
- Cell size:
- Row meanings:
- Column meanings:
- Contact anchor:
- Contact anchor meaning:
- Y-axis baseline or source plane:
- Alpha/background requirement:
```

## 3. Generation Prompt

Combine the resource brief with the atlas or asset template.

Every copy-ready generation prompt should include:

```text
Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.
```

The prompt should answer both:

- What should this feel like in the game?
- How will code slice and place it?

Do not send only the runtime contract unless the visual concept is already obvious from existing art.

## 4. Animation Preview Tool

For animated sprite atlases, create a local HTML animation tool together with the asset request.

Use this rule in requests:

```text
Animation Preview Tool Request:
- Also create a local HTML animation preview/production tool for this asset.
- Copy and adapt the generic SpriteMake animation player template instead of writing a one-off viewer from scratch.
- Tool output path:
- Preview manifest path:
- The tool must load the target PNG through the manifest, play each animation row/frame, expose sheet/animation/palette/FPS/scale controls, and show both an animation stage and the full sprite sheet.
- The tool must draw exact cell grid lines, selected frame bounds, contact anchor, Y-axis baseline/source plane, image size, cell size, alpha bbox, and path metadata.
- Use project-relative or user-configurable paths in the tool. Do not hardcode machine-specific source paths.
```

The generic template is:

```text
templates/animation-player-template.html
```

The copyable manifest starter is:

```text
templates/animation-manifest-template.json
```

Expected manifest shape:

```json
{
  "sheets": {
    "players": {
      "label": "Players",
      "image": "../assets/characters/player-atlas.png",
      "grid": { "columns": 4, "rows": 6 },
      "anchor": { "x": 192, "y": 252, "mode": "pixel" },
      "baselineY": 252,
      "defaultScale": 1,
      "animations": {
        "idle": { "row": 0, "frames": [0, 1, 2, 3], "fps": 8, "loop": true }
      }
    }
  }
}
```

Use normalized anchors only when the manifest explicitly says so:

```json
"anchor": { "x": 0.5, "y": 0.875, "mode": "normalized" }
```

## 5. QA

After generation, verify:

- The asset still matches the concept and gameplay role.
- It is readable at the intended in-game scale.
- Canvas/grid/cell sizes match the contract.
- Contact anchor and Y-axis baseline are usable.
- Alpha, bbox, and transparent corners are clean.
- The animation preview tool loads the manifest and PNG.
- The animation preview tool can play every intended row/frame.

## 6. Integration

Only move the asset into the game repo after QA passes.

Keep SpriteMake as the request, prompt, and QA workspace. Keep production game assets in each game project.


