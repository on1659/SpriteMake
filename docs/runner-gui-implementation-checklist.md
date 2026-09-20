# SpriteMake Local Runner Implementation Checklist

This checklist turns the reviewed specification into small, testable work. It
does not authorize a claim that subscription-based image generation is
available until the capability spike passes.

## Gate 0 — prove the integration boundary

- [ ] Generate App Server schemas from the locally installed `codex` binary;
      commit only schemas/test fixtures, never credentials.
- [ ] Build a Node JSONL test client for `initialize`, `account/read`, and
      `account/rateLimits/read`.
- [ ] Implement managed login (`chatgpt`, with device-code fallback); the
      runner opens the one-time OAuth URL locally and asserts that neither URL
      nor token is persisted or sent to the browser.
- [ ] Handle every App Server server-initiated approval/user-input request:
      v1 explicitly declines it with a sanitized job error; it never approves
      filesystem/network work automatically.
- [ ] Start a harmless thread/turn in a temp cwd and capture a redacted event
      map.
- [ ] Record image-tool availability as `available` or `unavailable` with the
      exact installed CLI version. Success requires a real PNG generated and
      recovered into staging, not a tool name. Protocol/login failure stops the
      runner; image-tool failure only disables image generation and leaves
      preparation mode available. Re-probe after CLI/account/config changes.

## Gate 1 — local security baseline

- [ ] Create a dedicated runner entry point; it binds loopback only and
      generates an `HttpOnly`, `SameSite=Strict` per-launch session cookie.
- [ ] Require the session for all `/api/*` and SSE routes; add strict method,
      Host, Origin, content-type, body-size, and CSP checks.
- [ ] Do not reuse `SPRITEMAKE_GUI_HOST` for runner mode.
- [ ] Create redaction tests for tokens, auth URLs, cookies, headers, and
      account email before log/SSE persistence.
- [ ] Test path and symlink escape rejection for staging and candidate import.

## Gate 2 — bridge and job state

- [ ] Implement `CodexBridge` around one stdio child process with request IDs,
      timeout, restart handling, and normalized notifications.
- [ ] Implement an in-memory single-worker queue plus durable sanitized job
      records under ignored `output/.runner/`.
- [ ] Support start, cancellation (`turn/interrupt`), timeout, child death,
      and restart-as-interrupted. Add one idempotency key per job submission,
      a 15-minute no-event watchdog, 20-minute whole-turn limit, and zero
      automatic retries.
- [ ] Test all of the above against a fake JSONL child process.

## Gate 3 — browser controls

- [ ] Account card: disconnected, connecting, connected (plan/rate window),
      rate-limited, error. Do not display account email by default.
- [ ] Request panel: natural-language request and optional batch slug only.
- [ ] Job card: prepare, queued, running, candidate/QA-needed, failed,
      cancelled. Include clear image-capability uncertainty.
- [ ] Keep existing Symphony dashboard and asset preview functionality intact.

## Gate 4 — batch handoff

- [ ] Reuse intake/template logic through a controlled service, not arbitrary
      user-provided PowerShell arguments.
- [ ] Have the batch service exclusively create docs, contracts, status, and
      QA records. Do not grant the agent a writable batch root.
- [ ] Restrict Codex agent cwd and actual sandbox writable root to an isolated
      staging area; reject any inherited `danger-full-access` policy.
- [ ] Test that an agent cannot write `final/`, `qa/`, contracts, `.runner/`,
      or the batch root; treat the existing promotion gate as integrity control,
      not a sandbox.
- [ ] Verify imported PNG content, realpath containment, size, SHA-256, and
      provenance before moving atomically into `generated/`.
- [ ] Create an unapproved `qa/asset-status*.json`; invoke existing QA and
      promotion gate without bypass.
- [ ] Add end-to-end fake-agent tests: PNG, no PNG, invalid path, cancelled,
      timeout, and agent tries to write `final/`.

## Release wording

Allowed: “Connects to locally managed Codex/ChatGPT login and prepares sprite
production jobs without storing an API key.”

Forbidden until verified: “Works with every ChatGPT subscription,” “uses
gpt-image-2,” or “always generates images from the web UI.”
