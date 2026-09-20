#!/usr/bin/env node
"use strict";

const { CodexAppServer, redact } = require("./codex-app-server");

async function main() {
  const bridge = new CodexAppServer({ executable: process.env.SPRITEMAKE_CODEX_BIN || "codex" });
  try {
    await bridge.start();
    const [account, rateLimits] = await Promise.all([bridge.readAccount(), bridge.readRateLimits()]);
    process.stdout.write(`${JSON.stringify({ ok: true, account, rateLimits: redact(rateLimits) }, null, 2)}\n`);
  } finally {
    await bridge.stop();
  }
}

main().catch((error) => {
  process.stderr.write(`SpriteMake App Server probe failed: ${error.message}\n`);
  process.exitCode = 1;
});
