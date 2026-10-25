# SpriteMake local Runner foundation

`asset_gate.py` makes final promotion a separate local action. It never calls an
image provider or stores a key.

Each asset needs a versioned contract and status record. The QA runner writes
the candidate and QA-report SHA-256 values. A human or signed local review flow
sets the required review statuses to `approved`. The gate checks every input is
still identical before atomically replacing the batch-local `final/` file.

```text
generated candidate -> automated QA -> visual review -> asset_gate promote -> final
```

Examples:

```text
python3 tools/runner/asset_gate.py validate --batch-root output/example --contract output/example/contracts/foo.json --status output/example/qa/asset-status.json
python3 tools/runner/asset_gate.py promote --batch-root output/example --contract output/example/contracts/foo.json --status output/example/qa/asset-status.json
```

`qa/asset-status.json` or `qa/asset-statuses.json` is the canonical input for
the Mini-Symphony dashboard. A failed validation rewrites only the status's
promotion block with blockers; it never creates or modifies `final/`.

## Shared PNG and animation inspection

`inspect_sprite.py` requires Pillow in the chosen Python environment. It reads
the asset contract, checks the PNG's exact canvas/grid/cell geometry and alpha,
and writes full/per-cell bboxes plus animation duplicate/diff/seam evidence.
It preserves the source image and writes reports only inside the batch's `qa/`.

```text
python3 tools/runner/inspect_sprite.py --batch-root output/example --contract output/example/contracts/foo.json --image output/example/generated/foo.png --output output/example/qa/foo-report.json --status output/example/qa/foo-status.json
```

The optional status output records candidate/report/contract hashes, declared
reference and curation input hashes, and pending human reviews. Re-running it
resets reviews; it never grants approval or promotes an image. A measurable QA
pass is separate from semantic placement and motion approval. Bbox bottoms do
not establish foot contact; duplicate/diff/seam metrics do not establish gait.
Halo, anatomy, style and other custom checks need the asset-specific verifier.
The existing adapted `file://` preview remains part of animation QA.

## Approval inputs

Contracts can declare `references: [{path, role, direction?}]` and
`qa.requiredInputs: [path]`, for example a curation sidecar or preview manifest.
These paths are relative to the batch and live in `source/`, `generated/`,
`manifests/` or `qa/`. The status binds them through
`qa.inputChecksums: [{path, sha256, role?}]` and binds the full contract bytes
through `qa.contractSha256`. Changed or missing inputs block promotion even
when the contract version is unchanged.

When a style review declares a reference or requires a comparison, record
`reviews.style.referenceSha256` and `reviews.style.comparisonSha256` against
the images actually reviewed. `reviews.placement.status` must be approved
when the contract requires placement review or lists `anchor`/`baseline` QA.
Animated contracts require `reviews.motion.required: true`; approval must
follow playback at the intended scale and FPS. Inspector-generated statuses
leave those reviews pending. A fresh review approves the unchanged exported
candidate, rather than a raw frame cache.

Old statuses without the new contract/input binding must be regenerated and
reviewed before their next promotion. Existing production files are not
migrated by these tools. See the updated skill workflow and QA checklist for
direction references, common scale and airborne-frame handling.

## Codex App Server capability spike

`codex-app-server.js` is a local stdio-only bridge for the official Codex App
Server protocol. The local GUI uses it only for Codex-managed account
connection and a sanitized account/rate-limit summary. It deliberately keeps
authentication inside Codex, redacts account credentials/identifiers from
normalized output, and declines all server-initiated approval requests. It
does not claim that image generation is available.

Run a read-only connection and rate-limit probe:

```text
node tools/runner/probe-app-server.js
```

The probe does not initiate login, create a thread, generate an image, or write
to a batch. The JSON schema emitted by the installed Codex CLI is kept under
`tools/runner/generated-schema/`; regenerate it when the CLI version changes
and rerun the bridge tests before enabling any image-capable path.

## Local batch-intake endpoint

While the local Symphony GUI server is running, `POST /api/batch-intake` accepts
only a natural-language `request`, optional safe `batchId`, and generation
`mode`. It creates the SpriteMake batch scaffold without running an image API,
storing a key, or accepting a filesystem path/command. It accepts loopback
requests only.

For a Claude Code session in this repository, use:

```text
node tools/runner/request-batch.js "create a rideable fire and ice dragon sprite"
```

The helper reads the current loopback URL from `output/SYMPHONY-GUI.json` and
posts the request; it does not need the caller to copy a port number.

## Offline PNG processing

For color variants, explicit alpha cleanup, frame extraction, upstream atlas
import and portable frame curation, use the [offline processing pipeline](../sprite_pipeline/README.md).
QA inputs also accept batch-local `contracts/` to bind the original authoring contract.
