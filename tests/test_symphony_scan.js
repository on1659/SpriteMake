"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { createSpriteBatch } = require("../tools/runner/batch-intake");
const { scanSymphony } = require("../tools/runner/symphony-scan");

test("motion and placement reviews block a stale eligible status on the board", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "spritemake-scan-"));
  try {
    const { batchRoot } = createSpriteBatch({ projectRoot: root, request: "animated character", batchId: "review" });
    fs.writeFileSync(path.join(batchRoot, "final", "hero.png"), "existing");
    const status = {
      assetId: "hero", qa: { status: "pass" },
      reviews: { motion: { required: true, status: "pending" }, placement: { required: true, status: "approved" } },
      promotion: { eligible: true, status: "promoted" },
    };
    const file = path.join(batchRoot, "qa", "asset-status.json");
    const scan = () => scanSymphony({ projectRoot: root }).Batches[0];
    fs.writeFileSync(file, JSON.stringify(status));
    assert.equal(scan().QaPendingCount, 1);
    assert.equal(scan().HasQaPass, false);
    status.reviews.motion.status = "approved";
    status.reviews.placement.status = "rejected";
    fs.writeFileSync(file, JSON.stringify(status));
    assert.equal(scan().QaFailedCount, 1);
    assert.equal(scan().State, "mixed-review");
    status.reviews.placement.status = "approved";
    fs.writeFileSync(file, JSON.stringify(status));
    assert.equal(scan().QaPassedCount, 1);
    assert.equal(scan().State, "final-candidate");
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
