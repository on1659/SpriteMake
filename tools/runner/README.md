# SpriteMake QA and promotion

`inspect_sprite.py` measures PNG canvas/grid/alpha/full and per-cell bboxes,
duplicate frames, adjacent differences and loop seams using the asset contract.
Measurements never approve anatomy, intended contact or correct gait.

```sh
python tools/runner/inspect_sprite.py --batch-root output/example --contract contracts/hero.json --image generated/hero.png --output qa/hero-report.json --status qa/hero-status.json
python tools/runner/asset_gate.py validate --batch-root output/example --contract contracts/hero.json --status qa/hero-status.json
python tools/runner/asset_gate.py promote --batch-root output/example --contract contracts/hero.json --status qa/hero-status.json
```

Statuses bind candidate/report/full-contract SHA-256 values and declared input
hashes. `references` and `qa.requiredInputs` may use batch-local `source/`,
`generated/`, `manifests/`, `qa/` and `contracts/` paths. The latter allows derived
processing contracts to bind their original authoring contract. Paths containing
symlinks, traversal, or missing fingerprints cannot be approved for promotion.

Human review must approve filename/content, placement, motion and style wherever
required. Animated assets always require motion approval; geometry alone cannot
approve walking. Re-running the inspector resets review statuses to pending.
Changed recipe, contract, reference, curation, manifest or comparison inputs
invalidate approval even if a version field was not incremented.

The gate checks all fingerprints and approvals before atomically replacing a
batch-local `final/` file. No API or generation provider is involved.

For color variants, explicit alpha cleanup, frame extraction, upstream atlas
import and portable frame curation, use the [offline processing pipeline](../sprite_pipeline/README.md).
