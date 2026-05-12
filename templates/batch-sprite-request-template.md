# Batch Sprite Request Template

Use this when SpriteMake should prepare multiple usable game sprites in one production pass.

The goal is not a set of pretty images. The goal is a batch setup that leads to game-ready sprite assets that can be sliced, placed, previewed, QA'd, and moved into the target game project.

SpriteMake does not store API keys or call image generation APIs directly. Treat this as the folder/markdown/manifest/QA setup layer around Codex direct generation or whatever external generation process is used.

Default generation target:

```text
Provider: OpenAI Images API
Required image model: gpt-image-2
Codex direct mode: allowed for keyless convenience, but model is not forced or verified as gpt-image-2
```

## Batch Overview

```text
Batch Sprite Production Request:
- Original user request:
- SpriteMake batch folder:
- Game / project:
- Game project root:
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Scene or feature:
- Shared gameplay purpose:
- Shared visual direction:
- Existing assets or style to match:
- In-game scale reference:
- Output root:
- Preview tool folder:
- QA output folder:
```

## Required Output Per Asset

Every asset in the batch should produce:

```text
- strict atlas PNG or static PNG
- manifest entry or manifest JSON
- target game asset path
- source/reference path when relevant
- contact anchor
- Y-axis baseline/source plane
- row and column meanings
- alpha bbox report
- per-cell bbox report for atlases
- local HTML animation/preview tool when animated
- QA notes and known issues
```

## Batch Asset List

Copy one block per asset.

```text
Asset:
- ID:
- Asset role:
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path:
- Source/reference path:
- Animation tool path:
- Preview manifest path:
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
- Y-axis baseline/source plane:
- Player-readable purpose:
- Visual direction override:
- QA priority:
```

## Batch Generation Rules

```text
Batch Rules:
- Use `gpt-image-2` for image generation/editing requests.
- Do not silently substitute another image model; stop and report if `gpt-image-2` is unavailable.
- Keep shared style, camera angle, outline weight, lighting, and in-game scale consistent across every asset.
- Do not change any target path after generation starts.
- Do not change grid, row order, column order, or anchor contract per asset unless the batch request is updated.
- Do not mix source/contact-sheet files with final game-ready atlas files.
- Keep generated source attempts separate from QA-passed final outputs.
- Use project-relative or user-configurable paths in preview tools.
- Do not hardcode temporary local source paths into docs or reusable templates.
```

## Suggested Output Folders

```text
output/{batch}/prompts/
output/{batch}/generated/
output/{batch}/qa/
output/{batch}/manifests/
output/{batch}/tools/
output/{batch}/source/
output/{batch}/final/
```

Final game assets still belong in the target game project after QA passes.

## Batch QA Summary

```text
Batch QA Summary:
- Batch ID:
- Asset count:
- Passed:
- Needs regeneration:
- Needs repack:
- Needs manual cleanup:
- Manifest updated:
- Preview tools updated:
- Ready for game integration:
```


