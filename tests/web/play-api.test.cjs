"use strict";
// Actual PlayIDE request reader with fetch and Response doubles. These checks are not observed browser evidence.
const {test} = require("node:test"), assert = require("node:assert/strict");
const PlayApi = require("../../src/eija_studio/resources/web/play-api.js");

const answer = (status, body, type = "application/json") => new Response(body, {status, headers: {"Content-Type": type}});
const serving = (response) => async () => response;

test("a JSON result passes through unchanged", async () => {
  assert.deepEqual(await PlayApi.request(serving(answer(200, '{"ok":true,"n":2}')), "/api/x", {}), {ok: true, n: 2});
});

test("a JSON refusal keeps the server's own code and message", async () => {
  await assert.rejects(PlayApi.request(serving(answer(409, '{"code":"MODEL_CHANGED","message":"Reload first"}')), "/api/x", {}),
    (error) => error.code === "MODEL_CHANGED" && error.message === "Reload first" && error.status === 409);
});

test("a refusal without a message still says the request failed", async () => {
  await assert.rejects(PlayApi.request(serving(answer(404, '{"code":"NOT_FOUND"}')), "/api/x", {}),
    (error) => error.code === "NOT_FOUND" && error.message === "Request failed");
});

test("a crash or proxy page is a readable RESPONSE_INVALID, not a JSON parse error", async () => {
  for (const [status, body] of [[500, "Internal Server Error"], [502, "<html><body>Bad Gateway</body></html>"], [200, ""]]) {
    await assert.rejects(PlayApi.request(serving(answer(status, body, "text/html")), "/api/x", {}), (error) =>
      error.code === "RESPONSE_INVALID" && error.status === status && error.message.includes(`HTTP ${status}`)
      && error.message.includes("eija serve") && !/JSON|token/i.test(error.message));
  }
});

test("a stopped server is SERVER_UNREACHABLE with a next step, not 'Failed to fetch'", async () => {
  const down = async () => { throw new TypeError("Failed to fetch"); };
  await assert.rejects(PlayApi.request(down, "/api/x", {}), (error) =>
    error.code === "SERVER_UNREACHABLE" && error.message.includes("eija serve") && !error.message.includes("Failed to fetch"));
});

test("the request is sent as given", async () => {
  const seen = [];
  await PlayApi.request(async (path, options) => { seen.push([path, options]); return answer(200, "{}"); }, "/api/play/x", {method: "POST"});
  assert.deepEqual(seen, [["/api/play/x", {method: "POST"}]]);
});
