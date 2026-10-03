"use strict";
// Actual Verify/task and evidence renderer with a small DOM; browser focus remains separately observed.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(process.env.EIJA_APP_MODULE||path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
const journey=fs.readFileSync(process.env.EIJA_HCI_JOURNEY_MODULE||path.join(__dirname,"../../quality/hci/journey.py"),"utf8");
const clone=value=>JSON.parse(JSON.stringify(value));
const names=["authority","assignment","reject_entry"];
function view(version=7){return {case:{id:"case-A",version,stage:version===7?"PREVIEW":"VERIFIED",decision:null},packet:{
  subject_hash:"subject-A",subject:{semantic:"model-A",presentation:"layout-A",implementation:"source-A",policy:"policy-A",environment:"env-A",harness:"harness-A"},
  eligible:version!==7,blockers:version===7?["RUNTIME_EVIDENCE_UNKNOWN"]:[],human_understanding:"UNKNOWN",
  questions:names.map(id=>({id,question:"Question "+id}))}};}
function harness(code=source){
  const nodes=new Map(),calls=[],errors=[],notices=[],doc={};
  class Element{
    constructor(id="",tagName="DIV"){this.tagName=tagName;this.dataset={};this.open=false;this.value="";this.checked=false;this.disabled=false;this.attributes={};this.children=[];if(id)this.id=id;}
    set id(value){this.identifier=value;nodes.set(value,this);}
    get id(){return this.identifier||"";}
    focus(){doc.activeElement=this;}
    getClientRects(){return [1];}
    setAttribute(key,value){this.attributes[key]=value;}
    removeAttribute(key){delete this.attributes[key];}
    append(...children){this.children.push(...children);}
    contains(value){return value===this||this.children.some(child=>child.contains(value));}
    replaceChildren(...children){if(this.children.some(child=>child.contains(doc.activeElement)))doc.activeElement=doc.body;this.children=children;}
    querySelectorAll(selector){assert.equal(selector,"input");return this.children.flatMap(child=>[...(child.tagName==="INPUT"?[child]:[]),...child.querySelectorAll(selector)]);}
  }
  const get=id=>{if(!nodes.has(id))new Element(id);return nodes.get(id);};
  doc.body=get("body");doc.documentElement=get("html");doc.activeElement=get("verify");
  const sandbox={current:view(),tab:"evidence",busy:false,document:doc,$:get,notice:value=>notices.push(value),reportError:error=>errors.push(error.message),
    el:tag=>new Element("",tag.toUpperCase()),renderFormal:()=>{},renderProblems:()=>{},renderEvidenceContext:()=>{},renderEvidenceTriage:()=>{}};
  sandbox.evidenceKey=p=>typeof p.subject_hash==="string"&&p.subject_hash?JSON.stringify([sandbox.current?.case.id||"no-case",p.subject_hash]):"";
  const taskStart=code.indexOf("function captureTaskFocus()"),taskEnd=code.indexOf("let caseInventory=",taskStart);
  const renderStart=code.indexOf("function renderEvidencePacket(p)"),renderEnd=code.indexOf("async function load(",renderStart);
  const start=code.indexOf("async function verifyForReview()"),end=code.indexOf('$("review-form").onsubmit',start);
  assert.ok(taskStart>=0&&taskEnd>taskStart&&renderStart>=0&&renderEnd>renderStart&&start>=0&&end>start,"Actual task, renderer and Verify handler must exist");
  vm.createContext(sandbox);vm.runInContext(code.slice(taskStart,taskEnd)+code.slice(renderStart,renderEnd)+code.slice(start,end),sandbox);
  const h={get,doc,sandbox,calls,errors,notices,get fields(){return get("questions").querySelectorAll("input");},
    publish(next=view(8)){sandbox.current=next;sandbox.renderEvidencePacket(next.packet);return clone(next.case);}};
  let outcome=()=>h.publish();
  sandbox.command=async action=>{calls.push(action);assert.equal(action,"verify","Verification must never answer, acknowledge, approve or apply");return outcome(h);};
  sandbox.renderEvidencePacket(sandbox.current.packet);
  h.outcome=fn=>{outcome=fn;};h.run=()=>get("verify").onclick();return h;
}
function assertUnsolicitedReviewAbsent(h){assert.equal(h.get("review-decision").open,false,"Verify must not open owner review");assert.equal(h.doc.activeElement,h.get("verify"),"Verify must not focus review questions");}
test("eligible verification reports its result and leaves deliberate owner review closed",async()=>{
  const h=harness();await h.run();assertUnsolicitedReviewAbsent(h);
  assert.deepEqual(h.fields.map(field=>field.value),["","",""]);assert.equal(h.get("acknowledge").checked,false);
  assert.equal(h.sandbox.current.case.decision,null);assert.equal(h.sandbox.current.case.stage,"VERIFIED");assert.equal(h.sandbox.current.packet.human_understanding,"UNKNOWN");
  assert.deepEqual(h.calls,["verify"]);assert.deepEqual(h.errors,[]);assert.equal(h.sandbox.busy,false);
  assert.equal(h.notices.at(-1),"Bounded runtime verification finished. Human evidence remains UNKNOWN.");
});
test("pending and duplicate activation cannot open review or duplicate verification",async()=>{
  const h=harness();let finish;h.outcome(()=>new Promise(resolve=>{finish=()=>resolve(h.publish());}));
  const pending=h.run();assertUnsolicitedReviewAbsent(h);assert.equal(h.sandbox.busy,true);await h.run();assert.deepEqual(h.calls,["verify"]);
  finish();await pending;assertUnsolicitedReviewAbsent(h);assert.equal(h.sandbox.busy,false);
});
test("refusal and reload failures preserve either disclosure state and same-subject owner drafts",async t=>{
  for(const reason of ["SOURCE_REVIEW_REQUIRED","STALE_VERSION","transport failure","case reload failed","affordance reload failed","case-list reload failed after render"]){
    for(const open of [false,true])await t.test(`${reason}; open=${open}`,async()=>{
      const h=harness();h.get("review-decision").open=open;h.fields[0].value="unsent draft";h.get("acknowledge").checked=true;
      h.outcome(()=>{if(reason.includes("after render"))h.publish();throw Error(reason);});await h.run();
      assert.equal(h.get("review-decision").open,open);assert.equal(h.doc.activeElement,h.get("verify"));assert.deepEqual(h.errors,[reason]);
      assert.equal(h.fields[0].value,"unsent draft");assert.equal(h.get("acknowledge").checked,true);assert.deepEqual(h.calls,["verify"]);
    });
  }
});
test("ineligible, stale and differently bound completions never initiate owner review",async t=>{
  const controls={
    "runtime still blocked":next=>{next.packet.eligible=false;next.packet.blockers=["RUNTIME_EVIDENCE_UNKNOWN"];},
    "source blocker despite eligibility":next=>{next.packet.blockers=["SOURCE_REVIEW_REQUIRED"];},
    "missing blocker inventory":next=>{delete next.packet.blockers;},
    "newer revision":next=>{next.case.version++;},
    "closed case":next=>{next.case.stage="APPLIED";},
    "existing owner decision":next=>{next.case.decision={subject_hash:"subject-A"};},
    "different case":next=>{next.case.id="case-B";},
    "different subject":next=>{next.packet.subject_hash="subject-B";next.packet.subject.semantic="model-B";},
    "missing subject hash":next=>{delete next.packet.subject_hash;}
  };
  for(const [name,mutate]of Object.entries(controls))await t.test(name,async()=>{
    const h=harness();h.outcome(()=>{const next=view(8);mutate(next);return h.publish(next);});await h.run();
    assertUnsolicitedReviewAbsent(h);assert.deepEqual(h.calls,["verify"]);assert.deepEqual(h.errors,[]);
  });
});
test("already opened same-subject review retains drafts and acknowledgement without forcing a field",async()=>{
  const h=harness();h.get("review-decision").open=true;h.fields[0].value="owner-authored draft";h.fields[1].value="  ";h.get("acknowledge").checked=true;
  const values=h.fields.map(field=>field.value);await h.run();assert.deepEqual(h.fields.map(field=>field.value),values);
  assert.equal(h.get("acknowledge").checked,true);assert.equal(h.get("review-decision").open,true);assert.equal(h.doc.activeElement,h.get("verify"));
});
test("the existing renderer clears a different subject instead of retaining another review's draft",async()=>{
  const h=harness();h.get("review-decision").open=true;h.fields[0].value="old subject draft";h.get("acknowledge").checked=true;
  h.outcome(()=>{const next=view(8);next.packet.subject_hash="subject-B";next.packet.subject.semantic="model-B";return h.publish(next);});await h.run();
  assertUnsolicitedReviewAbsent(h);assert.deepEqual(h.fields.map(field=>field.value),["","",""]);assert.equal(h.get("acknowledge").checked,false);
});
test("navigation or deliberate focus movement during verification is not pulled into review",async()=>{
  for(const target of ["source-reader","workspace-search","review-subject"]){
    const h=harness();h.outcome(()=>{const result=h.publish();h.sandbox.tab=target==="source-reader"?"code":"evidence";h.get(target).focus();return result;});await h.run();
    assert.equal(h.get("review-decision").open,false);assert.equal(h.doc.activeElement,h.get(target));
  }
});
test("task cleanup recovers a removed question focus without opening or erasing the same-subject draft",async()=>{
  const h=harness();h.get("review-decision").open=true;h.fields[2].value="owner draft";let finish;
  h.outcome(()=>new Promise(resolve=>{finish=()=>resolve(h.publish());}));const pending=h.run();h.fields[2].focus();finish();await pending;
  assert.equal(h.get("review-decision").open,true);assert.equal(h.fields[2].value,"owner draft");assert.equal(h.doc.activeElement,h.get("verify"));
});
test("negative controls reject unsolicited opening and unsolicited focus independently",async()=>{
  const marker='notice("Bounded runtime verification finished. Human evidence remains UNKNOWN.");';
  assert.equal(source.split(marker).length,2,"Mutation anchor must identify one result notice");
  for(const mutation of ['$("review-decision").open=true;','$("questions").querySelectorAll("input")[0].focus();']){
    const h=harness(source.replace(marker,marker+mutation));await h.run();
    assert.throws(()=>assertUnsolicitedReviewAbsent(h),assert.AssertionError,"The oracle must reject the unsolicited behavior");
  }
});

// Execute the journey's actual observation expression; no browser or DOM mutation is used.
const predicate=journey.match(/if e\.kind in \("verification_ready", "review_ready"\):\s+return self\.page\.evaluate\("""([\s\S]*?)""",/);
assert.ok(predicate,"The canonical journey must distinguish verification from deliberate review entry");
function checkpointObservation(review,change=()=>{}){
  const decision={open:review},verify={},summary={},fields=names.map(name=>({name,value:""})),ack={checked:false},stage={textContent:"VERIFIED"};
  const packet={eligible:true,blockers:[],human_understanding:"UNKNOWN"},state={decision,verify,summary,fields,ack,stage,packet,formVisible:review,summaryVisible:true,approveEnabled:true};
  state.focus=review?summary:verify;change(state);
  const elements={"#review-decision":decision,"#verify":verify,"#review-subject":summary,"#acknowledge":ack,"#case-stage":stage,"#packet":{textContent:JSON.stringify(packet)}};
  const document={activeElement:state.focus,querySelector:selector=>elements[selector],querySelectorAll:selector=>{assert.equal(selector,"#questions input");return fields;}};
  const window={__hci:{isVisible:selector=>selector==="#review-form"?state.formVisible:selector==="#review-subject"?state.summaryVisible:false,
    isEnabled:selector=>selector==="#approve"&&state.approveEnabled}};
  return vm.runInNewContext("("+predicate[1]+")",{document,window})({form:"#review-form",names,review});
}
test("canonical observations require closed verification and a distinct native-summary-focused review",()=>{
  assert.equal(checkpointObservation(false),true);assert.equal(checkpointObservation(true),true);
  assert.equal(checkpointObservation(false,s=>{s.decision.open=true;s.formVisible=true;s.focus=s.fields[0];}),false);
  assert.equal(checkpointObservation(true,s=>{s.focus=s.fields[0];}),false);
});
test("canonical observations reject false eligibility, omitted questions, owner input and disabled review",()=>{
  const changes=[s=>{s.packet.eligible=false;},s=>{s.packet.blockers=["SOURCE_REVIEW_REQUIRED"];},s=>{delete s.packet.blockers;},
    s=>{s.fields.pop();},s=>{s.fields[0].name="wrong";},s=>{s.fields[0].value="preanswered";},s=>{s.ack.checked=true;},
    s=>{s.approveEnabled=false;},s=>{s.stage.textContent="PREVIEW";}];
  for(const review of [false,true])for(const change of changes)assert.equal(checkpointObservation(review,change),false);
});
test("a closed review entry may be below the pane but native opening must reveal it",()=>{
  assert.equal(checkpointObservation(false,s=>{s.summaryVisible=false;}),true);
  assert.equal(checkpointObservation(true,s=>{s.summaryVisible=false;}),false);
});
