"use strict";
// Actual shell handlers in a native-dialog/visibility adapter; this is not browser proof.
const {test}=require("node:test"),assert=require("node:assert/strict");
const {harness,source}=require("./focus-layout.test.cjs");

function open(h,invoker=h.get("open-workspace")){
  invoker.focus();assert.equal(h.get("open-workspace").onclick(),true);
  assert.equal(h.get("workspace-dialog").open,true);
  assert.equal(h.get("open-workspace").getAttribute("aria-expanded"),"true");
  assert.equal(h.document.activeElement,h.get("close-workspace"));
}

test("Workspace native close, Escape and cancel restore the actual invoker",()=>{
  for(const action of [h=>h.get("close-workspace").onclick(),h=>h.get("workspace-dialog").dispatch("keydown",{key:"Escape"}),h=>h.get("workspace-dialog").dispatch("cancel")]){
    const h=harness({stored:null}),invoker=h.get("external-workspace-invoker");open(h,invoker);action(h);
    assert.equal(h.get("workspace-dialog").open,false);assert.equal(h.get("open-workspace").getAttribute("aria-expanded"),"false");assert.equal(h.document.activeElement,invoker);assert.deepEqual(h.callbacks,[]);assert.equal(h.writes.length,0);
  }
});

test("Workspace return falls back when the captured invoker becomes hidden",()=>{
  const h=harness(),invoker=h.get("temporary-invoker");open(h,invoker);invoker.hidden=true;h.get("workspace-dialog").dispatch("cancel");
  assert.equal(h.document.activeElement,h.get("open-workspace"));assert.ok(h.document.activeElement.getClientRects().length);
});

test("every Workspace work button closes the dialog and invokes only its exact route",()=>{
  const h=harness(),saved=h.stored();
  for(const button of h.workspaceViews){open(h);button.onclick();assert.equal(h.get("workspace-dialog").open,false);assert.deepEqual(h.callbacks.at(-1),["openTab",button.dataset.workspaceView]);}
  assert.equal(h.callbacks.length,9);assert.deepEqual(h.stored(),saved);
});

test("Workspace panel buttons reveal and focus the matching actual bottom tab",()=>{
  for(const target of ["problems-pane","evidence-pane","history-pane"]){
    const h=harness({stored:null});open(h);h.workspacePanels.find(button=>button.dataset.workspacePanel===target).onclick();
    assert.equal(h.get("workspace-dialog").open,false);h.assertPane("panel",true);assert.equal(h.get("bottom-pane").hidden,false);assert.equal(h.get("panel-resizer").hidden,false);
    for(const id of ["problems-pane","evidence-pane","history-pane"]){assert.equal(h.get(id).hidden,id!==target);assert.equal(h.get("tab-"+id).getAttribute("aria-selected"),String(id===target));assert.equal(h.get("tab-"+id).tabIndex,id===target?0:-1);}
    assert.equal(h.document.activeElement,h.get("tab-"+target));assert.ok(h.document.activeElement.getClientRects().length);assert.deepEqual(h.callbacks,[]);
  }
});

function assertClosedPanel(h){
  h.shell.bottom("history-pane");const action=h.get("history-action");h.get("history-pane").append(action);action.focus();h.get("collapse-bottom").onclick();
  h.assertPane("panel",false);assert.equal(h.get("bottom-pane").hidden,true);assert.equal(h.get("panel-resizer").hidden,true);assert.equal(h.get("focus-problems").hidden,false);assert.equal(h.document.activeElement,h.get("focus-problems"));
  for(const id of ["history-action","tab-history-pane","collapse-bottom","panel-resizer"]){assert.equal(h.get(id).getClientRects().length,0,id+" must be natively hidden");h.get(id).focus();assert.equal(h.document.activeElement,h.get("focus-problems"),id+" cannot receive focus while closed");}
}
test("closed bottom pane and splitter exclude their controls and preserve visible Problems recovery",()=>assertClosedPanel(harness({stored:null})));

test("Problems remains reachable before, during and after focus layout",()=>{
  const h=harness({stored:null});
  for(const focused of [false,true,false]){h.shell.focusWorkspace(focused);h.shell.toggle("panel",false);assert.equal(h.get("focus-problems").hidden,false);h.get("focus-problems").onclick();assert.equal(h.document.activeElement,h.get("tab-problems-pane"));assert.equal(h.get("problems-pane").hidden,false);assert.equal(h.get("bottom-pane").hidden,false);assert.equal(h.shell.isFocused(),focused);}
});

test("area changes relocate focus only when a bottom control becomes hidden",()=>{
  const h=harness({stored:null});h.shell.bottom("history-pane",{temporary:true});h.get("tab-history-pane").focus();h.shell.setArea("source");
  assert.equal(h.get("bottom-pane").hidden,true);assert.equal(h.document.activeElement,h.get("focus-problems"));
  const outside=h.get("outside-input");outside.focus();h.shell.setArea("model");assert.equal(h.document.activeElement,outside);
  h.shell.bottom("problems-pane",{temporary:true});h.get("panel-resizer").focus();h.shell.setArea("evidence");assert.equal(h.document.activeElement,h.get("focus-problems"));
});

function assertModalIsolation(h){
  h.shell.resizeMode(true);h.shell.toggle("explorer",true);const saved=h.stored(),dialog=h.get("edit-preview");dialog.showModal();
  assert.equal(h.get("open-workspace").onclick(),false);assert.equal(h.get("workspace-dialog").open,false);
  const shortcut=h.document.dispatch("keydown",{key:"b",ctrlKey:true});assert.notEqual(shortcut.prevented,true);h.assertPane("explorer",true);
  h.document.dispatch("keydown",{key:"Escape"});h.assertPane("explorer",true);assert.equal(dialog.open,true);assert.deepEqual(h.stored(),saved);
}
test("any open dialog blocks Workspace nesting and background Escape or Ctrl+B",()=>{
  assertModalIsolation(harness());
  for(const id of ["command-palette","unknown-extension-dialog"]){const h=harness();h.get(id).showModal();assert.equal(h.shell.openWorkspace(),false);assert.equal(h.get("workspace-dialog").open,false);}
});

test("Workspace absorbs shortcuts and closes only its own dialog on Escape",()=>{
  const h=harness({compact:true});h.shell.toggle("explorer",true);open(h);const saved=h.stored();
  for(const key of ["b","k"]){const event=h.get("workspace-dialog").dispatch("keydown",{key,ctrlKey:true});assert.equal(event.prevented,true);assert.equal(h.get("workspace-dialog").open,true);h.assertPane("explorer",true);}
  const event=h.get("workspace-dialog").dispatch("keydown",{key:"Escape"});assert.equal(event.prevented,true);assert.equal(h.get("workspace-dialog").open,false);h.assertPane("explorer",true);assert.deepEqual(h.stored(),saved);
});

test("background Ctrl+B closes Explorer and moves focus out of hidden content",()=>{
  const h=harness({stored:null}),child=h.get("explorer-item");h.get("explorer").append(child);child.focus();
  assert.equal(h.document.dispatch("keydown",{key:"b",ctrlKey:true}).prevented,true);h.assertPane("explorer",false);assert.equal(h.document.activeElement,h.get("open-workspace"));
});

test("closed-panel oracle rejects retaining native focusability behind the layout class",()=>{
  const guard='bottom.hidden=!paneOpen("panel");get("panel-resizer").hidden=bottom.hidden;';assert.equal(source.split(guard).length,2);
  assert.throws(()=>assertClosedPanel(harness({code:source.replace(guard,'bottom.hidden=false;get("panel-resizer").hidden=false;')})),assert.AssertionError);
});

test("modal-isolation oracle rejects the actual background-keyboard guard removal",()=>{
  const guard='document.addEventListener("keydown",event=>{if(document.querySelector("dialog[open]"))return;';assert.equal(source.split(guard).length,2);
  assert.throws(()=>assertModalIsolation(harness({code:source.replace(guard,'document.addEventListener("keydown",event=>{')})),assert.AssertionError);
});
