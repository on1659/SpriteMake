# SpriteMake Local Runner + Web GUI Product / Technical Specification

- Status: draft for architecture review
- Owner: SpriteMake
- Target: a local-only workflow on the creator's own computer
- Non-goal: a hosted SaaS that receives or spends other users' ChatGPT credentials

## 1. Product decision

SpriteMake should become a **local production cockpit**, not a generic image
generator. A creator opens a browser UI, describes a sprite batch in normal
language, signs in to Codex with their own ChatGPT account, and lets a local
runner prepare and drive the production job. Every image attempt remains a
candidate until the existing QA and promotion gate accept it.

The user value is not "one more prompt box." It is removing the manual hops
between prompt, download, folder placement, atlas contract, QA, and review.
The product stays useful even when image generation is unavailable: it can
still create a complete batch, prompt, contract, and review checklist.

### Success criteria for v1

1. `start-spritemake.bat` opens a loopback-only UI and starts a local runner.
2. A user can connect their ChatGPT account through Codex-managed login; no API
   key/token is entered, returned to the UI, written to the repo, or put in a
   batch document.
3. A single batch request can produce a durable job record, a complete batch
   folder, and a visible job timeline.
4. If the connected Codex environment can produce an image, one resulting PNG
   is copied to that batch's `generated/` directory with a provenance record.
5. If image generation is unavailable, rejected, or rate-limited, the job says
   so plainly and still leaves the batch prompt ready for an external step.
6. Existing asset contracts, automated QA, human review, and checksum-bound
   atomic promotion remain the only path to `final/`.

### Explicit non-goals for v1

- Remote/public hosting, shared accounts, multi-user access, or a cloud queue.
- Asking for, scraping, proxying, exporting, or storing ChatGPT access tokens.
- Claiming that a ChatGPT subscription guarantees `gpt-image-2`, image-tool
  availability, image quota, or a particular output model.
- Automatically approving visual QA or writing approval states from the agent.
- Changing game-project assets directly.

## 2. Feasibility and product boundary

Codex App Server is an official integration surface for rich local clients. It
supports local stdio JSON-RPC, managed ChatGPT login, account state, and
ChatGPT rate-limit reads. The official documentation labels the App Server
command and its WebSocket transport experimental/unsupported for production;
v1 therefore uses **one child process with stdio only**, never exposes App
Server on a network port, pins and checks a tested CLI schema version, and
keeps the SpriteMake HTTP server on `127.0.0.1`. Stdio reduces network exposure;
it is not a production-support guarantee.

Official Codex image-generation documentation describes an interactive
`$imagegen` flow using built-in `gpt-image-2` and consuming ordinary Codex
usage limits. It does not promise that this tool is exposed to every arbitrary
App Server client turn or provide a stable PNG artifact-return contract. Treat
that App Server path as a capability to discover at runtime, not a promise in
the product UI. The implementation must run a deliberate capability spike
before advertising "generate" as available.

This makes the project viable in two increments:

| Increment | What it proves | User-facing promise |
| --- | --- | --- |
| A: local connection | Codex-managed login, account/rate-limit state, browser job UI, intake and streamed agent state | "Connect your account and prepare a production batch." |
| B: image capability | Whether this installed Codex version/account can produce and save a PNG in this flow | "Generate candidate image" only when the probe succeeds; otherwise "prepare prompt." |

Go/no-go: build Increment A. Do not commit to an image-generation marketing
claim until Increment B has succeeded on a clean logged-in machine and has
been repeated after a Codex update.

## 3. Architecture

```text
Browser (127.0.0.1)
  ├─ UI requests: /api/account, /api/login, /api/jobs
  └─ SSE job/account events
          │ no credentials in payloads
SpriteMake Node server (127.0.0.1 only)
  ├─ local API validation, single-job queue, audit log
  ├─ Batch service: intake / contracts / output path validation
  └─ Codex bridge (child process, stdio JSON-RPC only)
          │ managed OAuth and tokens stay inside Codex
Codex App Server
  ├─ account/login/start, account/read, account/rateLimits/read
  ├─ thread/start, turn/start, turn/interrupt
  └─ streamed lifecycle notifications
          │
Batch filesystem
  output/{batch}/BATCH.md, PROMPT.md, contracts/, generated/, qa/, final/
          │
Existing QA and `asset_gate.py`
```

### Components and ownership

| Component | Responsibility | Must never do |
| --- | --- | --- |
| Browser UI | collect plain-language request; show account summary and job state | receive/persist credentials or an OAuth URL; decide QA approval |
| SpriteMake server | validate localhost requests; own job lifecycle; write sanitized job/provenance logs; bridge JSON-RPC | bind externally by default; run arbitrary shell supplied by UI |
| Codex bridge | start/stop one `codex app-server`; perform initialization; correlate JSON-RPC responses/events; redact errors | expose the App Server port/stdio stream to the browser |
| Batch service | create only validated child folders below `output/`; exclusively write deterministic request/contract/status artifacts | write outside project root or `final/` |
| Generation adapter | run a constrained agent in an isolated staging workspace and collect only staged candidate files | infer success from prose, write batch docs/status/QA/final, or let the agent self-approve |
| QA/promotion | retain existing checksum-bound candidate → QA → human-review → promotion gate | be bypassed by a completed generation job or trusted as a security sandbox |

## 4. Data model and state machine

All runtime records live under `output/.runner/`, are ignored by Git, and are
safe to delete after a job is finished. Batch artifacts remain under the normal
batch directory.

```text
created
  -> awaiting_login | queued | prepared_external
  -> preparing_batch
  -> running_agent
  -> collecting_candidate
  -> qa_needed
  -> completed

awaiting_login -> cancelled | failed
queued/running_agent/collecting_candidate -> failed | cancelled | interrupted
preparing_batch -> prepared_external (image unsupported/rate-limited) | failed
prepared_external -> completed (the request packet is ready; no candidate exists)
qa_needed -> completed (only after the existing promotion process; never automatic)
```

Required job fields:

```json
{
  "id": "job_uuid",
  "batchId": "validated-slug",
  "createdAt": "ISO-8601",
  "state": "awaiting_login",
  "codexThreadId": null,
  "turnId": null,
  "generationCapability": "unknown|available|unavailable",
  "candidate": { "path": null, "sha256": null, "provenance": null },
  "error": null
}
```

`completed` means the runner's work is terminal, not that the sprite has passed
QA. `qa_needed` is the only successful image-candidate exit. `prepared_external`
means the packet/prompt is ready but no candidate was generated. `interrupted`
means a child process or Runner restart made the result ambiguous; it is never
automatically retried or imported.

Only safe metadata is retained. It may include plan type and percentage/rate
limit windows supplied by App Server, but never email address, auth URL query
parameters, raw tokens, request headers, or App Server raw traffic.

## 5. API contract (v1)

On initial UI load the loopback server sets a per-launch random `HttpOnly`,
`SameSite=Strict`, path-scoped session cookie. Every `/api/*` route and SSE
connection requires that cookie and the exact loopback Host; state-changing
requests additionally require `POST`, JSON content type, and the exact
same-origin `Origin`. The cookie is never exposed to JavaScript, logs, or
batch files. The server rejects unknown methods and bodies over a small limit.

| Endpoint | Action | Response excludes |
| --- | --- | --- |
| `GET /api/health` | version and loopback safety state | paths/secrets |
| `GET /api/account` | normalized connection / plan / rate-limit summary | email, token, auth URL |
| `POST /api/login` | start managed `chatgpt` login; the local server opens the one-time login URL itself | credentials and OAuth URL |
| `POST /api/logout` | call App Server account logout | auth internals |
| `GET /api/jobs` | sanitized job list | prompt secrets, raw model output |
| `POST /api/jobs` | validate request and enqueue one batch job | arbitrary filesystem path |
| `POST /api/jobs/:id/cancel` | interrupt active turn or cancel queued job | process handles |
| `GET /api/events` | SSE normalized account/job events | raw JSON-RPC messages |

`POST /api/jobs` accepts only `request`, optional visual/reference notes, a
generated/validated batch slug, and a client-generated idempotency key. The
browser cannot set an output directory, command, model name, QA result, or
promotion state. Reusing an idempotency key returns the original job rather
than enqueuing another one.

## 6. Agent execution contract

The Node batch service, not the agent, creates all `BATCH.md`, prompt,
contract, status, QA, and final-path artifacts. The agent gets a fixed, short
instruction and a **separate staging workspace**. Its CWD and actual writable
root must be the staging workspace only; it must not receive the batch root as
a writable root. The process must use a restrictive Codex sandbox policy, not
inherit a user's `danger-full-access` configuration. It must:

1. use the prebuilt, read-only request packet and record generation uncertainty
   only in a staging result manifest;
2. attempt image generation only when its advertised capabilities permit it;
3. report an exact staged candidate path instead of declaring it final;
4. never write batch documentation, contracts, QA/status/approval fields,
   `final/`, or game-project paths.

After the turn completes, the Node service verifies that the reported/observed
candidate is a `.png`, resolves inside the staging root (including realpath
checks), applies size limits, hashes it, atomically moves it to `generated/`,
and writes provenance plus a new unapproved status record. A missing file is a
failed job even if the agent says "done." A candidate then enters the existing
QA workflow.

The existing gate protects candidate integrity after a trusted review has
created status/approval records; it is not a sandbox. In particular, a local
agent that can edit those records would collapse the review boundary. The
runner therefore treats the batch service and human reviewer as the only
writers of contract/status/review records.

Initial concurrency is exactly one active turn. Queueing, cancellation,
reconnect after child-process death, a 15-minute no-event watchdog, a 20-minute
whole-turn ceiling, and zero automatic retries are mandatory before broad
usage. A cancelled or timed-out turn can leave staged files behind, but the
importer ignores/removes them only after a human-visible terminal state; it
never imports a late PNG.

App Server may send approval or user-input JSON-RPC requests, not just responses
and notifications. v1 supports no automatic approval. It explicitly declines
unsupported requests and records a sanitized reason on the job. A later
feature may present only a narrowly scoped, human-confirmed approval UI after
the Sandbox policy is independently proven.

## 7. Security requirements

1. Bind only to `127.0.0.1` / `::1`; remove the current public host override
   for the runner mode. A separate, explicit future product decision is
   required for LAN access.
2. Use App Server stdio. Do not start its experimental WebSocket listener.
3. Never pass credentials on a command line, store them in the repo, return
   them to the browser, or append them to `SYMPHONY-GUI.log`.
4. Treat every agent-produced filename, event, and error as untrusted. Redact
   URLs and common secret patterns before persistence or SSE broadcast.
5. Validate normalised paths plus symlink/realpath containment for all output
   operations. The UI's strings are never filesystem paths.
6. The local UI is still a privilege boundary: protect state-changing routes
   from cross-site requests, require the launch capability token, and set a
   restrictive CSP.
7. Logout must call the managed App Server logout API; SpriteMake deletes only
   its own runtime state and does not delete Codex credential storage directly.
8. Batch preview HTML is never served with the runner UI's authenticated
   origin. Keep the current PNG-only `/assets/` behaviour; open preview tools
   via `file://` or a sandboxed iframe without `allow-same-origin`.
9. Candidate execution is enabled only when the installed App Server version
   can enforce a restrictive staging-only sandbox. If that cannot be proven,
   the runner remains in connection/preparation mode and does not start an
   agent turn that could write production folders.

## 8. Delivery plan and acceptance tests

### Slice 0 — capability spike (time-boxed)

Create a disposable local test program that starts `codex app-server` over
stdio, initializes it, reads account status, starts managed login if needed,
and exercises a minimal thread/turn in a restrictive test workspace. Generate
schemas from the installed CLI version. Confirm the actual event names and
whether an image capability is available. Do not use or log private
credentials. Result: a checked-in protocol adapter test fixture with redacted
transcripts, or a documented unsupported result. Failure to support
login/protocol blocks the runner; failure to produce and recover a real PNG
blocks only the image-capable slice and leaves the connection/preparation slice
viable.

### Slice 1 — secure runner bridge

Add a `CodexBridge` module, controlled child lifecycle, redaction, event
normalization, account endpoint, login/logout, and one active-job queue. Tests
use a fake JSONL App Server process; they must not require a real account.

### Slice 2 — GUI control plane

Upgrade the current read-only dashboard with account connection state, a
natural-language request panel, queue/cancel controls, and accessible job
states. Retain the existing status board as a separate panel.

### Slice 3 — batch and candidate handoff

Create the batch through existing templates; execute the constrained turn;
verify/atomically import a candidate to `generated/`; create an unapproved
asset-status record; then surface the QA link. The image-capable branch ships
only if Slice 0 proves it. Otherwise ship "prepare in browser" as an honest
fallback.

### Must-pass acceptance tests

- A fresh local user can launch the UI, authenticate through an official
  managed ChatGPT flow, refresh, log out, and never see a key/token.
- The browser cannot request arbitrary commands/paths, and a cross-origin POST
  cannot enqueue a job.
- Fake App Server login/account/turn events produce correct UI state and are
  recoverable after bridge restart.
- A failed/timeout/cancelled agent job cannot leave an untracked PNG in
  `final/`.
- An imported candidate has SHA-256 provenance, starts as unapproved, appears
  in the existing QA flow, and requires `asset_gate.py` to reach `final/`.
- No release claim says the subscription guarantees image generation or
  `gpt-image-2` unless Slice 0 establishes the exact supported contract.

## 9. Open decisions to resolve during Slice 0

1. Which installed Codex App Server schema/version is supported, and how will
   we fail fast if it changes?
2. Does the selected ChatGPT plan and installed Codex version expose an image
   tool in App Server turns? If yes, what is the file-output contract? If not,
   does the v1 UI stop at a copy-ready prompt or hand off to the desktop app?
3. Can managed ChatGPT login use the desired hosted callback reliably on a
   Windows machine with a locked-down browser? Use device code as fallback.
4. Is job history persistent across launches, or is an in-memory queue with
   durable terminal records sufficient for v1? Default: durable terminal
   records; active jobs become `interrupted` on restart.

## 10. Source basis

This design is constrained by the official [Codex App Server documentation](https://developers.openai.com/docs/app-server): it supports rich-client
authentication, thread/turn streaming, managed ChatGPT login, and rate-limit
reads; its default local transport is stdio. The official [Codex image-generation documentation](https://learn.chatgpt.com/docs/image-generation)
describes `$imagegen`, built-in `gpt-image-2`, and Codex usage consumption.
Neither source establishes a guaranteed image-artifact path for this custom
client, so the capability spike remains a release gate.
