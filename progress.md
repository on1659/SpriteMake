Original prompt: "목업만들어보자"

## 2026-04-29

- Building a Lettuce Raid playable mockup from the selected stage background and existing character atlases.
- Current asset status:
  - Real background: `output/lettuce-raid/stage/stage-background-v1.png`
  - Real character atlases: `output/lettuce-raid/characters/players-atlas-v3.png`, `owner-atlas-v1.png`
  - Individual lettuce PNG atlas is not yet processed into the project, so the first mockup draws temporary lettuce sprites on canvas at runtime.
- Need verify with the web-game Playwright loop after creating the HTML.
- Created `output/lettuce-raid/mockup/lettuce-raid-playmockup.html` as the first playable site-card mockup.
- Rebuilt the selected stage PNGs from the valid Downloads source because the project copies had corrupted PNG headers and could not decode in Chromium/PIL.
- Current mockup uses the real restored stage background plus canvas-drawn lettuce and fallback canvas characters.
- Existing character atlas PNG files under `output/lettuce-raid/characters/` currently fail browser/PIL decoding (`naturalWidth: 0`); the mockup will automatically use those atlases later if valid PNGs are restored at the same paths.
- Verified with the develop-web-game Playwright loop:
  - `output/lettuce-raid/mockup/qa/playtest-20260429-195723/shot-7.png`
  - final state reached `mode: won`, `result: 성공`, `collected: 14`.
  - controls checked: start, pause, resume, reset, zoom in, hint; no console/page errors.

Next suggestions:
- Restore or regenerate valid player/owner atlases so the mockup can use the intended character sprites instead of fallback figures.
- Replace the temporary canvas lettuce with a sliced valid lettuce PNG/atlas when the individual lettuce asset is ready.
