# SpriteMake Mini-Symphony Workflow

This file describes the lightweight Symphony-style orchestration used in this repo.

SpriteMake does not need a large external orchestration service for its current shape. The local control plane is the `output/*` folder: each batch folder is treated like a ticket, and `.agents/hooks/symphony.ps1` scans those folders to decide the next production action.

## Control Plane

```text
output/{batch}/
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

The batch folder is the unit of work. Agents should update the batch docs and QA notes instead of relying on conversation memory.

## Commands

Create a batch from a natural-language request:

```powershell
.\.agents\hooks\sprite-intake.ps1 -Request "드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 해."
```

Scan the SpriteMake board:

```powershell
.\.agents\hooks\symphony.ps1
```

Write a persistent status report:

```powershell
.\.agents\hooks\symphony.ps1 -WriteReport
```

Write JSON for another runner:

```powershell
.\.agents\hooks\symphony.ps1 -Json
```

## States

Use these states when thinking about batch work:

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

State meanings:

- `needs-scaffold`: required SpriteMake docs or folders are missing.
- `needs-prompt`: `PROMPT.md` is missing or empty.
- `needs-prompt-inject`: `PROMPT.md` exists but lacks the required `gpt-image-2` generation target.
- `needs-refine`: target path, grid/cell, contact anchor, Y-axis baseline/source plane, or placeholder fields need attention.
- `prompt-ready`: the prompt can be used with Codex direct generation for keyless convenience, or in an external `gpt-image-2` environment for strict model control; SpriteMake still does not call the API.
- `qa-needed`: generated PNGs exist under `generated/` and need inspection.
- `needs-regeneration`: QA records a failure; keep attempts in `generated/`.
- `mixed-review`: `final/` contains PNGs but QA also records failures.
- `final-review`: final PNGs exist but QA pass notes need to be explicit.
- `final-candidate`: QA indicates pass/ready status and assets may be reviewed for game integration.

## Agent Policy

1. Start with `AGENTS.md`, `README.md`, `USAGE.md`, and `HANDOFF.md`.
2. For short sprite/image requests, run `sprite-intake.ps1` first.
3. Run `symphony.ps1` after intake, after receiving PNGs, and before handoff.
4. Keep raw generated attempts under `generated/`.
5. Put assets in `final/` only after QA passes.
6. Do not write API keys or direct image API calls into this repo.
7. Keep contact anchor and Y-axis baseline/source plane separate in prompts, manifests, and QA notes.

## Human Handoff

A useful handoff should include:

- batch path
- current mini-Symphony state
- copy-ready prompt path
- generated PNG path, if any
- manifest path, if any
- preview tool path, if any
- QA result and blockers
- whether the asset is a final candidate for the game project
