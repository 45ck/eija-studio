"use strict";
// Actual packet presentation functions, isolated from transport. Browser paint is tested separately.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(process.env.EIJA_APP_MODULE||path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.open=false;this.value="";this.checked=false;this.ownText="";}
  set textContent(value){this.ownText=String(value);this.children=[];}
  get textContent(){return this.ownText+this.children.map(node=>node.textContent).join("");}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.ownText="";this.children=[...nodes];}
  get childElementCount(){return this.children.length;}
  querySelectorAll(selector){return descendants(this).filter(node=>selector==="input"?node.tag==="input":selector==="details[data-evidence-key][open]"?node.tag==="details"&&node.dataset.evidenceKey&&node.open:false);}
  querySelector(selector){return descendants(this).find(node=>node.tag===selector)||null;}
  focus(){Element.active=this;}
  scrollIntoView(){this.scrolled=true;}
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
  Element.active=null;
  const events=[],nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element("div"));return nodes.get(id);};
  const sandbox={impactSequence:0,current:{case:{id:"case-A",version:7,baseline_version:2},packet:null},modelView:"working",historyLabel:"",comparisonSelection:null,inspectorSelection:{kind:"transition",id:"Save"},$ : get,
    el:(tag,text,cls)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;},workbench:null,status:{trusted_fixture:false},lastDiagnostic:null,
    EijaShell:{renderEvidence:()=>{},bottom:(...args)=>events.push(["bottom",...args])},switchTab:name=>events.push(["view",name]),notice:(...args)=>events.push(["notice",...args]),api:()=>{throw Error("Presentation must not call transport");}};
  vm.createContext(sandbox);const start=code.indexOf("function formalList("),end=code.indexOf("async function load(");assert.ok(start>=0&&end>start);vm.runInContext(code.slice(start,end),sandbox);
  const problemsStart=code.indexOf("function renderProblems()"),problemsEnd=code.indexOf("let editPreview=",problemsStart);assert.ok(problemsStart>=0&&problemsEnd>problemsStart);vm.runInContext(code.slice(problemsStart,problemsEnd),sandbox);
  return {get,sandbox,events,active:()=>Element.active,render:p=>{sandbox.current.packet=p;sandbox.renderEvidencePacket(p);},formal:()=>get("formal").children.filter(node=>node.tag==="details"&&Object.hasOwn(node.dataset,"evidenceKind")),rows:()=>get("formal").children.filter(node=>node.tag==="details")};
}
function assertEveryClaim(h,p){
  h.render(p);const rows=h.rows().filter(row=>Object.hasOwn(row.dataset,"claim"));
  assert.equal(rows.length,Object.keys(p.technical_claims).length);
  for(const [key,value]of Object.entries(p.technical_claims)){
    const matches=rows.filter(node=>node.dataset.claim===key);assert.equal(matches.length,1,key);
    const row=matches[0],status=descendants(row.children[0]).find(node=>node.className==="evidence-status");
    assert.equal(status.textContent,value,key);assert.ok(visibleText(row).includes(value));
  }
}

const triageRows=h=>descendants(h.get("evidence-triage")).filter(node=>node.tag==="li");
const triageAction=(h,code)=>triageRows(h).find(row=>row.dataset.blockerCode===code)?.querySelector("button");
test("triage follows the actual blocker inventory and never promotes unrelated unknown records into blockers",()=>{
  const h=harness(),p=packet();p.blockers=["SOURCE_REVIEW_REQUIRED","RUNTIME_EVIDENCE_UNKNOWN","FORMAL_EVIDENCE_FAIL:smt","UNRECOGNIZED_LIMIT"];p.technical_claims.runtime_matrix="UNKNOWN";
  const before=JSON.stringify(p);h.render(deepFreeze(p));assert.equal(JSON.stringify(p),before);
  assert.deepEqual(triageRows(h).map(row=>row.dataset.blockerCode),p.blockers);
  assert.match(h.get("evidence-triage").textContent,/Owner review.*outstanding/);assert.match(h.get("evidence-triage").textContent,/Runtime evidence · UNKNOWN/);
  assert.equal(triageAction(h,"UNRECOGNIZED_LIMIT"),null);assert.ok(!triageRows(h).some(row=>row.textContent.includes("tlc")));
  assert.equal(h.get("blockers").textContent,"Review blocked: "+p.blockers.join(", "));
  assert.equal(h.get("evidence-triage").dataset.caseId,"case-A");assert.equal(h.get("evidence-triage").dataset.revision,"7");assert.equal(h.get("evidence-triage").dataset.subjectHash,"packet-A");
});
test("source restriction activation opens the real Problems diagnostic and focuses that exact rendered item",()=>{
  const h=harness(),p=packet();h.render(p);const button=triageAction(h,"SOURCE_REVIEW_REQUIRED");assert.ok(button);assert.equal(button.type,"button");
  const target=h.get("problems").children.find(node=>node.id==="source-review-problem");assert.ok(target);assert.match(target.textContent,/Owner review.*outstanding/);
  assert.equal(button.onclick(),true);assert.equal(h.events[0][0],"bottom");assert.equal(h.events[0][1],"problems-pane");assert.equal(h.active(),target);assert.equal(target.tabIndex,-1);assert.equal(target.scrolled,true);
});
test("runtime and formal blocker actions open only their exact current check and preserve the packet",()=>{
  const h=harness(),p=packet();p.blockers=["RUNTIME_EVIDENCE_UNKNOWN","FORMAL_EVIDENCE_FAIL:smt"];p.technical_claims.runtime_matrix="UNKNOWN";h.render(deepFreeze(p));
  for(const [code,claim]of [["RUNTIME_EVIDENCE_UNKNOWN","runtime_matrix"],["FORMAL_EVIDENCE_FAIL:smt","formal_smt"]]){
    const row=h.rows().find(item=>item.dataset.claim===claim);assert.equal(row.open,false);assert.equal(triageAction(h,code).onclick(),true);assert.equal(row.open,true);assert.equal(h.active(),row.querySelector("summary"));assert.equal(row.scrolled,true);
  }
  assert.deepEqual(h.events,[["view","evidence"],["view","evidence"]]);assert.equal(h.formal().length,p.formal_evidence.length);
});
test("triage never invents a check destination from ambiguous, inconsistent or unbound evidence",()=>{
  for(const change of [
    p=>p.formal_evidence.push({...p.formal_evidence[0]}),
    p=>{p.formal_evidence[0].status="PASS";},
    p=>{p.formal_evidence[0].subject_hash="another-packet";},
    p=>{p.formal_evidence[0].subject={semantic:p.subject.semantic};},
    p=>{delete p.technical_claims.formal_smt;},
    p=>{p.formal_evidence[0].kind="SMT";},
    p=>{delete p.subject_hash;}
  ]){const h=harness(),p=packet();change(p);h.render(p);assert.equal(triageAction(h,"FORMAL_EVIDENCE_FAIL:smt"),null);assert.equal(h.formal().length,p.formal_evidence.length);}
  const h=harness(),p=packet();p.blockers=["RUNTIME_EVIDENCE_UNKNOWN"];p.technical_claims.runtime_matrix="PASS";h.render(p);assert.equal(triageAction(h,p.blockers[0]),null);assert.match(h.get("evidence-triage").textContent,/UNKNOWN/);
});
test("triage rechecks packet, revision, blocker membership, status and target uniqueness before focus",()=>{
  for(const mutate of [
    (h,p)=>{h.sandbox.current.case.id="case-B";},
    (h,p)=>{h.sandbox.current.case.version++;},
    (h,p)=>{h.sandbox.current.packet={...p};},
    (h,p)=>{p.subject.semantic="different-candidate";},
    (h,p)=>{p.blockers=[];},
    (h,p)=>{p.technical_claims.runtime_matrix="PASS";},
    (h,p)=>{h.get("formal").append(h.rows().find(row=>row.dataset.claim==="runtime_matrix"));}
  ]){
    const h=harness(),p=packet();p.blockers=["RUNTIME_EVIDENCE_UNKNOWN"];p.technical_claims.runtime_matrix="UNKNOWN";h.render(p);const action=triageAction(h,p.blockers[0]);assert.ok(action);mutate(h,p);assert.equal(action.onclick(),false);assert.equal(h.active(),null);assert.equal(h.events.length,1);assert.equal(h.events[0][0],"notice");
  }
});
test("same-subject update replaces triage actions while leaving formal UNKNOWN and NOT_RUN visible",()=>{
  const h=harness(),p=packet();h.render(p);p.blockers=["RUNTIME_EVIDENCE_UNKNOWN"];p.technical_claims.runtime_matrix="UNKNOWN";h.render(p);
  assert.deepEqual(triageRows(h).map(row=>row.dataset.blockerCode),p.blockers);assert.ok(triageAction(h,p.blockers[0]));assert.match(h.get("formal").textContent,/NOT_RUN/);assert.match(h.get("formal").textContent,/UNKNOWN/);
  p.blockers=[];p.eligible=true;h.render(p);assert.match(h.get("evidence-triage").textContent,/No blockers.*Human authorisation remains separate/);assert.equal(triageRows(h).length,0);
  p.eligible=false;h.render(p);assert.match(h.get("evidence-triage").textContent,/blocked.*does not identify a reason/);
});
test("policy and dependency links retain their exact model claims rather than borrowing a source or runtime explanation",()=>{
  const h=harness(),p=packet();p.blockers=["POLICY_BLOCKED","IMPACT_INCOMPLETE","STALE_BASELINE","HUMAN_FIELD_EVIDENCE_REQUIRED","CASE_DISCARDED","MEANING_REQUIRED"];p.technical_claims.schema_policy="FAIL";h.render(p);
  for(const [code,claim]of [["POLICY_BLOCKED","schema_policy"],["IMPACT_INCOMPLETE","modelled_impact_closure"]]){
    const row=h.rows().find(item=>item.dataset.claim===claim);assert.equal(triageAction(h,code).onclick(),true);assert.equal(h.active(),row.querySelector("summary"));
  }
  for(const code of p.blockers.slice(2))assert.equal(triageAction(h,code),null);
  p.technical_claims.schema_policy="PASS";p.technical_claims.modelled_impact_closure="PASS";h.render(p);assert.equal(triageAction(h,"POLICY_BLOCKED"),null);assert.equal(triageAction(h,"IMPACT_INCOMPLETE"),null);
});
test("a source-restriction action resolves a repainted diagnostic and refuses an ambiguous duplicate",()=>{
  const h=harness(),p=packet();h.render(p);const action=triageAction(h,"SOURCE_REVIEW_REQUIRED"),old=h.get("problems").children.find(node=>node.id==="source-review-problem");
  h.sandbox.renderProblems();const next=h.get("problems").children.find(node=>node.id==="source-review-problem");assert.notEqual(next,old);assert.equal(action.onclick(),true);assert.equal(h.active(),next);
  h.get("problems").append(next);Element.active=null;assert.equal(action.onclick(),false);assert.equal(h.active(),null);
});
test("the stale-triage oracle rejects a renderer mutation that removes the exact revision guard",()=>{
  const marker='const same=JSON.stringify([current?.case.id,current?.case.version,p.subject_hash,p.subject])===identity;';assert.ok(source.includes(marker));
  const h=harness(source.replace(marker,'const same=true;')),p=packet();p.blockers=["RUNTIME_EVIDENCE_UNKNOWN"];p.technical_claims.runtime_matrix="UNKNOWN";h.render(p);const action=triageAction(h,p.blockers[0]);h.sandbox.current.case.version++;
  assert.throws(()=>assert.equal(action.onclick(),false),assert.AssertionError);
});
test("every technical claim is represented once and exact matching formal results share a row",()=>{
  const h=harness(),p=deepFreeze(packet()),before=JSON.stringify(p);assertEveryClaim(h,p);assert.equal(JSON.stringify(p),before);
  assert.equal(h.rows().length,6);assert.equal(h.formal().length,3);
  assert.equal(h.rows().find(row=>row.dataset.claim==="formal_smt").dataset.evidenceKind,"smt");
  assert.equal(h.rows().find(row=>row.dataset.claim==="formal_bend").dataset.evidenceKind,"bend");
  assert.equal(h.rows().filter(row=>row.dataset.evidenceKind==="tlc")[0].dataset.claim,undefined);
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
  assert.ok(h.rows().find(row=>row.dataset.claim==="injected").textContent.includes(hostile));assert.ok(h.get("formal").textContent.includes(hostile));assert.ok(h.get("questions").textContent.includes(hostile));
  for(const id of ["formal","questions"])assert.ok(!descendants(h.get(id)).some(node=>node.tag==="img"||node.tag==="script"));
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
  h.sandbox.workingModel=()=>({states:["Draft"],transitions:[]});h.sandbox.EijaShell={...h.sandbox.EijaShell,reveal:(...args)=>opened.push(args)};h.sandbox.EijaTree={reveal:()=>{}};h.sandbox.renderNavigator=()=>{};h.sandbox.switchTab=name=>switches.push(name);
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
  assert.match(h.get("formal").textContent,/Technical claims: not reported/);assert.match(h.get("formal").textContent,/not reported/);assert.match(h.get("evidence-subject").textContent,/Evidence subject: not available/);assert.match(h.get("review-subject").textContent,/blocked.*subject not available/);
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
  const h=harness(),opened=[],notices=[];h.sandbox.notice=(...args)=>notices.push(args);h.sandbox.EijaShell={...h.sandbox.EijaShell,bottom:id=>opened.push(id)};
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
  const h=harness();h.sandbox.workbench={pack:{id:"pack-A"},language:{terms:[{id:"case",label:"Change Case"}]}};h.sandbox.workingModel=()=>({states:[],transitions:[]});h.sandbox.EijaShell={...h.sandbox.EijaShell,reveal:()=>{}};h.sandbox.EijaTree={reveal:()=>{}};h.sandbox.renderNavigator=()=>{};h.sandbox.switchTab=()=>{};
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
  assert.match(context.textContent,/Comparison selection: transition · TR-VERIFY/);
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

test("only an exact unique declared kind and equal reported status can share a claim row",()=>{
  const cases=[
    ["absent kind",p=>{p.formal_evidence=p.formal_evidence.filter(e=>e.kind!=="smt");}],
    ["duplicate kind",p=>{p.formal_evidence.push({...p.formal_evidence[0],receipt_id:"other-receipt"});}],
    ["conflicting status",p=>{p.formal_evidence[0].status="PASS";}],
    ["case differs",p=>{p.formal_evidence[0].kind="SMT";}],
    ["whitespace differs",p=>{p.formal_evidence[0].kind="smt ";}],
    ["missing record status",p=>{delete p.formal_evidence[0].status;}],
    ["missing record kind",p=>{delete p.formal_evidence[0].kind;}],
    ["stale record subject",p=>{p.formal_evidence[0].subject_hash="old-packet";}],
    ["different source subject",p=>{p.formal_evidence[0].subject={...p.subject,implementation:"old-source"};}],
    ["incomplete explicit subject",p=>{p.formal_evidence[0].subject={semantic:p.subject.semantic};}],
    ["empty explicit subject",p=>{p.formal_evidence[0].subject={};}],
    ["missing packet subject",p=>{delete p.subject_hash;}]
  ];
  for(const [label,change]of cases){
    const h=harness(),p=packet();change(p);const frozen=deepFreeze(p),before=JSON.stringify(p);assertEveryClaim(h,frozen);
    const claim=h.rows().find(row=>row.dataset.claim==="formal_smt");assert.equal(claim.dataset.evidenceKind,undefined,label);
    assert.equal(h.formal().length,p.formal_evidence.length,label);
    p.formal_evidence.forEach((record,index)=>{assert.equal(h.formal()[index].dataset.status,record.status??"NOT_REPORTED",label);assert.equal(h.formal()[index].dataset.evidenceIndex,String(index),label);});
    assert.equal(JSON.stringify(p),before,label);
  }
});
test("conflicting result statuses and duplicate receipts remain individually reachable",()=>{
  const h=harness(),p=packet();p.formal_evidence[0].status="PASS";p.formal_evidence.push({...p.formal_evidence[0],status:"FAIL",receipt_id:"contradictory-receipt",reasons:["Second result conflicts"],counterexamples:[{state:"Denied",actor:"revoked"}]});h.render(deepFreeze(p));
  assert.equal(h.rows().find(row=>row.dataset.claim==="formal_smt").dataset.status,"FAIL");
  const duplicate=h.formal().filter(row=>row.dataset.evidenceKind==="smt");assert.equal(duplicate.length,2);
  assert.deepEqual(duplicate.map(row=>row.dataset.status),["PASS","FAIL"]);
  for(const row of duplicate){assert.match(visibleText(row),/Multiple formal records declare this kind/);row.open=true;}
  assert.ok(visibleText(duplicate[0]).includes("receipt-A"));assert.ok(visibleText(duplicate[1]).includes("contradictory-receipt"));assert.ok(visibleText(duplicate[1]).includes('{"state":"Denied","actor":"revoked"}'));
});
test("closed conflict summaries explain the separate statuses without hiding contradictions",()=>{
  const h=harness(),p=packet();p.formal_evidence[0].status="PASS";h.render(p);
  const claim=h.rows().find(row=>row.dataset.claim==="formal_smt"),record=h.formal()[0];
  for(const row of [claim,record]){assert.equal(row.open,false);assert.match(visibleText(row),/Claim and formal record statuses differ/);}
  assert.match(visibleText(claim),/FAIL/);assert.match(visibleText(record),/PASS/);
  delete p.technical_claims.formal_smt;p.formal_evidence.push({...p.formal_evidence[0],status:"UNKNOWN"});h.render(p);
  for(const row of h.formal().filter(row=>row.dataset.evidenceKind==="smt"))assert.match(visibleText(row),/Multiple formal records declare this kind/);
});
test("mismatched subject is visible alongside the reported status while collapsed",()=>{
  const h=harness(),p=packet();p.formal_evidence[0].status="PASS";p.technical_claims.formal_smt="PASS";p.formal_evidence[0].subject_hash="stale-packet";h.render(p);
  const row=h.formal()[0];assert.equal(row.open,false);assert.match(visibleText(row),/PASS/);assert.match(visibleText(row),/Subject mismatch/);assert.match(visibleText(row),/not evidence for this packet/);assert.equal(row.dataset.claim,undefined);
  row.open=true;assert.match(visibleText(row),/stale-packet/);assert.equal(h.get("blockers").textContent,"Review blocked: SOURCE_REVIEW_REQUIRED, FORMAL_EVIDENCE_FAIL:smt");
});
test("same exact subject repaints results and blockers while keeping deliberate disclosures",()=>{
  const h=harness(),p=packet();h.render(p);h.formal()[0].open=true;h.rows().find(row=>row.dataset.claim==="runtime_matrix").open=true;
  p.formal_evidence[0].status="UNKNOWN";p.formal_evidence[0].reasons=["Old result no longer admissible"];p.technical_claims.formal_smt="UNKNOWN";p.technical_claims.runtime_matrix="NOT_RUN";p.blockers=["NEW_BLOCKER"];h.render(p);
  assert.equal(h.formal()[0].open,true);assert.equal(h.formal()[0].dataset.status,"UNKNOWN");assert.match(visibleText(h.formal()[0]),/Old result no longer admissible/);
  const runtime=h.rows().find(row=>row.dataset.claim==="runtime_matrix");assert.equal(runtime.open,true);assert.equal(runtime.dataset.status,"NOT_RUN");assert.match(h.get("blockers").textContent,/NEW_BLOCKER/);assert.doesNotMatch(h.get("blockers").textContent,/FORMAL_EVIDENCE_FAIL/);
});
test("an open exact technical claim stays open when its matching formal record arrives",()=>{
  for(const identityChange of [()=>{},h=>{h.sandbox.current.case.id="case-B";},(_h,p)=>{p.subject_hash="packet-B";}]){
    const h=harness(),p=packet(),record=p.formal_evidence.shift();h.render(p);
    h.rows().find(row=>row.dataset.claim==="formal_smt").open=true;
    identityChange(h,p);p.formal_evidence.unshift(record);h.render(p);
    const paired=h.rows().find(row=>row.dataset.claim==="formal_smt");assert.equal(paired.dataset.evidenceKind,"smt");
    assert.equal(paired.open,h.sandbox.current.case.id==="case-A"&&p.subject_hash==="packet-A");
  }
});
test("a missing reciprocal technical claim is explicit even with the formal row closed",()=>{
  const h=harness(),p=packet();delete p.technical_claims.formal_smt;h.render(p);
  const row=h.formal()[0];assert.equal(row.open,false);assert.match(visibleText(row),/No matching technical claim is reported/);assert.match(visibleText(row),/FAIL/);assert.equal(row.dataset.status,"FAIL");assert.equal(row.dataset.claim,undefined);
});
test("missing identity never carries disclosures or owner drafts even in the same case",()=>{
  const h=harness(),p=packet();delete p.subject_hash;h.render(p);h.formal()[0].open=true;h.get("review-decision").open=true;h.get("acknowledge").checked=true;h.get("questions").querySelectorAll("input")[0].value="unbound draft";
  h.sandbox.current.case.version++;h.render(p);
  assert.equal(h.formal()[0].open,false);assert.equal(h.get("review-decision").open,false);assert.equal(h.get("acknowledge").checked,false);assert.equal(h.get("questions").querySelectorAll("input")[0].value,"");
  assert.match(visibleText(h.formal()[0]),/Subject unavailable/);assert.equal(h.formal()[0].dataset.claim,undefined);
});
test("expanded rows retain exact property, source, tool, receipt and empty or null metadata",()=>{
  const h=harness(),p=packet(),record=p.formal_evidence[0];record.property_id="property:approval";record.subject_hash=p.subject_hash;record.subject={...p.subject};record.provenance={source_hash:"source-A",path:"literal [draft].py",tool_version:"0.0.fixture"};record.additional_empty=[];record.additional_null=null;h.render(deepFreeze(p));
  const row=h.formal()[0];assert.equal(row.dataset.claim,"formal_smt");row.open=true;
  for(const value of [record.property_id,record.subject_hash,JSON.stringify(record.subject),JSON.stringify(record.provenance),"[]","null"])assert.ok(visibleText(row).includes(value),value);
  assert.equal(h.get("packet").textContent,JSON.stringify(p,null,2));
});
test("selected change remains navigation context under a single full case identity",()=>{
  const h=harness();h.sandbox.comparisonSelection={case:"case-A",revision:7,kind:"transition",id:"T"};h.render(packet());
  const context=h.get("evidence-subject");assert.equal(context.textContent.split("case-A").length-1,1);assert.match(context.textContent,/Case case-A · revision 7 · baseline revision 2/);assert.match(context.textContent,/Comparison selection: transition · T/);assert.match(context.textContent,/not an element-specific result/);
});
