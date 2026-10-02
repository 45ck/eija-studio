"use strict";
// Actual tab routing, keyboard handlers and HTML contract; no browser or API effects.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const web=process.env.EIJA_WEB_ROOT||path.join(__dirname,"../../src/eija_studio/resources/web"),app=fs.readFileSync(path.join(web,"app.js"),"utf8"),html=fs.readFileSync(path.join(web,"index.html"),"utf8");
function fragment(code,start,end){const from=code.indexOf(start),to=code.indexOf(end,from);assert.ok(from>=0&&to>from,start);return code.slice(from,to);}
const attrs=value=>Object.fromEntries([...value.matchAll(/([\w-]+)="([^"]*)"/g)].map(match=>[match[1],match[2]]));
const strip=value=>value.replace(/<[^>]*>/g,"").replaceAll("&amp;","&").trim();
function harness(code=app){
  const nodes=new Map(),calls=[],focus=[];let document;
  class Element{
    constructor(id,tag="div"){this.id=id;this.tagName=tag.toUpperCase();this.children=[];this.parentElement=null;this.dataset={};this.attributes={};this.hidden=false;this.disabled=false;this.open=false;this.isConnected=true;this.textContent="";this.value="";this.tabIndex=-1;this.events={};const values=new Set();this.classList={add:value=>values.add(value),contains:value=>values.has(value),toggle:(value,on)=>{on?values.add(value):values.delete(value);}};}
    append(...items){for(const item of items){item.parentElement=this;this.children.push(item);}}
    contains(node){return this===node||this.children.some(child=>child.contains(node));}
    setAttribute(key,value){this.attributes[key]=String(value);if(key==="tabindex")this.tabIndex=Number(value);}
    getAttribute(key){return this.attributes[key]??null;}
    removeAttribute(key){delete this.attributes[key];}
    addEventListener(name,fn){this.events[name]=fn;}
    matches(selector){if(selector==="summary")return this.tagName==="SUMMARY";if(selector.startsWith("#"))return this.id===selector.slice(1);if(selector.startsWith("."))return this.classList.contains(selector.slice(1));const match=selector.match(/^\[([\w-]+)(?:="([^"]+)")?\]$/);return !!match&&Object.hasOwn(this.attributes,match[1])&&(match[2]===undefined||this.attributes[match[1]]===match[2]);}
    closest(selector){for(let node=this;node;node=node.parentElement)if(node.matches(selector))return node;return null;}
    querySelectorAll(selector){return this.children.flatMap(child=>[...(child.matches(selector)?[child]:[]),...child.querySelectorAll(selector)]);}
    querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
    getClientRects(){for(let node=this;node;node=node.parentElement){if(node.hidden||!node.isConnected)return [];if(node.tagName==="DIALOG"&&!node.open)return [];if(node.tagName==="DETAILS"&&!node.open&&!node.children.find(child=>child.tagName==="SUMMARY")?.contains(this))return [];}return [{}];}
    focus(){if(!this.disabled&&this.getClientRects().length){document.activeElement=this;focus.push(this.id);}}
  }
  const get=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id);};
  function configure(node,properties){for(const [key,value]of Object.entries(properties)){node.setAttribute(key,value);if(key==="class")value.split(/\s+/).forEach(v=>node.classList.add(v));if(key.startsWith("data-"))node.dataset[key.slice(5).replace(/-([a-z])/g,(_,letter)=>letter.toUpperCase())]=value;}return node;}
  for(const match of html.matchAll(/<([a-z]+)\b([^>]*\bid="[^"]+"[^>]*)>/g)){const a=attrs(match[2]),node=get(a.id);node.tagName=match[1].toUpperCase();configure(node,a);node.hidden=/\bhidden(?:\s|$)/.test(match[2]);node.open=/\bopen(?:\s|$)/.test(match[2]);}
  const body=get("body"),editor=get("editor-navigation"),main=get("main-tabs"),workspace=get("workspace-dialog"),local=get("comparison-tabs"),outer=get("comparison-workspace");
  body.append(editor,outer,workspace);editor.append(main);outer.append(local,get("review"),get("repository-changes"));
  const mainMarkup=html.match(/<nav\b[^>]*aria-label="Work views"[^>]*>([\s\S]*?)<\/nav>/)?.[1],workspaceMarkup=html.match(/<dialog\b[^>]*id="workspace-dialog"[^>]*>([\s\S]*?)<\/dialog>/)?.[1],localMarkup=html.match(/<nav\b[^>]*id="comparison-tabs"[^>]*>([\s\S]*?)<\/nav>/)?.[1];
  assert.ok(mainMarkup&&workspaceMarkup&&localMarkup);
  function buttons(markup,group){return [...markup.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)].map(match=>{const a=attrs(match[1]),node=configure(get(a.id||group.id+"-"+(a["data-tab"]||a["data-workspace-view"]||a["data-workspace-panel"])),a);node.tagName="BUTTON";if(!Object.hasOwn(a,"tabindex"))node.tabIndex=0;node.textContent=strip(match[2]);group.append(node);return node;});}
  const primary=buttons(mainMarkup,main),workspaceButtons=buttons(workspaceMarkup,workspace),comparison=buttons(localMarkup,local);
  const panels=[...nodes.values()].filter(node=>node.classList.contains("tab-content"));for(const panel of panels)if(panel!==outer)body.append(panel);
  document={body,documentElement:get("html"),activeElement:body,querySelectorAll:selector=>selector==='[role="tablist"]'?[local]:selector===".tab-content"?panels:selector==="[data-tab]"?primary:selector==="[data-tab], [data-workspace-view]"?[...primary,...workspaceButtons.filter(node=>node.dataset.workspaceView)]:selector==="[data-comparison-tab]"?comparison:body.querySelectorAll(selector),querySelector:selector=>selector===".editor-navigation"?editor:body.querySelector(selector)};
  const preserved={current:{case:{id:"case-A",version:7},packet:{subject_hash:"model-subject",eligible:false}},instance:{state:"runtime-state"},comparisonSelection:{kind:"transition",id:"T1"},repositoryComparison:{comparison_id:"commit-pair"},repositorySelection:{path:"src/a.py",reference:"repo://src/a.py#f"},repositoryFile:{unified_diff:{text:"-before\n+after\n"}},sourceRecord:{text:"live source"},historyModel:{id:"historical-model"}};
  const context={...preserved,tab:"model",modelView:"history",workbench:{pack:{id:"p"}},caseViews:new Map([["case-A",{tab:"review",editId:"T1"}]]),navigatorMode:"task",document,$:get,
    EijaShell:{setArea:name=>calls.push(["area",name]),mountCanvas:key=>calls.push(["canvas",key]),toggle(){},focusWorkspace(){},bottom(){},fit(){},reveal(){}},renderNavigator:()=>calls.push(["navigator"]),renderEvidenceContext:()=>calls.push(["evidence"]),loadVisual:()=>calls.push(["visual"]),api(){throw Error("Tab navigation must not call an API");},openIntent(){},focusCasePicker(){calls.push(["case-picker"]);},openTransitionPicker(){},task(){throw Error("Navigation must not run a command");},refreshCurrentModel(){}};
  vm.createContext(context);vm.runInContext(fragment(code,'let lastComparisonTab=',"function formalList("),context);
  const clickLine=code.split("\n").find(line=>line.includes('document.querySelectorAll("[data-tab]").forEach(b=>b.onclick='));assert.ok(clickLine);vm.runInContext(clickLine.slice(clickLine.indexOf('document.querySelectorAll("[data-tab]")')),context);
  vm.runInContext(fragment(code,'document.querySelector(".editor-navigation").addEventListener("keydown"','const paletteCommands'),context);
  vm.runInContext(fragment(code,'const paletteCommands = [','async function refreshCurrentModel()'),context);
  context.switchTab("model");calls.length=0;
  const state=()=>JSON.stringify(Object.fromEntries(Object.keys(preserved).map(key=>[key,context[key]])));
  return {context,get,document,primary,workspaceButtons,comparison,main,local,editor,calls,focus,state,read:expression=>vm.runInContext(expression,context),switch:name=>context.switchTab(name),open:name=>context.openWorkTab(name),destination:name=>context.openWorkDestination(name),addControl(id,parent){const node=get(id);get(parent).append(node);return node;},key(group,target,key){let prevented=false;group.events.keydown({target,key,preventDefault(){prevented=true;}});return prevented;}};
}
function assertResumes(code=app){const h=harness(code);h.switch("repository-changes");h.switch("model");h.open("review");assert.equal(h.context.tab,"repository-changes");return h;}

test("Changes has one primary tab and two labelled local comparison panels",()=>{
  const h=harness();assert.deepEqual(h.primary.map(button=>button.dataset.tab),["model","code","change","review","try","evidence"]);assert.deepEqual(h.workspaceButtons.filter(button=>button.dataset.workspaceView).map(button=>button.dataset.workspaceView),["model","change","impact","review","code","try","evidence","visual","source"]);assert.deepEqual(h.comparison.map(button=>button.dataset.comparisonTab),["review","repository-changes"]);
  assert.equal(h.get("tab-changes").getAttribute("aria-controls"),"comparison-workspace");assert.equal(h.get("comparison-workspace").getAttribute("aria-labelledby"),"tab-changes");
  for(const [button,panel]of [["comparison-model-tab","review"],["comparison-code-tab","repository-changes"]]){assert.equal(h.get(button).getAttribute("aria-controls"),panel);assert.equal(h.get(panel).getAttribute("aria-labelledby"),button);assert.equal(h.get(panel).classList.contains("comparison-content"),true);assert.equal(h.get(panel).classList.contains("tab-content"),false);}
  assert.ok(html.indexOf('id="comparison-workspace"')<html.indexOf('id="review"')&&html.indexOf('id="review"')<html.indexOf('id="repository-changes"'));
});

test("primary Changes resumes the last comparison but explicit Model changes remains exact",()=>{
  const h=assertResumes();h.switch("review");assert.equal(h.context.tab,"review");h.switch("evidence");h.open("review");assert.equal(h.context.tab,"review");h.switch("repository-changes");h.switch("model");h.get("tab-changes").onclick();assert.equal(h.context.tab,"repository-changes");
});

test("both comparison subviews select Changes and expose only the corresponding inner panel",()=>{
  const h=harness();for(const name of ["review","repository-changes","review"]){h.switch(name);assert.equal(h.get("comparison-workspace").hidden,false);assert.equal(h.get("comparison-workspace").dataset.comparisonView,name);assert.equal(h.get("tab-changes").getAttribute("aria-current"),"page");assert.equal(h.get("tab-changes").tabIndex,0);
    for(const button of h.comparison){const selected=button.dataset.comparisonTab===name;assert.equal(button.getAttribute("aria-selected"),String(selected));assert.equal(button.tabIndex,selected?0:-1);assert.equal(h.get(button.dataset.comparisonTab).hidden,!selected);}assert.equal(h.primary.filter(button=>button.getAttribute("aria-current")==="page").length,1);assert.ok(h.primary.every(button=>button.tabIndex===0));}
  h.switch("model");assert.equal(h.get("comparison-workspace").hidden,true);assert.notEqual(h.get("tab-changes").getAttribute("aria-current"),"page");assert.equal(h.get("model").hidden,false);
});

test("native primary navigation leaves arrow keys alone and local comparison keyboard routes remain exact",()=>{
  const h=harness();h.switch("repository-changes");h.switch("model");const primary=h.primary.find(button=>button.dataset.tab==="change");primary.focus();assert.equal(h.key(h.editor,primary,"ArrowRight"),false);assert.equal(h.context.tab,"model");assert.equal(h.document.activeElement,primary);
  for(const [start,key,expected]of [["review","ArrowRight","repository-changes"],["repository-changes","ArrowLeft","review"],["review","End","repository-changes"],["repository-changes","Home","review"]]){h.switch(start);const button=h.comparison.find(button=>button.dataset.comparisonTab===start);assert.equal(h.key(h.local,button,key),true);assert.equal(h.context.tab,expected);assert.equal(h.document.activeElement,h.comparison.find(button=>button.dataset.comparisonTab===expected));}
  h.get("comparison-code-tab").onclick();assert.equal(h.context.tab,"repository-changes");h.get("comparison-model-tab").onclick();assert.equal(h.context.tab,"review");
  const outsider=h.primary[0],before=h.context.tab;assert.equal(h.key(h.local,outsider,"ArrowRight"),false);assert.equal(h.context.tab,before);
});

test("palette generic Changes resumes while Model and Code entries are explicit",()=>{
  const h=harness(),commands=h.read("paletteCommands"),run=label=>{const found=commands.filter(([name])=>name===label);assert.equal(found.length,1,label);found[0][1]();};
  run("Open Code changes");assert.equal(h.context.tab,"repository-changes");h.switch("model");run("Open Changes");assert.equal(h.context.tab,"repository-changes");run("Open Model changes");assert.equal(h.context.tab,"review");assert.equal(h.document.activeElement,h.get("comparison-model-tab"));
});

test("switching away relocates only focus hidden by the comparison navigation",()=>{
  const h=harness();h.switch("review");const inner=h.addControl("model-change-choice","review");inner.focus();h.switch("repository-changes");assert.equal(h.document.activeElement,h.get("comparison-code-tab"));assert.ok(h.document.activeElement.getClientRects().length);
  h.get("comparison-code-tab").focus();h.switch("evidence");assert.equal(h.document.activeElement,h.primary.find(button=>button.dataset.tab==="evidence"));assert.ok(h.document.activeElement.getClientRects().length);
  h.switch("repository-changes");const outside=h.addControl("outside-layout-button","body");outside.focus();h.switch("review");assert.equal(h.document.activeElement,outside);h.switch("model");assert.equal(h.document.activeElement,outside);
});

test("presentation switches preserve case, runtime, exact model and repository selections and saved case preferences",()=>{
  const h=harness(),before=h.state(),preferences=JSON.stringify([...h.context.caseViews]);h.get("unsent-owner-answer").value="draft answer";
  for(const tab of ["repository-changes","repository-changes","review","evidence","code","review"])h.switch(tab);
  assert.equal(h.state(),before);assert.equal(JSON.stringify([...h.context.caseViews]),preferences);assert.equal(h.get("unsent-owner-answer").value,"draft answer");assert.ok(h.calls.filter(([kind])=>kind==="area").some(([,name])=>name==="repository-changes"));
  h.switch(h.context.caseViews.get("case-A").tab);assert.equal(h.context.tab,"review");h.switch("model");h.open("review");assert.equal(h.context.tab,"review","an explicitly restored model Changes destination updates the last comparison view");
});

test("compact drawer dismissal applies to the local comparison tablist without saving pane preferences",()=>{
  const {harness:focusHarness}=require(process.env.EIJA_FOCUS_LAYOUT_HELPER||path.join(__dirname,"focus-layout.test.cjs"));const shell=fs.readFileSync(path.join(web,"shell.js"),"utf8");
  for(const focused of [false,true]){const h=focusHarness({code:shell,compact:true});if(focused)h.shell.focusWorkspace(true);const saved=h.stored();h.shell.toggle("inspector",true);h.shell.toggle("panel",true);h.get("comparison-tabs").dispatch("focusin");h.assertPane("explorer",false);h.assertPane("inspector",false);h.assertPane("panel",true);assert.deepEqual(h.stored(),saved);assert.equal(h.shell.isFocused(),focused);}
});

test("resume oracle rejects replacing the actual last-view route with the primary model route",()=>{
  const guard='name==="review"?lastComparisonTab:name';assert.equal(app.split(guard).length,2);assert.throws(()=>assertResumes(app.replace(guard,"name")),assert.AssertionError);
});

function assertDestinationFocus(code=app){
  const h=harness(code),before=h.state(),preferences=JSON.stringify([...h.context.caseViews]);
  h.switch("repository-changes");
  for(const name of ["model","change","impact","review","code","try","evidence","visual","source"]){
    h.document.activeElement=h.document.body;h.destination(name);
    const expected=name==="review"?"repository-changes":name,primary=h.primary.find(button=>button.dataset.tab===(name==="review"?"review":name));
    assert.equal(h.context.tab,expected);assert.equal(h.document.activeElement,primary||h.get(name),name+" destination gets visible focus");assert.ok(h.document.activeElement.getClientRects().length);
    const auxiliary=["impact","visual","source"].includes(name);assert.equal(h.get("workspace-destination").hidden,!auxiliary);
    assert.equal(h.primary.filter(button=>button.getAttribute("aria-current")==="page").length,auxiliary?0:1);
    for(const button of h.primary){assert.equal(button.tabIndex,0);assert.equal(button.getAttribute("role"),null);assert.equal(button.getAttribute("aria-selected"),null);}
  }
  assert.equal(h.state(),before);assert.equal(JSON.stringify([...h.context.caseViews]),preferences);
  const tab=h.context.tab,focused=h.document.activeElement;h.destination("unknown-destination");assert.equal(h.context.tab,tab);assert.equal(h.document.activeElement,focused);
}

test("all nine Workspace app destinations focus visible native navigation or the auxiliary region without changing subject",()=>assertDestinationFocus());

test("destination-focus oracle rejects removing focus from the actual shared destination handler",()=>{
  const original=fragment(app,"function openWorkDestination(","function switchTab("),focus='if(target?.getClientRects().length)target.focus();';assert.equal(original.split(focus).length,2);
  assert.throws(()=>assertDestinationFocus(app.replace(original,original.replace(focus,""))),assert.AssertionError);
});

test("actual palette entry refuses nesting with Workspace and edit dialogs before rendering commands",()=>{
  const code=fragment(app,"function openPalette()",'$("open-palette").onclick');
  for(const activeDialog of ["workspace-dialog","edit-preview","other-dialog",null]){
    const calls=[],search={value:"old",focus:()=>calls.push("focus")},palette={showModal:()=>calls.push("show")};
    const context={document:{querySelector:selector=>{assert.equal(selector,"dialog[open]");return activeDialog?{id:activeDialog}:null;}},$:id=>id==="palette-search"?search:palette,filterCommands:()=>calls.push("render")};
    vm.createContext(context);vm.runInContext(code,context);context.openPalette();
    assert.deepEqual(calls,activeDialog?[]:["render","show","focus"]);assert.equal(search.value,activeDialog?"old":"");
  }
});
