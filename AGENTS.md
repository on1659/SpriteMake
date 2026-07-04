# AGENTS.md

## Project Identity

SpriteMake is a sprite production setup workspace.

It is not an image-generation API client. Do not store API keys here.

Default image generation requests should target OpenAI `gpt-image-2`, but SpriteMake only records that requirement in prompts/docs. It does not call the API directly.

For keyless convenience, Codex may use its built-in image generation tool after the batch prompt is prepared. That path does not use API keys, but it also cannot force or verify `gpt-image-2`. Treat Codex-generated images as unverified attempts under `generated/` until QA passes.

The purpose is to prepare game-usable sprite batches through:

- folder setup
- markdown request documents
- copy-ready prompts
- strict atlas contracts
- manifests
- QA reports
- animation preview tools

The final goal is always a usable game sprite, not a pretty image.

Users should be able to make short natural-language requests such as:

```text
드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 하고 사람이 탈 수 있을 정도로 커야 해.
```

Do not require the user to paste SpriteMake boilerplate. Infer the batch name, output folder, timestamp, and default prompt structure automatically.

## Read First

Before changing or creating batch work, read:

- `README.md`
- `USAGE.md`
- `HANDOFF.md`

For templates, prefer:

- `templates/folder-md-setup-template.md`
- `templates/batch-sprite-request-template.md`
- `templates/resource-request-template.md`
- `templates/sprite-atlas-template.md`
- `templates/asset-qa-checklist.md`
- `templates/animation-player-template.html`
- `templates/animation-manifest-template.json`

## Core Workflow

Use this flow for sprite work:

```text
Batch request
-> per-asset brief
-> runtime contract
-> generated PNG from Codex direct tool or external process
-> manifest
-> animation preview tool
-> QA
-> game integration
```

SpriteMake prepares the request and verification structure. Codex's built-in image tool, external tools, or people may generate the actual PNG.

## Mini-Symphony Workflow

SpriteMake uses a local, lightweight Symphony-style control plane:

```text
output/* batch folders
-> .agents/hooks/symphony.ps1 scan
-> next production action
-> human review when final-candidate
```

Use `.agents/hooks/symphony.ps1` to inspect existing batch states. Use `-WriteReport` to write `output/SYMPHONY.md`.

The hook may classify batches as:

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

This is a status and handoff layer only. It must not call image APIs, store API keys, or move unverified PNGs into `final/`.

## Required Output For Usable Sprites

Every production sprite batch should aim to produce:

- strict atlas PNG or static PNG
- target asset path
- runtime slicing contract
- manifest JSON or manifest notes
- contact anchor
- Y-axis baseline or source plane
- alpha bbox report
- per-cell bbox report for atlases
- animation preview HTML tool for animated atlases
- QA notes

## Batch Folder Shape

Use this shape unless the user asks for a different one:

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

Do not put unverified generated images directly into `final/`.

## No API Key Rule

Never add API keys to:

- markdown files
- HTML files
- JSON files
- scripts
- batch folders

Do not write instructions that require SpriteMake itself to call image-generation APIs.

It is fine to write prompts for external generation tools. Those prompts should require `gpt-image-2` unless the user explicitly says otherwise.

For Codex direct generation, keep the same sprite contract, but do not claim the generated image is verified `gpt-image-2`.

When a prompt was not produced by `mockup.html` or a template that already includes `Generation Target`, run `.agents/hooks/prompt-inject.ps1` before handing it to a generation step.

## Generation Path Choice

When the user asks to make, draw, generate, or create a sprite/image and does not clearly choose a generation path, default to the keyless Codex path:

1. First capture the natural-language request with `.agents/hooks/sprite-intake.ps1`.
2. Let the hook infer a safe `output/{name}-{yyyyMMdd-HHmmss}/` folder and write `PROMPT.md`.
3. Use Codex direct image generation unless the user asks for strict `gpt-image-2` or setup-only work.

Example:

```powershell
.\.agents\hooks\sprite-intake.ps1 -Request "드래곤 스프라이트 그려줘. 불속성과 얼음속성 두 종류가 있어야 하고 사람이 탈 수 있을 정도로 커야 해."
```

If a choice is still needed, ask:

```text
생성 방식부터 정할게요.

1. Codex로 바로 생성
   - API key 없이 이 Codex 세션의 이미지 생성 기능으로 바로 시도합니다.
   - 모델을 gpt-image-2로 강제하거나 검증하지는 못합니다.
   - 결과물은 generated/의 검수 대상 시안으로 보고, QA 통과 전에는 final/로 옮기지 않습니다.

2. gpt-image-2 엄격 생성
   - 제가 gpt-image-2용 프롬프트를 만들어드립니다.
   - 실제 이미지는 ChatGPT 웹이나 API key가 있는 외부 생성 화면에 직접 입력해야 합니다.
   - 이 프로젝트에는 API key를 저장하거나 사용하지 않습니다.

3. Codex로 세팅만
   - 폴더, MD 요청서, 프롬프트, manifest, QA, preview tool만 세팅합니다.
   - 실제 이미지는 생성하지 않습니다.

어느 쪽으로 할까요?
```

You may print the same text with `.agents/hooks/generation-choice.ps1`.

If the user chooses Codex direct, prepare the batch artifacts, use the prepared prompt with Codex image generation, and keep the result in or referenced from `generated/` for QA. If the user chooses strict `gpt-image-2`, use `PROMPT.md` as the copy-ready prompt and explain that they must paste it into ChatGPT web or another external generation environment. If the user chooses Codex setup-only, stop after the SpriteMake artifacts are ready.

## Paths And Ownership

Use SpriteMake for:

- reusable sprite request rules
- batch setup
- prompt documents
- generated attempts before QA
- manifests and preview tools for verification
- QA reports

Use the actual game project for:

- final production assets
- game-specific integration
- runtime code changes
- production-specific docs

Only copy or move final PNG assets into a game project after QA passes, unless the user explicitly asks otherwise.

Do not hardcode temporary local source paths into reusable templates or docs.

## Anchor And Y-Axis Rules

Contact Anchor and Y-Axis Alignment are not the same thing.

Anchor:

- the point code uses to place the sprite
- examples: foot contact, tile contact, impact center, item attach point

Y-axis baseline/source plane:

- the local Y line that must not drift across frames or related rows
- examples: character foot baseline, tile plane, crack/break source plane

Always keep both explicit in prompts, manifests, and QA notes.

## Strict Atlas Rules

For sprite atlases, always specify:

- final canvas size
- columns and rows
- cell size
- column boundaries
- row boundaries
- row meanings
- column meanings
- no gutters
- no outer padding outside the exact canvas
- transparent padding only inside fixed cells

Do not accept loose contact sheets as final assets.

## Animation Preview Tool

Animated atlases should have a local HTML preview tool.

Use `templates/animation-player-template.html` as the starting point.

Do not hand the template path to the user as the actual preview for a sprite batch. The template is intentionally empty. For real QA, hand off the adapted batch file:

```text
output/{batch}/tools/animation-preview.html
```

Preview tools must be usable by double-clicking the HTML file.

Rules:

- Do not require a local HTTP server just to inspect a generated sprite.
- The adapted tool must work under `file://` with no external network, API key, or app server.
- For `file://` mode, embed or otherwise inline the preview manifest and the current PNG candidates as data URLs when browser security would block `fetch()` or canvas pixel reads.
- For local HTTP/server mode, prefer project-relative manifest and image paths so regenerated PNG files are read from disk.
- Auto-load the default manifest on page open; do not require the user to press `Load` before seeing the first sheet.
- Keep a manual `Load` button for alternate manifests.
- Verify with a real browser that `file://.../animation-preview.html` reaches `ready: true`, shows a nonblank canvas, has no console errors, and does not show `pixel read blocked on file://` for alpha bbox.

The preview tool should verify:

- manifest loading
- image loading
- sheet switching
- animation switching
- FPS and scale controls
- full sheet grid
- selected frame bounds
- contact anchor
- Y-axis baseline/source plane
- image size and cell size
- alpha bbox where possible

Use `templates/animation-manifest-template.json` as the manifest starter.

## QA Rules

Use `templates/asset-qa-checklist.md`.

At minimum, check:

- final size
- grid divisibility
- cell size
- each cell has one intended frame
- no frame bleeds into neighboring cells
- transparent corners
- full alpha bbox
- per-cell alpha bbox
- anchor correctness
- Y-axis baseline/source plane stability
- animation preview tool playback

If QA fails, keep the file in `generated/` or mark it as needing repack/regeneration. Do not treat it as final.

## When The User Asks For A New Sprite Batch

Do this:

1. Create the batch folder under `output/{game-or-feature}/`.
2. Create `BATCH.md`, `REQUESTS.md`, `MANIFEST.md`, and `QA.md`.
3. Use the batch and resource templates.
4. If the asset is animated, prepare manifest notes and an animation preview tool path.
5. Make copy-ready prompts requiring `gpt-image-2` for strict external generation, not API calls.
6. For Codex direct generation, document that the model is unverified and keep outputs in `generated/` until QA.
7. Keep target game paths explicit.

## When The User Provides Generated PNGs

Do this:

1. Put or reference them under the batch `generated/` area.
2. Inspect size, alpha, grid, cell boundaries, and bbox.
3. Create or update manifest JSON.
4. Copy/adapt the animation preview tool if needed.
5. Write QA results.
6. Mark files as `final/` only after passing QA.

## Tone Of Work

Prefer concrete production artifacts over abstract advice.

If a request is underspecified, create the folder/MD scaffolding with clear placeholders rather than waiting on every detail.

If a detail affects runtime placement, call it out explicitly in the request and QA docs.


