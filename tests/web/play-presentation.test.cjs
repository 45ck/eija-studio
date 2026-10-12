"use strict";
// Actual exported UI link/match helpers; no claim of browser rendering evidence.
const {test} = require("node:test"), assert = require("node:assert/strict");
const projection = require("../../src/eija_studio/resources/web/play-presentation.js");
const hash = "a".repeat(64), digest = "b".repeat(64);
const subject = {format: "eija.build-subject.v1", model_hash: hash, digest};
const report = {format: "eija.presentation-map.v1", support: "CHECKED_DESIGN", subject};
const running = {model: hash, subject};

test("only the whole current subject can indicate a matching app", () => {
  assert.equal(projection.matches(report, running), true);
  for (const other of [null, {}, {model: hash}, {...running, subject: {...subject, digest: "c".repeat(64)}},
    {...running, model: "c".repeat(64)}, {...running, subject: {...subject, model_hash: "c".repeat(64)}}]) {
    assert.equal(projection.matches(report, other), false);
  }
  assert.equal(projection.matches(report, running, false), false);
  assert.equal(projection.matches({...report, support: "EXECUTABLE"}, running), false);
  assert.equal(projection.matches({...report, subject: {...subject, digest: "short"}}, running), false);
});

test("screen cards follow the exact existing screen and stable model selections", () => {
  const calls = [], bridge = {openScreen: x => calls.push(["screen", x]), showTab: x => calls.push(["tab", x]),
    select: (x, outline) => calls.push(["select", x, outline])};
  const item = {use_case: "CheckOut", use_case_ref: "transition:TR-CHECKOUT", class_ref: "class:Loan"};
  projection.follow(item, "screen", bridge);
  projection.follow(item, "usecase", bridge);
  projection.follow(item, "class", bridge);
  assert.deepEqual(calls, [["screen", "CheckOut"], ["tab", "usecases"], ["select", "transition:TR-CHECKOUT", false],
    ["tab", "classes"], ["select", "class:Loan", false]]);
});

test("create means the existing null use-case, and absent links cause no API or mutation", () => {
  const calls = [], bridge = {openScreen: x => calls.push(x), showTab: () => assert.fail("invented model link"),
    select: () => assert.fail("invented model selection")};
  projection.follow({use_case: null}, "screen", bridge);
  for (const kind of ["class", "usecase", "approve", "apply"]) projection.follow({}, kind, bridge);
  assert.deepEqual(calls, [null]);
});
