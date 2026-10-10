#!/usr/bin/env python3
"""Create a disposable geometric human fixture for offline pipeline verification."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.batch_root
    if root.exists():
        parser.error("Choose a new batch directory; existing examples are never overwritten")
    for folder in ("source", "generated", "contracts", "manifests", "qa", "tools", "final", "prompts"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    for name, shift in (("idle", 0), ("hop", -2)):
        image = Image.new("RGBA", (16, 16))
        draw = ImageDraw.Draw(image)
        draw.rectangle((6, 2 + shift, 9, 5 + shift), fill="#edb78d")
        draw.rectangle((6, 2 + shift, 9, 2 + shift), fill="#382a24")
        draw.rectangle((5, 6 + shift, 10, 9 + shift), fill="#204080")
        draw.rectangle((4, 6 + shift, 4, 10 + shift), fill="#edb78d")
        draw.rectangle((11, 6 + shift, 11, 10 + shift), fill="#edb78d")
        draw.rectangle((5, 10 + shift, 6, 13 + shift), fill="#303948")
        draw.rectangle((9, 10 + shift, 10, 13 + shift), fill="#303948")
        image.save(root / f"source/{name}.png")
    contract = {"schemaVersion": 1, "assetId": "hero", "version": 1, "references": [],
        "target": {"finalPath": "final/hero.png"},
        "atlas": {"canvas": {"width": 64, "height": 64},
            "grid": {"columns": 2, "rows": 2, "cellWidth": 32, "cellHeight": 32},
            "anchor": {"x": 16, "y": 28, "meaning": "reference ground contact"}, "sourcePlaneY": 28,
            "animations": {"idle": {"row": 0, "frames": [0, 1], "fps": 4, "loop": True},
                           "hop": {"row": 1, "frames": [0, 1], "fps": 4, "loop": True}}},
        "qa": {"required": ["canvas", "grid", "alpha", "bbox", "anchor", "baseline"],
               "requiredInputs": [], "thresholds": {"maximumAlpha1To7Pixels": 0}},
        "reviews": {"filenameContent": {"required": True}, "placement": {"required": True},
                    "motion": {"required": True}, "style": {"required": False}}}
    frames = [{"path": f"source/{name}.png", "row": row, "column": col,
               "rect": [0, 0, 16, 16], "sourceAnchor": [8, 14], "offset": [0, 0]}
              for row in range(2) for col, name in enumerate(("idle", "idle") if row == 0 else ("idle", "hop"))]
    recipe = {"schemaVersion": 1, "contract": "contracts/hero.json", "scale": 2, "frames": frames,
              "recolor": {"map": {"#204080": "#806020"}, "match": "exact", "tolerance": 0, "alphaThreshold": 8}}
    save_json(root / "contracts/hero.json", contract)
    save_json(root / "manifests/hero.recipe.json", recipe)
    notes = {
        "BATCH.md": "# Offline pipeline example\n\nDeterministic geometric human fixture; no image generation.\n",
        "REQUESTS.md": "# Fixture contract\n\n64×64, 2×2, 32×32 cells. Contact anchor (16,28), independent source plane Y=28. Shared scale 2. Hop keeps its intentional height.\n",
        "PROMPT.md": "# No generation step\n\nThis fixture is drawn by local test code; no model was used.\n",
        "MANIFEST.md": "# Runtime contract\n\nThe bake writes manifests/{attempt}/hero.json. Target after review: final/hero.png; game path unspecified.\n",
        "QA.md": "# QA\n\nRun bake for measured results. Semantic placement, motion and filename reviews remain pending. No final asset is approved.\n"}
    for name, text in notes.items():
        (root / name).write_text(text, encoding="utf-8")
    print(root)


if __name__ == "__main__":
    main()
