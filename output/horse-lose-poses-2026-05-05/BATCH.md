# Horse Lose Poses Batch

- Batch ID: horse-lose-poses-2026-05-05
- Source of truth: D:\Work\LAMDiceBot\docs\spritemake-request\2026-05-05-horse-lose-poses.md
- Game project: LAMDiceBot horse-race
- Game project root: D:\Work\LAMDiceBot
- Required image model: gpt-image-2
- Generation mode: strict external generation only; Codex direct generation is intentionally not used.
- Target output root after QA: D:\Work\LAMDiceBot\assets\horse-race\sprites\lose\
- Batch folder: D:\Work\vibe\SpriteMake\output\horse-lose-poses-2026-05-05\

## Scope

Create 15 lose-state sprite atlases for horse-race vehicles. Each atlas is exactly 120x45 px, 2 horizontal frames, with 60x45 cells. The local contract uses contact anchor x=30, y=45 and Y baseline y=45 for every frame.

## Priority Order

- Phase 1: horse, rabbit, turtle, dinosaur, knight
- Phase 2: car, rocket, bird, ninja
- Phase 3: boat, bicycle, scooter, helicopter, eagle, crab

## Batch Status

- Prompts: prepared for strict gpt-image-2 external generation.
- Generated SVG atlases: prepared under generated/{vehicleId}-lose.svg for LAMDiceBot-style visual review.
- Generated PNGs: pending from the original strict gpt-image-2 raster request.
- Manifests: prepared and currently point at ../generated/{vehicleId}-lose.png for QA preview.
- Preview HTML tools: prepared from templates/animation-player-template.html.
- Batch preview tool: tools/all-lose-preview.html shows all 15 lose atlases in one screen.
- SVG atlas generator: tools/make-lose-svg-atlases.js
- Mandatory source reference lines: source/REFERENCE.md
- QA reports: created as pending reports; alpha bbox values require real PNGs.
- Final assets: none yet. Do not copy to LAMDiceBot until QA passes and user approves the phase-1 copy trigger.

## Asset Index

| Phase | Vehicle | Prompt | Manifest | Preview | QA | Target |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | horse | prompts/horse-lose-prompt.md | manifests/horse-lose.json | tools/horse-lose.html | qa/horse-lose-qa.md | assets/horse-race/sprites/lose/horse-lose.png |
| 1 | rabbit | prompts/rabbit-lose-prompt.md | manifests/rabbit-lose.json | tools/rabbit-lose.html | qa/rabbit-lose-qa.md | assets/horse-race/sprites/lose/rabbit-lose.png |
| 1 | turtle | prompts/turtle-lose-prompt.md | manifests/turtle-lose.json | tools/turtle-lose.html | qa/turtle-lose-qa.md | assets/horse-race/sprites/lose/turtle-lose.png |
| 1 | dinosaur | prompts/dinosaur-lose-prompt.md | manifests/dinosaur-lose.json | tools/dinosaur-lose.html | qa/dinosaur-lose-qa.md | assets/horse-race/sprites/lose/dinosaur-lose.png |
| 1 | knight | prompts/knight-lose-prompt.md | manifests/knight-lose.json | tools/knight-lose.html | qa/knight-lose-qa.md | assets/horse-race/sprites/lose/knight-lose.png |
| 2 | car | prompts/car-lose-prompt.md | manifests/car-lose.json | tools/car-lose.html | qa/car-lose-qa.md | assets/horse-race/sprites/lose/car-lose.png |
| 2 | rocket | prompts/rocket-lose-prompt.md | manifests/rocket-lose.json | tools/rocket-lose.html | qa/rocket-lose-qa.md | assets/horse-race/sprites/lose/rocket-lose.png |
| 2 | bird | prompts/bird-lose-prompt.md | manifests/bird-lose.json | tools/bird-lose.html | qa/bird-lose-qa.md | assets/horse-race/sprites/lose/bird-lose.png |
| 2 | ninja | prompts/ninja-lose-prompt.md | manifests/ninja-lose.json | tools/ninja-lose.html | qa/ninja-lose-qa.md | assets/horse-race/sprites/lose/ninja-lose.png |
| 3 | boat | prompts/boat-lose-prompt.md | manifests/boat-lose.json | tools/boat-lose.html | qa/boat-lose-qa.md | assets/horse-race/sprites/lose/boat-lose.png |
| 3 | bicycle | prompts/bicycle-lose-prompt.md | manifests/bicycle-lose.json | tools/bicycle-lose.html | qa/bicycle-lose-qa.md | assets/horse-race/sprites/lose/bicycle-lose.png |
| 3 | scooter | prompts/scooter-lose-prompt.md | manifests/scooter-lose.json | tools/scooter-lose.html | qa/scooter-lose-qa.md | assets/horse-race/sprites/lose/scooter-lose.png |
| 3 | helicopter | prompts/helicopter-lose-prompt.md | manifests/helicopter-lose.json | tools/helicopter-lose.html | qa/helicopter-lose-qa.md | assets/horse-race/sprites/lose/helicopter-lose.png |
| 3 | eagle | prompts/eagle-lose-prompt.md | manifests/eagle-lose.json | tools/eagle-lose.html | qa/eagle-lose-qa.md | assets/horse-race/sprites/lose/eagle-lose.png |
| 3 | crab | prompts/crab-lose-prompt.md | manifests/crab-lose.json | tools/crab-lose.html | qa/crab-lose-qa.md | assets/horse-race/sprites/lose/crab-lose.png |

## Batch Preview Tool

- All-in-one preview: tools/all-lose-preview.html
- Source toggle: auto, generated/, final/, or LAMDiceBot game target
- Phase filter: all, phase 1, phase 2, phase 3
- Per asset display: animated current frame, full 120x45 atlas, x=60 split, anchor x=30 y=45, baseline y=45, size status, alpha bbox summary when PNG is available
- Input fallback: the preview tries {vehicleId}-lose.png first, then {vehicleId}-lose.svg for visual inspection. Final QA still requires PNG atlas output.
- Current SVG-first review files are in generated/{vehicleId}-lose.svg. These match the existing inline-SVG direction better than the original image-generation handoff.
- Current SVG atlas files are derived from the base svgMap entries in D:\Work\LAMDiceBot\js\horse-race-sprites.js run.frame1, then normalized into strict 120x45 two-frame atlases. Booster/power variant art is not used.
