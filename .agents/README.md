# SpriteMake Local Agent Setup

This folder contains project-local agent support files.

```text
.agents/
  README.md
  skills/
    spritemake-batch/
  hooks/
    preflight.ps1
    sprite-intake.ps1
    sprite-intake.config.json
    symphony.ps1
    symphony.config.json
    new-batch.ps1
    generation-choice.ps1
    generation-choice.config.json
    prompt-inject.ps1
    prompt-hook.config.json
  ../tools/
    symphony-gui/
```

## Skill

`skills/spritemake-batch/SKILL.md` describes how agents should set up SpriteMake batches.

This local skill is project scaffolding. If you want it to be auto-discovered globally, copy or install it into the Codex skills directory.

## Hooks

`hooks/preflight.ps1` checks that core docs/templates exist and catches obvious syntax/secret problems.

`hooks/sprite-intake.ps1` is the normal first step for short user requests. It captures the original request, infers `output/{name}-{timestamp}`, creates the batch scaffold, writes `PROMPT.md`, injects the strict `gpt-image-2` target, and defaults to keyless Codex direct generation unless another mode is chosen.

`hooks/symphony.ps1` scans `output/*` as a lightweight SpriteMake control plane, classifies batch states, and suggests the next production action. Use `-WriteReport` to write `output/SYMPHONY.md`.

`../start-symphony-gui.bat` starts the read-only Mini-Symphony web dashboard. The Node.js server chooses a free local port and writes the latest URL to `output/SYMPHONY-GUI.url`. The dashboard also writes `output/SYMPHONY-GUI.log` and streams the same scan/server events into the live log panel.

`hooks/new-batch.ps1` creates a standard `output/{batch}` scaffold.

`hooks/generation-choice.ps1` prints the standard choice prompt when the user asks to make an image but has not chosen Codex direct generation, strict external `gpt-image-2` generation, or setup-only work.

`hooks/prompt-inject.ps1` adds the required `gpt-image-2` generation target block to prompts that were not produced through `mockup.html`.

`hooks/prompt-hook.config.json` documents the intended Claude-style timing: before sending an external generation prompt.

These hooks are intentionally local and non-destructive.


