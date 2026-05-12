const childProcess = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");
const url = require("url");

const projectRoot = path.resolve(__dirname, "..", "..");
const publicRoot = path.join(__dirname, "public");
const outputRoot = path.join(projectRoot, "output");
const logPath = path.join(outputRoot, "SYMPHONY-GUI.log");
const host = process.env.SPRITEMAKE_GUI_HOST || "127.0.0.1";
const requestedPort = Number(process.env.SPRITEMAKE_GUI_PORT || "0");
const shouldOpen = process.env.SPRITEMAKE_GUI_OPEN !== "0";
const eventClients = new Set();
let activeSymphonyRun = null;

const flowNodes = [
  { id: "intake", label: "Intake", states: ["needs-scaffold", "needs-prompt"] },
  { id: "refine", label: "Refine", states: ["needs-prompt-inject", "needs-refine"] },
  { id: "prompt", label: "Prompt", states: ["prompt-ready"] },
  { id: "generate", label: "Generated", states: [] },
  { id: "qa", label: "QA", states: ["qa-needed", "needs-regeneration", "mixed-review"] },
  { id: "final", label: "Final", states: ["final-review", "final-candidate"] },
];

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
};

function send(res, status, body, headers = {}) {
  const payload = Buffer.isBuffer(body) ? body : Buffer.from(String(body));
  res.writeHead(status, {
    "Content-Length": payload.length,
    "Cache-Control": "no-store",
    ...headers,
  });
  res.end(payload);
}

function sendJson(res, status, value) {
  send(res, status, JSON.stringify(value, null, 2), {
    "Content-Type": "application/json; charset=utf-8",
  });
}

function ensureOutputRoot() {
  fs.mkdirSync(outputRoot, { recursive: true });
}

function broadcastEvent(entry) {
  const payload = `event: log\ndata: ${JSON.stringify(entry)}\n\n`;
  for (const client of eventClients) {
    client.write(payload);
  }
}

function appendLog(kind, message, details = {}) {
  ensureOutputRoot();
  const entry = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    time: new Date().toISOString(),
    kind,
    message,
    ...details,
  };

  fs.appendFileSync(logPath, JSON.stringify(entry) + "\n", "utf8");
  broadcastEvent(entry);
  return entry;
}

function readLogs(limit = 160) {
  if (!fs.existsSync(logPath)) {
    return [];
  }

  const lines = fs.readFileSync(logPath, "utf8").split(/\r?\n/).filter(Boolean);
  return lines.slice(-limit).map((line) => {
    try {
      return JSON.parse(line);
    } catch {
      return {
        id: `raw-${Math.random().toString(16).slice(2)}`,
        time: new Date().toISOString(),
        kind: "raw",
        message: line,
      };
    }
  });
}

function safeStaticPath(requestPath) {
  const pathname = decodeURIComponent(requestPath.split("?")[0]);
  const normalized = pathname === "/" ? "/index.html" : pathname;
  const fullPath = path.normalize(path.join(publicRoot, normalized));

  if (!fullPath.startsWith(publicRoot)) {
    return null;
  }

  return fullPath;
}

function runSymphony() {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(projectRoot, ".agents", "hooks", "symphony.ps1");
    const args = [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      scriptPath,
      "-Json",
      "-WriteReport",
    ];

    childProcess.execFile(
      "powershell",
      args,
      {
        cwd: projectRoot,
        windowsHide: true,
        timeout: 30000,
        maxBuffer: 1024 * 1024 * 8,
      },
      (error, stdout, stderr) => {
        if (error) {
          error.stdout = stdout;
          error.stderr = stderr;
          reject(error);
          return;
        }

        try {
          resolve(JSON.parse(stdout));
        } catch (parseError) {
          parseError.stdout = stdout;
          parseError.stderr = stderr;
          reject(parseError);
        }
      }
    );
  });
}

function runSymphonyQueued() {
  if (!activeSymphonyRun) {
    activeSymphonyRun = runSymphony().finally(() => {
      activeSymphonyRun = null;
    });
  }

  return activeSymphonyRun;
}

function asArray(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function readIfExists(filePath) {
  if (!fs.existsSync(filePath)) return "";
  return fs.readFileSync(filePath, "utf8");
}

function isInside(parent, child) {
  const relative = path.relative(parent, child);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function readPngDimensions(filePath) {
  try {
    const buffer = Buffer.alloc(24);
    const fd = fs.openSync(filePath, "r");
    fs.readSync(fd, buffer, 0, 24, 0);
    fs.closeSync(fd);

    if (buffer.toString("ascii", 1, 4) !== "PNG") {
      return null;
    }

    return {
      width: buffer.readUInt32BE(16),
      height: buffer.readUInt32BE(20),
    };
  } catch {
    return null;
  }
}

function outputAssetUrl(filePath) {
  const relative = path.relative(outputRoot, filePath).split(path.sep).map(encodeURIComponent).join("/");
  return `/assets/${relative}`;
}

function walkPngFiles(rootDir, depth = 0) {
  if (!fs.existsSync(rootDir) || depth > 2) return [];
  const entries = fs.readdirSync(rootDir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkPngFiles(fullPath, depth + 1));
      continue;
    }

    if (entry.isFile() && path.extname(entry.name).toLowerCase() === ".png") {
      files.push(fullPath);
    }
  }

  return files.sort((a, b) => a.localeCompare(b));
}

function assetEntry(filePath, rootDir, kind) {
  const stat = fs.statSync(filePath);
  const dimensions = readPngDimensions(filePath);
  return {
    kind,
    name: path.basename(filePath),
    relativePath: path.relative(outputRoot, filePath),
    folderPath: path.relative(rootDir, filePath),
    url: outputAssetUrl(filePath),
    bytes: stat.size,
    modifiedAt: stat.mtime.toISOString(),
    width: dimensions?.width || null,
    height: dimensions?.height || null,
  };
}

function listPngAssets(batchName) {
  const safeBatchPath = path.normalize(path.join(outputRoot, batchName || ""));
  if (!isInside(outputRoot, safeBatchPath) || !fs.existsSync(safeBatchPath)) {
    return { generated: [], final: [] };
  }

  const generatedRoot = path.join(safeBatchPath, "generated");
  const finalRoot = path.join(safeBatchPath, "final");
  return {
    generated: walkPngFiles(generatedRoot).map((filePath) => assetEntry(filePath, generatedRoot, "generated")),
    final: walkPngFiles(finalRoot).map((filePath) => assetEntry(filePath, finalRoot, "final")),
  };
}

function extractOriginalRequest(text) {
  const fenced = text.match(/Original (?:user )?request:\s*```text\s*([\s\S]*?)```/i);
  if (fenced) return fenced[1].trim();

  const heading = text.match(/## Original User Request\s*```text\s*([\s\S]*?)```/i);
  if (heading) return heading[1].trim();

  return "";
}

function titleFromRequest(request, fallback) {
  let title = String(request || "").replace(/\s+/g, " ").trim();
  if (!title) return fallback;

  title = title
    .replace(/[,，.。!！?？]+/g, " ")
    .replace(/만들고\s*싶은데/g, " ")
    .replace(/만들고싶은데/g, " ")
    .replace(/만들어\s*줘/g, " ")
    .replace(/만들어줘/g, " ")
    .replace(/그려\s*줘/g, " ")
    .replace(/그려줘/g, " ")
    .replace(/생성해\s*줘/g, " ")
    .replace(/생성해줘/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  if (!/스프라이트/i.test(title) && /sprite/i.test(fallback)) {
    title = `${title} 스프라이트`.trim();
  }

  return title.length > 34 ? `${title.slice(0, 34)}...` : title || fallback;
}

function decorateBatch(batch) {
  const batchName = batch.Batch || "";
  const batchPath = path.join(outputRoot, batchName);
  const batchText = readIfExists(path.join(batchPath, "BATCH.md"));
  const promptText = readIfExists(path.join(batchPath, "PROMPT.md"));
  const originalRequest = extractOriginalRequest(batchText) || extractOriginalRequest(promptText);

  return {
    ...batch,
    DisplayName: titleFromRequest(originalRequest, batchName),
    OriginalRequest: originalRequest,
    Assets: listPngAssets(batchName),
  };
}

function nodeIdForBatch(batch) {
  if (!batch) return "intake";
  const state = batch.State;
  const direct = flowNodes.find((node) => node.states.includes(state));
  if (direct) return direct.id;

  if (Number(batch.GeneratedPng || 0) > 0 && Number(batch.FinalPng || 0) === 0) {
    return "qa";
  }

  if (Number(batch.GeneratedPng || 0) > 0) {
    return "generate";
  }

  return "intake";
}

function buildFlowState(batches) {
  const activeBatch = batches[0] || null;
  const activeNodeId = nodeIdForBatch(activeBatch);
  const activeIndex = Math.max(0, flowNodes.findIndex((node) => node.id === activeNodeId));
  const nodes = flowNodes.map((node, index) => {
    let status = "pending";
    if (index < activeIndex) status = "done";
    if (index === activeIndex) status = "active";
    if (activeBatch?.State === "final-candidate" && node.id === "final") status = "active";

    const count = batches.filter((batch) => nodeIdForBatch(batch) === node.id).length;
    return {
      ...node,
      status,
      count,
    };
  });

  return {
    activeNode: {
      id: activeNodeId,
      label: flowNodes.find((node) => node.id === activeNodeId)?.label || "Observe",
      batch: activeBatch?.Batch || null,
      state: activeBatch?.State || "none",
      nextAction: activeBatch?.NextAction || "No active batch.",
    },
    nodes,
  };
}

function summarize(data) {
  const batches = asArray(data.Batches).map((batch) => decorateBatch({
    ...batch,
    MissingDocs: asArray(batch.MissingDocs),
    MissingFolders: asArray(batch.MissingFolders),
    Blockers: asArray(batch.Blockers),
  }));

  const stateCounts = {};
  const totals = {
    batches: batches.length,
    generatedPng: 0,
    finalPng: 0,
    manifestJson: 0,
    previewHtml: 0,
    qaArtifacts: 0,
    promptVariants: 0,
    blockers: 0,
  };

  for (const batch of batches) {
    stateCounts[batch.State] = (stateCounts[batch.State] || 0) + 1;
    totals.generatedPng += Number(batch.GeneratedPng || 0);
    totals.finalPng += Number(batch.FinalPng || 0);
    totals.manifestJson += Number(batch.ManifestJson || 0);
    totals.previewHtml += Number(batch.PreviewHtml || 0);
    totals.qaArtifacts += Number(batch.QaArtifacts || 0);
    totals.promptVariants += Number(batch.PromptVariants || 0);
    totals.blockers += asArray(batch.Blockers).length;
  }

  const flow = buildFlowState(batches);

  const reportPath = path.join(outputRoot, "SYMPHONY.md");
  let reportText = "";
  if (fs.existsSync(reportPath)) {
    reportText = fs.readFileSync(reportPath, "utf8");
  }

  return {
    projectRoot,
    generatedAt: new Date().toISOString(),
    reportPath: data.ReportPath || "output\\SYMPHONY.md",
    reportText,
    totals,
    stateCounts,
    activeNode: flow.activeNode,
    nodes: flow.nodes,
    recentLogs: readLogs(),
    batches,
  };
}

function readReport() {
  const reportPath = path.join(outputRoot, "SYMPHONY.md");
  if (!fs.existsSync(reportPath)) {
    return "# SpriteMake Mini-Symphony Status\n\nNo report has been generated yet.";
  }
  return fs.readFileSync(reportPath, "utf8");
}

function openBrowser(targetUrl) {
  const platform = process.platform;
  if (platform === "win32") {
    childProcess.spawn("cmd", ["/c", "start", "", targetUrl], {
      detached: true,
      stdio: "ignore",
      windowsHide: true,
    }).unref();
    return;
  }

  if (platform === "darwin") {
    childProcess.spawn("open", [targetUrl], {
      detached: true,
      stdio: "ignore",
    }).unref();
    return;
  }

  childProcess.spawn("xdg-open", [targetUrl], {
    detached: true,
    stdio: "ignore",
  }).unref();
}

function writeUrlFiles(targetUrl, port) {
  ensureOutputRoot();
  fs.writeFileSync(
    path.join(outputRoot, "SYMPHONY-GUI.url"),
    `[InternetShortcut]\r\nURL=${targetUrl}\r\n`,
    "utf8"
  );
  fs.writeFileSync(
    path.join(outputRoot, "SYMPHONY-GUI.json"),
    JSON.stringify(
      {
        url: targetUrl,
        host,
        port,
        startedAt: new Date().toISOString(),
        projectRoot,
      },
      null,
      2
    ),
    "utf8"
  );
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);

  if (parsed.pathname === "/api/health") {
    sendJson(res, 200, {
      ok: true,
      projectRoot,
      now: new Date().toISOString(),
    });
    return;
  }

  if (parsed.pathname === "/api/status") {
    const scanId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    try {
      appendLog("scan:start", "Mini-Symphony scan started", {
        node: "scan",
        scanId,
      });
      const raw = await runSymphonyQueued();
      const summary = summarize(raw);
      appendLog("scan:complete", `Scan complete: ${summary.totals.batches} batch(es), ${summary.totals.blockers} blocker(s)`, {
        node: summary.activeNode.id,
        scanId,
        activeBatch: summary.activeNode.batch,
        activeState: summary.activeNode.state,
      });

      for (const batch of summary.batches) {
        appendLog("batch:state", `${batch.Batch} -> ${batch.State}`, {
          node: nodeIdForBatch(batch),
          scanId,
          batch: batch.Batch,
          state: batch.State,
          generatedPng: batch.GeneratedPng,
          finalPng: batch.FinalPng,
        });

        for (const blocker of asArray(batch.Blockers)) {
          appendLog("batch:blocker", blocker, {
            node: nodeIdForBatch(batch),
            scanId,
            batch: batch.Batch,
            state: batch.State,
          });
        }
      }

      summary.recentLogs = readLogs();
      sendJson(res, 200, summary);
    } catch (error) {
      appendLog("scan:error", error.message, {
        node: "scan",
        scanId,
        stderr: error.stderr || "",
      });
      sendJson(res, 500, {
        ok: false,
        message: error.message,
        stdout: error.stdout || "",
        stderr: error.stderr || "",
      });
    }
    return;
  }

  if (parsed.pathname === "/api/logs") {
    const limit = Math.min(Number(parsed.query.limit || 160), 500);
    sendJson(res, 200, {
      logPath: "output\\SYMPHONY-GUI.log",
      logs: readLogs(limit),
    });
    return;
  }

  if (parsed.pathname === "/api/events") {
    res.writeHead(200, {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    });
    res.write(`event: hello\ndata: ${JSON.stringify({ time: new Date().toISOString(), message: "connected" })}\n\n`);
    eventClients.add(res);
    req.on("close", () => {
      eventClients.delete(res);
    });
    return;
  }

  if (parsed.pathname.startsWith("/assets/")) {
    const assetRelative = decodeURIComponent(parsed.pathname.slice("/assets/".length));
    const assetPath = path.normalize(path.join(outputRoot, assetRelative));
    const ext = path.extname(assetPath).toLowerCase();

    if (!isInside(outputRoot, assetPath) || ext !== ".png") {
      send(res, 403, "Forbidden", { "Content-Type": "text/plain; charset=utf-8" });
      return;
    }

    fs.readFile(assetPath, (error, content) => {
      if (error) {
        send(res, 404, "Not found", { "Content-Type": "text/plain; charset=utf-8" });
        return;
      }

      send(res, 200, content, {
        "Content-Type": "image/png",
      });
    });
    return;
  }

  if (parsed.pathname === "/report") {
    send(res, 200, readReport(), {
      "Content-Type": "text/plain; charset=utf-8",
    });
    return;
  }

  const filePath = safeStaticPath(req.url);
  if (!filePath) {
    send(res, 403, "Forbidden", { "Content-Type": "text/plain; charset=utf-8" });
    return;
  }

  fs.readFile(filePath, (error, content) => {
    if (error) {
      send(res, 404, "Not found", { "Content-Type": "text/plain; charset=utf-8" });
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    send(res, 200, content, {
      "Content-Type": mimeTypes[ext] || "application/octet-stream",
    });
  });
});

server.listen(Number.isFinite(requestedPort) ? requestedPort : 0, host, () => {
  const address = server.address();
  const targetUrl = `http://${host}:${address.port}/`;
  writeUrlFiles(targetUrl, address.port);
  appendLog("server:start", `GUI server started on ${targetUrl}`, {
    node: "server",
    port: address.port,
    url: targetUrl,
  });
  console.log("");
  console.log("SpriteMake Mini-Symphony GUI");
  console.log(`Project: ${projectRoot}`);
  console.log(`URL: ${targetUrl}`);
  console.log("");
  console.log("Commands still happen in Codex chat or PowerShell.");
  console.log("This GUI is read-only and refreshes the mini-Symphony board.");
  console.log("Press Ctrl+C to stop.");
  console.log("");

  if (shouldOpen) {
    openBrowser(targetUrl);
  }
});

process.on("SIGINT", () => {
  appendLog("server:stop", "GUI server stopped", {
    node: "server",
  });
  server.close(() => process.exit(0));
});
