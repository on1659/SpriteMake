"use strict";

const fs = require("node:fs");
const path = require("node:path");

const MODES = new Set(["pending", "codex", "codex-setup", "gpt-image-2"]);
const REQUIRED_DIRS = ["prompts", "generated", "source", "manifests", "tools", "qa", "final", "contracts"];

function toSlug(value, fallback = "sprite-batch") {
  const slug = String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^[-._]+|[-._]+$/g, "")
    .slice(0, 48)
    .replace(/^[-._]+|[-._]+$/g, "");
  return slug || fallback;
}

function inferredBatchId(request) {
  const text = String(request || "").toLowerCase();
  const terms = [];
  if (/dragon|드래곤/.test(text)) terms.push("dragon");
  if (/fire|flame|불|화염/.test(text)) terms.push("fire");
  if (/ice|frost|얼음|빙결/.test(text)) terms.push("ice");
  if (/sprite|스프라이트/.test(text)) terms.push("sprite");
  if (/character|캐릭터/.test(text)) terms.push("character");
  if (/tile|타일/.test(text)) terms.push("tile");
  if (/effect|fx|이펙트/.test(text)) terms.push("fx");
  if (/icon|아이콘/.test(text)) terms.push("icon");
  const base = terms.length ? [...new Set(terms)].slice(0, 5).join("-") : toSlug(text);
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "").replace("T", "-");
  return `${base}-${stamp}`;
}

function makeUnique(root, desired) {
  let id = desired;
  let count = 2;
  while (fs.existsSync(path.join(root, id))) {
    id = `${desired}-${String(count).padStart(2, "0")}`;
    count += 1;
  }
  return id;
}

function writeUtf8(target, content) {
  fs.writeFileSync(target, content.replace(/\n/g, "\n"), "utf8");
}

function createSpriteBatch({ projectRoot, request, batchId, mode = "codex" }) {
  if (typeof request !== "string" || !request.trim()) throw new Error("request must be a non-empty string");
  if (request.length > 8_000) throw new Error("request must be 8000 characters or fewer");
  if (!MODES.has(mode)) throw new Error("mode must be pending, codex, codex-setup, or gpt-image-2");

  const outputRoot = path.resolve(projectRoot, "output");
  fs.mkdirSync(outputRoot, { recursive: true });
  const requestedId = batchId ? toSlug(batchId) : inferredBatchId(request);
  const id = makeUnique(outputRoot, requestedId);
  const batchRoot = path.resolve(outputRoot, id);
  if (!batchRoot.startsWith(`${outputRoot}${path.sep}`)) throw new Error("invalid batch id");
  fs.mkdirSync(batchRoot, { recursive: false });
  for (const directory of REQUIRED_DIRS) fs.mkdirSync(path.join(batchRoot, directory));

  const relative = `output/${id}`;
  writeUtf8(path.join(batchRoot, "BATCH.md"), `# ${id}\n\n- Status: intake-ready\n- Generation mode: ${mode}\n- Original request: ${request.trim()}\n- Target game path: TODO\n\n## Production rule\n\nCandidates belong in \`generated/\`. Only the checksum-bound QA and human review flow may place a file in \`final/\`.\n`);
  writeUtf8(path.join(batchRoot, "REQUESTS.md"), `# Asset Requests\n\n## Original request\n\n${request.trim()}\n\n## Runtime details to refine\n\n- Target asset path: TODO\n- Canvas / grid / cell size: TODO\n- Contact anchor: TODO\n- Y-axis baseline / source plane: TODO\n- Animation / manifest requirement: TODO\n\n## Character references when applicable\n\nRecord an accepted base and one single-pose reference per requested direction, with batch-relative path, SHA-256 and approval. Identity references, motion/timing references and layout guides have different roles. A direction reference is an image; the contact anchor is a runtime coordinate. Preserve asymmetric equipment; mirroring needs explicit approval. Regenerating or editing an approved reference invalidates its dependent QA and reviews.\n`);
  writeUtf8(path.join(batchRoot, "PROMPT.md"), `# Copy-ready sprite request\n\n${request.trim()}\n\n## Generation Target\n\n- Provider: OpenAI Images API\n- Required image model for strict external generation: gpt-image-2\n- Do not silently substitute another image model.\n- SpriteMake does not store API keys or call image APIs.\n- Codex-direct results are unverified attempts and must remain in \`generated/\` until QA passes.\n\n## Runtime contract\n\n- Final canvas / grid / cell size: TODO\n- Contact anchor: TODO\n- Y-axis baseline / source plane: TODO\n- No gutters or outer padding for strict atlases; transparent padding only inside fixed cells.\n`);
  writeUtf8(path.join(batchRoot, "MANIFEST.md"), `# Manifest Notes\n\n- Image: TODO\n- Grid columns / rows: TODO\n- Anchor: TODO\n- baselineY: TODO\n- Animation frames / fps: TODO\n`);
  writeUtf8(path.join(batchRoot, "QA.md"), `# QA\n\nStatus: pending candidate\n\n- [ ] Canvas and grid divisibility\n- [ ] Alpha / bbox per cell\n- [ ] Contact anchor\n- [ ] Y-axis baseline stability; preserve airborne height\n- [ ] Shared PNG inspection report (tools/runner/inspect_sprite.py)\n- [ ] Contract, reference and curation SHA-256 bindings\n- [ ] Preview playback when animated\n- [ ] Placement review\n- [ ] Motion review when animated: limb phases, anatomy, loop seam or one-shot start/middle/end\n- [ ] Human visual review\n\nA geometric pass does not approve motion or placement. Walk/run stays experimental until motion review passes. Use the asset gate to calculate promotion eligibility.\n`);
  writeUtf8(path.join(batchRoot, "qa", "asset-statuses.json"), JSON.stringify({ version: 1, assets: [] }, null, 2) + "\n");

  return {
    batchId: id,
    batchRoot,
    relativeBatchRoot: relative,
    mode,
    nextAction: mode === "codex-setup"
      ? "Batch and copy-ready prompt are ready; choose a generation environment when ready."
      : "Use PROMPT.md in a generation environment; keep every result under generated/ until QA passes.",
  };
}

module.exports = { createSpriteBatch, inferredBatchId, toSlug };
