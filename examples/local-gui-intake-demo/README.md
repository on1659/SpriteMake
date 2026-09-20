# Local GUI Intake Demo

This is a commit-safe showcase of the local SpriteMake GUI flow. It contains a
small, inspectable batch brief and contract, but no user artwork, account data,
API keys, or generated PNGs.

## What a user does

1. Double-click `start-symphony-gui_mac.command` on macOS (or run
   `start-symphony-gui.sh`).
2. Open the local browser page and connect the existing Codex/ChatGPT account.
   The local runner asks the official Codex CLI to handle login; this repository
   never saves an API key or an account token.
3. Enter a short production request, for example:

   ```text
   불과 얼음 속성의 탑승 가능한 드래곤 스프라이트를 만들어줘.
   ```

4. The GUI creates an isolated timestamped folder under `output/` with the
   same artifacts demonstrated here. Generation attempts remain in
   `generated/` until QA and explicit promotion succeed.

## What this demo proves

| Production concern | Demonstrated artifact |
| --- | --- |
| Natural-language intake | [PROMPT.md](PROMPT.md) |
| Runtime placement contract | [contracts/dragon-rider.json](contracts/dragon-rider.json) |
| Strict atlas request | [REQUESTS.md](REQUESTS.md) |
| QA-before-final rule | [QA.md](QA.md) |

`final/` is deliberately empty: a clean repository example must not pretend a
generated image passed visual and technical QA.
