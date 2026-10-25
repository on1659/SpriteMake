#!/usr/bin/env node
"use strict";

// Read-only (apart from the optional status report) Node fallback for the
// PowerShell Mini-Symphony hook. It intentionally does not generate images,
// write asset status records, or promote files into final/.
const fs = require("fs");
const path = require("path");

const REQUIRED_DOCS = ["BATCH.md", "REQUESTS.md", "PROMPT.md", "MANIFEST.md", "QA.md"];
const REQUIRED_DIRS = ["prompts", "generated", "source", "manifests", "tools", "qa", "final"];

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isInside(parent, child) {
  const relative = path.relative(parent, child);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function safeFilePath(root, ...segments) {
  const resolved = path.resolve(root, ...segments);
  return isInside(root, resolved) ? resolved : null;
}

function isRegularFile(filePath) {
  try {
    return fs.lstatSync(filePath).isFile();
  } catch {
    return false;
  }
}

function isDirectory(filePath) {
  try {
    return fs.lstatSync(filePath).isDirectory();
  } catch {
    return false;
  }
}

function readText(filePath) {
  if (!isRegularFile(filePath)) return "";
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return "";
  }
}

function readJson(filePath) {
  if (!isRegularFile(filePath)) return null;
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return null;
  }
}

function countFiles(root, extension = null) {
  if (!fs.existsSync(root)) return 0;
  let count = 0;
  const visit = (directory) => {
    let entries = [];
    try {
      entries = fs.readdirSync(directory, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      // Do not follow symlinks while inspecting a batch folder.
      if (entry.isSymbolicLink()) continue;
      const entryPath = safeFilePath(root, path.relative(root, directory), entry.name);
      if (!entryPath) continue;
      if (entry.isDirectory()) {
        visit(entryPath);
      } else if (entry.isFile() && (!extension || path.extname(entry.name).toLowerCase() === extension)) {
        count += 1;
      }
    }
  };
  visit(root);
  return count;
}

function hasPattern(text, pattern) {
  return Boolean(text) && pattern.test(text);
}

function outcome(value) {
  if (value === true) return "pass";
  if (value === false) return "fail";
  const normalized = String(value ?? "").trim().toLowerCase();
  if (["pass", "passed", "ok", "approved", "eligible", "ready", "promoted"].includes(normalized)) return "pass";
  if (["fail", "failed", "rejected", "ineligible", "blocked"].includes(normalized)) return "fail";
  return "pending";
}

function statusItems(document) {
  if (Array.isArray(document)) return document;
  if (!isPlainObject(document)) return [];
  for (const key of ["assets", "assetStatuses", "items"]) {
    if (Array.isArray(document[key])) return document[key];
  }
  return [document];
}

function summarizeCanonicalStatuses(batchRoot, qaRoot) {
  const candidates = [
    safeFilePath(batchRoot, "qa", "asset-status.json"),
    safeFilePath(batchRoot, "qa", "asset-statuses.json"),
    safeFilePath(batchRoot, "asset-status.json"),
    safeFilePath(batchRoot, "asset-statuses.json"),
  ].filter(Boolean);
  const summary = { count: 0, passed: 0, failed: 0, pending: 0, eligible: 0, files: [] };

  for (const filePath of candidates) {
    if (!isRegularFile(filePath)) continue;
    const document = readJson(filePath);
    const items = statusItems(document).filter((item) => isPlainObject(item) && (item.assetId || isPlainObject(item.qa)));
    if (items.length === 0) continue;
    summary.files.push(path.relative(batchRoot, filePath));
    for (const item of items) {
      const qa = outcome(item.qa?.status);
      let reviews = "pass";
      for (const name of ["filenameContent", "style", "placement", "motion"]) {
        const review = item.reviews?.[name];
        if (!isPlainObject(review) || review.required === false) continue;
        const reviewResult = outcome(review.status);
        if (reviewResult === "fail") reviews = "fail";
        else if (reviewResult === "pending" && reviews !== "fail") reviews = "pending";
      }
      const promotion = item.promotion || {};
      const promotionResult = promotion.eligible === true ? "pass" : outcome(promotion.status);
      summary.count += 1;
      if (qa === "fail" || reviews === "fail" || promotionResult === "fail") {
        summary.failed += 1;
      } else if (qa === "pass" && reviews === "pass" && promotionResult === "pass") {
        summary.passed += 1;
        summary.eligible += 1;
      } else {
        summary.pending += 1;
      }
    }
  }
  return summary;
}

function summarizeQaReports(qaRoot, finalPngCount) {
  if (!fs.existsSync(qaRoot)) return { count: 0, passed: 0, failed: 0, pending: 0, files: [] };
  let entries = [];
  for (const entry of fs.readdirSync(qaRoot, { withFileTypes: true })) {
    if (!entry.isFile() || entry.isSymbolicLink() || path.extname(entry.name).toLowerCase() !== ".json") continue;
    if (entry.name === "asset-status.json" || entry.name === "asset-statuses.json") continue;
    const document = readJson(path.join(qaRoot, entry.name));
    if (!isPlainObject(document)) continue;
    const value = document.pass ?? document.qa?.status;
    if (value === undefined) continue;
    entries.push({
      file: entry.name,
      result: outcome(value),
      isFinal: typeof document.output === "string" && /(^|[\\/])final([\\/]|$)/.test(document.output),
    });
  }
  const finalEntries = entries.filter((entry) => entry.isFinal);
  if (finalPngCount > 0 && finalEntries.length > 0) entries = finalEntries;
  return {
    count: entries.length,
    passed: entries.filter((entry) => entry.result === "pass").length,
    failed: entries.filter((entry) => entry.result === "fail").length,
    pending: entries.filter((entry) => entry.result === "pending").length,
    files: entries.map((entry) => `qa/${entry.file}`),
  };
}

function legacyQa(qaText) {
  const text = qaText.split(/\r?\n/).filter((line) => !/PASS\s*\/\s*FAIL/i.test(line)).join("\n");
  return {
    pass: hasPattern(text, /(->|→|:|\bstatus\s*=\s*)\s*PASS\b|\bqa-passed\b|\bready-for-game\b|\bfinal candidate\b|\bcopied-to-game\b/im),
    fail: hasPattern(text, /(->|→|:|\bstatus\s*=\s*)\s*FAIL\b|\bqa-failed\b|\bneeds (regeneration|repack)\s+[1-9]|\bdo not integrate\b|\bnot integrate\b/im),
  };
}

function scanBatch(outputRoot, batchName) {
  const batchRoot = safeFilePath(outputRoot, batchName);
  if (!batchRoot) return null;
  const requiredDocs = REQUIRED_DOCS.filter((name) => !isRegularFile(path.join(batchRoot, name)));
  const requiredDirs = REQUIRED_DIRS.filter((name) => !isDirectory(path.join(batchRoot, name))).map((name) => `${name}/`);
  const files = Object.fromEntries(REQUIRED_DOCS.map((name) => [name, readText(path.join(batchRoot, name))]));
  const allText = Object.values(files).join("\n");
  const generatedPng = countFiles(path.join(batchRoot, "generated"), ".png");
  const finalPng = countFiles(path.join(batchRoot, "final"), ".png");
  const canonical = summarizeCanonicalStatuses(batchRoot, path.join(batchRoot, "qa"));
  const reports = canonical.count === 0 ? summarizeQaReports(path.join(batchRoot, "qa"), finalPng) : null;
  const legacy = canonical.count === 0 && !reports?.count ? legacyQa(files["QA.md"]) : null;
  const qa = canonical.count > 0 ? canonical : reports || { count: 0, passed: 0, failed: 0, pending: 0, files: [] };
  const qaStatusSource = canonical.count > 0 ? "asset-status" : reports?.count > 0 ? "qa-report" : legacy ? "legacy-qa-md" : "none";
  const qaPassed = canonical.count > 0 || reports?.count > 0 ? qa.passed : legacy?.pass ? 1 : 0;
  const qaFailed = canonical.count > 0 || reports?.count > 0 ? qa.failed : legacy?.fail ? 1 : 0;
  const qaPending = canonical.count > 0 || reports?.count > 0 ? qa.pending : 0;
  const hasPrompt = Boolean(files["PROMPT.md"].trim());
  const hasGenerationTarget = hasPattern(files["PROMPT.md"], /Required image model:\s*gpt-image-2/i);
  const hasGrid = hasPattern(allText, /(Grid columns|Grid:|grid columns|columns and rows|Cell size|cell size)/i);
  const hasAnchor = hasPattern(allText, /(Contact anchor|contact anchor|Anchor:|anchor:)/i);
  const hasBaseline = hasPattern(allText, /(Y-axis|Y baseline|baseline|source plane)/i);
  const hasTargetPath = hasPattern(allText, /(Target file path|Target path|target asset path|Target file path after QA|Target file path after integration)/i);
  const hasPlaceholders = hasPattern(files["REQUESTS.md"], /\bTBD\b|TODO|\{[A-Z0-9_ -]+\}|-\s*(Target file path|Final canvas size|Grid columns|Grid rows|Contact anchor|Y-axis baseline\/source plane):\s*$/im);
  const blockers = [];
  if (requiredDocs.length) blockers.push(`missing docs: ${requiredDocs.join(", ")}`);
  if (requiredDirs.length) blockers.push(`missing folders: ${requiredDirs.join(", ")}`);
  if (hasPrompt && !hasGenerationTarget) blockers.push("PROMPT.md lacks required gpt-image-2 generation target");
  if (hasPrompt && !hasGrid) blockers.push("grid/cell contract is not explicit");
  if (hasPrompt && !hasAnchor) blockers.push("contact anchor is not explicit");
  if (hasPrompt && !hasBaseline) blockers.push("Y-axis baseline/source plane is not explicit");
  if (hasPrompt && !hasTargetPath) blockers.push("target asset path is not explicit");
  if (hasPlaceholders) blockers.push("REQUESTS.md still contains TBD/TODO or blank runtime fields");

  let state = "unknown";
  let priority = 5;
  let nextAction = "Review the batch docs and decide the next production step.";
  if (requiredDocs.length || requiredDirs.length) {
    state = "needs-scaffold"; priority = 1;
    nextAction = "Create the standard batch docs/folders or fill the missing files manually.";
  // Documentation is a creation-time gate. Once a batch already contains
  // reviewed final assets, missing legacy prompt wording is documentation debt
  // rather than a reason to hide the real final-review state.
  } else if (!hasPrompt && finalPng === 0) {
    state = "needs-prompt"; priority = 1;
    nextAction = "Create PROMPT.md with a copy-ready gpt-image-2 prompt and SpriteMake output contract.";
  } else if (!hasGenerationTarget && finalPng === 0) {
    state = "needs-prompt-inject"; priority = 1;
    nextAction = "Run prompt-inject.ps1 to add the required gpt-image-2 generation target.";
  } else if (finalPng === 0 && (!hasGrid || !hasAnchor || !hasBaseline || !hasTargetPath || hasPlaceholders)) {
    state = "needs-refine"; priority = 2;
    nextAction = "Refine REQUESTS.md and PROMPT.md with target path, grid/cell, contact anchor, and Y-axis baseline/source plane.";
  } else if (finalPng === 0 && qaFailed > 0) {
    state = "needs-regeneration"; priority = 2;
    nextAction = "Keep failed PNGs in generated/ and write regeneration or repack notes before producing a new attempt.";
  } else if (finalPng === 0 && qaStatusSource === "asset-status" && qa.count > 0 && qa.eligible === qa.count) {
    state = "final-review"; priority = 3;
    nextAction = "All structured checks are promotion-eligible; run the local asset gate to atomically promote the approved candidate into final/.";
  } else if (generatedPng === 0 && finalPng === 0) {
    state = "prompt-ready"; priority = 3;
    nextAction = "Use PROMPT.md with Codex direct image generation or an external gpt-image-2 environment; put received PNGs under generated/.";
  } else if (generatedPng > 0 && finalPng === 0) {
    state = "qa-needed"; priority = 2;
    nextAction = "Inspect generated PNG size, alpha, grid, per-cell bbox, anchor, baseline, manifest, and preview playback.";
  } else if (finalPng > 0 && qaFailed > 0) {
    state = "mixed-review"; priority = 2;
    nextAction = "Review the structured QA status before integration; final/ contains PNGs but the current candidate has failed checks.";
  } else if (finalPng > 0 && qaStatusSource === "asset-status" && (qaPending > 0 || qa.eligible < qa.count)) {
    state = "final-review"; priority = 4;
    nextAction = "Complete the required human reviews and run asset_gate.py validate to refresh promotion eligibility before final approval.";
  } else if (finalPng > 0 && qaPassed > 0 && qaFailed === 0) {
    state = "final-candidate"; priority = 4;
    nextAction = "Human review: confirm the QA status and copy final assets to the game project only if the target path is correct.";
  } else if (finalPng > 0) {
    state = "final-review"; priority = 4;
    nextAction = "Final assets exist; add explicit QA pass notes before game integration.";
  }

  return {
    Batch: batchName, State: state, Priority: priority, Path: path.relative(path.dirname(outputRoot), batchRoot),
    MissingDocs: requiredDocs, MissingFolders: requiredDirs,
    GeneratedPng: generatedPng, FinalPng: finalPng,
    ManifestJson: countFiles(path.join(batchRoot, "manifests"), ".json"),
    PreviewHtml: countFiles(path.join(batchRoot, "tools"), ".html"),
    QaArtifacts: countFiles(path.join(batchRoot, "qa")), PromptVariants: countFiles(path.join(batchRoot, "prompts"), ".md"),
    HasGenerationTarget: hasGenerationTarget, HasGrid: hasGrid, HasAnchor: hasAnchor, HasBaseline: hasBaseline, HasTargetPath: hasTargetPath,
    HasQaFail: qaFailed > 0, HasQaPass: qaPassed > 0 && qaFailed === 0,
    QaStatusSource: qaStatusSource, QaStatusFiles: qa.files || [], QaStatusCount: qa.count || 0,
    QaPassedCount: qaPassed, QaFailedCount: qaFailed, QaPendingCount: qaPending, QaEligibleCount: qa.eligible || 0,
    Blockers: blockers, NextAction: nextAction,
  };
}

function writeReport(outputRoot, batches) {
  const lines = [
    "# SpriteMake Mini-Symphony Status", "",
    `- Generated at: ${new Date().toISOString()}`,
    "- Control plane: `output/*` batch folders",
    "- Scanner: Node fallback (no image API calls and no final promotion)", "",
    "## Board", "",
    "| Batch | State | Generated PNG | Final PNG | Next Action |",
    "| --- | --- | ---: | ---: | --- |",
    ...batches.map((batch) => `| \`${batch.Batch}\` | \`${batch.State}\` | ${batch.GeneratedPng} | ${batch.FinalPng} | ${batch.NextAction.replace(/\|/g, "/")} |`),
  ];
  const reportPath = path.join(outputRoot, "SYMPHONY.md");
  fs.writeFileSync(reportPath, `${lines.join("\n")}\n`, "utf8");
  return reportPath;
}

function scanSymphony({ projectRoot, writeReport: shouldWriteReport = false } = {}) {
  const root = path.resolve(projectRoot || path.join(__dirname, "..", ".."));
  const outputRoot = path.join(root, "output");
  if (!isDirectory(outputRoot)) {
    throw new Error(`SpriteMake output folder not found: ${outputRoot}`);
  }
  const batches = fs.readdirSync(outputRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.isSymbolicLink())
    .filter((entry) => REQUIRED_DOCS.some((document) => isRegularFile(path.join(outputRoot, entry.name, document))))
    .map((entry) => scanBatch(outputRoot, entry.name))
    .filter(Boolean)
    .sort((a, b) => a.Priority - b.Priority || a.Batch.localeCompare(b.Batch));
  const reportPath = shouldWriteReport ? writeReport(outputRoot, batches) : null;
  return { ProjectRoot: root, ReportPath: reportPath ? path.relative(root, reportPath) : null, Batches: batches };
}

if (require.main === module) {
  const argumentsList = process.argv.slice(2);
  const rootIndex = argumentsList.indexOf("--project-root");
  const projectRoot = rootIndex >= 0 ? argumentsList[rootIndex + 1] : undefined;
  try {
    process.stdout.write(`${JSON.stringify(scanSymphony({ projectRoot, writeReport: argumentsList.includes("--write-report") }), null, 2)}\n`);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}

module.exports = { scanSymphony };
