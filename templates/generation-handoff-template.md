# Generation-only Handoff

Use this for every batch where Codex generated source attempts but did not normalize, QA, promote, or integrate them.

```text
# Handoff — {batch-id}

## Completion
- Completed at:
- Scope completed: generation only
- Explicitly not performed: crop, resize, frame assembly, recolor, background removal, QA/gates, final promotion, game-path copy

## Generation Provenance
- Mode: unverified Codex direct generation | strict external gpt-image-2
- Model claim: never call an unverified direct result gpt-image-2
- Generated root: output/{batch-id}/generated/

## Style References
| Source | Batch copy | Role |
| --- | --- | --- |
| | | |

## Generated Attempts
| Asset ID | Attempt count | All attempt paths | Current best attempt | Notes |
| --- | ---: | --- | --- | --- |

## Exclusions
- Cancelled / intentionally not generated:

## QA And Integration
- QA status: not run | delegated | passed | failed
- Next owner:
- `final/` written: no | yes
- Game paths copied: no | yes
```
