# SpriteMake Batch Workflow Reference

## Purpose

SpriteMake prepares usable game sprite batches. The project manages request docs, manifests, QA, and preview tools around Codex direct generation or an external generation process.

## Per-Asset Minimum

Each asset should document:

- asset ID
- generation path: Codex direct or strict external generation
- required image model for strict external generation: gpt-image-2
- Codex direct model guarantee: unverified
- gameplay role
- target asset path
- final canvas size
- grid columns and rows
- cell size
- row meanings
- column meanings
- contact anchor
- Y-axis baseline/source plane
- alpha/background requirements
- animation preview tool path when animated
- preview manifest path when animated

## QA Minimum

Check and record:

- final image size
- `width % columns`
- `height % rows`
- cell size
- full alpha bbox
- per-cell alpha bbox
- transparent corners
- frame bleed
- anchor correctness
- Y-axis baseline/source plane stability
- preview tool playback

## Status Values

Use these values in batch docs:

```text
planned
prompted
generated
repack-needed
qa-needed
qa-failed
qa-passed
ready-for-game
copied-to-game
```

## Mini-Symphony States

`.agents/hooks/symphony.ps1` scans `output/*` and may classify batch folders as:

```text
needs-scaffold
needs-prompt
needs-prompt-inject
needs-refine
prompt-ready
qa-needed
needs-regeneration
mixed-review
final-review
final-candidate
```

Use `.\.agents\hooks\symphony.ps1 -WriteReport` to write `output/SYMPHONY.md` before a handoff.

## Final Asset Rule

Only QA-passed PNGs belong in `final/`. Game projects should receive assets from `final/`, not from raw `generated/` attempts.


