# Batch: local-gui-intake-demo

## Purpose

Show the output structure made by the local GUI from one short request. This is
a documentation-only demo, not production art.

## Target

- Target game path: `Assets/Sprites/Creatures/dragon-rider.png`
- Required external generation target: `gpt-image-2`
- Local Codex generation status: unverified until QA
- Status: `prompted`

## Asset

| Asset ID | Role | Atlas | Contact anchor | Source plane |
| --- | --- | --- | --- | --- |
| `dragon-rider` | mountable fire/ice dragon idle | 4 columns × 2 rows, 128×128 cells | belly/ground contact at `(64, 110)` | `110` |

The contact anchor tells game code where to place the sprite. The source plane
is the shared local Y line that must not drift between variants or frames.
