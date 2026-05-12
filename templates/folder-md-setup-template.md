# Folder And Markdown Setup Template

Use this when starting a new sprite batch in SpriteMake.

SpriteMake is a setup workspace, not a direct image-generation API client. A batch should be organized so generated images, prompts, manifests, QA reports, and preview tools can be reviewed before anything is copied into the target game project.

## Batch Folder Shape

Recommended structure:

```text
output/{game-or-feature}/
  BATCH.md
  REQUESTS.md
  PROMPT.md
  MANIFEST.md
  QA.md
  prompts/
  generated/
  source/
  manifests/
  tools/
  qa/
  final/
```

## File Roles

```text
BATCH.md
- Batch purpose
- Shared style rules
- Required generation model: gpt-image-2
- Target game project
- Asset list
- Production status

REQUESTS.md
- Copy-ready prompts per asset
- Resource briefs
- Runtime contracts
- Animation preview tool requests

PROMPT.md
- Original natural-language user request
- SpriteMake output paths
- Required generation model: gpt-image-2
- Copy-ready generation prompt for Codex direct or strict external gpt-image-2 generation

MANIFEST.md
- Manifest paths
- Grid/anchor/baseline summaries
- Runtime integration notes

QA.md
- Size/grid checks
- Alpha bbox reports
- Per-cell bbox reports
- Animation preview notes
- Pass/fail state
```

## Output Folder Roles

```text
generated/
- Raw generated attempts that are not yet QA-passed.

prompts/
- Prompt variants, regenerated prompt attempts, or per-asset prompt splits.

source/
- Reference images, source sheets, or intermediate cleanup files.

manifests/
- JSON manifests used by preview tools and game integration.

tools/
- Copied/adapted animation preview HTML tools.

qa/
- QA reports, screenshots, bbox logs, and comparison images.

final/
- QA-passed PNGs ready to copy into the target game project.
```

## Batch Status Terms

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

## No API Key Rule

```text
- Do not store API keys in SpriteMake.
- Do not commit API keys to batch folders.
- Require gpt-image-2 in generation request docs.
- Do not silently substitute another image model.
- Do not make reusable docs depend on a private local source path.
```


