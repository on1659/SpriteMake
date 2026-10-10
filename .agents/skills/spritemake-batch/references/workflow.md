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

### Character reference sequence (when animating a character)

```text
Accepted base -> approved single-pose reference for each actual direction
-> matching state generation -> deterministic fixed-grid candidate
-> geometric inspection -> semantic placement/motion review -> promotion gate
```

1. Record the accepted base path and SHA-256. Reject cropped, wrong-style or
   identity-weak bases before deriving further references.
2. Approve exactly one single-pose reference per generated direction. A whole
   animation row is a timing reference, not the identity reference. If a pose is
   selected from a row, record its row/frame selection and source hash.
3. State prompts attach the matching approved direction reference for identity
   and facing. Optional gait sequences own timing/contact phases; layout guides
   own count, spacing and safe margins. A single peak walk/run pose must not
   substitute for an opposite-contact motion reference.
4. Record side-specific markings, equipment and handedness. Generate actual
   opposite views when these would flip incorrectly. Mirrored derivations need
   explicit approval and a recorded source/transform; never silently mirror.
5. A direction reference image is separate from the contact anchor coordinate
   and Y-axis baseline/source plane. Keep all three fields explicit.
6. Any edit, replacement or regeneration changes the reference generation.
   Invalidate dependent QA/reviews and regenerate affected states or explicitly
   review them against the new reference. A reused filename/frame index does
   not preserve approval; compare content hashes.

### Intermediate rows and final layout

Loose generated rows/contact sheets may be intermediate inputs in `generated/`.
Compose one intended frame into each declared final cell, with no empty cells,
gutters, outer padding or bleed. The final canvas, rows, columns, cell dimensions
and meanings remain the versioned runtime contract.

Use a common documented scale across related frames and directions. Do not
resize each silhouette independently to fill its cell. Preserve intentional
airborne displacement, crouches, squash/stretch and effects; aligning every
bottommost bbox pixel to the ground would erase intended motion. For airborne
frames, use the declared ground/source plane and semantic pose judgement.
Record frame offsets and transformations so the repack can be reproduced.

### Inspection and approval contract

`tools/runner/inspect_sprite.py` accepts `--batch-root`, `--contract`, `--image`
and `--output`, plus optional `--status`. It operates on batch-local inputs,
writes a geometry/evidence report and fingerprints, and never promotes files.
Use `generated/` for candidates and `qa/` for report/status outputs.

The contract declares `references: [{path, role, direction?}]` and
`qa.requiredInputs: [path]`. Include every accepted base/direction reference,
runtime manifest and selection/edit recipe used to compose the candidate.
Dependency paths are relative to the batch and confined to `source/`,
`generated/`, `manifests/` or `qa/`; do not point to external mutable files.
Copy external references into `source/` first.

Status records require `qa.contractSha256` and
`qa.inputChecksums: [{path, sha256, role?}]`, in addition to candidate/report
checksums and contract version. Even an unchanged version number cannot preserve
QA after the contract bytes change. Old approvals without these fingerprints
must be regenerated. A style review requiring a comparison/reference also
records `comparisonSha256` / `referenceSha256`; file existence is insufficient.
Record these fingerprints when approving the current inspected result.

Automatic inspection covers supported canvas/grid/cell/alpha/bbox tests and
emits duplicate-frame, frame-diff and loop-seam measurements when animations
are declared. Those numbers are evidence, not identity, motion or foot-contact
approval. `maximumHaloPixels` cannot be established by the common inspector;
counting alpha values 1..7 is not a halo measurement. A declared halo threshold
requires a manual/custom QA result and remains unverified until that exists.

Keep these review decisions separate:

| Review | Required judgement | Gate rule |
|---|---|---|
| Filename/content | Requested object and state semantics match | Approved when required by contract |
| Style | Identity, direction, asymmetric details, outline and lighting match references | Approved with comparison/reference fingerprints when declared |
| Placement | Contact point/source plane match intended runtime placement, including airborne frames | Required when `qa.required` includes `anchor` or `baseline`, or `reviews.placement.required` is true |
| Motion | Real motion, anatomy, contact phases, intentional duplicates, readability and loop/non-loop behaviour | `reviews.motion.required: true` for animated assets; explicit approval after watching playback |

Walk/run remain experimental until their motion review passes. A seamless image
diff or a stable bbox cannot prove a gait. Watch every frame and loop at intended
game scale; reject broken joints, identity drift, static bobbing and visible wrap
jumps. For non-loop gestures judge start/middle/end rather than forcing a loop.
Failed semantic motion requires regeneration or an explicitly reviewed sequence
change; slowing playback cannot turn a failure into a pass. Every new exported
candidate or changed dependency requires fresh QA and review.

For static assets leave `atlas.animations` empty and `reviews.motion.required`
false. For animated assets declare actual frame sequences, fps and loop intent,
then enable motion review. Custom/manual QA must resolve unsupported required
automatic measurements before `qa.status` can be `pass`. Geometric QA may pass
while semantic placement/motion reviews remain pending; inspection alone never
approves those reviews. Keep the adapted `file://` HTML preview and browser verification
as the required playback evidence; optional server tools do not replace it.

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


