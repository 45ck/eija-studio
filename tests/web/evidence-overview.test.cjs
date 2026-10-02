"use strict";
// Actual packet presentation functions, isolated from transport. Browser paint is tested separately.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.open=false;this.value="";this.checked=false;this.ownText="";}
  set textContent(value){this.ownText=String(value);this.children=[];}
  get textContent(){return this.ownText+this.children.map(node=>node.textContent).join("");}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.ownText="";this.children=[...nodes];}
  get childElementCount(){return this.children.length;}
  querySelectorAll(selector){return descendants(this).filter(node=>selector==="input"?node.tag==="input":selector==="details[data-evidence-kind][open]"?node.tag==="details"&&node.dataset.evidenceKind&&node.open:false);}
}
const descendants=node=>node.children.flatMap(child=>[child,...descendants(child)]);
const visibleText=node=>node.tag==="details"&&!node.open?node.children.filter(child=>child.tag==="summary").map(child=>child.textContent).join("\n"):node.ownText+node.children.map(visibleText).join("\n");
const deepFreeze=value=>{if(value&&typeof value==="object"){Object.values(value).forEach(deepFreeze);Object.freeze(value);}return value;};
function packet(){return {
  eligible:false,subject_hash:"packet-A",subject:{semantic:"candidate-A",implementation:"source-A",presentation:"layout-A",environment:"env-A",harness:"harness-A",policy:"policy-A"},
  technical_claims:{schema_policy:"PASS",runtime_matrix:"PARTIAL",modelled_impact_closure:"UNKNOWN",formal_smt:"FAIL",formal_bend:"NOT_RUN"},
  blockers:["SOURCE_REVIEW_REQUIRED","FORMAL_EVIDENCE_FAIL:smt"],
  formal_evidence:[
    {kind:"smt",claim:"encoded_laws",status:"FAIL",evidence_level:"bounded_model",establishes:"Encoded law is violated.",reasons:["Counterexample found"],does_not_establish:["General source correctness"],assumptions:["Actor mapping is declared"],bounds:{depth:4},counterexamples:[{from:"Draft",to:"Approved",actor:"teacher"}],prerequisites:"Encoded law and checked tool",tool:{name:"solver",version:"fixture-1"},receipt_id:"receipt-A",receipts:["receipt-A"],extra_provenance:{scope:"declared graph"}},
    {kind:"bend",claim:"equational_model",status:"NOT_RUN",evidence_level:"sealed_tool_verdict",establishes:"Declared equations",reasons:["No compatible tool"],does_not_establish:["Reviewer understanding"],prerequisites:"Bend tool"},
    {kind:"tlc",status:"UNKNOWN",evidence_level:"bounded_model",establishes:"Declared state graph",reasons:["No admissible result"],prerequisites:"Bounded model"}
  ],
  blocked_meanings:[{label:"Teacher approval",policy_errors:["PROTECTED_AUTHORITY"],explanations:[{control:"registrar-only",source:"policy.py",witness:{actor:"teacher"},note:"Authority remains unchanged"}]}],
  explanations:[{control:"approval-route",source:"model",trace:[["Draft","Submit"],["Submitted","Approve"]],final_state:"Approved",note:"Counterexample only"}],
  questions:[{id:"authority",question:"Who retains approval?"}],human_understanding:"UNKNOWN"
};}
function harness(code=source){
  const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element("div"));return nodes.get(id);};
  const sandbox={impactSequence:0,current:{case:{id:"case-A",version:7,baseline_version:2},packet:null},modelView:"working",historyLabel:"",comparisonSelection:null,inspectorSelection:{kind:"transition",id:"Save"},$ : get,
    el:(tag,text,cls)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;},renderProblems:()=>{},api:()=>{throw Error("Presentation must not call transport");}};
  vm.createContext(sandbox);const start=code.indexOf("function formalList("),end=code.indexOf("async function load(id)");assert.ok(start>=0&&end>start);vm.runInContext(code.slice(start,end),sandbox);
  return {get,sandbox,render:p=>{sandbox.current.packet=p;sandbox.renderEvidencePacket(p);},formal:()=>get("formal").children.filter(node=>node.tag==="details")};
}
function assertEveryClaim(h,p){h.render(p);const rows=h.get("claims").children;assert.equal(rows.length,Object.keys(p.technical_claims).length);for(const [key,value]of Object.entries(p.technical_claims)){const row=rows.find(node=>node.dataset.claim===key);assert.ok(row,key);assert.equal(row.children[1].textContent,value,key);assert.ok(visibleText(row).includes(value));}}
test("every independent technical claim remains visible with its exact unmerged status",()=>{
  const h=harness(),p=deepFreeze(packet()),before=JSON.stringify(p);assertEveryClaim(h,p);assert.equal(JSON.stringify(p),before);assert.equal(h.get("claims").children.length,5);
});
test("closed formal summaries preserve every kind, status and scope; opening exposes all exact details",()=>{
  const h=harness(),p=deepFreeze(packet());h.render(p);
  for(const record of p.formal_evidence){const row=h.formal().find(node=>node.dataset.evidenceKind===record.kind);assert.ok(row);assert.equal(row.open,false);assert.equal(row.dataset.status,record.status);assert.ok(visibleText(row).includes(record.status));assert.ok(visibleText(row).includes(record.evidence_level.replaceAll("_"," ")));row.open=true;
    for(const [field,value]of Object.entries(record)){if(["kind","status","evidence_level"].includes(field))continue;const values=Array.isArray(value)?value:[value];for(const part of values)assert.ok(row.textContent.includes(typeof part==="string"?part:JSON.stringify(part)),field);}
  }
});
test("blocked meanings, codes and policy witnesses are retained apart from formal statuses",()=>{
  const h=harness();h.render(packet());const text=h.get("formal").textContent;
  for(const expected of ["Teacher approval","PROTECTED_AUTHORITY","registrar-only","policy.py",'{"actor":"teacher"}',"Authority remains unchanged","Draft Submit -> Submitted Approve","ends Approved","Counterexample only"])assert.ok(text.includes(expected),expected);
  assert.equal(h.get("blockers").textContent,"Review blocked: SOURCE_REVIEW_REQUIRED, FORMAL_EVIDENCE_FAIL:smt");
});
test("hostile markup remains literal data in claims, metadata, explanations and questions",()=>{
  const h=harness(),p=packet(),hostile='<img src=x onerror="oops()">';p.technical_claims.injected=hostile;p.formal_evidence[0].tool=hostile;p.questions[0].question=hostile;p.explanations[0].note=hostile;h.render(p);
  assert.ok(h.get("claims").textContent.includes(hostile));assert.ok(h.get("formal").textContent.includes(hostile));assert.ok(h.get("questions").textContent.includes(hostile));
  for(const id of ["claims","formal","questions"])assert.ok(!descendants(h.get(id)).some(node=>node.tag==="img"||node.tag==="script"));
});
test("the raw packet is preserved and exact subject dimensions are available without inventing freshness",()=>{
  const h=harness(),p=deepFreeze(packet());h.render(p);assert.deepEqual(JSON.parse(h.get("packet").textContent),p);
  for(const exact of [p.subject_hash,...Object.values(p.subject)])assert.ok(h.get("evidence-identities").textContent.includes(exact),exact);
  assert.equal(h.get("evidence-subject").dataset.subjectHash,"packet-A");assert.equal(h.get("evidence-subject").dataset.caseId,"case-A");assert.equal(h.get("evidence-subject").dataset.revision,"7");assert.equal(h.get("evidence-subject").dataset.freshness,undefined);
});
test("historical and baseline previews cannot borrow current candidate evidence",()=>{
  const h=harness(),p=packet();h.sandbox.modelView="history";h.sandbox.historyLabel="Initial protected meaning";h.render(p);let text=h.get("evidence-subject").textContent;
  assert.match(text,/current candidate · semantic candidate-A/);assert.match(text,/historical preview · Initial protected meaning/);assert.match(text,/not evidence for that preview/);
  h.sandbox.modelView="baseline";h.sandbox.renderEvidenceContext();text=h.get("evidence-subject").textContent;assert.match(text,/original baseline/);assert.match(text,/not the baseline/);
  h.sandbox.modelView="working";h.sandbox.renderEvidenceContext();assert.doesNotMatch(h.get("evidence-subject").textContent,/historical preview/);assert.match(h.get("evidence-subject").textContent,/Model inspector selection: transition · Save/);
});
test("selecting a term, role or law while Evidence stays open updates the actual context immediately",()=>{
  const h=harness(),switches=[],opened=[];h.sandbox.workbench={pack:{id:"pack-A"},language:{terms:[{id:"case",label:"Change Case"},{id:"model",label:"Model"}]},roles:[{id:"reviewer",label:"Reviewer"}],laws:[{id:"protected",description:"Protected authority"}]};
  h.sandbox.workingModel=()=>({states:["Draft"],transitions:[]});h.sandbox.EijaShell={reveal:(...args)=>opened.push(args)};h.sandbox.EijaTree={reveal:()=>{}};h.sandbox.renderNavigator=()=>{};h.sandbox.switchTab=name=>switches.push(name);
  vm.runInContext(source.slice(source.indexOf("function selectedConcept()"),source.indexOf("function renderNavigator()")),h.sandbox);
  vm.runInContext(source.slice(source.indexOf("function showSelection("),source.indexOf("function followReference(")),h.sandbox);
  h.render(packet());
  for(const [kind,item]of [["term",{id:"case"}],["term",{id:"model"}],["role",{id:"reviewer"}],["law",{id:"protected"}]]){
    h.sandbox.showSelection(kind,item);assert.ok(h.get("evidence-subject").textContent.includes(`Model inspector selection: ${kind} · ${item.id}`));assert.equal(h.get("selection-detail").dataset.eijaId,`pack-A.detail.${kind}.${item.id}`);
  }
  h.sandbox.showSelection("term",{id:"missing"});assert.doesNotMatch(h.get("evidence-subject").textContent,/Model inspector selection:/);assert.equal(h.sandbox.inspectorSelection,null);
  assert.deepEqual(switches,[]);assert.equal(opened.length,5);assert.equal(h.get("evidence-subject").dataset.subjectHash,"packet-A");
});
test("missing evidence is explicitly unavailable and cannot become an eligible or PASS summary",()=>{
  const h=harness();h.render({eligible:false,blockers:["MEANING_REQUIRED"],human_understanding:"UNKNOWN"});
  assert.match(h.get("claims").textContent,/Not reported/);assert.match(h.get("formal").textContent,/not reported/);assert.match(h.get("evidence-subject").textContent,/Evidence subject: not available/);assert.match(h.get("review-subject").textContent,/blocked.*subject not available/);
  h.render({eligible:false});assert.match(h.get("blockers").textContent,/Review blocked/);assert.doesNotMatch(h.get("blockers").textContent,/scope eligible/);
});
test("same-subject refresh retains deliberate details, draft answers and acknowledgement",()=>{
  const h=harness(),p=packet();h.render(p);h.get("review-decision").open=true;h.get("questions").querySelectorAll("input")[0].value="unsent owner draft";h.get("acknowledge").checked=true;h.formal()[0].open=true;h.render(p);
  assert.equal(h.get("review-decision").open,true);assert.equal(h.get("questions").querySelectorAll("input")[0].value,"unsent owner draft");assert.equal(h.get("acknowledge").checked,true);assert.equal(h.formal()[0].open,true);
});
test("different subject or case closes the review and removes prior-subject draft answers",()=>{
  for(const change of [h=>{h.sandbox.current.case.id="case-B";},(h,p)=>{p.subject_hash="packet-B";p.subject.semantic="candidate-B";}]){
    const h=harness(),p=packet();h.render(p);h.get("review-decision").open=true;h.get("questions").querySelectorAll("input")[0].value="belongs to A";h.get("acknowledge").checked=true;h.formal()[0].open=true;change(h,p);h.render(p);
    assert.equal(h.get("review-decision").open,false);assert.equal(h.get("questions").querySelectorAll("input")[0].value,"");assert.equal(h.get("acknowledge").checked,false);assert.equal(h.formal()[0].open,false);
  }
});
test("packet refresh preserves an explicit review opening but never opens it automatically",()=>{
  const h=harness(),p=packet();h.render(p);assert.equal(h.get("review-decision").open,false);p.eligible=true;p.blockers=[];h.render(p);assert.equal(h.get("review-decision").open,false);assert.match(h.get("review-subject").textContent,/eligible for local review/);
  h.get("review-decision").open=true;p.eligible=false;p.blockers=["STALE_BASELINE"];h.render(p);assert.equal(h.get("review-decision").open,true);assert.match(h.get("blockers").textContent,/STALE_BASELINE/);assert.match(h.get("review-subject").textContent,/blocked/);
});
test("existing error handling still reveals exact Problems and never dismisses the refusal",()=>{
  const h=harness(),opened=[],notices=[];h.sandbox.notice=(...args)=>notices.push(args);h.sandbox.EijaShell={bottom:id=>opened.push(id)};
  vm.runInContext(source.slice(source.indexOf("function reportError("),source.indexOf("function clearDiagnostic(")),h.sandbox);
  h.sandbox.reportError({code:"EDIT_REFUSED",message:"Candidate unchanged",details:{codes:["PROTECTED_AUTHORITY"],refs:["transition:Save"]}});
  assert.deepEqual(opened,["problems-pane"]);assert.deepEqual(notices,[["Candidate unchanged · PROTECTED_AUTHORITY",true]]);assert.equal(h.get("error-details").hidden,false);assert.deepEqual(JSON.parse(h.get("error-json").textContent),{code:"EDIT_REFUSED",message:"Candidate unchanged",details:{codes:["PROTECTED_AUTHORITY"],refs:["transition:Save"]}});
});
test("information oracle rejects an actual-renderer mutation dropping a technical claim",()=>{
  const marker="Object.entries(p.technical_claims||{})";assert.ok(source.includes(marker));const mutated=source.replace(marker,marker+".slice(1)");assert.throws(()=>assertEveryClaim(harness(mutated),packet()),assert.AssertionError);
});
test("status oracle rejects an actual-renderer mutation upgrading an unrun formal result",()=>{
  const marker='status=e.status??"NOT_REPORTED"';assert.ok(source.includes(marker));const h=harness(source.replace(marker,'status="PASS"'));h.render(packet());assert.throws(()=>assert.equal(h.formal().find(row=>row.dataset.evidenceKind==="bend").dataset.status,"NOT_RUN"),assert.AssertionError);
});
test("context oracle rejects the original missing refresh after a concept selection",()=>{
  const h=harness();h.sandbox.workbench={pack:{id:"pack-A"},language:{terms:[{id:"case",label:"Change Case"}]}};h.sandbox.workingModel=()=>({states:[],transitions:[]});h.sandbox.EijaShell={reveal:()=>{}};h.sandbox.EijaTree={reveal:()=>{}};h.sandbox.renderNavigator=()=>{};h.sandbox.switchTab=()=>{};
  vm.runInContext(source.slice(source.indexOf("function selectedConcept()"),source.indexOf("function renderNavigator()")),h.sandbox);
  const original=source.slice(source.indexOf("function showSelection("),source.indexOf("function followReference("));assert.ok(original.includes("  renderEvidenceContext();"));
  vm.runInContext(original.replace("  renderEvidenceContext();", ""),h.sandbox);h.render(packet());h.sandbox.showSelection("term",{id:"case"});
  assert.equal(h.get("selection-detail").dataset.eijaId,"pack-A.detail.term.case");
  assert.throws(()=>assert.match(h.get("evidence-subject").textContent,/Model inspector selection: term · case/),assert.AssertionError);
});
function comparisonHarness(code=source){
  const h=harness(code),references=[],tabs=[];let callbacks;
  h.sandbox.workbench={language:{terms:[]}};
  h.sandbox.followReference=ref=>references.push(ref);
  h.sandbox.switchTab=name=>{tabs.push(name);h.sandbox.renderEvidenceContext();};
  h.sandbox.selectTransition=()=>{throw Error("Evidence/source navigation must not change the Model inspector");};
  h.sandbox.EijaCompare={render:(_root,_current,value)=>{callbacks=value;return {destroy(){}};}};
  const start=code.indexOf("function renderChanges("),end=code.indexOf("let inspectorSelection = null;");assert.ok(start>=0&&end>start);
  vm.runInContext("const comparisonViews=new Map();let comparison=null;\n"+code.slice(start,end),h.sandbox);
  h.render(packet());h.sandbox.renderChanges();
  return {...h,references,tabs,callbacks:()=>callbacks};
}
const comparisonRef=(kind="transition",id="TR-VERIFY")=>({case:"case-A",revision:7,kind,id});
test("actual comparison selection updates Evidence without borrowing Model inspector identity",()=>{
  const h=comparisonHarness(),p=deepFreeze(packet());h.render(p);const before=JSON.stringify(p);
  h.callbacks().onSelection(comparisonRef());
  const context=h.get("evidence-subject");assert.equal(context.dataset.comparisonId,"TR-VERIFY");assert.equal(context.dataset.comparisonCaseId,"case-A");assert.equal(context.dataset.comparisonRevision,"7");assert.equal(context.dataset.comparisonKind,"transition");
  assert.match(context.textContent,/Comparison selection: transition · TR-VERIFY · case case-A · revision 7/);
  assert.match(context.textContent,/Model inspector selection: transition · Save/);assert.equal(h.sandbox.inspectorSelection.id,"Save");
  assert.match(context.textContent,/case-wide for the current candidate/);assert.match(context.textContent,/not an element-specific result/);
  assert.equal(JSON.stringify(p),before);assert.deepEqual(h.tabs,[]);
});
test("actual source and Evidence callbacks retain their supplied exact comparison identity",()=>{
  const h=comparisonHarness(),ref="repo://src/studio.py#Studio.verify";
  h.callbacks().openReference(ref,comparisonRef());assert.deepEqual(h.references,[ref]);assert.equal(h.get("evidence-subject").dataset.comparisonId,"TR-VERIFY");
  h.callbacks().openEvidence(comparisonRef("state","REMOVED"));assert.deepEqual(h.tabs,["evidence"]);assert.equal(h.get("evidence-subject").dataset.comparisonId,"REMOVED");assert.equal(h.get("evidence-subject").dataset.comparisonKind,"state");
  h.callbacks().openReference("repo://src/other.py");assert.deepEqual(h.references,[ref,"repo://src/other.py"]);assert.equal(h.get("evidence-subject").dataset.comparisonId,"REMOVED");
});
test("removed state and initial-state selections remain context without requiring candidate membership",()=>{
  const h=comparisonHarness();h.sandbox.current.case.candidate={states:["AFTER"],initial_state:"AFTER",transitions:[]};
  for(const ref of [comparisonRef("state","BEFORE_ONLY"),comparisonRef("initial","initial_state")]){
    Object.freeze(ref);const before=JSON.stringify(ref);h.callbacks().onSelection(ref);
    assert.equal(h.get("evidence-subject").dataset.comparisonId,ref.id);assert.equal(h.get("evidence-subject").dataset.comparisonKind,ref.kind);assert.equal(JSON.stringify(ref),before);
  }
  assert.deepEqual(h.sandbox.current.case.candidate,{states:["AFTER"],initial_state:"AFTER",transitions:[]});
});
test("obsolete case or revision callbacks cannot relabel Evidence or navigate to source",()=>{
  for(const change of [h=>{h.sandbox.current.case.id="case-B";},h=>{h.sandbox.current.case.version=8;}]){
    const h=comparisonHarness();h.callbacks().onSelection(comparisonRef());change(h);h.sandbox.renderEvidenceContext();
    const context=h.get("evidence-subject");assert.equal(context.dataset.comparisonId,"");assert.equal(context.dataset.comparisonCaseId,"");assert.equal(context.dataset.comparisonRevision,"");assert.equal(context.dataset.comparisonKind,"");assert.doesNotMatch(context.textContent,/Comparison selection:/);
    h.callbacks().openReference("repo://stale.py",comparisonRef());h.callbacks().openEvidence(comparisonRef());assert.deepEqual(h.references,[]);assert.deepEqual(h.tabs,[]);
  }
});
test("a rebuilt comparison drops an obsolete selection until its renderer restores a valid one",()=>{
  const h=comparisonHarness();h.callbacks().onSelection(comparisonRef());h.sandbox.renderChanges();h.sandbox.renderEvidenceContext();assert.equal(h.get("evidence-subject").dataset.comparisonId,"");
  h.callbacks().onSelection(comparisonRef());assert.equal(h.get("evidence-subject").dataset.comparisonId,"TR-VERIFY");
  h.sandbox.current=null;h.sandbox.renderEvidenceContext();assert.equal(h.get("evidence-subject").dataset.comparisonId,"");assert.doesNotMatch(h.get("evidence-subject").textContent,/Comparison selection:/);
});
test("comparison context oracle rejects the original disconnected onSelection wiring",()=>{
  const marker="onSelection:rememberComparisonSelection";assert.ok(source.includes(marker));
  const h=comparisonHarness(source.replace(marker,"onSelection:()=>{}"));h.callbacks().onSelection(comparisonRef());
  assert.throws(()=>assert.equal(h.get("evidence-subject").dataset.comparisonId,"TR-VERIFY"),assert.AssertionError);
});
