# Source References

- Source of truth request: D:\Work\LAMDiceBot\docs\spritemake-request\2026-05-05-horse-lose-poses.md
- Main inline SVG definition file: D:\Work\LAMDiceBot\js\horse-race-sprites.js
- Mandatory style reference: each base svgMap vehicle object's run.frame1 SVG markup at the line anchor below.
- Excluded source: POWER_VEHICLE_VARIANT_OVERRIDES / booster / power-state art.
- Additional tone reference only: source/horse-flat-reference.png
- Additional tone reference only: source/horse-generated-tone-reference.png

## Vehicle Definition Line Anchors

| Vehicle | Source line | Reference state |
| --- | ---: | --- |
| car | L3 | run.frame1 |
| rocket | L49 | run.frame1 |
| bird | L91 | run.frame1 |
| boat | L135 | run.frame1 |
| bicycle | L169 | run.frame1 |
| rabbit | L217 | run.frame1 |
| turtle | L275 | run.frame1 |
| eagle | L315 | run.frame1 |
| scooter | L363 | run.frame1 |
| helicopter | L405 | run.frame1 |
| horse | L463 | run.frame1 |
| knight | L886 | run.frame1 |
| dinosaur | L1267 | run.frame1 |
| ninja | L1677 | run.frame1 |
| crab | L2027 | run.frame1 |

## Contract Note

Inline SVG source viewBox sizes may vary by vehicle. The generated lose atlas is normalized to a strict 120x45 SVG atlas, two 60x45 cells, with no gutters. The atlas clips each cell to prevent source artwork from bleeding across x=60.
