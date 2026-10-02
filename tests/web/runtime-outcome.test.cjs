"use strict";
// Actual task, API, lifecycle and Run handlers; controlled HTTP responses, not browser evidence.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
class Element{
  constructor(tag="div"){this.tag=tag;this.children=[];this.dataset={};this.attributes={};this.value="";this.textContent="";this.disabled=false;this.hidden=false;}
  append(...items){this.children.push(...items);}replaceChildren(...items){this.children=[...items];this.textContent="";}
  setAttribute(name,value){this.attributes[name]=String(value);}removeAttribute(name){delete this.attributes[name];}
}
const clone=value=>JSON.parse(JSON.stringify(value)),tick=()=>new Promise(resolve=>setImmediate(resolve));
const response=(data,status=200)=>({ok:status>=200&&status<300,status,json:async()=>clone(data)});
const deferred=()=>{let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return {promise,resolve,reject};};
function fixture(id="A",semantic="semantic-A",version=7){return {case:{id,version,stage:"PREVIEW",candidate:{states:["Draft","Submitted","Recommended"],transitions:[]}},packet:{subject:{semantic},subject_hash:"review-"+semantic},observations:[{kind:"previous observation"}]};}
function preview(id="instance-A",version=0,state="Draft",caseId="A",hash="semantic-A"){return {id,case_id:caseId,model_hash:hash,state,version};}
function committed(version=1,state="Submitted"){return {duplicate:false,committed:true,instance:preview("instance-A",version,state),effects:["Audit"]};}
function harness(code=source){
  const nodes=new Map(),requests=[],notices=[],bottom=[],posts=[],server={value:fixture(),fail:null},get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};let uuid=0;
  const s={current:fixture(),instance:preview(),status:{pack:{actions:["Submit","Recommend","Approve"]}},busy:false,lastDiagnostic:null,
    caseViews:new Map(),editId:null,inspectorSelection:null,modelView:"working",historyModel:null,historyLabel:"",canvasDirection:"AUTO",tab:"try",caseHistory:{can_undo:true,can_redo:true},affordanceData:{},
    token:"test",crypto:{randomUUID:()=>`operation-${++uuid}`},$:get,el:(tag,text)=>{const node=new Element(tag);if(text!==undefined)node.textContent=String(text);return node;},
    document:{body:new Element()},captureTaskFocus:()=>({}),restoreTaskFocus(){},cancelSourceRead(){},renderProblems(){},EijaShell:{bottom:(...args)=>bottom.push(args)},
    notice:(message,error=false)=>notices.push({message,error}),
    fetch:async(url,options)=>{
      const body=options.body?JSON.parse(options.body):undefined,request={path:url.slice(5),method:options.method||"GET",body};requests.push(request);
      if(body!==undefined){assert.ok(posts.length,"unexpected mutation "+request.path);return posts.shift()(request);}
      if(server.fail===request.path)throw Error("Refresh transport failed");
      if(request.path.endsWith("/affordances"))return response({affordances:[]});
      if(request.path.endsWith("/history"))return response({status:"ready",can_undo:true,can_redo:true});
      return response(server.value);
    },cases:async()=>{if(server.fail==="cases")throw Error("Case list refresh failed");}};
  s.render=()=>s.renderRuntime();vm.createContext(s);
  for(const [start,end]of [["class ApiError","function captureTaskFocus("],["async function task(","async function cases("],["async function load(","function render(){"]]){
    const from=code.indexOf(start),to=code.indexOf(end,from);assert.ok(from>=0&&to>from,start);vm.runInContext(code.slice(from,to),s);
  }
  for(const id of ["reset","undo-edit","redo-edit"]){const line=code.split("\n").find(line=>line.startsWith(`$("${id}").onclick=`));assert.ok(line);vm.runInContext(line,s);}
  get("actor").value="actor-A";s.renderRuntime();
  return {s,get,requests,notices,bottom,server,posts,
    action:name=>get("runtime-actions").children.find(node=>node.dataset.action===name),
    enqueue:(data,status=200)=>posts.push(()=>response(data,status)),
    feedback:()=>({text:get("runtime-result").textContent,data:{...get("runtime-result").dataset},commit:get("runtime-last-commit").textContent,state:get("runtime-state").textContent}),
    state:()=>JSON.parse(vm.runInContext("JSON.stringify({runtimeAttempt,runtimeCommit,runtimeEpoch,runtimeUncertain})",s))};
}
async function succeed(h){h.enqueue(committed());await h.action("Submit").onclick();assert.equal(h.feedback().data.status,"committed");}
test("a refusal replaces success as the latest attempt while preserving confirmed state and exact request identity",async()=>{
  const h=harness();await succeed(h);const before=clone(h.s.instance);h.get("actor").value="actor-B";
  h.enqueue({code:"ROLE_DENIED",message:"Wrong role",details:{refs:["law:role"],codes:["ROLE_DENIED"]}},409);await h.action("Approve").onclick();
  const feedback=h.feedback();assert.equal(feedback.data.status,"refused");assert.match(feedback.text,/Refused: Approve.*ROLE_DENIED/);assert.doesNotMatch(feedback.text,/Committed: Submit/);assert.match(feedback.commit,/Last acknowledged commit: Submit/);
  assert.deepEqual(clone(h.s.instance),before);assert.equal(feedback.state,"Submitted");assert.equal(feedback.data.actorId,"actor-B");assert.equal(feedback.data.caseRevision,"7");assert.equal(feedback.data.expectedVersion,"1");assert.equal(feedback.data.semanticHash,"semantic-A");
  assert.deepEqual(h.requests.filter(item=>item.method==="POST").map(item=>item.body),[{operation_id:"operation-1",actor_id:"actor-A",instance_id:"instance-A",action:"Submit",expected_version:0},{operation_id:"operation-2",actor_id:"actor-B",instance_id:"instance-A",action:"Approve",expected_version:1}]);
  assert.deepEqual(h.bottom,[]);assert.match(h.get("error-json").textContent,/law:role/);assert.equal(h.get("error-details").hidden,false);
});
test("transport, malformed JSON, malformed success and server errors remain unknown without a retry",async()=>{
  const failures=[()=>Promise.reject(Error("Failed to fetch")),()=>({ok:true,status:200,json:async()=>{throw Error("broken JSON");}}),()=>response({committed:true}),()=>response({code:"ROLE_DENIED",message:"Misleading server failure"},500),()=>response({code:"ROLE_DENIED"},409)];
  for(const fail of failures){const h=harness();await succeed(h);const before=clone(h.s.instance),count=h.requests.length;h.posts.push(fail);await h.action("Approve").onclick();
    assert.equal(h.feedback().data.status,"unknown");assert.match(h.feedback().text,/may have committed.*no automatic retry/);assert.match(h.feedback().commit,/Submit/);assert.deepEqual(clone(h.s.instance),before);assert.equal(h.requests.length,count+1);assert.equal(h.state().runtimeAttempt.command.operation_id,"operation-2");assert.deepEqual(h.bottom,[]);
  }
});
test("acknowledged commit survives case, affordance and case-list refresh failures",async()=>{
  for(const failure of ["cases/A","cases/A/affordances","cases"]){const h=harness();h.server.fail=failure;h.enqueue(committed());await h.action("Submit").onclick();
    assert.equal(h.feedback().data.status,"committed");assert.equal(h.feedback().data.refresh,"failed");assert.match(h.feedback().text,/Committed: Submit.*observations refresh failed/);assert.equal(h.s.instance.version,1);assert.equal(h.feedback().state,"Submitted");assert.match(h.get("error-json").textContent,/RUNTIME_REFRESH_FAILED/);assert.deepEqual(h.bottom,[]);
    h.server.fail=null;await h.s.load("A");assert.equal(h.feedback().data.status,"committed");assert.equal(h.s.instance.version,1);assert.equal(h.feedback().data.refresh,"current");assert.doesNotMatch(h.feedback().text,/refresh failed/);
  }
});
test("duplicate acknowledgement uses current returned instance without claiming new effects",async()=>{
  const h=harness(),original=committed();h.enqueue({duplicate:true,committed:false,instance:preview("instance-A",3,"Recommended"),original_result:original,effects:[]});await h.action("Submit").onclick();
  assert.equal(h.feedback().data.status,"duplicate");assert.match(h.feedback().text,/Previously committed.*no effects/);assert.doesNotMatch(h.feedback().text,/^Committed:/);assert.equal(h.s.instance.version,3);assert.equal(h.feedback().state,"Recommended");assert.equal(h.state().runtimeAttempt.result.original_result.instance.version,1);
});
test("preview creation acknowledgement survives refresh failure and removes an older instance's commit",async()=>{
  const h=harness();await succeed(h);h.server.fail="cases/A";h.enqueue(preview("new-instance"));await h.get("reset").onclick();
  assert.equal(h.feedback().data.status,"preview");assert.equal(h.feedback().data.refresh,"failed");assert.equal(h.s.instance.id,"new-instance");assert.equal(h.feedback().commit,"");assert.match(h.feedback().text,/New isolated preview acknowledged/);assert.equal(h.state().runtimeAttempt.command.expected_version,7);
});
test("same candidate refresh preserves observations but case/semantic changes clear runtime feedback and instance",async()=>{
  const h=harness();await succeed(h);h.server.value=fixture("A","semantic-A",8);await h.s.load("A");assert.equal(h.feedback().data.status,"committed");assert.equal(h.s.instance.version,1);assert.equal(h.feedback().data.caseRevision,"7");
  h.server.value=fixture("A","semantic-B",9);await h.s.load("A");assert.equal(h.s.instance,null);assert.equal(h.feedback().text,"");assert.equal(h.feedback().commit,"");assert.equal(h.feedback().data.operationId,undefined);
  h.server.value=fixture("B","semantic-C",1);await h.s.load("B");assert.equal(h.s.instance,null);assert.equal(h.feedback().text,"");
});
test("late success and failure cannot restore an old case or replace a newer attempt",async()=>{
  for(const reject of [false,true]){const h=harness(),pending=deferred();h.posts.push(()=>pending.promise);const run=h.action("Submit").onclick();await tick();h.server.value=fixture("B","semantic-B",2);await h.s.load("B");const count=h.requests.length;
    if(reject)pending.reject(Error("old transport failure"));else pending.resolve(response(committed()));await run;
    assert.equal(h.s.current.case.id,"B");assert.equal(h.s.instance,null);assert.equal(h.feedback().text,"");assert.equal(h.requests.length,count);assert.equal(h.s.lastDiagnostic,null);
  }
});
test("a pending request captures actor once and task busy guard prevents a second activation",async()=>{
  const h=harness(),pending=deferred();h.posts.push(()=>pending.promise);const action=h.action("Submit"),run=action.onclick();h.get("actor").value="changed-during-request";await action.onclick();
  assert.equal(h.requests.length,1);assert.equal(h.feedback().data.actorId,"actor-A");assert.match(h.feedback().text,/Actor: actor-A/);assert.doesNotMatch(h.feedback().text,/changed-during-request/);assert.equal(h.state().runtimeAttempt.command.actor_id,"actor-A");pending.resolve(response(committed()));await run;assert.equal(h.requests.filter(item=>item.method==="POST").length,1);assert.match(h.feedback().text,/Actor: actor-A/);
});
test("an old action callback cannot issue a command for another case revision",async()=>{
  const h=harness(),action=h.action("Submit");h.s.current.case.version=8;await action.onclick();assert.equal(h.requests.length,0);assert.equal(h.feedback().text,"");
});
test("an old action callback cannot target a replacement preview on the same case revision",async()=>{
  const h=harness(),old=h.action("Submit");h.enqueue(preview("new-instance"));await h.get("reset").onclick();const count=h.requests.length;
  await old.onclick();assert.equal(h.requests.length,count);assert.equal(h.s.instance.id,"new-instance");assert.equal(h.feedback().data.status,"preview");
});
test("attempt diagnostics remain the owned request error after an unrelated global error",async()=>{
  const h=harness();h.enqueue({code:"STATE_DENIED",message:"Unavailable here",details:{refs:["state:Draft"]}},409);await h.action("Submit").onclick();
  h.s.reportError(Error("Unrelated failure"));h.s.renderRuntimeFeedback();const text=h.get("runtime-attempt-identity").children.map(node=>node.textContent).join("\n");
  assert.match(text,/STATE_DENIED/);assert.match(text,/state:Draft/);assert.doesNotMatch(text,/Unrelated failure/);assert.equal(h.bottom.length,1);
});
test("history aliases cannot bypass current closed/missing-case undo and redo guards",async()=>{
  for(const id of ["undo-edit","redo-edit"])for(const stage of ["APPLIED","DISCARDED",null]){const h=harness();h.s.command=()=>{throw Error("Closed history must not send");};if(stage)h.s.current.case.stage=stage;else h.s.current=null;await h.get(id).onclick();assert.equal(h.requests.length,0);assert.equal(h.s.lastDiagnostic,null);}
});
test("acknowledged undo redo or discard clears obsolete runtime even if its case refresh fails",async()=>{
  for(const action of ["undo","redo","discard"]){const h=harness();await succeed(h);h.server.fail="cases/A";h.enqueue({id:"A",version:8});await assert.rejects(h.s.command(action),/Refresh transport failed/);assertClearedRuntimeSurface(h);}
});
function assertClearedRuntimeSurface(h){
  assert.equal(h.s.instance,null);assert.equal(h.feedback().text,"");assert.equal(h.feedback().commit,"");assert.equal(h.feedback().data.operationId,undefined);
  assert.equal(h.get("runtime-state").textContent,"Not started");assert.doesNotMatch(h.get("runtime-version").textContent,/instance-A|version 1/);
  assert.match(h.get("runtime-version").textContent,/No preview instance/);assert.ok(h.get("runtime-actions").children.length>0);assert.ok(h.get("runtime-actions").children.every(button=>button.disabled),"every old runtime action must immediately become disabled");
}
test("acknowledged semantic edit immediately invalidates the visible runtime when refresh fails",async()=>{
  const h=harness();await succeed(h);h.s.editable=()=>true;h.s.renderCanvas=()=>{};
  vm.runInContext(source.slice(source.indexOf("function commitChoice(choice)"),source.indexOf('$("transition-select").onchange')),h.s);
  h.enqueue({legal:true});h.enqueue({id:"A",version:8});h.server.fail="cases/A";
  await h.s.commitChoice({transaction:{kind:"retarget_transition",transition:"T",end:"target",state:"Recommended"}});assertClearedRuntimeSurface(h);
});
test("counterexample oracle detects the old success-text retention pattern",async()=>{
  const begin="  renderRuntimeFeedback();return runtimeAttempt;",failure="  renderRuntimeFeedback();reportError(error,{reveal:false});return false;";
  assert.ok(source.includes(begin)&&source.includes(failure));const h=harness(source.replace(begin,"  return runtimeAttempt;").replace(failure,"  reportError(error,{reveal:false});return false;"));
  await succeed(h);h.enqueue({code:"ROLE_DENIED",message:"Wrong role"},409);await h.action("Approve").onclick();assert.match(h.feedback().text,/Committed: Submit/);assert.throws(()=>assert.equal(h.feedback().data.status,"refused"),assert.AssertionError);
});
