# sprite-gen offline integration — 2026-10-10 KST

The [assessment](sprite-gen-reassessment-2026-10-10.md) is now followed by an
implemented PNG processing path. Usage and exact supported contracts live in
[tools/sprite_pipeline/README.md](../tools/sprite_pipeline/README.md).

## Delivered

- Pinned sprite-gen 2.44.0 recolor helpers, full Apache-2.0 LICENSE/NOTICE and
  source revision/SHA-256 provenance. Seven copied function ASTs match upstream.
- Local explicit chroma/despill, connected component suggestions, rect slicing,
  shared nearest-neighbor scale and exact fixed-grid packing. Native alpha is
  preserved unless the recipe explicitly requests a transformation.
- Absolute upstream frame-layout import with repeated rectangles expanded into
  physical target cells and incompatible timing rejected.
- Double-click animation preview and frame curation: swapping, rejecting,
  restoring, pixel nudges, alpha bbox, anchor/baseline, playback and recipe export.
- Versioned candidate attempts, derived contracts and pending QA statuses.
  Source, authoring contract, recipe, imported manifest and processing outputs
  are fingerprinted. Input changes during inspection roll back the attempt.
- Existing local PNG inspector and approval/promotion gate, including separate
  placement/motion approvals and original-contract fingerprint support.

The integration branch includes that QA foundation previously present only in
the local working tree. Other local hooks, account/GUI work and production asset
batches are outside the submitted implementation.

## Validation

Python 3.12.14, Pillow 12.3.0 and NumPy 2.3.5: **46 unittest tests passed**,
including 21 pipeline cases. Coverage includes exact pixels/alpha, deterministic
PNG bytes, shared scale and airborne height, invalid/missing/duplicate/clipped
cells, unsafe paths/symlinks, failed-attempt rollback, timing compatibility,
source/recipe/manifest/contract approval invalidation, and explicit motion review
requirements on contracts without animation metadata.

Compile, JSON parsing and generated contract/status JSON Schema validation
passed. Full copied LICENSE/NOTICE bytes and original helper function ASTs were
compared to the pinned upstream checkout.

Real Chromium loaded both generated HTML tools under `file://`, reported
`ready:true`, rendered nonblank canvases and showed no console errors or blocked
alpha pixel reads. Animation switching and the curation offset/export flow were
exercised. A browser-exported +1px X edit rebaked to exactly the live alpha bbox.

An existing provisional Cyrano south-run PNG was copied into a separate local
proof batch and repacked into eight 256×256 cells. All original RGBA pixels were
preserved. This verifies the processing path on actual human-character art;
it does not establish an improvement in anatomy, identity or gait. Its semantic
placement/motion reviews remain pending and no final/game asset was changed.

PowerShell preflight was not executed because PowerShell is not installed on
the validation machine. Python tests and static validation were executed; the
unrun PowerShell check is not reported as passing.

## Boundaries

This is an offline PNG implementation. Its conservative chroma clamp and
pixelGrid transform are local tools; they are not the full upstream chroma unmix
or Backbone Lattice engines. Video/RIFE generation and restoration, scene tools,
automatic anatomy repair and idle breathing are not included. Attempt status
files do not replace Symphony's canonical root status files. Source generation
models remain unverified; no model/API/login was invoked by the pipeline.
