"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { createSpriteBatch } = require("../tools/runner/batch-intake");

test("batch intake creates a safe SpriteMake scaffold without a key", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "spritemake-intake-"));
  try {
    const result = createSpriteBatch({ projectRoot: root, request: "드래곤 스프라이트 만들어줘", mode: "codex" });
    assert.match(result.batchId, /^dragon-sprite-/);
    assert.ok(fs.existsSync(path.join(result.batchRoot, "PROMPT.md")));
    assert.ok(fs.existsSync(path.join(result.batchRoot, "generated")));
    assert.ok(fs.existsSync(path.join(result.batchRoot, "contracts")));
    assert.match(fs.readFileSync(path.join(result.batchRoot, "PROMPT.md"), "utf8"), /gpt-image-2/);
    assert.doesNotMatch(fs.readFileSync(path.join(result.batchRoot, "PROMPT.md"), "utf8"), /sk-[a-z]/i);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
