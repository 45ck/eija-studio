"use strict";
// Actual shell code in isolated DOM/storage adapters. Browser paint and human value remain separate.
const {test}=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const shellPath=process.env.EIJA_SHELL_JS||path.join(process.env.EIJA_WEB_ROOT||path.join(__dirname,"../../src/eija_studio/resources/web"),"shell.js");
const source=fs.readFileSync(shellPath,"utf8"),storageKey="eija-ui-layout";
const normal={explorer:230,inspector:288,panel:160,explorerOpen:true,inspectorOpen:true,panelOpen:true};

function harness({code=source,stored=normal,storageFailure=false,compact=false}={}) {
  const nodes=new Map(),storage=new Map(stored===null?[]:[[storageKey,typeof stored==="string"?stored:JSON.stringify(stored)]]),writes=[],callbacks=[],focused=[];
  const classList=()=>{const values=new Set();return {add(...names){names.forEach(n=>values.add(n));},remove(...names){names.forEach(n=>values.delete(n));},contains:n=>values.has(n),toggle(n,on){on=on===undefined?!values.has(n):on;on?values.add(n):values.delete(n);return on;}};};
  const listeners=target=>{target.events=new Map();target.addEventListener=(name,fn)=>{const values=target.events.get(name)||[];values.push(fn);target.events.set(name,values);};target.removeEventListener=(name,fn)=>target.events.set(name,(target.events.get(name)||[]).filter(value=>value!==fn));target.dispatch=(name,extra={})=>{const event={target,key:"",preventDefault(){this.prevented=true;},stopPropagation(){},...extra};for(const fn of target.events.get(name)||[])fn(event);return event;};return target;};
  let document;
  class Element {
    constructor(id,tag="div"){this.id=id;this.tagName=tag.toUpperCase();this.tag=tag;this.dataset={};this.attributes={};this.classList=classList();this.children=[];this.parentElement=null;this.hidden=false;this.open=false;this.disabled=false;this.isConnected=true;this.style={};this.rectangles=null;this.textContent="";this.value="";listeners(this);}
    append(...items){for(const item of items){item.parentElement=this;this.children.push(item);}}
    replaceChildren(...items){this.children=[];this.append(...items);}
    setAttribute(name,value){this.attributes[name]=String(value);if(name==="open")this.open=true;}
    getAttribute(name){return Object.hasOwn(this.attributes,name)?this.attributes[name]:null;}
    removeAttribute(name){delete this.attributes[name];if(name==="open")this.open=false;}
    contains(node){return this===node||this.children.some(child=>child.contains(node));}
    closest(selector){for(let node=this;node;node=node.parentElement){if(selector.startsWith("button")&&node.tag==="button"&&(!selector.includes("#close-explorer")||node.id!=="close-explorer"))return node;if(selector.includes("details")&&node.tag==="details"&&(!selector.includes(":not([open])")||!node.open))return node;if(selector.startsWith("dialog")&&node.tag==="dialog"&&(!selector.includes("[open]")||node.open))return node;}return null;}
    getClientRects(){if(this.rectangles)return this.rectangles;for(let node=this;node;node=node.parentElement){if(node.hidden)return [];if(node.tag==="dialog"&&!node.open)return [];if(node.tag==="details"&&!node.open&&!node.children.find(child=>child.tag==="summary")?.contains(this))return [];if(["explorer","inspector","panel"].includes(node.id)&&document.body.classList.contains(node.id+"-collapsed"))return [];}return [{}];}
    getBoundingClientRect(){return {x:0,y:0,width:800,height:400};}
    focus(){if(!this.getClientRects().length||["hidden","collapse"].includes(computedVisibility(this)))return;for(let ancestor=this.parentElement;ancestor;ancestor=ancestor.parentElement)if(ancestor.tag==="details"&&!ancestor.open&&this!==ancestor.children.find(child=>child.tag==="summary"))return;document.activeElement=this;focused.push(this.id);}
    querySelector(selector){return this.children.find(node=>node.tag===selector)||null;}
    showModal(){if(this.open)throw new Error("dialog already open");this.open=true;this.modalInvoker=document.activeElement;}
    close(){if(!this.open)return;this.open=false;this.modalInvoker?.focus();this.dispatch("close");}
    setPointerCapture(){}hasPointerCapture(){return false;}releasePointerCapture(){}
  }
  function get(id){if(!nodes.has(id))nodes.set(id,new Element(id,id==="workspace-layout"?"details":id==="workspace-layout-summary"?"summary":id.endsWith("dialog")||["command-palette","edit-preview"].includes(id)?"dialog":"div"));return nodes.get(id);}
  const bottomIds=["problems-pane","evidence-pane","history-pane"];
  const bottomTabs=bottomIds.map(id=>{const node=get("tab-"+id);node.dataset.bottom=id;return node;});
  get("workspace-layout").append(get("workspace-layout-summary"),get("toggle-explorer"),get("toggle-inspector"),get("toggle-bottom"),get("reset-layout"));
  const workspaceViews=["model","change","impact","review","code","try","evidence","visual","source"].map(name=>{const node=get("workspace-view-"+name);node.dataset.workspaceView=name;return node;});
  const workspacePanels=bottomIds.map(id=>{const node=get("workspace-panel-"+id);node.dataset.workspacePanel=id;return node;});
  get("workspace-dialog").append(get("close-workspace"),...workspaceViews,...workspacePanels,get("workspace-layout"));
  get("bottom-pane").append(...bottomTabs,...bottomIds.map(get),get("collapse-bottom"));
  get("explorer").append(get("close-explorer"));get("inspector").append(get("close-inspector"));
  const styleValues=new Map(),style={setProperty:(key,value)=>styleValues.set(key,value),getPropertyValue:key=>styleValues.get(key)};
  document=listeners({body:get("body"),documentElement:{style},activeElement:get("body"),getElementById:get,createElement:tag=>new Element("",tag),querySelector:selector=>selector===".editor-navigation"?get("editor-navigation"):selector==="dialog[open]"?[...nodes.values()].find(node=>node.tag==="dialog"&&node.open)||null:bottomTabs.find(tab=>selector===`[data-bottom="${tab.dataset.bottom}"]`)||null,querySelectorAll:selector=>selector==="[data-bottom]"?bottomTabs:selector===".bottom-tab"?bottomIds.map(get):selector==="[data-workspace-view]"?workspaceViews:selector==="[data-workspace-panel]"?workspacePanels:selector==="dialog[open]"?[...nodes.values()].filter(node=>node.tag==="dialog"&&node.open):[]});
  const computedVisibility=node=>{for(let item=node;item;item=item.parentElement){if(item.style.visibility)return item.style.visibility;if(["explorer","inspector","panel"].includes(item.id)&&document.body.classList.contains(item.id+"-collapsed"))return "hidden";}return "visible";};
  const media=listeners({matches:compact}),window=listeners({matchMedia:()=>media,getComputedStyle:node=>({visibility:computedVisibility(node),display:node.hidden?"none":"block"})});
  const sessionStorage={getItem(key){if(storageFailure)throw new Error("storage unavailable");return storage.get(key)||null;},setItem(key,value){if(storageFailure)throw new Error("storage unavailable");writes.push([key,value]);storage.set(key,value);}};
  const sandbox={module:{exports:{}},document,window,sessionStorage,ResizeObserver:class{observe(){}},console,fetch(){throw new Error("Layout must not make a request");}};
  vm.createContext(sandbox);vm.runInContext(code,sandbox,{filename:shellPath});const shell=sandbox.module.exports;
  shell.init({newIntent:()=>callbacks.push("newIntent"),openTab:name=>callbacks.push(["openTab",name])});
  return {shell,get,document,media,writes,callbacks,focused,styleValues,workspaceViews,workspacePanels,stored:()=>JSON.parse(storage.get(storageKey)||"null"),pane(key){return !document.body.classList.contains(key+"-collapsed");},assertPane(key,open){assert.equal(this.pane(key),open,key+" painted layout class");assert.equal(get(key==="panel"?"toggle-bottom":"toggle-"+key).getAttribute("aria-expanded"),String(open),key+" toggle ARIA");}};
}
function assertNormalPreserved(h){
  const before=h.stored();h.shell.focusWorkspace(true);
  for(const key of ["explorer","inspector","panel"])h.assertPane(key,false);
  assert.deepEqual(h.stored(),before,"focus entry must not persist temporary pane closures");
  h.shell.focusWorkspace(false);assert.deepEqual(h.stored(),before,"focus exit must preserve normal preferences");
}
function assertExplicitPanelSurvives(h){
  h.shell.focusWorkspace(true);h.shell.toggle("panel",true);h.assertPane("panel",true);
  for(const area of ["evidence","source","model","try","evidence"]){h.shell.setArea(area);h.assertPane("panel",true);assert.equal(h.shell.isFocused(),true);}
}

module.exports={harness,source,normal};

if(require.main===module){
test("focus closes panes using temporary layout classes and ARIA without persisting normal preferences",()=>{
  const h=harness();h.get("focus-evidence").focus();assertNormalPreserved(h);
  assert.equal(h.shell.isFocused(),false);for(const key of ["explorer","inspector","panel"])h.assertPane(key,true);
  assert.equal(h.document.activeElement,h.get("focus-evidence"));assert.deepEqual(h.callbacks,[]);
});

test("focus entry and exit are idempotent, retaining explicit openings until real restore",()=>{
  const h=harness();h.get("focus-evidence").focus();h.shell.focusWorkspace(true);
  assert.equal(h.shell.isFocused(),true);assert.equal(h.document.activeElement,h.get("restore-workspace"));assert.ok(h.document.activeElement.getClientRects().length);
  h.shell.toggle("panel",true);h.shell.focusWorkspace(true);h.assertPane("panel",true);
  h.shell.focusWorkspace(false);h.shell.focusWorkspace(false);for(const key of ["explorer","inspector","panel"])h.assertPane(key,true);
  assert.equal(h.document.activeElement,h.get("focus-evidence"));assert.deepEqual(h.stored(),normal);
});

test("explicit focused pane openings survive work-area changes and repeated renders",()=>{
  const h=harness();assertExplicitPanelSurvives(h);
  h.shell.toggle("explorer",true);h.shell.toggle("inspector",true);
  for(const area of ["model","evidence","evidence","code","try"]){h.shell.setArea(area);for(const key of ["explorer","inspector","panel"])h.assertPane(key,true);}
  h.shell.toggle("inspector",false);h.shell.setArea("model");h.assertPane("inspector",false);assert.deepEqual(h.stored(),normal);
});

test("opening Problems reveals the real panel and selects its tab while focus remains active",()=>{
  const h=harness();h.get("error-json").textContent="STALE_VERSION at case A revision 7";h.shell.focusWorkspace(true);h.shell.bottom("problems-pane");
  h.assertPane("panel",true);assert.equal(h.shell.isFocused(),true);assert.equal(h.get("problems-pane").hidden,false);
  for(const id of ["problems-pane","evidence-pane","history-pane"]){const selected=id==="problems-pane";assert.equal(h.get("tab-"+id).getAttribute("aria-selected"),String(selected));assert.equal(h.get("tab-"+id).tabIndex,selected?0:-1);assert.equal(h.get(id).hidden,!selected);}
  assert.equal(h.get("error-json").textContent,"STALE_VERSION at case A revision 7");h.shell.setArea("source");h.assertPane("panel",true);assert.deepEqual(h.stored(),normal);
});

test("restore retains the current area and restores pre-focus contextual inspector preferences",()=>{
  const preferences={...normal,explorerOpen:false,panelOpen:false},h=harness({stored:preferences});
  h.shell.setArea("evidence");h.shell.toggle("inspector",true);h.shell.setArea("try");h.assertPane("inspector",false);const saved=h.stored();
  h.shell.focusWorkspace(true);h.shell.toggle("explorer",true);h.shell.toggle("inspector",true);h.shell.toggle("panel",true);h.shell.setArea("evidence");h.shell.focusWorkspace(false);
  h.assertPane("explorer",false);h.assertPane("panel",false);h.assertPane("inspector",true);
  h.shell.setArea("try");h.assertPane("inspector",false);h.shell.setArea("model");h.assertPane("inspector",true);h.shell.setArea("evidence");h.assertPane("inspector",true);assert.deepEqual(h.stored(),saved);
});

test("real splitter keyboard changes survive restore without saving temporary open states",()=>{
  const preferences={...normal,explorerOpen:false,panelOpen:false},h=harness({stored:preferences});
  h.shell.focusWorkspace(true);h.shell.toggle("explorer",true);
  const event=h.get("explorer-resizer").dispatch("keydown",{key:"ArrowRight"});assert.equal(event.prevented,true);
  assert.equal(h.get("explorer-resizer").getAttribute("aria-valuenow"),"246");assert.equal(h.stored().explorer,246);
  assert.equal(h.stored().explorerOpen,false,"resizing a temporarily opened focused pane must not change its normal open preference");
  h.shell.focusWorkspace(false);h.assertPane("explorer",false);assert.equal(h.styleValues.get("--explorer-size"),"246px");assert.equal(h.stored().explorer,246);
});

test("compact focused side drawers remain mutually exclusive and do not close an explicit bottom panel",()=>{
  const h=harness({compact:true});h.shell.focusWorkspace(true);h.shell.toggle("panel",true);h.shell.toggle("explorer",true);
  h.assertPane("explorer",true);h.assertPane("inspector",false);h.assertPane("panel",true);assert.equal(h.get("drawer-backdrop").hidden,false);
  h.shell.toggle("inspector",true);h.assertPane("explorer",false);h.assertPane("inspector",true);h.assertPane("panel",true);
  h.shell.setArea("evidence");h.shell.resizeMode(true);h.assertPane("panel",true);assert.ok(!(h.pane("explorer")&&h.pane("inspector")));
  assert.deepEqual(h.stored(),normal);
});

test("crossing responsive modes during focus preserves normal preferences and explicit panel access",()=>{
  const preferences={...normal,inspectorOpen:false},h=harness({stored:preferences});
  h.shell.focusWorkspace(true);h.shell.toggle("explorer",true);h.shell.toggle("inspector",true);h.shell.toggle("panel",true);h.shell.resizeMode(true);
  assert.ok(!(h.pane("explorer")&&h.pane("inspector")));h.assertPane("panel",true);
  h.shell.resizeMode(false);h.shell.focusWorkspace(false);h.assertPane("explorer",true);h.assertPane("inspector",false);h.assertPane("panel",true);assert.deepEqual(h.stored(),preferences);
});

test("optional unavailable or malformed storage does not prevent focus, Problems, resize or restore",()=>{
  for(const options of [{storageFailure:true},{stored:"not json"}]){
    const h=harness(options);assert.doesNotThrow(()=>{h.shell.focusWorkspace(true);h.shell.bottom("problems-pane");h.shell.toggle("explorer",true);h.get("explorer-resizer").dispatch("keydown",{key:"ArrowRight"});h.shell.focusWorkspace(false);});
    assert.equal(h.shell.isFocused(),false);h.assertPane("explorer",true);h.assertPane("inspector",false);h.assertPane("panel",false);assert.equal(h.styleValues.get("--explorer-size"),"246px");
  }
});

test("focus presentation leaves exact subject, source selection, historical preview and unsent answers untouched",()=>{
  const h=harness(),sentinels={"case-title":"Case A revision 7","model-version":"history","transition-select":"TR-SAVE","source-reference":"repo://src/a.py#save","q-authority":"owner answer draft","model-source":"PREVIEW","error-json":"SOURCE_REVIEW_REQUIRED"};
  for(const [id,value] of Object.entries(sentinels)){h.get(id).value=value;h.get(id).textContent=value;}
  h.get("model-canvas").dataset.selected="TR-SAVE";h.get("model-canvas").setAttribute("data-subject","candidate-sha-A");
  h.shell.focusWorkspace(true);h.shell.setArea("evidence");h.shell.bottom("history-pane");h.shell.setArea("source");h.shell.focusWorkspace(false);
  for(const [id,value] of Object.entries(sentinels)){assert.equal(h.get(id).value,value,id);assert.equal(h.get(id).textContent,value,id);}
  assert.equal(h.get("model-canvas").dataset.selected,"TR-SAVE");assert.equal(h.get("model-canvas").getAttribute("data-subject"),"candidate-sha-A");assert.deepEqual(h.callbacks,[]);
});

test("restoring an unavailable invoker and closing compact drawers return focus to visible controls",()=>{
  const h=harness();h.get("focus-evidence").focus();h.shell.focusWorkspace(true);h.get("focus-evidence").hidden=true;h.shell.focusWorkspace(false);
  assert.equal(h.document.activeElement,h.get("open-workspace"));assert.ok(h.document.activeElement.getClientRects().length);
  h.shell.resizeMode(true);h.shell.focusWorkspace(true);h.shell.toggle("explorer",true);h.get("close-explorer").onclick();
  h.assertPane("explorer",false);assert.ok(h.document.activeElement.getClientRects().length,"drawer close must not focus a toggle inside closed Workspace");assert.equal(h.document.activeElement,h.get("open-workspace"));
  h.shell.toggle("inspector",true);h.document.dispatch("keydown",{key:"Escape"});h.assertPane("inspector",false);assert.equal(h.document.activeElement,h.get("open-workspace"));assert.ok(h.document.activeElement.getClientRects().length);
});

function assertStyledInvokerFallback(h,visibility){
  const invoker=h.get("focus-origin");invoker.rectangles=[{width:180,height:32}];invoker.focus();
  h.shell.focusWorkspace(true);invoker.style.visibility=visibility;
  assert.ok(invoker.getClientRects().length,"CSS-hidden controls can retain layout rectangles");
  h.shell.focusWorkspace(false);assert.equal(h.document.activeElement.id,"open-workspace",visibility+" invoker must fall back to visible Workspace");
}

test("restore rejects hidden or collapsed CSS invokers even when layout rectangles remain",()=>{
  for(const visibility of ["hidden","collapse"])assertStyledInvokerFallback(harness(),visibility);
});

test("restore rejects an invoker in closed native details despite retained layout rectangles",()=>{
  const h=harness(),details=h.document.createElement("details"),invoker=h.get("nested-details-invoker");details.append(invoker);
  details.open=true;invoker.rectangles=[{width:180,height:32}];invoker.focus();assert.equal(h.document.activeElement,invoker);
  h.shell.focusWorkspace(true);details.open=false;assert.ok(invoker.getClientRects().length);
  h.shell.focusWorkspace(false);assert.equal(h.document.activeElement,h.get("open-workspace"));assert.ok(h.document.activeElement.getClientRects().length);
});

test("normal-preference oracle rejects an actual-shell mutation that persists focus closures",()=>{
  const signature=/function focusWorkspace\([^)]*\)\s*\{/;assert.ok(signature.test(source),"mutation must target the actual focus entry function");
  const mutated=source.replace(signature,match=>match+'settings.explorerOpen=false;persist();');
  assert.throws(()=>assertNormalPreserved(harness({code:mutated})),assert.AssertionError);
});

test("explicit-opening oracle rejects an actual-shell mutation that recloses panels on navigation",()=>{
  const signature=/function setArea\([^)]*\)\s*\{/;assert.ok(signature.test(source),"mutation must target the actual area transition");
  const mutated=source.replace(signature,match=>match+'toggle("panel",false);');
  assert.throws(()=>assertExplicitPanelSurvives(harness({code:mutated})),assert.AssertionError);
});


test("paint-visibility oracle rejects removal of the actual computed-visibility guard",()=>{
  const guard='if(available&&["hidden","collapse"].includes(window.getComputedStyle(target).visibility))available=false;';
  assert.equal(source.split(guard).length,2,"mutation must remove exactly the actual computed-visibility guard");
  const mutated=source.replace(guard,"");
  assert.throws(()=>assertStyledInvokerFallback(harness({code:mutated}),"hidden"),assert.AssertionError);
});

}
