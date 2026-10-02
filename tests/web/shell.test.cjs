"use strict";
// Isolated presentation/adapter checks. These do not claim browser or human validation.
const {test}=require("node:test"),assert=require("node:assert/strict"),path=require("node:path"),fs=require("node:fs"),vm=require("node:vm");
const web=path.join(__dirname,"../../src/eija_studio/resources/web"),shell=require(path.join(web,"shell.js")),review=require(path.join(web,"review.js"));
class Node {
  constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.attributes={};this.textContent="";this.events={};}
  append(...items){this.children.push(...items);}replaceChildren(...items){this.children=items;}
  setAttribute(key,value){this.attributes[key]=String(value);}getAttribute(key){return this.attributes[key];}removeAttribute(key){delete this.attributes[key];}
  addEventListener(key,value){this.events[key]=value;}querySelector(){return this.children.find(n=>n.tag==="svg")||null;}
  getBoundingClientRect(){return {width:800,height:400};}
}
const flatten=node=>[node,...node.children.flatMap(flatten)],text=node=>flatten(node).map(n=>n.textContent).join("\n");
function dom(){const nodes=new Map();global.document={createElement:tag=>new Node(tag),getElementById:id=>{if(!nodes.has(id))nodes.set(id,new Node("div"));return nodes.get(id);}};return id=>document.getElementById(id);}
function freeze(value){if(value&&typeof value==="object"){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
const old=freeze({states:["A","B","Gone"],initial_state:"A",transitions:[{id:"T",action:"Send",role:"owner",from_state:"A",to_state:"B",guards:["two","one"],required_effects:[],forbidden_effects:[]},{id:"R",action:"Remove",role:"owner",from_state:"B",to_state:"Gone",guards:[]}]});
const next=freeze({states:["A","B","New"],initial_state:"A",transitions:[{id:"T",action:"Send",role:"reviewer",from_state:"A",to_state:"New",guards:["one","two"],required_effects:[],forbidden_effects:[]},{id:"N",action:"Add",role:"owner",from_state:"New",to_state:"B",guards:[]}]});
test("semantic review identifies changed fields and added/removed elements without altering snapshots",()=>{
  const before=JSON.stringify({old,next}),diff=review.compare(old,next);assert.deepEqual(diff.addedStates,["New"]);assert.deepEqual(diff.removedStates,["Gone"]);
  assert.deepEqual(diff.transitions.map(t=>[t.id,t.status]),[["N","added"],["R","removed"],["T","changed"]]);assert.deepEqual(diff.transitions[2].changes.map(x=>x[0]),["role","to_state"]);assert.equal(JSON.stringify({old,next}),before);
});
test("changes review connects exact source bindings and retains blocked evidence as literal text",()=>{
  dom();const root=new Node("div"),opened=[],hostile="repo://<script>#x";
  review.render(root,{case:{request:"Change send",selected_meaning:"m",version:3,baseline:old,candidate:next,transactions:[]},packet:{impact:{complete:false,affected:[]},blockers:["SOURCE_REVIEW_REQUIRED"],formal_evidence:[{kind:"implementation_conformance",status:"NOT_RUN"}]}},{terms:[{refs:["transition:T"],binds:[hostile]}],openReference:ref=>opened.push(ref)});
  assert.match(text(root),/BEFORE · BASELINE/);assert.match(text(root),/AFTER · CANDIDATE/);assert.match(text(root),/SOURCE_REVIEW_REQUIRED/);assert.match(text(root),/NOT_RUN/);assert.match(text(root),/Human comprehension: UNKNOWN/);
  flatten(root).find(n=>n.tag==="button"&&n.textContent===hostile).onclick();assert.deepEqual(opened,[hostile]);assert.ok(!flatten(root).some(n=>n.tag==="script"));
});
test("read-only source preserves CRLF line content and snapshot identity with hostile markup inert",()=>{
  const get=dom(),data=freeze({status:"connected",text:'def f():\r\n    return "<img src=x>"\r\n',lines:{start:41,end:42},symbol_lines:{start:41,end:42},path:"src/a.py",symbol:"f",reference:"repo://src/a.py#f",file_hash:"filehash",snippet_hash:"snippethash",source_hash:"sourcehash",graph_hash:"graphhash",fragment_resolution:"python_ast",scope:"Captured only",truncated:true});
  shell.renderSource(data);assert.deepEqual(shell.sourceLines(data),[{number:41,text:"def f():"},{number:42,text:'    return "<img src=x>"'}]);assert.match(text(get("source-reader")),/41/);assert.match(text(get("source-reader")),/<img src=x>/);assert.ok(!flatten(get("source-reader")).some(n=>n.tag==="img"));assert.match(text(get("source-metadata")),/excerpt truncated/);assert.match(text(get("source-metadata")),/filehash/);
});
test("unavailable source clears stale code and malformed source ranges fail explicitly",()=>{
  const get=dom();get("source-reader").append(new Node("code"));shell.renderSource({status:"unavailable",reason:"Snapshot missing"});assert.match(text(get("source-reader")),/UNAVAILABLE/);assert.match(text(get("source-reader")),/Snapshot missing/);assert.ok(!flatten(get("source-reader")).some(n=>n.tag==="code"));assert.throws(()=>shell.sourceLines({text:"x",lines:{start:0}}),/valid line range/);
});
test("latest source selection wins when read responses arrive in reverse order",async()=>{
  const source=fs.readFileSync(path.join(web,"app.js"),"utf8"),fn=source.slice(source.indexOf("async function openSource("),source.indexOf('$("source-open-form").onsubmit'));
  const pending=[],rendered=[],sandbox={sourceSequence:0,sourceHistory:[],sourceHistoryIndex:-1,switchTab:()=>{},EijaShell:{sourceLoading:()=>{},renderSource:x=>rendered.push(x.reference),sourceError:()=>{}},api:()=>new Promise(resolve=>pending.push(resolve)),$:()=>({disabled:true}),notice:()=>{}};vm.createContext(sandbox);vm.runInContext(fn,sandbox);
  const first=sandbox.openSource("repo://first.py#A"),second=sandbox.openSource("repo://second.py#B");pending[1]({status:"connected",reference:"repo://second.py#B"});await second;pending[0]({status:"connected",reference:"repo://first.py#A"});await first;assert.deepEqual(rendered,["repo://second.py#B"]);assert.deepEqual(Array.from(sandbox.sourceHistory),["repo://second.py#B"]);
});
test("history uses the server protected boundary and exposes previews without changing the current model",()=>{
  const get=dom(),seen=[],history=freeze({status:"ready",version:8,cursor:1,selection:{label:"Send for review",model:old,transactions:[],semantic_hash:"s0"},edits:[{index:1,model:next,transaction:{kind:"retarget_transition"},semantic_hash:"s1"}],redo:[],events:[],can_undo:true});
  shell.renderHistory({case:{version:8}},history,(model,label)=>seen.push({model,label}));assert.match(text(get("case-history")),/protected/);assert.match(text(get("case-history")),/read only/);flatten(get("case-history")).filter(n=>n.tag==="button")[1].onclick();assert.equal(seen[0].model,next);assert.match(seen[0].label,/applied/);assert.equal(history.cursor,1);
});
test("missing history and unrun evidence never become successful checks",()=>{
  const get=dom();shell.renderHistory({case:{version:1}},{status:"unavailable",reason:"404"},()=>{});assert.match(text(get("case-history")),/Undo and redo are disabled/);shell.renderEvidence(get("evidence-summary"),null);assert.match(text(get("evidence-summary")),/NOT_RUN/);assert.match(text(get("evidence-summary")),/UNKNOWN/);assert.doesNotMatch(text(get("evidence-summary")),/PASS/);
});
test("canvas viewport starts readable, fits with correct aspect and zooms without altering the server model",()=>{
  const get=dom(),svg=new Node("svg");svg.setAttribute("viewBox","0 0 2000 500");svg.dataset={initialX:"50",initialY:"75"};get("model-canvas").append(svg);get("model").hidden=false;
  shell.mountCanvas("test-case");assert.equal(get("canvas-zoom").textContent,"100%");let values=svg.getAttribute("viewBox").split(" ").map(Number);assert.equal(values[2]/values[3],2);assert.equal(values[2],800);
  shell.fit();assert.equal(get("canvas-zoom").textContent,"40%");values=svg.getAttribute("viewBox").split(" ").map(Number);assert.equal(values[2],2000);assert.equal(values[3],1000);shell.zoom(2);assert.equal(get("canvas-zoom").textContent,"80%");assert.equal(svg.getAttribute("viewBox").split(" ")[2],"1000");
});

test("returning from overview restores readable vertical scale around the selected model location",()=>{
  const get=dom(),svg=new Node("svg");svg.setAttribute("viewBox","0 0 600 950");svg.dataset={initialX:"50",initialY:"75",focusX:"150",focusY:"375",direction:"TB"};get("model-canvas").append(svg);get("model").hidden=false;
  shell.mountCanvas("vertical-case");let box=svg.getAttribute("viewBox").split(" ").map(Number);assert.equal(get("canvas-zoom").textContent,"100%");assert.equal(box[0]+box[2]/2,245);assert.equal(box[1],330);
  shell.fit();assert.ok(Number.parseInt(get("canvas-zoom").textContent)<85);assert.match(get("canvas-zoom").title,/Overview scale/);shell.readable();assert.equal(get("canvas-zoom").textContent,"100%");assert.equal(svg.getAttribute("viewBox").split(" ")[3],"400");
});

test("compact reflow closes drawers without overwriting desktop visibility preferences",()=>{
  const get=dom(),classes=new Set();document.documentElement={style:{setProperty(){}}};document.body={dataset:{},classList:{toggle(key,on){if(on)classes.add(key);else classes.delete(key);}}};
  shell.resizeMode(false);shell.toggle("explorer",true);shell.toggle("inspector",false);shell.toggle("panel",true);
  shell.resizeMode(true);assert.ok(classes.has("explorer-collapsed"));assert.ok(classes.has("inspector-collapsed"));assert.ok(classes.has("panel-collapsed"));assert.equal(document.body.dataset.compactExplorer,"false");assert.equal(get("drawer-backdrop").hidden,true);
  shell.toggle("explorer",true);assert.equal(document.body.dataset.compactExplorer,"true");assert.equal(get("drawer-backdrop").hidden,false);
  shell.toggle("inspector",true);assert.equal(document.body.dataset.compactExplorer,"false");assert.equal(document.body.dataset.compactInspector,"true");
  shell.resizeMode(false);assert.ok(!classes.has("explorer-collapsed"));assert.ok(classes.has("inspector-collapsed"));assert.ok(!classes.has("panel-collapsed"));assert.equal(get("drawer-backdrop").hidden,true);assert.equal(get("explorer-resizer").hidden,false);
  shell.resizeMode(true);assert.equal(document.body.dataset.compactInspector,"false");assert.equal(get("drawer-backdrop").hidden,true);
});

test("a short canvas preserves the reported physical scale instead of silently shrinking to a logical minimum",()=>{
  const get=dom(),svg=new Node("svg"),surface=get("model-canvas");surface.getBoundingClientRect=()=>({width:320,height:62});svg.setAttribute("viewBox","0 0 600 950");svg.dataset={initialX:"50",initialY:"75",direction:"TB"};surface.append(svg);get("model").hidden=false;
  const actualScale=()=>{const box=svg.getAttribute("viewBox").split(" ").map(Number);return Math.min(320/box[2],62/box[3]);};
  shell.mountCanvas("short-viewport");assert.equal(get("canvas-zoom").textContent,"100%");assert.equal(actualScale(),1);
  shell.zoom(1.2);assert.equal(get("canvas-zoom").textContent,"120%");assert.ok(Math.abs(actualScale()-1.2)<1e-10);
  shell.fit();assert.ok(Math.abs(actualScale()*100-Number.parseInt(get("canvas-zoom").textContent))<=.5);
  shell.readable();assert.equal(actualScale(),1);assert.equal(svg.getAttribute("viewBox").split(" ")[3],"62");
});

test("the concept inspector follows the task while explicit area overrides and modelling preferences survive",()=>{
  const get=dom(),classes=new Set();document.documentElement={style:{setProperty(){}}};document.body={dataset:{},classList:{toggle(key,on){if(on)classes.add(key);else classes.delete(key);}}};
  shell.resizeMode(false);shell.setArea("model");shell.toggle("inspector",true);assert.ok(!classes.has("inspector-collapsed"));
  shell.setArea("evidence");assert.ok(classes.has("inspector-collapsed"));shell.toggle("inspector",true);assert.ok(!classes.has("inspector-collapsed"));
  shell.setArea("try");assert.ok(classes.has("inspector-collapsed"));shell.setArea("model");assert.ok(!classes.has("inspector-collapsed"));shell.setArea("evidence");assert.ok(!classes.has("inspector-collapsed"));shell.setArea("model");
});
function focusHarness(){
  const code=fs.readFileSync(path.join(web,"app.js"),"utf8"),functions=code.slice(code.indexOf("function captureTaskFocus()"),code.indexOf("async function task("));
  const focused=[],nodes=new Map(),body={},documentElement={},document={body,documentElement,activeElement:body,querySelectorAll:selector=>[...nodes.values()].filter(n=>selector==="[data-action]"?n.dataset.action:n.dataset.meaning)};
  const node=(id,options={})=>{const value={id,disabled:false,dataset:{},getClientRects:()=>[{}],focus:()=>focused.push(id),...options};nodes.set(id,value);return value;};
  node("case-title");const sandbox={document,$:id=>nodes.get(id)};vm.createContext(sandbox);vm.runInContext(functions,sandbox);return {node,document,focused,restore:sandbox.restoreTaskFocus};
}
test("case creation deliberately advances focus from the hidden create form to interpretation request",()=>{
  const h=focusHarness();h.node("create",{getClientRects:()=>[]});h.node("propose");h.restore({id:"create"});assert.deepEqual(h.focused,["propose"]);
});
test("runtime rerender restores the equivalent action instead of dropping focus to the document",()=>{
  const h=focusHarness();h.node("new-submit-button",{dataset:{action:"Submit"}});h.restore({action:"Submit"});assert.deepEqual(h.focused,["new-submit-button"]);
});
test("disabled approval advances focus to apply without activating it, while completed meaning returns to case context",()=>{
  const h=focusHarness();h.node("approve",{disabled:true});h.node("apply");h.restore({id:"approve"});assert.deepEqual(h.focused,["apply"]);
  h.node("meaning",{dataset:{meaning:"chosen"},disabled:true});h.restore({meaning:"chosen"});assert.deepEqual(h.focused,["apply","case-title"]);
});
test("async completion never steals a focus the user moved to another field",()=>{
  const h=focusHarness();h.document.activeElement=h.node("request");h.restore({id:"create"});assert.deepEqual(h.focused,[]);h.document.activeElement=h.document.body;h.restore({});assert.deepEqual(h.focused,[]);
});

function editorHarness(){
  const get=dom(),code=fs.readFileSync(path.join(web,"app.js"),"utf8"),calls=[],notices=[];
  const transition=(id,action,role="Teacher")=>({id,action,role,from_state:"Draft",to_state:"Submitted",guards:[],required_effects:[],forbidden_effects:[]});
  const modelA=freeze({states:["Draft","Submitted"],transitions:[transition("TR-SAVE","Save")]}),modelB=freeze({states:["Draft","Submitted"],transitions:[transition("TR-APPROVE","Approve","Principal")]}),data={A:{case:{id:"A",version:3,stage:"EDITING",candidate:modelA,baseline:modelA}},B:{case:{id:"B",version:8,stage:"EDITING",candidate:modelB,baseline:modelB}}};
  const sandbox={current:data.A,affordanceData:{affordances:[]},caseHistory:null,workbench:{pack:{id:"sample"},language:{terms:[{id:"intent",label:"Intent",definition:"Declared intent"}]},roles:[],laws:[],model:modelA},editId:"TR-SAVE",inspectorSelection:{kind:"transition",id:"TR-SAVE"},modelView:"working",historyModel:null,historyLabel:"",canvasDirection:"AUTO",tab:"model",caseViews:new Map(),busy:false,lastDiagnostic:null,
    $:get,el:(tag,value,cls)=>{const node=new Node(tag);if(value!==undefined)node.textContent=value;if(cls)node.className=cls;return node;},
    EijaCanvas:require(path.join(web,"canvas.js")),notice:value=>notices.push(value),renderProblems:()=>{get("problems").textContent=sandbox.lastDiagnostic?.message||"No active request error";},cases:async()=>{},
    api:async(url,body)=>{calls.push({url,body});if(sandbox.failure)throw sandbox.failure;const parts=url.split("/");return parts.length===2?data[parts[1]]:parts[2]==="affordances"?{affordances:[]}:{case_id:parts[1],status:"ready"};}
  };
  vm.createContext(sandbox);
  for(const [start,end] of [["function clearDiagnostic()","function captureTaskFocus()"],["async function load(id)","async function command("],["function workingModel()","function renderCanvas()"],["function renderSelectionDetail()","function followReference("],["function cancelDraft()",'$("cancel-draft").onclick'],["async function refreshCurrentModel()","function filterCommands()"]])vm.runInContext(code.slice(code.indexOf(start),code.indexOf(end)),sandbox);
  sandbox.render=()=>{sandbox.renderEditor();sandbox.renderSelectionDetail();};
  return {sandbox,get,calls,notices,data};
}

test("case switches rebuild the inspector from that case's authoritative model and restore historical context",async()=>{
  const h=editorHarness(),s=h.sandbox,history=freeze({states:["Draft","Submitted"],transitions:[{...h.data.A.case.candidate.transitions[0],action:"Earlier save"}]});
  s.modelView="history";s.historyModel=history;s.historyLabel="Protected meaning";s.render();
  s.caseViews.set("B",{tab:"model",editId:"TR-APPROVE",inspectorSelection:{kind:"transition",id:"TR-APPROVE"},modelView:"working",canvasDirection:"TB"});
  await s.load("B");assert.equal(h.get("transition-select").value,"TR-APPROVE");assert.match(text(h.get("selection-detail")),/Approve/);assert.doesNotMatch(text(h.get("selection-detail")),/Earlier save/);assert.equal(h.get("selection-detail").dataset.eijaId,"sample.detail.transition.TR-APPROVE");
  await s.load("A");assert.equal(s.modelView,"history");assert.equal(s.historyModel,history);assert.match(text(h.get("selection-detail")),/Earlier save/);assert.equal(h.get("edit-role").disabled,true);assert.ok(h.calls.every(call=>call.body===undefined));
});

test("case-specific concept selection resolves current pack data and a missing selection clears old details",async()=>{
  const h=editorHarness(),s=h.sandbox;s.inspectorSelection={kind:"term",id:"intent"};s.render();await s.load("B");assert.match(text(h.get("selection-detail")),/Explore a concept/);assert.doesNotMatch(text(h.get("selection-detail")),/Declared intent/);
  await s.load("A");assert.match(text(h.get("selection-detail")),/Declared intent/);s.inspectorSelection={kind:"transition",id:"removed"};s.renderSelectionDetail();assert.equal(s.inspectorSelection,null);assert.match(text(h.get("selection-detail")),/Explore a concept/);
});

test("cancelling an unsent edit restores source target and role without sending or changing server state",()=>{
  const h=editorHarness(),s=h.sandbox,before=JSON.stringify(h.data);s.render();h.get("model-source").value="Submitted";h.get("target-state").value="Draft";h.get("transition-role").value="Agent";s.cancelDraft();
  assert.equal(h.get("model-source").value,"Draft");assert.equal(h.get("target-state").value,"Submitted");assert.equal(h.get("transition-role").value,"Teacher");assert.equal(h.calls.length,0);assert.equal(JSON.stringify(h.data),before);assert.equal(s.editId,"TR-SAVE");assert.match(h.notices.at(-1),/no transaction was sent/);
  s.busy=true;h.get("transition-role").value="Agent";s.cancelDraft();assert.equal(h.get("transition-role").value,"Agent","an in-flight commit is never presented as cancelled");
});

test("a failed refresh retains model and diagnostic; a successful retry removes stale errors and completes feedback",async()=>{
  const h=editorHarness(),s=h.sandbox;s.render();const before=s.current; s.lastDiagnostic={code:"REQUEST_FAILED",message:"Failed to fetch"};h.get("error-details").hidden=false;h.get("error-json").textContent=JSON.stringify(s.lastDiagnostic);s.renderProblems();s.failure=new Error("Connection unavailable");
  await assert.rejects(s.refreshCurrentModel(),/Connection unavailable/);assert.equal(s.current,before);assert.equal(s.editId,"TR-SAVE");assert.equal(h.get("error-details").hidden,false);assert.match(h.get("problems").textContent,/Failed to fetch/);
  delete s.failure;await s.refreshCurrentModel();assert.equal(s.current,before);assert.equal(s.lastDiagnostic,null);assert.equal(h.get("error-details").hidden,true);assert.equal(h.get("error-json").textContent,"");assert.doesNotMatch(h.get("problems").textContent,/Failed to fetch/);assert.match(h.notices.at(-1),/refreshed from the server/);assert.ok(h.calls.every(call=>call.body===undefined));
});
