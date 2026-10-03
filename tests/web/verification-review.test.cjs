"use strict";
// Exercise the shipped Verify handler/task with controlled command completion; no owner endpoint is called.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(process.env.EIJA_APP_MODULE||path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
const clone=value=>JSON.parse(JSON.stringify(value));
function view(version=7){return {case:{id:"case-A",version,stage:version===7?"PREVIEW":"VERIFIED",decision:null},packet:{
  subject_hash:"subject-A",subject:{semantic:"model-A",presentation:"layout-A",implementation:"source-A",policy:"policy-A",environment:"env-A",harness:"harness-A"},
  eligible:version!==7,blockers:version===7?["RUNTIME_EVIDENCE_UNKNOWN"]:[],human_understanding:"UNKNOWN"}};}
function harness(code=source){
  const nodes=new Map(),calls=[],errors=[],notices=[],doc={};
  class Element{
    constructor(id){this.id=id;this.dataset={};this.open=false;this.value="";this.checked=false;this.disabled=false;this.attributes={};}
    focus(){doc.activeElement=this;}
    getClientRects(){return [1];}
    setAttribute(key,value){this.attributes[key]=value;}
    removeAttribute(key){delete this.attributes[key];}
    querySelectorAll(selector){assert.equal(this.id,"questions");assert.equal(selector,"input");return fields;}
  }
  const get=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id);};
  const fields=["authority","assignment","reject_entry"].map(name=>Object.assign(get("q-"+name),{name}));
  doc.body=get("body");doc.documentElement=get("html");doc.activeElement=get("verify");
  const sandbox={current:view(),tab:"evidence",busy:false,document:doc,$:get,notice:value=>notices.push(value),reportError:error=>errors.push(error.message)};
  sandbox.evidenceKey=p=>typeof p.subject_hash==="string"&&p.subject_hash?JSON.stringify([sandbox.current?.case.id||"no-case",p.subject_hash]):"";
  const h={get,fields,doc,sandbox,calls,errors,notices,publish(){sandbox.current=view(8);get("review-decision").dataset.subjectKey='["case-A","subject-A"]';return clone(sandbox.current.case);}};
  let outcome=()=>h.publish();
  sandbox.command=async action=>{calls.push(action);assert.equal(action,"verify","The handoff must never submit answers, approve or apply");return outcome(h);};
  const taskStart=code.indexOf("function captureTaskFocus()"),taskEnd=code.indexOf("let caseInventory=",taskStart);
  const start=code.indexOf("async function verifyForReview()"),end=code.indexOf('$("review-form").onsubmit',start);
  assert.ok(taskStart>=0&&taskEnd>taskStart&&start>=0&&end>start,"Actual task and handler must exist");
  vm.createContext(sandbox);vm.runInContext(code.slice(taskStart,taskEnd)+code.slice(start,end),sandbox);
  h.outcome=fn=>{outcome=fn;};h.run=()=>get("verify").onclick();
  return h;
}
function assertClosed(h){assert.equal(h.get("review-decision").open,false);assert.equal(h.doc.activeElement,h.get("verify"));}
test("explicit successful eligible Verify opens the exact reloaded review and hands keyboard focus to a blank question",async()=>{
  const h=harness();await h.run();assert.equal(h.get("review-decision").open,true);assert.equal(h.doc.activeElement,h.fields[0]);
  assert.deepEqual(h.fields.map(field=>field.value),["","",""]);assert.equal(h.get("acknowledge").checked,false);
  assert.equal(h.sandbox.current.case.decision,null);assert.equal(h.sandbox.current.case.stage,"VERIFIED");assert.equal(h.sandbox.current.packet.human_understanding,"UNKNOWN");
  assert.deepEqual(h.calls,["verify"]);assert.deepEqual(h.errors,[]);assert.equal(h.sandbox.busy,false);
});
test("a pending command cannot open review early and task cleanup preserves the handed-off focus",async()=>{
  const h=harness();let finish;h.outcome(()=>new Promise(resolve=>{finish=()=>resolve(h.publish());}));
  const pending=h.run();assertClosed(h);assert.equal(h.sandbox.busy,true);finish();await pending;
  assert.equal(h.doc.activeElement,h.fields[0]);assert.equal(h.get("review-decision").open,true);assert.equal(h.sandbox.busy,false);
});
test("verify refusal and every reload failure leave disclosure and owner input unchanged",async t=>{
  for(const reason of ["SOURCE_REVIEW_REQUIRED","STALE_VERSION","transport failure","case reload failed","affordance reload failed","case-list reload failed after render"]){
    await t.test(reason,async()=>{
      const h=harness();h.fields[0].value="unsent draft";h.get("acknowledge").checked=true;
      h.outcome(()=>{if(reason.includes("after render"))h.publish();throw Error(reason);});await h.run();
      assertClosed(h);assert.deepEqual(h.errors,[reason]);assert.equal(h.fields[0].value,"unsent draft");assert.equal(h.get("acknowledge").checked,true);
      assert.deepEqual(h.calls,["verify"]);
    });
  }
});
test("HTTP success cannot hand off an ineligible, stale, different or unbound subject",async t=>{
  const controls={
    "runtime still blocked":(h)=>{h.sandbox.current.packet.eligible=false;h.sandbox.current.packet.blockers=["RUNTIME_EVIDENCE_UNKNOWN"];},
    "source blocker despite eligibility":(h)=>{h.sandbox.current.packet.blockers=["SOURCE_REVIEW_REQUIRED"];},
    "missing blocker inventory":(h)=>{delete h.sandbox.current.packet.blockers;},
    "wrong acknowledged case":(h,result)=>{result.id="case-B";},
    "wrong acknowledged revision":(h,result)=>{result.version++;},
    "wrong acknowledged stage":(h,result)=>{result.stage="APPROVED";},
    "switched current case":(h)=>{h.sandbox.current.case.id="case-B";},
    "newer current revision":(h)=>{h.sandbox.current.case.version++;},
    "closed current case":(h)=>{h.sandbox.current.case.stage="APPLIED";},
    "current owner decision":(h)=>{h.sandbox.current.case.decision={subject_hash:"subject-A"};},
    "changed subject hash":(h)=>{h.sandbox.current.packet.subject_hash="subject-B";},
    "changed subject dimensions":(h)=>{h.sandbox.current.packet.subject.semantic="model-B";},
    "missing subject hash":(h)=>{delete h.sandbox.current.packet.subject_hash;},
    "form belongs to another subject":(h)=>{h.get("review-decision").dataset.subjectKey='["case-B","subject-A"]';}
  };
  for(const [name,mutate]of Object.entries(controls))await t.test(name,async()=>{
    const h=harness();h.outcome(()=>{const result=h.publish();mutate(h,result);return result;});await h.run();assertClosed(h);assert.deepEqual(h.errors,[]);
  });
});
test("an existing owner decision is not treated as a fresh review opportunity",async()=>{
  const h=harness();h.sandbox.current.case.stage="APPROVED";h.sandbox.current.case.decision={subject_hash:"subject-A"};
  await h.run();assertClosed(h);assert.equal(h.sandbox.current.case.stage,"VERIFIED");assert.equal(h.sandbox.current.case.decision,null);
  // The service's explicit re-verification already clears an earlier decision; this UI adds no automatic new decision.
  const failed=harness();failed.sandbox.current.case.stage="APPROVED";failed.sandbox.current.case.decision={subject_hash:"subject-A"};
  failed.get("review-decision").open=true;const before=clone(failed.sandbox.current.case);
  failed.outcome(()=>{throw Error("verification failed");});await failed.run();
  assert.deepEqual(failed.sandbox.current.case,before);assert.equal(failed.get("review-decision").open,true);
});
test("leaving Evidence or moving focus during verification does not pull the user back",async()=>{
  for(const navigation of [h=>{h.sandbox.tab="code";},h=>{h.doc.activeElement=h.get("workspace-search");},
    h=>{h.doc.activeElement=h.doc.body;},h=>{h.doc.activeElement=h.doc.documentElement;}]){
    const h=harness();h.outcome(()=>{const result=h.publish();navigation(h);return result;});await h.run();
    assert.equal(h.get("review-decision").open,false);assert.notEqual(h.doc.activeElement,h.fields[0]);
  }
});
test("a pending review-input focus lost when reload replaces questions does not trigger the handoff",async()=>{
  const h=harness();let finish;h.outcome(()=>new Promise(resolve=>{finish=()=>{
    const result=h.publish();h.doc.activeElement=h.doc.body;resolve(result);
  };}));
  const pending=h.run();h.fields[2].focus();finish();await pending;
  assert.equal(h.get("review-decision").open,false);assert.notEqual(h.doc.activeElement,h.fields[0]);
});
test("same-subject drafts and acknowledgement are untouched; focus chooses the first unanswered field",async()=>{
  const h=harness();h.fields[0].value="owner-authored draft";h.fields[1].value="  ";h.get("acknowledge").checked=true;
  const values=h.fields.map(field=>field.value);await h.run();assert.deepEqual(h.fields.map(field=>field.value),values);
  assert.equal(h.get("acknowledge").checked,true);assert.equal(h.doc.activeElement,h.fields[1]);
  const complete=harness();complete.fields.forEach(field=>{field.value="owner-authored draft";});await complete.run();
  assert.equal(complete.doc.activeElement,complete.get("review-subject"));assert.deepEqual(complete.calls,["verify"]);
});
test("handoff oracles reject removed eligibility and current-revision guards",async()=>{
  for(const [marker,mutate]of [["p.eligible!==true||",h=>{h.sandbox.current.packet.eligible=false;}],
    ["c.version!==result.version||",h=>{h.sandbox.current.case.version++;}]]){
    assert.ok(source.includes(marker));const h=harness(source.replace(marker,""));
    h.outcome(()=>{const result=h.publish();mutate(h);return result;});await h.run();
    assert.throws(()=>assertClosed(h),assert.AssertionError,"The control must detect the unsafe auto-open");
  }
});
test("handoff oracle rejects an implementation that forgets to move keyboard focus",async()=>{
  const marker='(unanswered||$("review-subject")).focus();';assert.ok(source.includes(marker));
  const h=harness(source.replace(marker,""));await h.run();
  assert.throws(()=>assert.equal(h.doc.activeElement,h.fields[0]),assert.AssertionError);
});
