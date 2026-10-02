"use strict";
// State and accessibility observations of the real shell; no browser or model/API mutations.
const {test}=require("node:test"),assert=require("node:assert/strict");
const {harness,source,normal}=require("./focus-layout.test.cjs");
const areas=["model","code","source","changes","evidence","try","journeys"];

function assertTaskDefaults(h){
  for(const area of areas){h.shell.setArea(area);h.assertPane("explorer",true);h.assertPane("inspector",false);h.assertPane("panel",false);}
}
function assertTemporaryIsolation(code=source){
  const h=harness({code,stored:{...normal,inspectorOpen:false,panelOpen:false}}),before=h.stored();
  h.shell.setArea("evidence");h.shell.reveal("inspector");h.shell.bottom("problems-pane",{temporary:true});
  h.assertPane("inspector",true);h.assertPane("panel",true);assert.deepEqual(h.stored(),before,"selection and error reveals must not save pane choices");
  h.shell.setArea("model");h.assertPane("inspector",false);h.assertPane("panel",false);
  h.shell.setArea("evidence");h.assertPane("inspector",false);h.assertPane("panel",false);
}
function assertWidthIsolation(code=source){
  const h=harness({code,stored:{...normal,inspectorOpen:false,panelOpen:false}});
  h.shell.setArea("evidence");h.shell.reveal("inspector");
  const event=h.get("inspector-resizer").dispatch("keydown",{key:"ArrowLeft"});assert.equal(event.prevented,true);
  assert.equal(h.styleValues.get("--inspector-size"),"304px");assert.equal(h.get("inspector-resizer").getAttribute("aria-valuenow"),"304");
  h.shell.setArea("model");h.assertPane("inspector",false);
  const reloaded=harness({stored:h.stored()});reloaded.assertPane("inspector",false);assert.equal(reloaded.styleValues.get("--inspector-size"),"304px");
  reloaded.shell.setArea("evidence");reloaded.assertPane("inspector",false);
}

test("absent and invalid saved preferences use task defaults without manufacturing saved open choices",()=>{
  for(const stored of [null,"not json","null",{paneOverrides:{model:{inspector:"true",panel:1},evidence:null}}]){
    const h=harness({stored});assertTaskDefaults(h);assert.equal(h.writes.length,0);
  }
});

test("legacy saved booleans retain their scope while new explicit choices persist for one area",()=>{
  const legacy={...normal,explorerOpen:false},h=harness({stored:legacy});
  for(const area of areas){h.shell.setArea(area);h.assertPane("explorer",false);h.assertPane("panel",true);h.assertPane("inspector",["model","code"].includes(area));}
  h.shell.setArea("evidence");h.shell.toggle("explorer",true);h.shell.toggle("inspector",true);h.shell.toggle("panel",false);
  const saved=h.stored();for(const key of ["explorerOpen","inspectorOpen","panelOpen"])assert.equal(saved[key],legacy[key],"legacy fallback must retain its meaning");
  const reloaded=harness({stored:saved});reloaded.assertPane("explorer",false);reloaded.assertPane("inspector",true);reloaded.assertPane("panel",true);
  reloaded.shell.setArea("evidence");reloaded.assertPane("explorer",true);reloaded.assertPane("inspector",true);reloaded.assertPane("panel",false);
  reloaded.shell.setArea("try");reloaded.assertPane("explorer",false);reloaded.assertPane("inspector",false);reloaded.assertPane("panel",true);
});

test("temporary selection and error reveals leave saved preferences and other areas untouched",()=>assertTemporaryIsolation());

test("manual close cancels a reveal through same-area renders, navigation and reload",()=>{
  const h=harness({stored:null});h.shell.setArea("evidence");h.shell.reveal("inspector");h.assertPane("inspector",true);
  h.shell.toggle("inspector",false);const saved=h.stored();
  for(let i=0;i<3;i++){h.shell.setArea("evidence");h.assertPane("inspector",false);}
  h.shell.setArea("model");h.shell.setArea("evidence");h.assertPane("inspector",false);
  const reloaded=harness({stored:saved});reloaded.shell.setArea("evidence");reloaded.assertPane("inspector",false);
  reloaded.shell.reveal("inspector");reloaded.assertPane("inspector",true);assert.deepEqual(reloaded.stored(),saved,"a new explicit item selection may reveal without erasing the closed preference");
});

test("one-argument bottom remains a manual area preference and selects the real tab",()=>{
  const h=harness({stored:null});h.shell.setArea("evidence");h.shell.bottom("history-pane");h.assertPane("panel",true);
  assert.equal(h.get("history-pane").hidden,false);assert.equal(h.get("tab-history-pane").getAttribute("aria-selected"),"true");assert.equal(h.get("tab-history-pane").tabIndex,0);
  h.shell.setArea("try");h.assertPane("panel",false);h.shell.setArea("evidence");h.assertPane("panel",true);
  const reloaded=harness({stored:h.stored()});reloaded.shell.setArea("evidence");reloaded.assertPane("panel",true);reloaded.shell.setArea("try");reloaded.assertPane("panel",false);
});

test("contextual pane resizing saves only its width and never changes model visibility",()=>assertWidthIsolation());

test("compact exclusivity and automatic dismissal preserve independently chosen wide panes",()=>{
  const h=harness({stored:null});h.shell.toggle("explorer",true);h.shell.toggle("inspector",true);const before=h.stored();
  h.shell.resizeMode(true);h.assertPane("explorer",false);h.assertPane("inspector",false);
  h.shell.reveal("inspector");h.assertPane("inspector",true);h.shell.reveal("explorer");h.assertPane("explorer",true);h.assertPane("inspector",false);
  h.get("editor-navigation").dispatch("focusin");h.assertPane("explorer",false);h.assertPane("inspector",false);assert.deepEqual(h.stored(),before);
  h.shell.resizeMode(false);h.assertPane("explorer",true);h.assertPane("inspector",true);
  h.shell.resizeMode(true);h.shell.toggle("explorer",false);h.shell.toggle("inspector",true);h.get("drawer-backdrop").onclick();
  h.shell.resizeMode(false);h.assertPane("explorer",true);h.assertPane("inspector",true);assert.deepEqual(h.stored(),before);
  const reloaded=harness({stored:h.stored()});reloaded.assertPane("explorer",true);reloaded.assertPane("inspector",true);
});

test("temporary errors during focus preserve stored choices, current context and unsent content",()=>{
  const h=harness({stored:null});h.shell.setArea("evidence");h.shell.toggle("inspector",true);const saved=h.stored();
  h.get("q-authority").value="unsent owner answer";h.get("error-json").textContent="STALE_VERSION on revision 7";
  h.shell.focusWorkspace(true);h.shell.bottom("problems-pane",{temporary:true});h.assertPane("panel",true);assert.equal(h.shell.isFocused(),true);
  h.shell.setArea("source");h.assertPane("panel",true);h.shell.resizeMode(true);h.shell.resizeMode(false);h.shell.focusWorkspace(false);
  h.assertPane("panel",false);h.assertPane("inspector",false);assert.deepEqual(h.stored(),saved);
  h.shell.setArea("evidence");h.assertPane("inspector",true);assert.equal(h.get("q-authority").value,"unsent owner answer");assert.equal(h.get("error-json").textContent,"STALE_VERSION on revision 7");assert.deepEqual(h.callbacks,[]);
});

test("reset action clears legacy and per-area visibility, exits focus and retains independent sizes",()=>{
  const h=harness({stored:{...normal,explorer:306,inspector:330,panel:218,explorerOpen:false}});
  h.shell.setArea("evidence");h.shell.toggle("inspector",true);h.shell.toggle("panel",true);h.shell.focusWorkspace(true);h.shell.reveal("inspector");
  h.get("workspace-layout").open=true;h.get("reset-layout").onclick();assert.equal(h.shell.isFocused(),false);assert.equal(h.get("workspace-layout").open,false);assert.equal(h.document.activeElement,h.get("layout-summary"));
  assertTaskDefaults(h);assert.equal(h.styleValues.get("--explorer-size"),"306px");assert.equal(h.styleValues.get("--inspector-size"),"330px");assert.equal(h.styleValues.get("--panel-size"),"218px");
  assertTaskDefaults(harness({stored:h.stored()}));assert.deepEqual(h.callbacks,[]);
});

test("optional storage failure cannot block temporary reveal, explicit choice or reset",()=>{
  const h=harness({storageFailure:true});h.shell.setArea("evidence");
  assert.doesNotThrow(()=>{h.shell.reveal("inspector");h.shell.bottom("problems-pane",{temporary:true});h.shell.toggle("panel",false);h.shell.resetLayout();});assertTaskDefaults(h);
});

test("temporary-reveal oracle rejects saving an explicit choice from reveal",()=>{
  const signature=/function reveal\(key\)\s*\{/;assert.ok(signature.test(source));
  const mutated=source.replace(signature,match=>match+'toggle(key,true);return;');
  assert.throws(()=>assertTemporaryIsolation(mutated),assert.AssertionError);
});

test("width oracle rejects restoring the former global-open side effect",()=>{
  const signature='settings[key] = clamp(value, minimum, maximum);';assert.equal(source.split(signature).length,2);
  const mutated=source.replace(signature,signature+'settings[key+"Open"]=true;');
  assert.throws(()=>assertWidthIsolation(mutated),assert.AssertionError);
});


test("compact Explorer item dismissal preserves Inspector revealed by the selected item",()=>{
  for(const focused of [false,true]){
    const h=harness({stored:null,compact:true});if(focused)h.shell.focusWorkspace(true);
    h.shell.reveal("explorer");const item=h.document.createElement("button");h.get("explorer").append(item);
    h.shell.reveal("inspector");h.get("explorer").dispatch("click",{target:item});
    h.assertPane("explorer",false);h.assertPane("inspector",true);assert.equal(h.writes.length,0);assert.equal(h.shell.isFocused(),focused);
  }
});


test("compact entry and manual drawer choices preserve closed desktop Inspector and open desktop Panel",()=>{
  const preferences={...normal,inspectorOpen:false},h=harness({stored:preferences});
  h.shell.resizeMode(true);for(const key of ["explorer","inspector","panel"])h.assertPane(key,false);
  h.shell.toggle("inspector",true);h.shell.bottom("problems-pane");h.assertPane("inspector",true);h.assertPane("panel",true);assert.deepEqual(h.stored(),preferences);
  h.shell.resizeMode(false);h.assertPane("explorer",true);h.assertPane("inspector",false);h.assertPane("panel",true);assert.deepEqual(h.stored(),preferences);
});
