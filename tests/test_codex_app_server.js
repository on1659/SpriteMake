"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const { CodexAppServer } = require("../tools/runner/codex-app-server");

const fixture = path.join(__dirname, "fixtures", "fake-codex-app-server.js");

test("bridge initializes, redacts account data, and declines server approvals", async () => {
  const bridge = new CodexAppServer({ executable: process.execPath, args: [fixture] });
  const serverRequests = [];
  bridge.on("serverRequest", (entry) => serverRequests.push(entry));
  await bridge.start();

  assert.deepEqual(await bridge.readAccount(), {
    connected: true,
    authMode: "chatgpt",
    planType: "plus",
    requiresOpenaiAuth: true,
  });
  const limits = await bridge.readRateLimits();
  assert.equal(limits.accessToken, "[redacted]");
  assert.equal(limits.accountId, "[redacted]");

  const login = await bridge.beginManagedLogin();
  assert.equal(login.authUrl, "https://chatgpt.com/auth?code=private");

  const thread = await bridge.startRestrictedThread({ cwd: "/tmp/staging", developerInstructions: "fixture" });
  await bridge.startRestrictedTurn({
    threadId: thread.thread.id,
    cwd: "/tmp/staging",
    input: [{ type: "text", text: "fixture" }],
  });
  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.deepEqual(serverRequests, [{ method: "item/commandExecution/requestApproval", disposition: "declined" }]);
  await bridge.stop();
});
