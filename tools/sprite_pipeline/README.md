# Offline sprite processing

Turn existing PNGs into fixed-grid SpriteMake candidates, color variants and
portable review tools. No generation provider, login, API key or server is used.
`vendor/sprite_gen/` contains pinned recolor helpers from sprite-gen 2.44.0;
other processing and adapters are local. See its LICENSE, NOTICE and provenance.

Use Python 3.11+ in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/sprite_pipeline/requirements.txt
```

On Windows use `.venv\Scripts\python.exe`. The commands below use `python` for
that environment's interpreter. Generation model provenance stays unverified;
deterministic processing does not establish which model made the source.

## Try a complete local example

```sh
python examples/sprite-pipeline/create_demo.py --batch-root output/sprite-pipeline-demo
python tools/sprite_pipeline/run.py bake --batch-root output/sprite-pipeline-demo --recipe manifests/hero.recipe.json --attempt first
```

The example is a small geometric human fixture drawn by code for testing. It is
not generated character artwork or evidence of improved anatomy or walking.
Double-click `output/sprite-pipeline-demo/tools/first/animation-preview.html`
or `curation.html`. Both embed their PNGs and manifests and work under `file://`.

## Recipe

Keep your original PNGs in `source/` or `generated/`, a versioned contract under
`contracts/`, and the recipe under `manifests/`. Paths inside JSON and CLI inputs
are batch-relative POSIX paths. Every fixed target cell needs one explicit frame.

```json
{
  "schemaVersion": 1,
  "contract": "contracts/hero.json",
  "scale": 1,
  "frames": [
    {
      "path": "source/idle.png",
      "rect": [0, 0, 32, 32],
      "row": 0,
      "column": 0,
      "sourceAnchor": [16, 28],
      "offset": [0, 0]
    }
  ],
  "recolor": {
    "map": {"#204080": "#804020"},
    "match": "exact",
    "tolerance": 0,
    "alphaThreshold": 8
  }
}
```

`rect` is optional and defaults to the complete PNG. `sourceAnchor` is relative
to that rect and names its original contact/reference plane, including airborne
frames. It may lie outside the visible sprite or the rect. It is never inferred
from the bottom of the alpha bbox. The target anchor and sourcePlaneY remain
separate fields in `contract.atlas`. Declare both in pixels.

Placement is `targetAnchor - sourceAnchor * scale + offset`, rounded with
`floor(value + 0.5)`. The same nearest-neighbor scale applies to every frame.
Visible pixels crossing the cell boundary, missing cells, duplicate target
slots and blank frames are errors. Transparent overflow is permitted.

Optional transforms, applied before shared scaling:

- `chroma: {"key":"#ff00ff","tolerance":0,"despill":false}` explicitly removes
  near-key pixels. `despill:true` applies a conservative near-key dominant-channel
  clamp. This is not the complete upstream unmix engine. Native alpha is
  preserved by default. Review subject colors and edges after chroma processing.
- `recolor` applies all replacements simultaneously, preserving alpha and
  geometry. Alpha values **greater than** alphaThreshold are eligible. Tolerance
  mode uses a max-channel radius, nearest squared RGB distance, then map order
  to break ties. A shared RGB in eyes and clothing changes both regions.
- `pixelGrid:2` reduces and expands each crop with nearest-neighbor before
  scaling. The factor must divide each crop's width/height. Use only for suitable
  pixel art; it changes detail and is not the upstream Backbone Lattice estimator.

Unknown options fail. Automatic anatomy repair, new drawing generation, video
loop generation and breathing animation are not included in this PNG pipeline.

## Palette and extraction

```sh
python tools/sprite_pipeline/run.py palette --batch-root output/example --image source/hero.png --output qa/palette.json
python tools/sprite_pipeline/run.py components --batch-root output/example --image source/hero.png --output qa/components.json --minimum-pixels 3
```

Palette reports contain RGB counts and a copyable map, capped at 256 colors with
an explicit omitted-color count. Components are 8-connected alpha regions and
return `[x,y,width,height]` suggestions. Detached accessories may need grouping;
connected figures and missing body parts cannot be recovered by segmentation.
Review rectangles and use them in `recipe.frames[].rect`.

To adapt an existing sprite-gen atlas and absolute-rectangle manifest:

```sh
python tools/sprite_pipeline/run.py import-upstream --batch-root output/example --atlas source/upstream.png --manifest source/upstream.json --contract contracts/hero.json --output manifests/imported.recipe.json
python tools/sprite_pipeline/run.py bake --batch-root output/example --recipe manifests/imported.recipe.json --attempt imported
```

Contract animations map each upstream state into an explicit target row and
column sequence. Source cells must match the target cell size, state names,
frame counts and FPS/loop settings. Reused upstream rectangles become distinct
physical target cells. Unequal durations, unassigned target cells and conflicting
target assignments are rejected; author an explicit recipe/contract instead of
losing timing or guessing padding. The imported source manifest is fingerprinted.

## Review and rebake

The curation tool can swap cell sources, nudge placement, reject and restore
frames, change order, and replay animations with anchor/baseline/bbox overlays.
Rejected cells are visibly incomplete and must be filled before a bake. Save the
recipe JSON, copy it into the batch's `manifests/`, and bake with a **new attempt**.
Reload a downloaded recipe through the tool's file picker. The live canvas is a
review aid; the exported PNG and its QA report are the approval inputs.

Each attempt writes only these batch-local paths:

```text
generated/{attempt}/{asset}.png
contracts/{attempt}/{asset}.json
manifests/{attempt}/{asset}.json
qa/{attempt}/transform.json
qa/{attempt}/{asset}-report.json
qa/{attempt}/asset-status.json
tools/{attempt}/animation-preview.html
tools/{attempt}/curation.html
```

The source contract, recipe, PNGs, source manifests, transform report and runtime
manifest are bound into the derived contract and QA input hashes. Re-baking
creates pending reviews. Any input change invalidates approval. The PNG inspector
measures canvas/grid/alpha/bboxes/duplicates/seams; placement and motion meanings
need separate review. Custom unsupported thresholds stay pending rather than
being treated as passed. `qaStatus` in bake output is the actual QA state even
when candidate creation succeeded. Runtime errors roll back that attempt's output.

Reviewers use the existing gate with the **derived** contract and status:

```sh
python tools/runner/asset_gate.py validate --batch-root output/example --contract contracts/imported/hero.json --status qa/imported/asset-status.json
python tools/runner/asset_gate.py promote --batch-root output/example --contract contracts/imported/hero.json --status qa/imported/asset-status.json
```

The tools never approve reviews automatically. Promotion requires the unchanged
candidate, all required approvals, and passing QA. No final or game path is
written during processing. Attempt statuses live under `qa/{attempt}/`; the
current Symphony scanner's canonical root status files are not replaced.

## Verification

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

Tests cover observable pixels, common scaling/airborne placement, alpha-preserving
recolor, deterministic bytes, upstream duplicated rects, path restrictions,
failed-attempt rollback, and approval invalidation. Real-browser checks should
also verify `render_game_to_text().ready`, nonblank canvases, controls, no console
errors, and no blocked file:// alpha reads in both generated HTML tools.
