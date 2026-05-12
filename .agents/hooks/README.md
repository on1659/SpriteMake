# SpriteMake Hooks

Local helper scripts for SpriteMake agents.

## preflight.ps1

Run after editing core docs, templates, skill files, hook files, or HTML tools.

```powershell
.\.agents\hooks\preflight.ps1
```

Checks:

- required project files exist
- required templates exist
- animation manifest template parses as JSON
- HTML script blocks parse with Node when Node is available
- mini-Symphony scan works on a temporary batch
- obvious API key patterns are not present

## symphony.ps1

Scan `output/*` as a lightweight SpriteMake control plane.

```powershell
.\.agents\hooks\symphony.ps1
```

Write a persistent board report:

```powershell
.\.agents\hooks\symphony.ps1 -WriteReport
```

JSON output for automation:

```powershell
.\.agents\hooks\symphony.ps1 -Json
```

Common states:

- `needs-scaffold`
- `needs-prompt`
- `needs-prompt-inject`
- `needs-refine`
- `prompt-ready`
- `qa-needed`
- `needs-regeneration`
- `mixed-review`
- `final-review`
- `final-candidate`

The hook only reads batch docs/assets and optionally writes `output/SYMPHONY.md`. It does not call image APIs and does not move assets into `final/`.

## Mini-Symphony GUI

Start the browser dashboard from the project root:

```powershell
.\start-symphony-gui.bat
```

The server chooses a free local port automatically and writes:

```text
output/SYMPHONY-GUI.url
output/SYMPHONY-GUI.json
output/SYMPHONY-GUI.log
```

The GUI is read-only. Commands still happen in Codex chat or PowerShell. The node flow and live log panels show the current scan node, active batch state, blockers, and server events as they happen.

## new-batch.ps1

Create a new batch folder scaffold.

```powershell
.\.agents\hooks\new-batch.ps1 -BatchId demo-feature
```

If `-BatchId` is omitted, pass `-UserRequest` and the script infers a safe name with a timestamp.

```powershell
.\.agents\hooks\new-batch.ps1 -UserRequest "dragon sprite with fire and ice variants"
```

Optional:

```powershell
.\.agents\hooks\new-batch.ps1 -BatchId demo-feature -GameProjectRoot "D:\Work\SomeGame"
```

## sprite-intake.ps1

Use this for the normal user flow: a short natural-language sprite request comes in and SpriteMake creates the batch scaffold automatically.

```powershell
.\.agents\hooks\sprite-intake.ps1 -Request "드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 해."
```

This creates:

- `output/{inferred-name}-{yyyyMMdd-HHmmss}/`
- `BATCH.md`
- `REQUESTS.md`
- `PROMPT.md`
- `MANIFEST.md`
- `QA.md`
- `prompts/`, `generated/`, `source/`, `manifests/`, `tools/`, `qa/`, `final/`

It also writes the strict `gpt-image-2` generation target and SpriteMake output paths into `PROMPT.md`.

If `-Mode` is omitted, it defaults to keyless Codex direct generation:

```text
codex
```

Use `-Mode gpt-image-2` for strict external generation, `-Mode codex-setup` for setup-only work, or `-Mode pending` to print the standard choice question.

## prompt-inject.ps1

Use this before sending a prompt to a generation step when the prompt was not produced by `mockup.html`.

```powershell
"Create a sprite atlas..." | .\.agents\hooks\prompt-inject.ps1
```

Or rewrite a file:

```powershell
.\.agents\hooks\prompt-inject.ps1 -InputPath .\output\demo\REQUESTS.md -OutputPath .\output\demo\REQUESTS.injected.md
```

Check only:

```powershell
.\.agents\hooks\prompt-inject.ps1 -InputPath .\output\demo\REQUESTS.md -CheckOnly
```

This hook injects the required `gpt-image-2` `Generation Target` block. It is a SpriteMake-local helper; Codex must call it or use templates/mockup that already include the same block.

## generation-choice.ps1

Use this when the user asks to make/draw/generate a sprite or image but does not say whether they want Codex direct generation, strict external `gpt-image-2` generation, or setup-only work.

```powershell
.\.agents\hooks\generation-choice.ps1
```

Short version:

```powershell
.\.agents\hooks\generation-choice.ps1 -Short
```

This prints the standard Korean choice prompt:

- Codex direct: generate with Codex image tooling without API keys; model is not forced or verified as `gpt-image-2`
- Strict `gpt-image-2`: prepare the prompt, then the user directly enters it into ChatGPT web or another external generation environment
- Codex setup-only: folder/MD/prompt/manifest/QA/preview setup only


