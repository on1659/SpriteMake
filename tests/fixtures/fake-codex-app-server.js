"use strict";

const readline = require("node:readline");
const rl = readline.createInterface({ input: process.stdin });

function send(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

rl.on("line", (line) => {
  const message = JSON.parse(line);
  if (message.method === "initialize") return send({ id: message.id, result: { userAgent: "fake" } });
  if (message.method === "initialized") return;
  if (message.method === "account/read") {
    return send({ id: message.id, result: { account: { type: "chatgpt", email: "private@example.test", planType: "plus" }, requiresOpenaiAuth: true } });
  }
  if (message.method === "account/rateLimits/read") {
    return send({ id: message.id, result: { rateLimits: { primary: { usedPercent: 10 } }, accessToken: "not-for-logs", accountId: "private-account" } });
  }
  if (message.method === "account/login/start") {
    return send({ id: message.id, result: { type: "chatgpt", loginId: "login-1", authUrl: "https://chatgpt.com/auth?code=private" } });
  }
  if (message.method === "thread/start") return send({ id: message.id, result: { thread: { id: "thread-1" } } });
  if (message.method === "turn/start") {
    send({ id: message.id, result: { turn: { id: "turn-1" } } });
    return send({ id: 991, method: "item/commandExecution/requestApproval", params: {} });
  }
  if (message.id === 991 && message.result?.decision === "decline") return send({ method: "approval/declined", params: {} });
  if (message.method === "turn/interrupt") return send({ id: message.id, result: {} });
  if (message.method === "account/logout") return send({ id: message.id, result: {} });
});
