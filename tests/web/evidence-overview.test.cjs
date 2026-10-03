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
  setAttribute(name,value){this.attributes??={};this.attributes[name]=String(value);}
  getAttribute(name){return this.attributes?.[name]??null;}
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
  // Evidence fixtures have no selected runtime attempt; use the actual empty-context recovery renderers.
  const sandbox={runtimeAttempt:null,runtimeRuleInspection:null,impactSequence:0,current:{case:{id:"case-A",version:7,baseline_version:2},packet:null},modelView:"working",historyLabel:"",comparisonSelection:null,inspectorSelection:{kind:"transition",id:"Save"},$ : get,
    el:(tag,text,cls)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;},workbench:null,status:{trusted_fixture:false},lastDiagnostic:null,
    EijaShell:{renderEvidence:()=>{},bottom:(...args)=>events.push(["bottom",...args])},switchTab:name=>events.push(["view",name]),notice:(...args)=>events.push(["notice",...args]),api:()=>{throw Error("Presentation must not call transport");}};
  vm.createContext(sandbox);const start=code.indexOf("function formalList("),end=code.indexOf("async function load(");assert.ok(start>=0&&end>start);vm.runInContext(code.slice(start,end),sandbox);
  const problemsStart=code.indexOf("function renderProblems()"),problemsEnd=code.indexOf("let editPreview=",problemsStart);assert.ok(problemsStart>=0&&problemsEnd>problemsStart);vm.runInContext(code.slice(problemsStart,problemsEnd),sandbox);
  const recoveryStart=code.indexOf("function runtimeRuleTarget("),recoveryEnd=code.indexOf("function renderRuntimeFeedback(",recoveryStart);assert.ok(recoveryStart>=0&&recoveryEnd>recoveryStart);vm.runInContext(code.slice(recoveryStart,recoveryEnd),sandbox);
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

// Synthetic display contracts only; these specimens are not formal tool results or receipts.
function inspectedPacket(){
  const p=packet(),e=p.formal_evidence[0];
  p.scope="local-demo";e.receipt_id="deciding-receipt-A";
  e.inspection={schema_version:"eija.formal-inspection.v1",display_only:true,scope:"formal-record-inspection",kind:e.kind,status:e.status,reasons:[...e.reasons],availability:"available",availability_reasons:[],
    review:{case_id:"case-A",case_version:7,scope:"local-demo",subject_json:JSON.stringify(p.subject),subject_hash:p.subject_hash,candidate_semantic_hash:p.subject.semantic,pack_id:"pack-A",pack_digest:"pack-digest-A"},
    receipt:{id:"deciding-receipt-A",subject_json:JSON.stringify(p.subject),artifact_hash:"artifact-A",producer:"synthetic contract",method:"test-only",subject_matches_review:true},artifact_json:'{"synthetic":true}',record_count:3,projection_reasons:[],
    records:["counterexample","negative_control","diagnostic"].map((origin,index)=>({artifact_path:"/items/"+index,origin,label:"same-invariant",invariant:"INV-A",raw_json:JSON.stringify({origin,index}),
      steps:[{index:0,text:"revoke actor",raw_json:'"revoke actor"'},{index:1,text:"actor Save",raw_json:'"actor Save"'}],
      model:{availability:"not_provided",slot:"slot-"+index,supplied_semantic_hash:"specimen-"+index,computed_semantic_hash:null,raw_json:null,workflow:null,validation_errors:[]},
      navigation:{current_model:null,source:null,reasons:["EXPLICIT_REFERENCE_BINDING_NOT_PROVIDED"]}}))};
  return p;
}
const inspectionBox=row=>descendants(row).find(node=>Object.hasOwn(node.dataset,"inspectionAvailability"));
const inspectionItems=row=>descendants(row).filter(node=>Object.hasOwn(node.dataset,"inspectionPath"));
const disclosure=(row,label)=>descendants(row).find(node=>node.tag==="details"&&node.children[0]?.textContent===label);
test("inspection retains every ordered origin and literal step without changing evidence or using transport",()=>{
  const h=harness(),p=inspectedPacket(),x=p.formal_evidence[0].inspection;
  x.records.push(...Array.from({length:5},(_,i)=>({...structuredClone(x.records[0]),artifact_path:"/extra/"+i})));x.record_count=x.records.length;
  const before=JSON.stringify(p);h.render(deepFreeze(p));const row=h.formal()[0],box=inspectionBox(row),items=inspectionItems(row);
  assert.equal(box.dataset.inspectionAvailability,"available");assert.equal(items.length,8);assert.deepEqual(items.map(item=>item.dataset.inspectionPath),x.records.map(record=>record.artifact_path));
  assert.deepEqual(items.map(item=>item.dataset.inspectionOrigin),x.records.map(record=>record.origin));assert.deepEqual(descendants(items[0]).filter(node=>node.dataset.stepIndex!==undefined).map(node=>node.textContent),["revoke actor","actor Save"]);
  assert.equal(row.dataset.status,"FAIL");assert.equal(JSON.stringify(p),before);assert.deepEqual(JSON.parse(h.get("packet").textContent),p);assert.deepEqual(h.events,[]);
  assert.equal(descendants(box).some(node=>["a","svg","canvas"].includes(node.tag)),false);assert.ok(descendants(box).filter(node=>node.tag==="button").every(node=>node.dataset.inspectionReturn==="check"));assert.match(items[1].textContent,/Seeded control.*not a reported failure/);
  assert.equal(items[1].children[0].textContent,"Negative control · same-invariant");
});
test("UNKNOWN without an admitted artifact remains uncertainty with no invented records or candidate specimen",()=>{
  const h=harness(),p=inspectedPacket(),e=p.formal_evidence[0],x=e.inspection;e.status=x.status=p.technical_claims.formal_smt="UNKNOWN";e.reasons=x.reasons=["No deciding receipt"];
  Object.assign(x,{availability:"unavailable",availability_reasons:["NO_DECIDING_RECEIPT"],receipt:null,artifact_json:null,records:[],record_count:0});h.render(deepFreeze(p));
  const row=h.formal()[0],box=inspectionBox(row);assert.equal(row.dataset.status,"UNKNOWN");assert.equal(box.dataset.inspectionAvailability,"unavailable");assert.equal(inspectionItems(row).length,0);box.open=true;
  assert.match(visibleText(box),/NO_DECIDING_RECEIPT/);assert.match(visibleText(box),/No admitted recorded artifact/);assert.equal(disclosure(box,"Complete recorded artifact"),undefined);
});
test("an authentic UNKNOWN diagnostic is not relabelled as a counterexample",()=>{
  const h=harness(),p=inspectedPacket(),e=p.formal_evidence[0],x=e.inspection;e.status=x.status=p.technical_claims.formal_smt="UNKNOWN";e.reasons=x.reasons=["Bound incomplete"];x.records=[x.records[2]];x.record_count=1;h.render(p);
  assert.equal(h.formal()[0].dataset.status,"UNKNOWN");assert.equal(inspectionItems(h.formal()[0])[0].children[0].textContent,"Diagnostic · same-invariant");
});
test("review, deciding receipt, and each specimen preserve their distinct identities and invalid raw data",()=>{
  const h=harness(),p=inspectedPacket(),x=p.formal_evidence[0].inspection;x.receipt.subject_json='{"semantic":"older-candidate"}';x.receipt.subject_matches_review=false;
  Object.assign(x.records[0].model,{availability:"raw_invalid",raw_json:'{"transitions":[{"id":"TR-SAVE"}]}',validation_errors:["Missing mandatory guards"],supplied_semantic_hash:"producer-specimen"});
  Object.assign(x.records[1].model,{availability:"valid_workflow",computed_semantic_hash:"computed-control",raw_json:'{"id":"other-specimen"}',workflow:{id:"other-specimen"}});h.render(deepFreeze(p));const box=inspectionBox(h.formal()[0]);box.open=true;
  assert.match(visibleText(box),/deciding receipt subject differs/);assert.equal(disclosure(box,"Full review subject").querySelector("pre").textContent,JSON.stringify(p.subject));assert.equal(disclosure(box,"Original receipt subject").querySelector("pre").textContent,x.receipt.subject_json);
  const items=inspectionItems(box);for(const item of items)item.open=true;
  assert.match(visibleText(items[0]),/not a valid Workflow/);assert.match(visibleText(items[0]),/Missing mandatory guards/);assert.match(items[0].textContent,/producer-specimen/);assert.match(items[1].textContent,/computed-control/);
  assert.equal(disclosure(items[0],"Raw model specimen").querySelector("pre").textContent,x.records[0].model.raw_json);assert.equal(descendants(box).some(node=>node.tag==="svg"||node.tag==="a"),false);
});
test("incompatible inspection context stays raw and unassociated without altering the reported check",()=>{
  const changes=[x=>{x.schema_version="future";},x=>{x.display_only=false;},x=>{x.kind="other";},x=>{x.status="PASS";},x=>{x.reasons=["different"];},x=>{x.review.case_id="case-B";},x=>{x.review.case_version++;},x=>{x.review.subject_hash="other";},x=>{x.review.candidate_semantic_hash="other";},x=>{x.review.subject_json='{"semantic":"candidate-A"}';},x=>{x.review.subject_json="invalid JSON";},x=>{x.review.pack_digest="other";},x=>{x.record_count++;},x=>{x.records=null;},x=>{x.receipt=null;},x=>{x.artifact_json=null;}];
  for(const change of changes){const h=harness(),p=inspectedPacket(),x=p.formal_evidence[0].inspection;h.sandbox.workbench={pack:{id:"pack-A",digest:"pack-digest-A"}};change(x);h.render(deepFreeze(p));const row=h.formal()[0],box=inspectionBox(row);
    assert.equal(box.dataset.inspectionAvailability,"unassociated");assert.equal(row.dataset.status,"FAIL");assert.equal(inspectionItems(row).length,0);assert.deepEqual(JSON.parse(disclosure(box,"Raw inspection data").querySelector("pre").textContent),x);}
});
test("malformed and absent inspection data is retained without crashing or borrowing a model",()=>{
  for(const value of [null,{},"unrecognised"]){const h=harness(),p=packet();p.formal_evidence[0].inspection=value;h.render(p);assert.equal(inspectionBox(h.formal()[0]).dataset.inspectionAvailability,"unassociated");}
  const h=harness(),p=inspectedPacket(),x=p.formal_evidence[0].inspection;x.records=[null,{origin:"future",raw_json:"literal"}];x.record_count=2;h.render(p);assert.equal(inspectionItems(h.formal()[0]).length,0);assert.match(h.formal()[0].textContent,/Record 1 has an unsupported shape/);assert.match(h.formal()[0].textContent,/Record 2 has an unsupported shape/);
});
test("inspection cannot hide a conflicting formal-record subject or unavailable artifact contradiction",()=>{
  for(const mutate of [p=>{p.formal_evidence[0].subject_hash="old-subject";},p=>{p.formal_evidence[0].inspection.availability="unavailable";}]){
    const h=harness(),p=inspectedPacket();mutate(p);h.render(p);const row=h.formal()[0];assert.equal(inspectionBox(row).dataset.inspectionAvailability,"unassociated");assert.equal(inspectionItems(row).length,0);assert.equal(row.dataset.status,"FAIL");
  }
});
test("review scope and exact deciding receipt association are required, while receipt subject mismatch stays inspectable",()=>{
  for(const mutate of [x=>{x.review.scope="field";},x=>{x.receipt.id="not-the-deciding-receipt";}]){
    const h=harness(),p=inspectedPacket();mutate(p.formal_evidence[0].inspection);h.render(p);assert.equal(inspectionBox(h.formal()[0]).dataset.inspectionAvailability,"unassociated");assert.equal(inspectionItems(h.formal()[0]).length,0);
  }
  const h=harness(),p=inspectedPacket();p.formal_evidence[0].inspection.receipt.subject_matches_review=false;h.render(p);assert.equal(inspectionBox(h.formal()[0]).dataset.inspectionAvailability,"available");assert.equal(inspectionItems(h.formal()[0]).length,3);
});
test("all raw inspection regions have native keyboard entry and an exact accessible name",()=>{
  const h=harness(),p=inspectedPacket();h.render(p);const box=inspectionBox(h.formal()[0]),raw=descendants(box).filter(node=>node.tag==="pre");assert.ok(raw.length>=6);
  for(const region of raw){assert.equal(region.tabIndex,0);assert.equal(region.getAttribute("role"),"region");assert.ok(region.getAttribute("aria-label"));region.focus();assert.equal(h.active(),region);}
  assert.equal(box.children[0].tag,"summary");box.open=true;box.open=false;box.children[0].focus();assert.equal(h.active(),box.children[0]);assert.deepEqual(h.events,[]);
});
test("inspection open state survives only the same case revision, deciding receipt and artifact",()=>{
  const mutations=[()=>{},(h,p)=>{h.sandbox.current.case.version++;p.formal_evidence[0].inspection.review.case_version++;},(h,p)=>{h.sandbox.current.case.id="case-B";p.formal_evidence[0].inspection.review.case_id="case-B";},(_h,p)=>{p.formal_evidence[0].receipt_id=p.formal_evidence[0].inspection.receipt.id="other-receipt";},(_h,p)=>{p.formal_evidence[0].inspection.receipt.artifact_hash="other-artifact";}];
  mutations.forEach((mutate,index)=>{const h=harness(),p=inspectedPacket();h.render(p);h.formal()[0].open=true;inspectionBox(h.formal()[0]).open=true;inspectionItems(h.formal()[0])[0].open=true;mutate(h,p);h.render(p);assert.equal(inspectionBox(h.formal()[0]).open,index===0);assert.equal(inspectionItems(h.formal()[0])[0].open,index===0);});
});
test("duplicate check kinds keep separate deciding records and cannot inherit each other's open inspection",()=>{
  const h=harness(),p=inspectedPacket(),extra=structuredClone(p.formal_evidence[0]);extra.receipt_id=extra.inspection.receipt.id="other-receipt";extra.inspection.receipt.artifact_hash="other-artifact";p.formal_evidence.push(extra);h.render(p);
  const rows=h.formal().filter(row=>row.dataset.evidenceKind==="smt");assert.equal(rows.length,2);for(const row of rows)assert.match(visibleText(row),/Multiple formal records/);
  inspectionBox(rows[0]).open=true;p.formal_evidence.reverse();h.render(p);for(const row of h.formal().filter(row=>row.dataset.evidenceKind==="smt"))assert.equal(inspectionBox(row).open,false);
});
test("hostile record text and unknown fields remain literal, available raw data",()=>{
  const h=harness(),p=inspectedPacket(),x=p.formal_evidence[0].inspection,hostile='<script>doNotRun()</script>';x.records[0].label=hostile;x.records[0].steps[0].text=hostile;x.records[0].extra={unsupported:[null,hostile]};h.render(p);const box=inspectionBox(h.formal()[0]);
  assert.ok(box.textContent.includes(hostile));assert.equal(descendants(box).some(node=>["script","img","iframe"].includes(node.tag)),false);assert.deepEqual(JSON.parse(disclosure(box,"Raw inspection data").querySelector("pre").textContent),x);
});
test("inspection inventory oracle rejects silently omitting a recorded item",()=>{
  const marker="x.records.forEach((record,index)=>inspectionRecord(box,record,index,key,opened,context));";assert.ok(source.includes(marker));
  const h=harness(source.replace(marker,"x.records.slice(1).forEach((record,index)=>inspectionRecord(box,record,index,key,opened,context));")),p=inspectedPacket();h.render(p);
  assert.throws(()=>assert.equal(inspectionItems(h.formal()[0]).length,p.formal_evidence[0].inspection.record_count),assert.AssertionError);
});
test("inspection association oracle rejects removing the exact review identity guard",()=>{
  const marker='review.case_version!==current?.case.version';assert.ok(source.includes(marker));const h=harness(source.replace(marker,"false")),p=inspectedPacket();p.formal_evidence[0].inspection.review.case_version=6;h.render(p);
  assert.throws(()=>assert.equal(inspectionBox(h.formal()[0]).dataset.inspectionAvailability,"unassociated"),assert.AssertionError);
});
test("record origin oracle rejects presenting a seeded control as an actual counterexample",()=>{
  const marker='negative_control:"Negative control"';assert.ok(source.includes(marker));const h=harness(source.replace(marker,'negative_control:"Counterexample"')),p=inspectedPacket();h.render(p);
  assert.throws(()=>assert.equal(inspectionItems(h.formal()[0])[1].children[0].textContent,"Negative control · same-invariant"),assert.AssertionError);
});
const returnControl=rawDisclosure=>descendants(rawDisclosure).find(node=>node.dataset.inspectionReturn==="check");
test("open raw inspection carries its exact reported check and origin without adding closed-disclosure chrome",()=>{
  const h=harness(),p=inspectedPacket();h.render(deepFreeze(p));const row=h.formal()[0],raw=disclosure(inspectionItems(row)[1],"Raw recorded item");
  assert.equal(raw.open,false);assert.doesNotMatch(visibleText(raw),/Back to check|smt · FAIL/);raw.open=true;
  assert.match(visibleText(raw),/smt · FAIL/);assert.match(visibleText(raw),/Negative control · same-invariant/);assert.match(visibleText(raw),/Back to check/);
  assert.equal(raw.querySelector("pre").textContent,p.formal_evidence[0].inspection.records[1].raw_json);assert.equal(returnControl(raw).type,"button");
});
test("Back to check focuses the exact owning summary and leaves selection, unrelated disclosures and authority unchanged",()=>{
  const h=harness(),p=inspectedPacket();h.sandbox.comparisonSelection={case:"case-A",revision:7,kind:"transition",id:"TR-SAVE"};h.render(deepFreeze(p));
  const row=h.formal()[0],box=inspectionBox(row),item=inspectionItems(row)[1],raw=disclosure(item,"Raw recorded item"),other=h.formal()[1],button=returnControl(raw);
  row.open=box.open=item.open=raw.open=other.open=true;raw.querySelector("pre").focus();const state=JSON.stringify([p,h.sandbox.comparisonSelection,h.sandbox.inspectorSelection]);
  assert.equal(button.onclick(),true);assert.equal(h.active(),row.children[0]);assert.equal(row.children[0].scrolled,true);assert.ok(box.open&&item.open&&raw.open&&other.open);
  assert.equal(JSON.stringify([p,h.sandbox.comparisonSelection,h.sandbox.inspectorSelection]),state);assert.deepEqual(h.events,[]);
});
test("duplicate check kinds return to their own captured row rather than the first matching kind",()=>{
  const h=harness(),p=inspectedPacket(),extra=structuredClone(p.formal_evidence[0]);extra.receipt_id=extra.inspection.receipt.id="another-receipt";extra.inspection.receipt.artifact_hash="another-artifact";p.formal_evidence.push(extra);h.render(p);
  const rows=h.formal().filter(row=>row.dataset.evidenceKind==="smt");for(const row of rows){const button=returnControl(disclosure(inspectionItems(row)[0],"Raw recorded item"));assert.equal(button.onclick(),true);assert.equal(h.active(),row.children[0]);}
  assert.deepEqual(h.events,[]);
});
test("stale, replaced, detached or hidden inspection controls refuse focus without requests or a new context",()=>{
  const changes=[h=>{h.sandbox.current.case.id="case-B";},h=>{h.sandbox.current.case.version++;},(h,p)=>{h.sandbox.current.packet={...p};},(_h,p)=>{p.subject.semantic="another-model";},(_h,p)=>{p.subject_hash="another-subject";},(_h,p)=>{p.formal_evidence[0].inspection.receipt.artifact_hash="other-artifact";},(_h,p)=>{p.formal_evidence[0]={...p.formal_evidence[0]};},h=>{h.get("formal").replaceChildren();},h=>{h.get("evidence").hidden=true;},(h,p)=>h.render(p),h=>{h.formal()[0].children[0]=new Element("summary");}];
  for(const change of changes){const h=harness(),p=inspectedPacket();h.render(p);const button=returnControl(disclosure(inspectionItems(h.formal()[0])[0],"Raw recorded item"));change(h,p);assert.equal(button.onclick(),false);assert.equal(h.active(),null);assert.deepEqual(h.events,[]);}
});
test("repainting a new subject removes parked inspection context and rejects its old return handler",()=>{
  const h=harness(),p=inspectedPacket();h.render(p);const old=inspectionBox(h.formal()[0]),button=returnControl(disclosure(inspectionItems(old)[0],"Raw recorded item"));old.open=true;
  const next=packet();next.subject_hash="new-subject";h.render(next);assert.ok(!descendants(h.get("formal")).includes(old));assert.equal(descendants(h.get("formal")).some(node=>node.className==="formal-raw-context"),false);assert.equal(button.onclick(),false);assert.equal(h.active(),null);
});
test("exact-owning-check oracle rejects a return implementation redirected to another record",()=>{
  const marker='row.open=true;summary.focus();';assert.ok(source.includes(marker));const h=harness(source.replace(marker,'row.open=true;[...$("formal").children].find(n=>n.dataset.evidenceKind==="bend").querySelector("summary").focus();')),p=inspectedPacket();h.render(p);const row=h.formal()[0],button=returnControl(disclosure(inspectionItems(row)[0],"Raw recorded item"));button.onclick();
  assert.throws(()=>assert.equal(h.active(),row.children[0]),assert.AssertionError);
});
test("returning from unavailable or unassociated raw data names its reported check without manufacturing records",()=>{
  for(const missingContext of [false,true]){const h=harness(),p=inspectedPacket(),e=p.formal_evidence[0],x=e.inspection;e.status=x.status="UNKNOWN";p.technical_claims.formal_smt="UNKNOWN";Object.assign(x,{availability:"unavailable",availability_reasons:["NO_DECIDING_RECEIPT"],receipt:null,artifact_json:null,records:[],record_count:0});if(missingContext)x.review.case_version=6;h.render(p);
    const row=h.formal()[0],raw=disclosure(row,"Raw inspection data");raw.open=true;assert.match(visibleText(raw),/smt · UNKNOWN/);assert.equal(inspectionItems(row).length,0);assert.equal(returnControl(raw).onclick(),true);assert.equal(h.active(),row.children[0]);assert.equal(row.dataset.status,"UNKNOWN");assert.deepEqual(h.events,[]);}
});
test("stale-return oracle rejects bypassing its case and subject identity check",()=>{
  const marker='const same=current?.packet===packet&&packet.formal_evidence?.[index]===record&&inspectionContextIdentity(packet,record)===identity;';assert.ok(source.includes(marker));const h=harness(source.replace(marker,'const same=true;')),p=inspectedPacket();h.render(p);const button=returnControl(disclosure(inspectionItems(h.formal()[0])[0],"Raw recorded item"));h.sandbox.current.case.version++;
  assert.throws(()=>assert.equal(button.onclick(),false),assert.AssertionError);
});

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
