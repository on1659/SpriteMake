"use strict";

const { EventEmitter } = require("node:events");
const { spawn } = require("node:child_process");
const readline = require("node:readline");

const DEFAULT_TIMEOUT_MS = 15_000;

function redact(value, key = "") {
  const sensitiveKey = /(?:access|refresh|token|secret|password|authorization|cookie|email|authurl|verificationurl|usercode|accountid)/i;
  if (sensitiveKey.test(key)) return "[redacted]";

  if (Array.isArray(value)) return value.map((item) => redact(item));
  if (!value || typeof value !== "object") {
    if (typeof value === "string" && /(?:access_token|refresh_token|authorization:|https:\/\/chatgpt\.com\/.*(?:code|state)=)/i.test(value)) {
      return "[redacted]";
    }
    return value;
  }

  return Object.fromEntries(Object.entries(value).map(([childKey, childValue]) => [childKey, redact(childValue, childKey)]));
}

function asError(message) {
  return message instanceof Error ? message : new Error(String(message));
}

class CodexAppServer extends EventEmitter {
  constructor(options = {}) {
    super();
    this.executable = options.executable || "codex";
    this.args = options.args || ["app-server"];
    this.spawn = options.spawn || spawn;
    this.timeoutMs = options.timeoutMs || DEFAULT_TIMEOUT_MS;
    this.clientInfo = options.clientInfo || {
      name: "spritemake-local-runner",
      title: "SpriteMake Local Runner",
      version: "0.1.0",
    };
    this.child = null;
    this.nextId = 1;
    this.pending = new Map();
    this.started = false;
  }

  async start() {
    if (this.started) return;

    this.child = this.spawn(this.executable, this.args, {
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
    });
    this.child.once("error", (error) => this.#failAll(error));
    this.child.once("exit", (code, signal) => {
      const error = new Error(`Codex App Server exited (${code ?? "null"}${signal ? `, ${signal}` : ""})`);
      this.#failAll(error);
      this.emit("exit", { code, signal });
    });
    this.child.stderr.on("data", (chunk) => {
      // App Server stderr is diagnostic only. It is deliberately not persisted
      // because a child process may include account/browser details there.
      this.emit("diagnostic", { message: "Codex App Server emitted stderr", bytes: Buffer.byteLength(chunk) });
    });

    const lines = readline.createInterface({ input: this.child.stdout });
    lines.on("line", (line) => this.#onLine(line));

    await this.request("initialize", { clientInfo: this.clientInfo });
    this.notify("initialized", {});
    this.started = true;
  }

  async stop() {
    if (!this.child) return;
    const child = this.child;
    this.child = null;
    this.started = false;
    this.#failAll(new Error("Codex App Server stopped"));
    child.kill();
  }

  request(method, params = {}, timeoutMs = this.timeoutMs) {
    if (!this.child?.stdin?.writable) return Promise.reject(new Error("Codex App Server is not running"));
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Codex App Server timed out: ${method}`));
      }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer, method });
      this.#write({ method, id, params });
    });
  }

  notify(method, params = {}) {
    this.#write({ method, params });
  }

  async readAccount() {
    const result = await this.request("account/read", { refreshToken: false });
    const account = result?.account || null;
    return {
      connected: account?.type === "chatgpt",
      authMode: account?.type || null,
      planType: account?.planType || null,
      requiresOpenaiAuth: Boolean(result?.requiresOpenaiAuth),
    };
  }

  async readRateLimits() {
    const result = await this.request("account/rateLimits/read");
    return redact(result);
  }

  async beginManagedLogin() {
    // The caller may open authUrl on this same machine, but must not log it or
    // return it through SpriteMake's browser API.
    return this.request("account/login/start", {
      type: "chatgpt",
      useHostedLoginSuccessPage: true,
      appBrand: "chatgpt",
    });
  }

  async beginDeviceLogin() {
    return this.request("account/login/start", { type: "chatgptDeviceCode" });
  }

  cancelLogin(loginId) {
    return this.request("account/login/cancel", { loginId });
  }

  logout() {
    return this.request("account/logout");
  }

  async startRestrictedThread({ cwd, developerInstructions, model }) {
    if (!cwd || typeof cwd !== "string") throw new Error("A staging cwd is required");
    return this.request("thread/start", {
      cwd,
      model: model || null,
      developerInstructions,
      approvalPolicy: "untrusted",
      approvalsReviewer: "user",
      sandbox: "workspace-write",
    });
  }

  startRestrictedTurn({ threadId, input, cwd }) {
    if (!threadId || !Array.isArray(input) || !cwd) throw new Error("threadId, input, and staging cwd are required");
    return this.request("turn/start", {
      threadId,
      input,
      cwd,
      approvalPolicy: "untrusted",
      sandboxPolicy: {
        type: "workspaceWrite",
        networkAccess: false,
        writableRoots: [cwd],
      },
    });
  }

  interruptTurn(threadId, turnId) {
    return this.request("turn/interrupt", { threadId, turnId });
  }

  #write(message) {
    if (!this.child?.stdin?.writable) throw new Error("Codex App Server input is unavailable");
    this.child.stdin.write(`${JSON.stringify(message)}\n`);
  }

  #onLine(line) {
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      this.emit("protocolError", { message: "Invalid JSONL from Codex App Server" });
      return;
    }

    if (message.method && Object.prototype.hasOwnProperty.call(message, "id")) {
      this.#handleServerRequest(message);
      return;
    }
    if (Object.prototype.hasOwnProperty.call(message, "id")) {
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      clearTimeout(pending.timer);
      if (message.error) pending.reject(asError(message.error.message || `Codex App Server error: ${pending.method}`));
      else pending.resolve(message.result);
      return;
    }

    if (message.method) {
      this.emit("notification", redact({ method: message.method, params: message.params || {} }));
    }
  }

  #handleServerRequest(message) {
    const approval = /\/requestApproval$/.test(message.method);
    const input = message.method === "item/tool/requestUserInput";
    const result = approval ? { decision: "decline" } : input ? { action: "decline", content: null } : null;
    this.emit("serverRequest", {
      method: message.method,
      disposition: result ? "declined" : "unsupported",
    });
    if (result) this.#write({ id: message.id, result });
    else this.#write({ id: message.id, error: { code: -32000, message: "Unsupported by SpriteMake runner" } });
  }

  #failAll(error) {
    for (const [id, pending] of this.pending) {
      this.pending.delete(id);
      clearTimeout(pending.timer);
      pending.reject(asError(error));
    }
  }
}

module.exports = { CodexAppServer, redact };
