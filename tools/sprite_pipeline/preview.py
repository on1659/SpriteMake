"""Build portable, offline review tools for one pipeline attempt."""
from __future__ import annotations

import html
import json
from pathlib import Path
import re


def _inline(value: object) -> str:
    # Script elements are raw text even when their MIME type is application/json.
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def build_tools(root: Path, recipe: dict, contract: dict, manifest: dict,
                images: dict[str, str], output_dir: Path) -> dict:
    """Embed all inputs; neither review tool needs a server or a network."""
    output_dir.mkdir(parents=True, exist_ok=True)
    project = Path(__file__).resolve().parents[2]
    template = (project / "templates/animation-player-template.html").read_text(encoding="utf-8-sig")
    for element, value in (("embeddedManifest", manifest), ("embeddedImages", images)):
        pattern = rf'(<script id="{element}" type="application/json">).*?(</script>)'
        template = re.sub(pattern, lambda match: match[1] + _inline(value) + match[2], template, flags=re.S)
    template = re.sub(r'<p class="template-notice" id="templateNotice">.*?</p>', "", template, flags=re.S)
    asset = contract.get("assetId", "sprite")
    manifest_path = f"../../manifests/{output_dir.name}/{asset}.json"
    template = template.replace('value="sprite-manifest.json"', f'value="{html.escape(manifest_path, quote=True)}"')
    template = template.replace('<html lang="en">', '<html lang="ko">')
    template = template.replace('<canvas id="stageCanvas"', '<canvas aria-label="현재 애니메이션 프레임, 접점과 기준선" id="stageCanvas"')
    template = template.replace('<canvas id="sheetCanvas"', '<canvas aria-label="전체 아틀라스와 프레임 격자" id="sheetCanvas"')
    # The stock player always prefers embedded data on file://. A deliberate Load
    # can also accept a local manifest via file picker, without blocked fetch().
    template = template.replace('<button id="loadBtn"', '<input id="manifestFile" type="file" accept=".json,application/json" aria-label="다른 manifest JSON 선택"><button id="loadBtn"')
    template = template.replace('const embeddedImageMap = embeddedImages();', 'const embeddedImageMap = embeddedImages();\n      let manualManifest = null;\n      document.getElementById("manifestFile").addEventListener("change", async (event) => {\n        try { manualManifest = JSON.parse(await event.target.files[0].text()); await loadManifest(); }\n        catch (error) { setStatus(error.message, "bad"); }\n      });')
    template = template.replace('const inlineManifest = embeddedManifest();', 'const inlineManifest = manualManifest || embeddedManifest();')
    template = re.sub(
        r'function setStatus\(message, kind = ""\) \{.*?\n      \}',
        'function setStatus(message, kind = "") {\n        els.status.textContent = message.replace(/<[^>]*>/g, "");\n        els.status.className = "status " + kind;\n      }',
        template, flags=re.S,
    )
    preview = output_dir / "animation-preview.html"
    preview.write_text(template, encoding="utf-8")
    curation_template = Path(__file__).with_name("curation-template.html").read_text(encoding="utf-8")
    data = {"recipe": recipe, "contract": contract, "manifest": manifest, "images": images}
    curation = output_dir / "curation.html"
    curation.write_text(curation_template.replace("__SPRITEMAKE_DATA__", _inline(data)), encoding="utf-8")
    return {"preview": str(preview), "curation": str(curation)}
