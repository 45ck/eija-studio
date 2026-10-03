"use strict";
// Actual app projections with controlled DOM/transport boundaries; no browser/layout claim.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const app=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
const review=require("../../src/eija_studio/resources/web/review.js"),compare=require("../../src/eija_studio/resources/web/compare.js");
class Element{
  constructor(tag="div"){this.tag=tag;this.children=[];this.dataset={};this.attributes={};this.hidden=false;this.open=false;this.value="";this.ownText="";this.events={};this.queries=new Map();this.classList={toggle(){}};}
  set textContent(value){this.ownText=String(value);this.children=[];}get textContent(){return this.ownText+this.children.map(node=>node.textContent).join("\n");}
  append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.ownText="";this.children=[...nodes];}get childElementCount(){return this.children.length;}
  setAttribute(key,value){this.attributes[key]=String(value);}getAttribute(key){return this.attributes[key];}removeAttribute(key){delete this.attributes[key];}
  querySelector(selector){return this.queries.get(selector)||null;}addEventListener(name,fn){this.events[name]=fn;}contains(){return false;}focus(){this.focused=true;}getClientRects(){return this.hidden?[]:[{}];}
}
const all=node=>[node,...node.children.flatMap(all)],freeze=value=>{if(value&&typeof value==="object"){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
function harness(code=app){
  const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);},writes=[],reveals=[],opens=[],references=[];
  const transition={id:"T",action:"Send",role:"Owner",from_state:"A",to_state:"B",guards:["authorized"],required_effects:["Audit"],forbidden_effects:[]};
  const model=freeze({states:["A","B"],transitions:[transition]});
  // Navigation fixtures have no runtime inspection; execute the actual recovery renderer in that state.
  const s={runtimeAttempt:null,runtimeRuleInspection:null,current:{case:{id:"case-A",version:4,stage:"PREVIEW",candidate:model,baseline:model},packet:{eligible:false,blockers:["SOURCE_REVIEW_REQUIRED","RUNTIME_EVIDENCE_UNKNOWN"]}},workbench:{pack:{id:"p",digest:"p-digest"},model,language:{terms:[{id:"TERM",label:"Declared term",definition:"One declared concept",refs:["transition:T"],binds:["repo://src/x.py#X"]}]},roles:[{id:"Owner"}],laws:[{id:"L",code:"LAW_X"}],connection:{status:"connected",lint:{verdict:"NOT_RUN",findings:[]}}},status:{trusted_fixture:false},inspectorSelection:{kind:"transition",id:"T"},editId:"T",modelView:"working",historyModel:null,historyLabel:"",tab:"model",impactSequence:0,lastDiagnostic:null,affordanceData:{affordances:[]},document:{activeElement:null},$:get,
    editNeedsRefresh:new Map(),sessionStorage:{getItem:()=>null,setItem:(key,value)=>writes.push([key,value])},el:(tag,text,cls)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;},
    EijaTree:{setVisible:(root,visible)=>root.hidden=!visible,reveal:()=>true},EijaShell:{reveal:key=>reveals.push([s.tab,key]),bottom:(id,options)=>opens.push({id,options}),renderEvidence:()=>{}},EijaCanvas:{entries:()=>[]},
    api:()=>{throw Error("Presentation must not call transport");},notice:()=>{},switchTab:name=>{s.tab=name;},renderCanvas:()=>{},renderEvidenceContext:()=>{},currentComparisonSelection:()=>s.comparisonSelection||null,followReference:ref=>references.push(ref)};
  vm.createContext(s);
  for(const [start,end]of [["function runtimeRuleTarget(","function renderRuntimeFeedback("],["let navigatorMode=","function fillStates("],["class ApiError","async function api("],["function reportError(","function clearDiagnostic("],["function workingModel()","function renderCanvas()"],["function selectTransition(","function cancelDraft("],["function showSelection(","function followReference("],["function renderProblems()","function commitChoice("]]){
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
function subjectHarness(code=app){
  const h=harness(code),s=h.s,projected={tree:null,canvas:null},messages=[];
  Object.assign(s,{caseHistory:null,canvasDirection:"AUTO",comparisonViews:new Map(),comparison:null,comparisonSelection:null,EijaReview:review,EijaCompare:compare,
    EijaSource:{state:()=>({title:"Connected"}),render(){}},evidenceValue:value=>JSON.stringify(value),previewHistory(){},commitChoice(){throw Error("Navigation must not edit");},notice:text=>messages.push(text)});
  s.EijaTree.render=(_root,_workbench,model)=>{projected.tree=model;};s.EijaShell.mountCanvas=()=>{};s.EijaShell.renderHistory=()=>{};
  s.EijaCanvas.render=(_root,options)=>{projected.canvas=options;};
  for(const kind of ["history","baseline"])h.get("model-version").queries.set(`option[value="${kind}"]`,new Element("option"));
  h.get("rules-journeys").queries.set("summary",new Element("summary"));
  for(const [start,end]of [["function currentComparisonSelection()","function renderEvidencePacket("],["function renderCanvas()","function selectTransition("],["function renderRules()","function showSelection("],["function renderChanges()","let inspectorSelection = null;"]]){
    const from=code.indexOf(start),to=code.indexOf(end,from);assert.ok(from>=0&&to>from,start);vm.runInContext(code.slice(from,to),s);
  }
  const baseline=freeze({id:"m",initial_state:"A",states:["A","B"],transitions:[{...h.model.transitions[0],action:"Before send",to_state:"A"}]}),
    candidate=freeze({id:"m",initial_state:"A",states:["A","B","C"],transitions:[{...h.model.transitions[0],action:"Send",to_state:"C",role:"Agent"},{...h.model.transitions[0],id:"NEW",action:"New action",from_state:"C"}]}),
    historical=freeze({id:"m",initial_state:"B",states:["A","B"],transitions:[{...h.model.transitions[0],action:"Earlier send",from_state:"B",to_state:"A"}]});
  s.current.case={...s.current.case,baseline,candidate};s.workbench.pack={...s.workbench.pack,name:"Example",version:1};s.workbench.baseline_version=2;s.workbench.model=baseline;
  s.current.packet.subject={semantic:"candidate-semantic-identity"};
  s.historyModel=historical;s.historyLabel="Earlier semantic edit";
  return {...h,projected,messages,baseline,candidate,historical};
}
const ruleButton=(h,id)=>all(h.get("rule-table").children.find(row=>row.dataset.transitionId===id)).find(node=>node.tag==="button");
function assertCandidateSurface(h,id){
  assert.equal(h.s.tab,"model");assert.equal(h.s.modelView,"working");assert.equal(h.get("model-version").value,"working");assert.match(h.get("model-revision").textContent,/r4 · candidate/);
  assert.equal(h.projected.tree,h.candidate);assert.equal(h.projected.canvas.model,h.candidate);assert.equal(h.projected.canvas.selected,id);assert.equal(h.get("transition-select").value,id);
  assert.equal(h.s.inspectorSelection.id,id);assert.equal(h.get("evidence-subject").dataset.displayedModel,"working");assert.equal(h.get("evidence-subject").dataset.caseId,"case-A");assert.equal(h.get("evidence-subject").dataset.revision,"4");
  assert.match(h.get("model-empty").textContent,/Every edit is checked/);assert.equal(h.get("transition-select").focused,true);assert.ok(h.reveals.every(([area])=>area==="model"));
}
test("Rules uses the current candidate while historical or original previews remain available",()=>{
  for(const view of ["history","baseline"])for(const id of ["T","NEW"]){
    const h=subjectHarness();h.s.modelView=view;h.s.tab="impact";const before=JSON.stringify([h.s.current,h.historical]);h.s.renderWorkbench();
    assert.match(h.get("rules-subject").textContent,/Current candidate · case case-A · revision 4/);assert.match(h.get("rules-subject").textContent,/Model workspace shows/);
    assert.equal(h.get("rules-subject").dataset.semanticHash,"candidate-semantic-identity");assert.match(h.get("rules-subject").textContent,/Semantic candidate-se/);assert.match(h.get("rules-edit-help").textContent,/read-only preview/);
    assert.match(h.get("rule-table").textContent,/Agent/);assert.doesNotMatch(h.get("rule-table").textContent,/Earlier send|Before send/);
    assert.equal(h.get("rule-table").children.find(row=>row.dataset.transitionId===id).dataset.changeStatus,id==="NEW"?"added":"changed");
    ruleButton(h,id).onclick();assertCandidateSurface(h,id);assert.match(h.get("selection-detail").textContent,id==="T"?/A → C/:/C → B/);
    assert.equal(h.s.historyModel,h.historical);assert.equal(h.s.historyLabel,"Earlier semantic edit");assert.equal(JSON.stringify([h.s.current,h.historical]),before);
    h.s.modelView="history";h.s.renderWorkbench();assert.equal(h.projected.canvas.model,h.historical);assert.equal(h.projected.tree,h.historical);assert.equal(h.get("model-version").value,"history");
  }
});
test("initial Rules renders the loaded baseline without a case or transport and has an explicit empty state",()=>{
  const h=subjectHarness();h.s.current=null;h.s.historyModel=null;h.s.tab="impact";h.s.renderWorkbench();
  assert.match(h.get("rules-subject").textContent,/Loaded baseline · no change case · revision 2/);assert.match(h.get("rule-table").textContent,/Before send/);assert.match(h.get("state-flow").textContent,/Before send/);
  assert.equal(h.get("layout-node").children.length,2);assert.equal(h.get("rules-evidence").disabled,true);assert.match(h.get("impact-summary").textContent,/Baseline rules only/);
  assert.equal(h.get("rules-subject").dataset.semanticHash,"");assert.match(h.get("rules-edit-help").textContent,/baseline is read only/);
  ruleButton(h,"T").onclick();assert.equal(h.s.tab,"model");assert.equal(h.projected.canvas.model,h.baseline);assert.equal(h.projected.canvas.editable,false);assert.match(h.get("selection-detail").textContent,/A → A/);
  h.s.workbench.model=freeze({id:"empty",states:[],transitions:[]});h.s.renderWorkbench();assert.match(h.get("rule-table").textContent,/No transitions are declared/);assert.equal(h.get("state-flow").children.length,0);
});
test("Rules callbacks refuse an obsolete case or revision and absent transition without disturbing the preview",()=>{
  for(const change of [h=>{h.s.current.case.id="case-B";},h=>{h.s.current.case.version=5;},h=>{h.s.current.case.candidate=freeze({...h.candidate,transitions:[]});}]){
    const h=subjectHarness();h.s.modelView="history";h.s.tab="impact";h.s.renderWorkbench();const click=ruleButton(h,"T").onclick;h.get("model-source").value="unsent input";
    change(h);const before=JSON.stringify([h.s.current,h.s.inspectorSelection]);assert.equal(click(),false);assert.equal(h.s.tab,"impact");assert.equal(h.s.modelView,"history");assert.equal(h.get("model-source").value,"unsent input");assert.equal(JSON.stringify([h.s.current,h.s.inspectorSelection]),before);
  }
});
test("Changes Inspect in model carries its exact subject and synchronizes the entire current-model surface",()=>{
  const h=subjectHarness();let callbacks;h.s.EijaCompare={...compare,render:(_root,_current,value)=>{callbacks=value;return {destroy(){}};}};
  h.s.modelView="history";h.s.tab="review";h.s.renderWorkbench();h.s.renderChanges();const selection={case:"case-A",revision:4,kind:"transition",id:"T"};callbacks.inspectTransition("T",selection);
  assertCandidateSurface(h,"T");assert.equal(h.s.historyModel,h.historical);assert.equal(h.get("evidence-subject").dataset.comparisonId,"T");
  h.s.modelView="history";h.s.tab="review";h.s.current.case.version=5;callbacks.inspectTransition("T",selection);assert.equal(h.s.modelView,"history");assert.equal(h.s.tab,"review");
});
test("Rules Evidence navigation transfers focus without opening or acting on the decision",()=>{
  const h=subjectHarness();h.s.tab="impact";h.s.renderWorkbench();h.get("rules-evidence").onclick();assert.equal(h.s.tab,"evidence");assert.equal(h.get("evidence-subject").focused,true);assert.equal(h.get("evidence-subject").tabIndex,-1);assert.equal(h.get("review-decision").open,false);
  h.s.current=null;h.s.tab="impact";assert.equal(h.get("rules-evidence").onclick(),false);assert.equal(h.s.tab,"impact");
});
test("closed case Rules retain current subject but explain why selecting a rule cannot enable editing",()=>{
  for(const stage of ["APPLIED","DISCARDED"]){const h=subjectHarness();h.s.current.case.stage=stage;h.s.renderWorkbench();ruleButton(h,"T").onclick();assert.match(h.get("rules-edit-help").textContent,new RegExp(`case is ${stage}.*read only`));assert.equal(h.get("edit-state").disabled,true);assert.equal(h.projected.canvas.editable,false);}
});
test("Model and History aliases stay disabled across rendering until edit reconciliation clears",()=>{
  const h=subjectHarness();h.s.caseHistory={can_undo:true,can_redo:true};h.s.renderWorkbench();
  for(const id of ["undo-edit","redo-edit","history-undo","history-redo"])assert.equal(h.get(id).disabled,false,id+" initially enabled");
  h.s.editNeedsRefresh.set("case-A",{caseId:"case-A",version:4,semanticHash:"candidate-semantic-identity",status:"unknown"});h.s.renderWorkbench();
  for(const id of ["undo-edit","redo-edit","history-undo","history-redo","edit-source","edit-target","edit-role","edit-state"])assert.equal(h.get(id).disabled,true,id+" remains disabled after render");assert.equal(h.projected.canvas.editable,false);
  h.s.editNeedsRefresh.delete("case-A");h.s.renderWorkbench();for(const id of ["undo-edit","redo-edit","history-undo","history-redo"])assert.equal(h.get(id).disabled,false,id+" reenables after reconciliation");assert.equal(h.projected.canvas.editable,true);
});
test("impact navigation recomputes its destination, retains preview and never executes a runtime action",()=>{
  const h=subjectHarness(),selected=[];h.s.comparison={select:value=>{selected.push(value);return true;}};h.s.modelView="history";
  const selection={case:"case-A",revision:4,kind:"transition",id:"T"},before=JSON.stringify([h.s.current,h.historical]);
  const action=new Element("button");action.dataset.action="Send";action.onclick=()=>{throw Error("Navigation must not execute");};h.get("runtime-actions").append(action);
  assert.equal(h.s.openComparisonImpact({reference:"rule:Send",target:{view:"try"}},selection),true);assert.equal(h.s.tab,"review");assert.equal(selected[0].id,"T");assert.equal(h.get("comparison-model-tab").focused,true);
  h.s.openComparisonImpact({reference:"runtime:Send"},selection);assert.equal(h.s.tab,"try");assert.equal(action.focused,true);
  h.s.openComparisonImpact({reference:"journey:Send"},selection);assert.equal(h.s.tab,"impact");assert.equal(h.get("rules-journeys").open,true);assert.equal(h.get("rules-journeys").querySelector("summary").focused,true);assert.match(h.get("rules-subject").textContent,/Current candidate/);
  h.s.openComparisonImpact({reference:"receipt:Send"},selection);assert.equal(h.s.tab,"evidence");assert.equal(h.get("evidence-subject").focused,true);assert.equal(h.get("review-decision").open,false);assert.match(h.messages.at(-1),/Case-wide evidence/);
  h.s.openComparisonImpact({reference:"local-decision"},selection);assert.equal(h.get("review-decision").open,true);assert.equal(h.get("review-subject").focused,true);
  assert.equal(h.s.modelView,"history");assert.equal(JSON.stringify([h.s.current,h.historical]),before);
});
test("impact navigation rejects obsolete selection and unknown projection references without moving or editing",()=>{
  for(const [reference,selection]of [["rule:Send",{case:"other",revision:4,kind:"transition",id:"T"}],["runtime:Send",{case:"case-A",revision:3,kind:"transition",id:"T"}],["runtime:missing",{case:"case-A",revision:4,kind:"transition",id:"T"}],["repo://undeclared.py#send",{case:"case-A",revision:4,kind:"transition",id:"T"}]]){
    const h=subjectHarness();h.s.tab="impact";h.s.modelView="history";const before=JSON.stringify([h.s.current,h.s.inspectorSelection]);assert.equal(h.s.openComparisonImpact({reference,target:{view:"evidence"}},selection),false);assert.equal(h.s.tab,"impact");assert.equal(h.s.modelView,"history");assert.equal(JSON.stringify([h.s.current,h.s.inspectorSelection]),before);assert.equal(h.s.comparisonSelection,null);
  }
});
test("closed-case Run navigation focuses the visible runtime state when every action is disabled",()=>{
  for(const stage of ["APPLIED","DISCARDED"]){
    const h=subjectHarness(),action=new Element("button"),state=h.get("runtime-state"),reset=h.get("reset"),origin=new Element("button");
    h.s.current.case.stage=stage;h.s.tab="review";h.s.document.activeElement=origin;action.dataset.action="Send";action.disabled=true;reset.disabled=true;
    action.focus=reset.focus=()=>{throw Error("Disabled controls cannot receive destination focus");};state.focus=()=>{h.s.document.activeElement=state;};h.get("runtime-actions").append(action);
    const before=JSON.stringify(h.s.current),selection={case:"case-A",revision:4,kind:"transition",id:"T"};
    assert.equal(h.s.openComparisonImpact({reference:"runtime:Send"},selection),true);assert.equal(h.s.tab,"try");assert.equal(h.s.document.activeElement,state);assert.equal(state.tabIndex,-1);assert.equal(JSON.stringify(h.s.current),before);assert.equal(reset.disabled,true);assert.equal(action.disabled,true);
  }
});
test("Run navigation focuses an enabled reset when its action is unavailable",()=>{
  const h=subjectHarness(),action=new Element("button");action.dataset.action="Send";action.disabled=true;h.get("runtime-actions").append(action);h.get("reset").disabled=false;
  h.s.openComparisonImpact({reference:"runtime:Send"},{case:"case-A",revision:4,kind:"transition",id:"T"});assert.equal(h.get("reset").focused,true);assert.notEqual(h.get("runtime-state").focused,true);
});
test("subject regression oracle rejects the original partial switch even when the inspector looks current",()=>{
  const marker='switchTab("model");renderWorkbench();EijaShell.reveal("inspector");';assert.ok(app.includes(marker));
  const h=subjectHarness(app.replace(marker,'switchTab("model");renderEditor();renderSelectionDetail();renderCanvas();renderEvidenceContext();EijaShell.reveal("inspector");'));
  h.s.modelView="history";h.s.tab="impact";h.s.renderWorkbench();ruleButton(h,"T").onclick();assert.match(h.get("selection-detail").textContent,/A → C/);
  assert.throws(()=>assertCandidateSurface(h,"T"),assert.AssertionError);
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
