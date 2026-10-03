"use strict";
// Actual shell handlers in a native-dialog/visibility adapter; this is not browser proof.
const {test}=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const {harness:baseHarness,source}=require("./focus-layout.test.cjs");
const workViews=["model","change","review","code","try","evidence"];
const referenceViews=["impact","visual","source"];

function harness(options){
  const h=baseHarness(options),dialog=h.get("workspace-dialog");
  const group=(id,nodes)=>{
    const details=h.get(id);details.tag="details";details.tagName="DETAILS";
    const summary=h.document.createElement("summary");details.append(summary);
    for(const node of nodes){if(node.parentElement)node.parentElement.children=node.parentElement.children.filter(child=>child!==node);details.append(node);}
    dialog.append(details);return details;
  };
  group("workspace-work-views",h.workspaceViews.filter(node=>workViews.includes(node.dataset.workspaceView)));
  group("workspace-panels",h.workspacePanels);
  group("workspace-connections",[h.get("repository-status"),h.get("open-source"),h.get("doctor")]);
  dialog.append(h.get("workspace-context"));
  return h;
}

function openGroup(h,id){
  const details=h.get(id);details.children[0].focus();details.open=true;
}

function open(h,invoker=h.get("open-workspace")){
  invoker.focus();assert.equal(h.get("open-workspace").onclick(),true);
  assert.equal(h.get("workspace-dialog").open,true);
  assert.equal(h.document.body.dataset.workspaceChooser,"true");
  assert.equal(h.get("open-workspace").getAttribute("aria-expanded"),"true");
  assert.equal(h.document.activeElement,h.get("close-workspace"));
}

test("Workspace native close, Escape and cancel restore the actual invoker",()=>{
  for(const action of [h=>h.get("close-workspace").onclick(),h=>h.get("workspace-dialog").dispatch("keydown",{key:"Escape"}),h=>h.get("workspace-dialog").dispatch("cancel")]){
    const h=harness({stored:null}),invoker=h.get("external-workspace-invoker");open(h,invoker);action(h);
    assert.equal(h.get("workspace-dialog").open,false);assert.equal(Object.hasOwn(h.document.body.dataset,"workspaceChooser"),false);assert.equal(h.get("open-workspace").getAttribute("aria-expanded"),"false");assert.equal(h.document.activeElement,invoker);assert.deepEqual(h.callbacks,[]);assert.equal(h.writes.length,0);
  }
});

test("Workspace keeps all nine routes with primary duplicates and panel utilities natively disclosed",()=>{
  const webRoot=process.env.EIJA_WEB_ROOT||path.join(__dirname,"../../src/eija_studio/resources/web"),html=fs.readFileSync(path.join(webRoot,"index.html"),"utf8");
  const dialog=html.match(/<dialog\b[^>]*id="workspace-dialog"[^>]*>([\s\S]*?)<\/dialog>/)?.[1];assert.ok(dialog);
  const routes=value=>[...value.matchAll(/data-workspace-view="([^"]+)"/g)].map(match=>match[1]).sort();
  assert.deepEqual(routes(dialog),[...workViews,...referenceViews].sort());
  const disclosed=id=>{
    const found=dialog.match(new RegExp(`<details\\b([^>]*\\bid="${id}"[^>]*)>([\\s\\S]*?)<\\/details>`));assert.ok(found,id+" is a native disclosure");
    assert.doesNotMatch(found[1],/\bopen(?:\s|=|$)/,id+" starts closed");assert.match(found[2],/<summary\b/);return found;
  };
  const work=disclosed("workspace-work-views"),panels=disclosed("workspace-panels");
  assert.deepEqual(routes(work[2]),[...workViews].sort());
  assert.deepEqual([...panels[2].matchAll(/data-workspace-panel="([^"]+)"/g)].map(match=>match[1]).sort(),["evidence-pane","history-pane","problems-pane"]);
  assert.deepEqual(routes(dialog.replace(work[0],"").replace(panels[0],"")),[...referenceViews].sort());
});

test("Workspace connections belong to a native menu disclosure and are not duplicated in Explorer",()=>{
  const webRoot=process.env.EIJA_WEB_ROOT||path.join(__dirname,"../../src/eija_studio/resources/web"),html=fs.readFileSync(path.join(webRoot,"index.html"),"utf8");
  const dialog=html.match(/<dialog\b[^>]*id="workspace-dialog"[^>]*>([\s\S]*?)<\/dialog>/)?.[1],explorer=html.match(/<aside\b[^>]*id="explorer"[^>]*>([\s\S]*?)<\/aside>/)?.[1];assert.ok(dialog);assert.ok(explorer);
  const connections=dialog.match(/<details\b([^>]*)>\s*<summary>Workspace connections<\/summary>([\s\S]*?)<\/details>/);assert.ok(connections);assert.doesNotMatch(connections[1],/\bopen(?:\s|=|$)/);
  for(const id of ["repository-status","open-source","doctor"]){assert.ok(connections[2].includes(`id="${id}"`));assert.equal(html.split(`id="${id}"`).length,2,"one authoritative "+id);assert.ok(!explorer.includes(`id="${id}"`));}
});

test("Inspect checkout closes the chooser before opening only Repository and preserves pane preferences",()=>{
  const h=harness({stored:null}),saved=h.stored(),observed=[],push=h.callbacks.push.bind(h.callbacks);
  h.callbacks.push=(...calls)=>{observed.push({open:h.get("workspace-dialog").open,chooser:Object.hasOwn(h.document.body.dataset,"workspaceChooser")});return push(...calls);};
  open(h);assert.equal(h.get("open-source").getClientRects().length,0);openGroup(h,"workspace-connections");h.get("open-source").focus();h.get("open-source").onclick();
  assert.deepEqual([...h.callbacks],[["openTab","source"]]);assert.deepEqual(observed,[{open:false,chooser:false}]);
  assert.equal(h.get("open-workspace").getAttribute("aria-expanded"),"false");assert.deepEqual(h.stored(),saved);assert.equal(h.writes.length,0);
});

test("Provider diagnostics keeps its app handler and closes Workspace with the actual invoker restored",()=>{
  const setup='document.getElementById("doctor").onclick=()=>{document.getElementById("doctor").dataset.calls="1";};\n';
  const h=harness({stored:null,code:setup+source}),invoker=h.get("external-diagnostics-invoker"),saved=h.stored(),doctor=h.get("doctor");
  open(h,invoker);assert.equal(doctor.getClientRects().length,0);openGroup(h,"workspace-connections");doctor.focus();
  assert.equal(typeof doctor.onclick,"function","shell setup must not replace the app diagnostics handler");doctor.onclick();doctor.dispatch("click");
  assert.equal(doctor.dataset.calls,"1");assert.equal(h.get("workspace-dialog").open,false);assert.equal(Object.hasOwn(h.document.body.dataset,"workspaceChooser"),false);
  assert.equal(h.get("open-workspace").getAttribute("aria-expanded"),"false");assert.equal(h.document.activeElement,invoker);assert.ok(invoker.getClientRects().length);
  assert.deepEqual(h.callbacks,[]);assert.deepEqual(h.stored(),saved);assert.equal(h.writes.length,0);
});

test("Workspace context follows the actual case while opening and cancellation preserve unsent work and layout",()=>{
  const h=harness({stored:null});h.shell.setArea("review");h.shell.toggle("inspector",true);
  h.get("pack-name").textContent="EIJA review reference";h.get("case-id").textContent="Case CA-7 / revision 12 / baseline 4";h.get("case-stage").textContent="PREVIEW";
  h.get("transition-select").value="TR-SAVE";h.get("model-version").value="history";h.get("q-authority").value="unsent owner answer";
  h.get("explorer").scrollTop=123;h.get("source-reader").scrollTop=456;
  const preferences=h.stored(),widths=[...h.styleValues],writes=h.writes.length,panes=["explorer","inspector","panel"].map(key=>h.pane(key));
  for(const close of [()=>h.get("close-workspace").onclick(),()=>h.get("workspace-dialog").dispatch("cancel")]){
    open(h);
    for(const id of ["pack-name","case-id","case-stage"])assert.ok(h.get("workspace-context").textContent.includes(h.get(id).textContent),id+" is identified in chooser context");
    assert.equal(h.shell.isFocused(),false,"navigation must not enter persistent focus layout");
    assert.deepEqual(["explorer","inspector","panel"].map(key=>h.pane(key)),panes);
    close();assert.equal(Object.hasOwn(h.document.body.dataset,"workspaceChooser"),false);
    assert.deepEqual(h.stored(),preferences);assert.equal(h.writes.length,writes);assert.deepEqual([...h.styleValues],widths);
    assert.equal(h.get("transition-select").value,"TR-SAVE");assert.equal(h.get("model-version").value,"history");assert.equal(h.get("q-authority").value,"unsent owner answer");
    assert.equal(h.get("explorer").scrollTop,123);assert.equal(h.get("source-reader").scrollTop,456);
    h.get("case-id").textContent="Case CB-2 / revision 3 / baseline 1";h.get("case-stage").textContent="DRAFT";
  }
  assert.deepEqual(h.callbacks,[]);
});

test("disclosed work views and panels cannot receive focus until their native group is opened",()=>{
  const h=harness({stored:null});open(h);
  for(const id of ["workspace-work-views","workspace-panels"]){
    const group=h.get(id),target=group.children[1];assert.equal(target.getClientRects().length,0);target.focus();assert.equal(h.document.activeElement,h.get("close-workspace"));
    openGroup(h,id);target.focus();assert.equal(h.document.activeElement,target);assert.ok(target.getClientRects().length);
    h.get("close-workspace").focus();
  }
  h.get("workspace-dialog").dispatch("cancel");assert.equal(h.document.activeElement,h.get("open-workspace"));
});

test("Workspace return falls back when the captured invoker becomes hidden",()=>{
  const h=harness(),invoker=h.get("temporary-invoker");open(h,invoker);invoker.hidden=true;h.get("workspace-dialog").dispatch("cancel");
  assert.equal(h.document.activeElement,h.get("open-workspace"));assert.ok(h.document.activeElement.getClientRects().length);
});

test("every Workspace work button closes the dialog and invokes only its exact route",()=>{
  const h=harness(),saved=h.stored();
  for(const button of h.workspaceViews){open(h);if(workViews.includes(button.dataset.workspaceView))openGroup(h,"workspace-work-views");assert.ok(button.getClientRects().length);button.focus();button.onclick();assert.equal(h.get("workspace-dialog").open,false);assert.equal(Object.hasOwn(h.document.body.dataset,"workspaceChooser"),false);assert.deepEqual(h.callbacks.at(-1),["openTab",button.dataset.workspaceView]);}
  assert.equal(h.callbacks.length,9);assert.deepEqual(h.stored(),saved);
});

test("Workspace panel buttons reveal and focus the matching actual bottom tab",()=>{
  for(const target of ["problems-pane","evidence-pane","history-pane"]){
    const h=harness({stored:null});open(h);openGroup(h,"workspace-panels");const button=h.workspacePanels.find(button=>button.dataset.workspacePanel===target);assert.ok(button.getClientRects().length);button.focus();button.onclick();
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
