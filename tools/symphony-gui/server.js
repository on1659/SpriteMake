const childProcess = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");
const url = require("url");
const { createSpriteBatch } = require("../runner/batch-intake");
const { CodexAppServer } = require("../runner/codex-app-server");

const projectRoot = path.resolve(__dirname, "..", "..");
const publicRoot = path.join(__dirname, "public");
const outputRoot = path.join(projectRoot, "output");
const logPath = path.join(outputRoot, "SYMPHONY-GUI.log");
// This server now exposes account actions. It is intentionally loopback-only:
// do not turn it into a LAN service through an environment variable.
const host = "127.0.0.1";
const requestedPort = Number(process.env.SPRITEMAKE_GUI_PORT || "0");
const shouldOpen = process.env.SPRITEMAKE_GUI_OPEN !== "0";
const eventClients = new Set();
let activeSymphonyRun = null;
let codexBridge = null;
let codexBridgeStarting = null;
let accountLoginPending = false;
let accountLoginExpiry = null;
let serverOrigin = "";

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

function isLoopbackRequest(req) {
  const address = String(req.socket.remoteAddress || "").replace(/^::ffff:/, "");
  return address === "::1" || address === "127.0.0.1" || address.startsWith("127.");
}

function isSameOriginLocalMutation(req) {
  if (!isLoopbackRequest(req) || req.method !== "POST") return false;
  const originHeader = String(req.headers.origin || "");
  return Boolean(serverOrigin) && originHeader === serverOrigin;
}

function isSafeLocalRead(req) {
  if (!isLoopbackRequest(req)) return false;
  const originHeader = String(req.headers.origin || "");
  return !originHeader || originHeader === serverOrigin;
}

function summarizeRateLimits(payload) {
  const source = payload?.rateLimitsByLimitId || payload?.rateLimits || {};
  const entries = Object.values(source)
    .map((value) => ({
      remainingPercent: value?.primary?.usedPercent === null || value?.primary?.usedPercent === undefined
        ? null
        : Math.max(0, 100 - Number(value.primary.usedPercent)),
      windowDurationMins: value?.primary?.windowDurationMins ?? null,
      resetsAt: value?.primary?.resetsAt ?? null,
    }))
    .filter((entry) => entry.remainingPercent !== null)
    .slice(0, 3);
  return entries;
}

function safePlanLabel(planType) {
  const allowed = new Set(["free", "plus", "pro", "prolite", "business", "enterprise", "team"]);
  return allowed.has(String(planType || "").toLowerCase()) ? String(planType) : null;
}

function clearAccountLoginPending() {
  accountLoginPending = false;
  if (accountLoginExpiry) clearTimeout(accountLoginExpiry);
  accountLoginExpiry = null;
}

function startAccountLoginPending() {
  clearAccountLoginPending();
  accountLoginPending = true;
  accountLoginExpiry = setTimeout(() => {
    clearAccountLoginPending();
    appendLog("account:login-timeout", "ChatGPT login window expired; retry is available", { node: "account" });
  }, 5 * 60 * 1000);
}

async function ensureCodexBridge() {
  if (codexBridge) return codexBridge;
  if (codexBridgeStarting) return codexBridgeStarting;

  codexBridgeStarting = (async () => {
    const bridge = new CodexAppServer({
      executable: process.env.SPRITEMAKE_CODEX_BIN || "codex",
    });
    bridge.on("notification", (entry) => {
      if (entry.method === "account/updated" || entry.method === "account/login/completed" || entry.method === "account/rateLimits/updated") {
        if (entry.method === "account/login/completed") clearAccountLoginPending();
        appendLog("account:updated", "Codex account state changed", { node: "account" });
      }
    });
    bridge.on("serverRequest", (entry) => {
      // The bridge declines every approval/user-input request. Persist only the
      // generic method/disposition, never the request's params.
      appendLog("account:server-request", `Codex ${entry.disposition}: ${entry.method}`, { node: "account" });
    });
    bridge.on("exit", () => {
      if (codexBridge === bridge) codexBridge = null;
    });
    await bridge.start();
    codexBridge = bridge;
    appendLog("account:bridge", "Codex account bridge started", { node: "account" });
    return bridge;
  })();

  try {
    return await codexBridgeStarting;
  } finally {
    codexBridgeStarting = null;
  }
}

async function readAccountPayload() {
  const bridge = await ensureCodexBridge();
  const [account, rateLimits] = await Promise.all([bridge.readAccount(), bridge.readRateLimits()]);
  return {
    connected: account.connected,
    planType: safePlanLabel(account.planType),
    rateLimits: summarizeRateLimits(rateLimits),
    loginPending: accountLoginPending,
  };
}

function readJsonBody(req, maxBytes = 10_000) {
  return new Promise((resolve, reject) => {
    const contentType = String(req.headers["content-type"] || "").toLowerCase();
    if (!contentType.startsWith("application/json")) {
      reject(new Error("Content-Type must be application/json"));
      return;
    }
    let size = 0;
    const chunks = [];
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > maxBytes) {
        reject(new Error(`Request body must be ${maxBytes} bytes or smaller`));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      } catch {
        reject(new Error("Request body must be valid JSON"));
      }
    });
    req.on("error", reject);
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

function decodeRequestPath(value) {
  try {
    const decoded = decodeURIComponent(String(value || ""));
    return decoded.includes("\0") ? null : decoded;
  } catch {
    // A malformed percent escape is a bad request path, not a server error.
    return null;
  }
}

function safeChildPath(root, requestPath) {
  const decodedPath = decodeRequestPath(requestPath);
  if (decodedPath === null) return null;

  // Prefix with "." so an encoded/decoded leading slash can never make this
  // an absolute path. path.relative below also prevents sibling-prefix bugs
  // such as /public-evil being accepted as a child of /public.
  const fullPath = path.resolve(root, `.${path.sep}${decodedPath}`);
  return isInside(root, fullPath) ? fullPath : null;
}

function safeStaticPath(requestPath) {
  const rawPath = String(requestPath || "").split("?")[0];
  const pathname = rawPath === "/" ? "index.html" : rawPath.replace(/^\/+/, "");
  return safeChildPath(publicRoot, pathname);
}

function isRealPathInside(root, candidate) {
  try {
    return isInside(fs.realpathSync(root), fs.realpathSync(candidate));
  } catch {
    return false;
  }
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
      "-ProjectRoot",
      projectRoot,
      "-Json",
      "-WriteReport",
    ];

    // Windows PowerShell remains a supported fallback. macOS/Linux require
    // PowerShell 7 (`pwsh`), which is the cross-platform PowerShell runtime.
    const commands = process.platform === "win32"
      ? ["pwsh.exe", "powershell.exe", "powershell"]
      : ["pwsh"];

    function execute(commandIndex) {
      const command = commands[commandIndex];
      childProcess.execFile(
        command,
        args,
        {
          cwd: projectRoot,
          windowsHide: true,
          timeout: 30000,
          maxBuffer: 1024 * 1024 * 8,
        },
        (error, stdout, stderr) => {
          if (error) {
            // Only try the next executable when this one is unavailable. A
            // PowerShell/script error must be reported as-is instead of being
            // hidden by a fallback invocation.
            if (error.code === "ENOENT" && commandIndex < commands.length - 1) {
              execute(commandIndex + 1);
              return;
            }

            if (error.code === "ENOENT") {
              try {
                // Keep the GUI usable on hosts without PowerShell (notably a
                // fresh macOS install). The fallback is read-only except for
                // refreshing the same SYMPHONY.md status report requested by
                // the PowerShell invocation above.
                const { scanSymphony } = require("../runner/symphony-scan");
                resolve(scanSymphony({ projectRoot, writeReport: true }));
                return;
              } catch (fallbackError) {
                fallbackError.message = `PowerShell was not found and the Node status fallback failed: ${fallbackError.message}`;
                fallbackError.stdout = stdout;
                fallbackError.stderr = stderr;
                reject(fallbackError);
                return;
              }
            }
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
    }

    execute(0);
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

  if (parsed.pathname === "/api/account") {
    if (req.method !== "GET" || !isSafeLocalRead(req)) {
      send(res, 403, "Forbidden", { "Content-Type": "text/plain; charset=utf-8" });
      return;
    }
    try {
      sendJson(res, 200, { ok: true, account: await readAccountPayload() });
    } catch (error) {
      sendJson(res, 503, { ok: false, message: "Codex account bridge is unavailable" });
    }
    return;
  }

  if (parsed.pathname === "/api/account/login") {
    if (!isSameOriginLocalMutation(req)) {
      send(res, 403, "Forbidden", { "Content-Type": "text/plain; charset=utf-8" });
      return;
    }
    if (accountLoginPending) {
      sendJson(res, 409, { ok: false, message: "A ChatGPT login is already in progress" });
      return;
    }
    startAccountLoginPending();
    try {
      const bridge = await ensureCodexBridge();
      const login = await bridge.beginManagedLogin();
      if (!login?.authUrl) throw new Error("Codex did not provide a managed login URL");
      // Open only on this machine. The URL has OAuth state and is never sent to
      // the GUI, persisted, or written to the GUI log.
      openBrowser(login.authUrl);
      appendLog("account:login", "ChatGPT login opened in the local browser", { node: "account" });
      sendJson(res, 202, { ok: true, status: "login-opened" });
    } catch (error) {
      clearAccountLoginPending();
      sendJson(res, 503, { ok: false, message: "Could not open Codex account login" });
    }
    return;
  }

  if (parsed.pathname === "/api/account/logout") {
    if (!isSameOriginLocalMutation(req)) {
      send(res, 403, "Forbidden", { "Content-Type": "text/plain; charset=utf-8" });
      return;
    }
    try {
      const bridge = await ensureCodexBridge();
      await bridge.logout();
      appendLog("account:logout", "Codex account logged out", { node: "account" });
      sendJson(res, 200, { ok: true, account: await readAccountPayload() });
    } catch (error) {
      sendJson(res, 503, { ok: false, message: "Could not log out of Codex" });
    }
    return;
  }

  if (parsed.pathname === "/api/batch-intake") {
    if (req.method !== "POST" || !isLoopbackRequest(req)) {
      send(res, 403, "Forbidden", { "Content-Type": "text/plain; charset=utf-8" });
      return;
    }
    try {
      const body = await readJsonBody(req);
      const batch = createSpriteBatch({
        projectRoot,
        request: body.request,
        batchId: body.batchId,
        mode: body.mode || "codex",
      });
      appendLog("batch:intake", `Batch scaffold created: ${batch.batchId}`, {
        node: "intake",
        batch: batch.batchId,
        mode: batch.mode,
      });
      sendJson(res, 201, {
        ok: true,
        batchId: batch.batchId,
        batchPath: batch.relativeBatchRoot,
        promptPath: `${batch.relativeBatchRoot}/PROMPT.md`,
        mode: batch.mode,
        nextAction: batch.nextAction,
      });
    } catch (error) {
      sendJson(res, 400, { ok: false, message: error.message });
    }
    return;
  }

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
    const assetPath = safeChildPath(outputRoot, parsed.pathname.slice("/assets/".length));
    const ext = assetPath ? path.extname(assetPath).toLowerCase() : "";

    if (!assetPath || ext !== ".png") {
      send(res, 403, "Forbidden", { "Content-Type": "text/plain; charset=utf-8" });
      return;
    }

    if (fs.existsSync(assetPath) && !isRealPathInside(outputRoot, assetPath)) {
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

  if (fs.existsSync(filePath) && !isRealPathInside(publicRoot, filePath)) {
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
  serverOrigin = `http://${host}:${address.port}`;
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
  console.log("Use the GUI to create a batch scaffold or refresh the mini-Symphony board.");
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
  codexBridge?.stop();
  server.close(() => process.exit(0));
});
