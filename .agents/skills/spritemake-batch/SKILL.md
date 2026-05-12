---
name: spritemake-batch
description: Set up and maintain SpriteMake sprite batches. Use when Codex is working in the SpriteMake project to create folder/MD scaffolds, copy-ready sprite prompts, manifests, QA reports, animation preview tools, or final handoff notes for game-usable sprite assets without using image-generation API keys.
---

# SpriteMake Batch

## Overview

Use this skill to turn a short natural-language sprite request or generated PNG into a usable SpriteMake batch: folders, markdown request files, copy-ready prompts, strict atlas contracts, manifests, QA notes, and animation preview tools.

SpriteMake is not an image-generation API client. Do not store API keys and do not call image generation APIs from this project.

The default convenience path is Codex direct image generation without API keys. That path cannot force or verify `gpt-image-2`, so treat results as unverified generated attempts until QA passes. When preparing strict external image generation requests, require OpenAI `gpt-image-2`. Do not silently substitute another image model.

## Workflow

1. Read root `AGENTS.md`, `README.md`, and `USAGE.md`.
2. If the user gives a short request like "draw a dragon sprite", do not ask them to rewrite it as a long template.
3. Use `.agents/hooks/sprite-intake.ps1` to create `output/{inferred-name}-{timestamp}/`, capture the original request, and write `PROMPT.md`.
4. Default to Codex direct generation when the user wants keyless convenience; ask only if strict `gpt-image-2` or setup-only mode is unclear.
5. Run `.agents/hooks/symphony.ps1` when you need a board view of existing batch states or next actions.
6. Create or update `BATCH.md`, `REQUESTS.md`, `PROMPT.md`, `MANIFEST.md`, and `QA.md`.
7. Use `mockup.html` or the templates to refine brief, paths, atlas contract, and preview tool paths when more detail is needed.
8. Keep generated attempts in `generated/` and QA-passed files in `final/`.
9. Prepare manifests and animation preview tools for animated atlases.
10. Mark game integration readiness only after QA passes.

## Batch Folder

Use this structure unless the user asks otherwise:

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

Use `.agents/hooks/sprite-intake.ps1` for natural-language user requests. Use `.agents/hooks/new-batch.ps1` when a known batch id is already available.

## Required Rules

- When the user asks to make/draw/generate a sprite or image, infer a suitable batch id and output folder automatically instead of requiring a long setup prompt.
- For short natural requests, run `.agents/hooks/sprite-intake.ps1 -Request "<user request>"` and let it create the batch scaffold and `PROMPT.md`.
- If generation mode is unclear after intake, ask the Codex direct vs strict `gpt-image-2` vs setup-only question once. Use `.agents/hooks/generation-choice.ps1` for the standard wording.
- Use `.agents/hooks/symphony.ps1` as the local mini-Symphony status board for `output/*` batches. Use `-WriteReport` when a durable `output/SYMPHONY.md` handoff is useful.
- Make copy-ready prompts, not API calls.
- Require `gpt-image-2` in generation prompts.
- If a prompt was not produced by `mockup.html`, run `.agents/hooks/prompt-inject.ps1` before generation handoff.
- For Codex direct generation, do not claim the result is verified `gpt-image-2`; keep it in `generated/` until QA.
- Do not silently substitute another image model.
- Do not store API keys in markdown, HTML, JSON, scripts, or batch folders.
- Keep target game paths explicit when known; if unknown, use SpriteMake output paths and leave target game paths as placeholders.
- Do not hardcode temporary local source paths into reusable docs.
- Keep Contact Anchor separate from Y-axis baseline/source plane.
- Treat loose contact sheets as source/intermediate files, not final assets.
- Use animation preview tools for animated atlases.
- Do not copy final assets into game projects unless QA passes or the user explicitly asks.

## Templates

Prefer these root templates:

- `templates/folder-md-setup-template.md`
- `templates/batch-sprite-request-template.md`
- `templates/resource-request-template.md`
- `templates/sprite-atlas-template.md`
- `templates/asset-qa-checklist.md`
- `templates/animation-player-template.html`
- `templates/animation-manifest-template.json`

Read `references/workflow.md` when the task needs a fuller production checklist.

## Validation

Run `.agents/hooks/preflight.ps1` after changing project scaffolding, templates, skill files, or hooks.

