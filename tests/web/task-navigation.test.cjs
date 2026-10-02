"use strict";
// Actual app projections with controlled DOM/transport boundaries; no browser/layout claim.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const app=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
class Element{
  constructor(tag="div"){this.tag=tag;this.children=[];this.dataset={};this.attributes={};this.hidden=false;this.open=false;this.value="";this.ownText="";this.events={};}
  set textContent(value){this.ownText=String(value);this.children=[];}get textContent(){return this.ownText+this.children.map(node=>node.textContent).join("\n");}
  append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.ownText="";this.children=[...nodes];}get childElementCount(){return this.children.length;}
  setAttribute(key,value){this.attributes[key]=String(value);}getAttribute(key){return this.attributes[key];}removeAttribute(key){delete this.attributes[key];}
  querySelector(){return null;}addEventListener(name,fn){this.events[name]=fn;}contains(){return false;}focus(){this.focused=true;}
}
const all=node=>[node,...node.children.flatMap(all)],freeze=value=>{if(value&&typeof value==="object"){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
function harness(code=app){
  const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);},writes=[],reveals=[],opens=[],references=[];
  const transition={id:"T",action:"Send",role:"Owner",from_state:"A",to_state:"B",guards:["authorized"],required_effects:["Audit"],forbidden_effects:[]};
  const model=freeze({states:["A","B"],transitions:[transition]});
  const s={current:{case:{id:"case-A",version:4,stage:"PREVIEW",candidate:model,baseline:model},packet:{eligible:false,blockers:["SOURCE_REVIEW_REQUIRED","RUNTIME_EVIDENCE_UNKNOWN"]}},workbench:{pack:{id:"p",digest:"p-digest"},model,language:{terms:[{id:"TERM",label:"Declared term",definition:"One declared concept",refs:["transition:T"],binds:["repo://src/x.py#X"]}]},roles:[{id:"Owner"}],laws:[{id:"L",code:"LAW_X"}],connection:{status:"connected",lint:{verdict:"NOT_RUN",findings:[]}}},status:{trusted_fixture:false},inspectorSelection:{kind:"transition",id:"T"},editId:"T",modelView:"working",historyModel:null,historyLabel:"",tab:"model",impactSequence:0,lastDiagnostic:null,affordanceData:{affordances:[]},document:{activeElement:null},$:get,
    sessionStorage:{getItem:()=>null,setItem:(key,value)=>writes.push([key,value])},el:(tag,text,cls)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;},
    EijaTree:{setVisible:(root,visible)=>root.hidden=!visible,reveal:()=>true},EijaShell:{reveal:key=>reveals.push([s.tab,key]),bottom:(id,options)=>opens.push({id,options}),renderEvidence:()=>{}},EijaCanvas:{entries:()=>[]},
    api:()=>{throw Error("Presentation must not call transport");},notice:()=>{},switchTab:name=>{s.tab=name;},renderCanvas:()=>{},renderEvidenceContext:()=>{},currentComparisonSelection:()=>s.comparisonSelection||null,followReference:ref=>references.push(ref)};
  vm.createContext(s);
  for(const [start,end]of [["let navigatorMode=","function fillStates("],["class ApiError","async function api("],["function reportError(","function clearDiagnostic("],["function workingModel()","function renderCanvas()"],["function selectTransition(","function cancelDraft("],["function showSelection(","function followReference("],["function renderProblems()","function commitChoice("]]){
    const from=code.indexOf(start),to=code.indexOf(end,from);assert.ok(from>=0&&to>from,start);vm.runInContext(code.slice(from,to),s);
  }
  return {s,get,writes,reveals,opens,references,model};
}
test("task navigator defaults follow destinations; an explicit Domain pin survives every destination",()=>{
  const h=harness();for(const tab of ["model","review","evidence","code","change","try"]){h.s.tab=tab;h.s.renderNavigator();assert.equal(h.get("domain-tree").hidden,tab!=="model");assert.equal(h.get("task-navigator").hidden,tab!=="review");assert.equal(h.get("navigator-context").hidden,["model","review"].includes(tab));}
  h.get("navigator-mode").onchange({target:{value:"domain"}});for(const tab of ["review","evidence","code","model"]){h.s.tab=tab;h.s.renderNavigator();assert.equal(h.get("domain-tree").hidden,false);assert.equal(h.get("task-navigator").hidden,true);assert.equal(h.get("navigator-context").hidden,true);}
  assert.deepEqual(h.writes,[["eija-ui-navigator","domain"]]);h.get("navigator-mode").onchange({target:{value:"task"}});h.s.tab="review";h.s.renderNavigator();assert.equal(h.get("task-navigator").hidden,false);
});
test("task context preserves deliberate detail opening until context changes and uses only declared references",()=>{
  const h=harness();h.s.tab="evidence";h.s.inspectorSelection={kind:"term",id:"TERM"};h.s.renderNavigator();const detail=all(h.get("navigator-context")).find(node=>node.tag==="details");detail.open=true;
  h.s.renderNavigator();assert.equal(all(h.get("navigator-context")).find(node=>node.tag==="details"),detail);assert.equal(detail.open,true);
  const refs=all(detail).filter(node=>node.tag==="button");assert.deepEqual(refs.map(node=>node.textContent),["transition:T","repo://src/x.py#X"]);refs.forEach(node=>node.onclick());assert.deepEqual(h.references,refs.map(node=>node.textContent));
  assert.match(h.get("navigator-context").textContent,/not a per-concept verdict/);h.s.current.case.version=5;h.s.renderNavigator();assert.notEqual(all(h.get("navigator-context")).find(node=>node.tag==="details"),detail);assert.match(h.get("navigator-context").textContent,/revision 5/);
});
test("a disappeared or cross-case selection does not display old bindings as current",()=>{
  const h=harness();h.s.tab="code";h.s.inspectorSelection={kind:"term",id:"TERM"};h.s.renderNavigator();assert.match(h.get("navigator-context").textContent,/repo:\/\//);
  h.s.current.case={...h.s.current.case,id:"case-B",version:1};h.s.inspectorSelection=null;h.s.renderNavigator();assert.doesNotMatch(h.get("navigator-context").textContent,/repo:\/\/|Declared term/);assert.match(h.get("navigator-context").textContent,/No model concept selected/);
});
test("comparison context stays distinct from an older model selection and returns to the actual Changes view",()=>{
  const h=harness();h.s.tab="evidence";h.s.comparisonSelection={case:"case-A",revision:4,kind:"transition",id:"REMOVED"};h.s.renderNavigator();assert.match(h.get("navigator-context").textContent,/Selected change: transition · REMOVED/);
  const detail=all(h.get("navigator-context")).find(node=>node.tag==="details"&&node.children[0].textContent.startsWith("Model inspector:"));assert.ok(detail);assert.equal(detail.open,false);assert.match(detail.children[0].textContent,/transition · T/);all(h.get("navigator-context")).find(node=>node.tag==="button"&&node.textContent==="Return to selected change").onclick();assert.equal(h.s.tab,"review");assert.equal(h.s.inspectorSelection.id,"T");assert.equal(h.s.comparisonSelection.id,"REMOVED");
});
test("concept inspector hides an unrelated transition editor without changing unsent fields",()=>{
  const h=harness();h.s.renderEditor();h.get("model-source").value="unsent destination";h.s.inspectorSelection={kind:"term",id:"TERM"};h.s.renderSelectionDetail();assert.equal(h.get("transition-inspector").hidden,true);assert.match(h.get("selection-detail").textContent,/Declared term/);assert.doesNotMatch(h.get("selection-detail").textContent,/Send/);assert.equal(h.get("model-source").value,"unsent destination");assert.equal(h.s.editId,"T");
  h.s.inspectorSelection={kind:"transition",id:"T"};h.s.renderSelectionDetail();assert.equal(h.get("transition-inspector").hidden,false);assert.match(h.get("selection-detail").textContent,/A → B/);assert.equal(h.get("model-source").value,"unsent destination");assert.doesNotMatch(h.get("transition-details").textContent,/Send/);assert.match(h.get("transition-details").textContent,/authorized/);
});
test("state and transition reveal occurs in destination Model without overwriting originating area choices",()=>{
  for(const [kind,item]of [["state",{id:"A"}],["transition",harness().model.transitions[0]]]){
    const h=harness();h.s.tab="evidence";h.s.showSelection(kind,item);assert.equal(h.s.tab,"model");assert.ok(h.reveals.length>0);assert.ok(h.reveals.every(([area,pane])=>area==="model"&&pane==="inspector"));assert.deepEqual(h.writes,[]);
  }
});
test("rule-table selection changes destination before the temporary Inspector reveal",()=>{
  const h=harness(),line=app.split("\n").find(line=>line.includes('choose.onclick = () => {')&&line.includes('selectTransition(transition.id)'));assert.ok(line);h.s.tab="impact";h.s.transition=h.model.transitions[0];const fn=line.slice(line.indexOf('() => {'),line.indexOf('; action.append'));
  vm.runInContext('('+fn+')()',h.s);assert.equal(h.s.tab,"model");assert.ok(h.reveals.every(([area])=>area==="model"));assert.equal(h.s.inspectorSelection.id,"T");
});
test("the actual palette transition command exposes and focuses the picker without choosing or editing",()=>{
  const h=harness(),line=app.split("\n").find(line=>line.includes('["Select a transition",'));assert.ok(line);const entries=vm.runInContext("["+line.trim()+"]",h.s);h.get("transition-inspector").hidden=true;const before=JSON.stringify(h.model);entries[0][1]();assert.equal(h.s.tab,"model");assert.equal(h.get("transition-inspector").hidden,false);assert.equal(h.get("transition-select").focused,true);assert.equal(JSON.stringify(h.model),before);assert.deepEqual(h.writes,[]);
});
test("opening the transition picker after concept inspection reconciles its heading without resetting drafts",()=>{
  const h=harness();h.s.renderEditor();h.get("model-source").value="unsent choice";h.s.inspectorSelection={kind:"law",id:"L"};h.s.renderSelectionDetail();assert.match(h.get("selection-detail").textContent,/LAW_X/);h.s.openTransitionPicker();assert.equal(h.s.inspectorSelection.kind,"transition");assert.equal(h.s.inspectorSelection.id,"T");assert.match(h.get("selection-detail").textContent,/Send/);assert.doesNotMatch(h.get("selection-detail").textContent,/LAW_X/);assert.equal(h.get("transition-inspector").hidden,false);assert.equal(h.get("model-source").value,"unsent choice");
});
test("Problems deduplicates one code while preserving both origins, all blockers and exact diagnostic refs",()=>{
  const h=harness();h.s.lastDiagnostic={code:"EDIT_REFUSED",message:"EDIT_REFUSED: unchanged",details:{codes:["LAW_A","EDIT_REFUSED"],refs:["law:L","repo://x.py#f"]}};const before=JSON.stringify(h.s.current.packet);h.s.renderProblems();
  const rows=h.get("problems").children.filter(node=>node.dataset.problemCode);assert.equal(rows.filter(node=>node.dataset.problemCode==="SOURCE_REVIEW_REQUIRED").length,1);const source=rows.find(node=>node.dataset.problemCode==="SOURCE_REVIEW_REQUIRED");assert.deepEqual(JSON.parse(source.dataset.problemOrigins),["Implementation identity","Current packet blocker"]);assert.match(source.textContent,/Owner review of changed implementation/);
  assert.deepEqual(rows.map(node=>node.dataset.problemCode),["SOURCE_LINK_LINT","SOURCE_REVIEW_REQUIRED","RUNTIME_EVIDENCE_UNKNOWN","EDIT_REFUSED","LAW_A"]);assert.equal(String(h.get("problem-count").textContent),"5");assert.equal(String(h.get("focus-problem-count").textContent),"5");assert.match(h.get("problems").textContent,/NOT_RUN/);assert.match(h.get("status-evidence").textContent,/blocked · human UNKNOWN/);assert.equal(JSON.stringify(h.s.current.packet),before);assert.deepEqual(h.opens,[]);
  const refs=h.get("problems").children.find(node=>node.className==="diagnostic-references");all(refs).filter(node=>node.tag==="button").forEach(node=>node.onclick());assert.deepEqual(h.references,["law:L","repo://x.py#f"]);
});
test("new operation refusal temporarily opens Problems and preserves the exact server diagnostic",()=>{
  const h=harness();h.s.reportError(Object.assign(new Error("Changed on server"),{code:"CASE_STALE",details:{codes:["EXPECTED_VERSION"],refs:["case:A"]}}));assert.equal(h.opens.length,1);assert.equal(h.opens[0].id,"problems-pane");assert.equal(h.opens[0].options.temporary,true);assert.equal(JSON.parse(h.get("error-json").textContent).code,"CASE_STALE");assert.match(h.get("problems").textContent,/SOURCE_REVIEW_REQUIRED|EXPECTED_VERSION/);
});
test("clearing operation feedback never removes packet blockers or source-review restriction",()=>{
  const h=harness();h.s.lastDiagnostic={code:"OFFLINE",message:"Network failed",details:{codes:[],refs:[]}};h.s.renderProblems();h.s.lastDiagnostic=null;h.s.renderProblems();assert.doesNotMatch(h.get("problems").textContent,/Network failed/);assert.match(h.get("problems").textContent,/SOURCE_REVIEW_REQUIRED/);assert.match(h.get("problems").textContent,/RUNTIME_EVIDENCE_UNKNOWN/);assert.equal(String(h.get("problem-count").textContent),"3");
});
test("zero issues means zero, rather than counting the helpful empty-state sentence as a problem",()=>{
  const h=harness();h.s.status.trusted_fixture=true;h.s.workbench.connection.lint.verdict="PASS";h.s.current.packet.blockers=[];h.s.renderProblems();assert.equal(String(h.get("problem-count").textContent),"0");assert.match(h.get("problems").textContent,/No review blockers reported/);
});
test("negative control: dropping duplicate origins is detected even if a blocker still appears once",()=>{
  const marker='issue.origins.add(origin)';assert.ok(app.includes(marker));const h=harness(app.replace(marker,'if(!issue.origins.size)issue.origins.add(origin)'));h.s.renderProblems();const source=h.get("problems").children.find(node=>node.dataset.problemCode==="SOURCE_REVIEW_REQUIRED");assert.throws(()=>assert.deepEqual(JSON.parse(source.dataset.problemOrigins),["Implementation identity","Current packet blocker"]),assert.AssertionError);
});
