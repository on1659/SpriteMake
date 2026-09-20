#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const [request, mode = "codex"] = process.argv.slice(2);
if (!request) {
  process.stderr.write("Usage: node tools/runner/request-batch.js \"sprite request\" [codex|codex-setup|gpt-image-2|pending]\n");
  process.exitCode = 1;
} else {
  (async () => {
    const projectRoot = path.resolve(__dirname, "..", "..");
    const runtimePath = path.join(projectRoot, "output", "SYMPHONY-GUI.json");
    try {
      const runtime = JSON.parse(fs.readFileSync(runtimePath, "utf8"));
      const endpoint = new URL("/api/batch-intake", runtime.url);
      if (endpoint.hostname !== "127.0.0.1" && endpoint.hostname !== "localhost" && endpoint.hostname !== "::1") {
        throw new Error("SpriteMake endpoint must be loopback-only");
      }
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request, mode }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.message || `Endpoint returned ${response.status}`);
      process.stdout.write(`${JSON.stringify(body, null, 2)}\n`);
    } catch (error) {
      process.stderr.write(`SpriteMake batch request failed: ${error.message}\nStart start-symphony-gui.bat first.\n`);
      process.exitCode = 1;
    }
  })();
}
