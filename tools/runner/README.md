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
