"use strict";
// Actual task, API, lifecycle and Run handlers; controlled HTTP responses, not browser evidence.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(process.env.EIJA_RUNTIME_APP||path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
class Element{
  constructor(tag="div"){this.tag=tag;this.children=[];this.dataset={};this.attributes={};this.value="";this.textContent="";this.disabled=false;this.hidden=false;}
  append(...items){this.children.push(...items);}replaceChildren(...items){this.children=[...items];this.textContent="";}
  setAttribute(name,value){this.attributes[name]=String(value);}removeAttribute(name){delete this.attributes[name];}
  addEventListener(name,fn){this.events??={};this.events[name]=fn;}showModal(){this.open=true;}close(){this.open=false;}focus(){this.focused=true;}getClientRects(){return this.hidden?[]:[{}];}
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
    document:{body:new Element()},captureTaskFocus:()=>({}),restoreTaskFocus(){},cancelSourceRead(){},renderProblems(){},renderEditor(){},renderCanvas(){},EijaShell:{bottom:(...args)=>bottom.push(args)},
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
  for(const id of ["reset","undo-edit","redo-edit","history-undo"]){const line=code.split("\n").find(line=>line.startsWith(`$("${id}").onclick=`));assert.ok(line);vm.runInContext(line,s);}
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
  h.s.EijaCompare={render:()=>({select:()=>true,destroy(){}})};
  const original={states:["Draft","Submitted","Recommended"],transitions:[{id:"T",action:"Submit",role:"Owner",from_state:"Draft",to_state:"Submitted",guards:[],required_effects:[],forbidden_effects:[]}]};
  h.s.current.case.candidate=clone(original);const candidate=clone(original);candidate.transitions[0].to_state="Recommended";
  const transaction={kind:"retarget_transition",transition:"T",end:"target",state:"Recommended"};
  const previewStart=source.indexOf("let editPreview=null");assert.ok(previewStart>=0);
  vm.runInContext(source.slice(previewStart,source.indexOf('$("transition-select").onchange',previewStart)),h.s);
  h.enqueue({scope:"semantic-edit-preview",applied:false,persisted:false,case_id:"A",version:7,stage:"PREVIEW",semantic_hash:"semantic-A",current:original,transaction,legal:true,codes:[],refs:[],candidate,candidate_semantic_hash:"semantic-edited"});
  const before=clone(h.s.instance);await h.s.commitChoice({transaction});assert.deepEqual(clone(h.s.instance),before);assert.match(h.feedback().text,/Committed: Submit/);
  assert.equal(h.requests.filter(item=>item.path==="cases/A/edit").length,0);assert.equal(h.requests.at(-1).path,"cases/A/edit/preview");
  h.enqueue({id:"A",version:8,candidate});h.server.fail="cases/A";await h.get("edit-preview-apply").onclick();assertClearedRuntimeSurface(h);
  assert.equal(h.get("edit-preview-status").dataset.status,"committed");assert.match(h.get("edit-preview-status").textContent,/refresh failed/);
  assert.deepEqual(h.requests.filter(item=>item.path==="cases/A/edit").map(item=>item.body),[{expected_version:7,transaction}]);
});
test("edit reconciliation lock survives refused or unrelated refresh and clears only after its successful case load",async()=>{
  for(const failure of ["cases/A","cases/A/affordances","cases"]){const h=harness();vm.runInContext(source.slice(source.indexOf("function editable()"),source.indexOf("function selectedTransition()")),h.s);
    vm.runInContext('editNeedsRefresh.set("A",{caseId:"A",version:7,semanticHash:"semantic-A",status:"unknown"});editNeedsRefresh.set("B",{caseId:"B",version:1,semanticHash:"semantic-B",status:"committed"})',h.s);h.s.renderEditReconciliation();assert.equal(h.get("edit-reconciliation").hidden,false);assert.equal(h.s.editable(),false);
    h.server.fail=failure;await assert.rejects(h.s.load("A"),/refresh|Refresh/);assert.equal(vm.runInContext('editNeedsRefresh.has("A")',h.s),true);assert.equal(h.get("edit-reconciliation").hidden,false);assert.equal(h.s.editable(),false);h.server.fail=null;
    assert.equal(await h.s.load("A",()=>false),false);assert.equal(vm.runInContext('editNeedsRefresh.has("A")',h.s),true);
    h.server.value=fixture("B","semantic-B",2);await h.s.load("B");assert.equal(vm.runInContext('editNeedsRefresh.has("A")',h.s),true);assert.equal(vm.runInContext('editNeedsRefresh.has("B")',h.s),false);assert.equal(h.get("edit-reconciliation").hidden,true);assert.equal(h.s.editable(),true);
    h.server.value=fixture("A","semantic-edited",8);assert.equal(await h.s.load("A"),true);assert.equal(vm.runInContext("editNeedsRefresh.size",h.s),0);assert.equal(h.get("edit-reconciliation").hidden,true);assert.equal(h.get("edit-reconciliation-status").textContent,"");assert.equal(h.get("edit-reconciliation").dataset.caseId,undefined);assert.equal(h.s.editable(),true);
  }
});
test("an unresolved edit cannot undo an older edit before reconciliation",async()=>{
  const h=harness();vm.runInContext('editNeedsRefresh.set("A",{caseId:"A",version:7,semanticHash:"semantic-A",status:"unknown"})',h.s);
  h.enqueue({id:"A",version:8});let refusal=null;try{await h.s.command("undo");}catch(error){refusal=error;}
  assert.equal(h.requests.filter(item=>item.method==="POST").length,0,"the prior Undo must not reach transport while the edit outcome is unresolved");
  assert.equal(refusal?.code,"EDIT_RECONCILIATION_REQUIRED");assert.equal(vm.runInContext('editNeedsRefresh.has("A")',h.s),true);
});
test("all case commands stop before transport while its edit outcome requires reconciliation",async()=>{
  for(const status of ["unknown","committed"])for(const action of ["select","propose","save","discard","layout","verify","approve","apply","undo","redo"]){const h=harness(),before=JSON.stringify(h.s.current),instanceBefore=clone(h.s.instance);
    vm.runInContext(`editNeedsRefresh.set("A",{caseId:"A",version:7,semanticHash:"semantic-A",status:${JSON.stringify(status)}})`,h.s);
    h.enqueue({id:"A",version:8});let refusal=null;try{await h.s.command(action,{test_context:"unchanged request"});}catch(error){refusal=error;}
    assert.equal(h.requests.length,0,`${status}: ${action} must not reach any transport`);assert.equal(refusal?.code,"EDIT_RECONCILIATION_REQUIRED");assert.equal(JSON.stringify(h.s.current),before);assert.deepEqual(clone(h.s.instance),instanceBefore);assert.equal(vm.runInContext('editNeedsRefresh.has("A")',h.s),true);
  }
});
test("a reconciliation lock for one case does not prohibit another case's command",async()=>{
  const h=harness();vm.runInContext('editNeedsRefresh.set("A",{caseId:"A",version:7,semanticHash:"semantic-A",status:"unknown"})',h.s);h.s.current=fixture("B","semantic-B",2);h.server.value=fixture("B","semantic-B",3);h.enqueue({id:"B",version:3});await h.s.command("save");
  assert.deepEqual(h.requests.filter(item=>item.method==="POST").map(item=>({path:item.path,body:item.body})),[{path:"cases/B/save",body:{expected_version:2}}]);assert.equal(vm.runInContext('editNeedsRefresh.has("A")',h.s),true);assert.equal(h.s.current.case.id,"B");
});
test("locked Model History and runtime handlers reject retained callbacks without replacing runtime evidence",async()=>{
  for(const status of ["unknown","committed"]){const h=harness();await succeed(h);const oldAction=h.action("Submit").onclick,origin={caseId:"A",revision:7,semanticHash:"semantic-A",instanceId:"instance-A",instanceVersion:1};
    vm.runInContext(`editNeedsRefresh.set("A",{caseId:"A",version:7,semanticHash:"semantic-A",status:${JSON.stringify(status)}})`,h.s);h.s.renderEditReconciliation();h.s.renderRuntime();
    const before={requests:h.requests.length,current:JSON.stringify(h.s.current),instance:clone(h.s.instance),runtime:h.state(),feedback:h.feedback()};
    for(const id of ["undo-edit","redo-edit","history-undo","history-redo","reset"]){assert.equal(h.get(id).disabled,true,id+" disabled");await h.get(id).onclick();}
    assert.ok(h.get("runtime-actions").children.every(button=>button.disabled));await oldAction();await h.action("Submit").onclick();assert.equal(await h.s.executeRuntime("Submit",origin),false);assert.equal(await h.s.startRuntimePreview(),false);
    assert.equal(h.requests.length,before.requests);assert.equal(JSON.stringify(h.s.current),before.current);assert.deepEqual(clone(h.s.instance),before.instance);assert.deepEqual(h.state(),before.runtime);assert.deepEqual(h.feedback(),before.feedback);assert.equal(h.s.lastDiagnostic,null);
  }
});
test("another case can execute or start its runtime while the original case remains locked",async()=>{
  const h=harness();vm.runInContext('editNeedsRefresh.set("A",{caseId:"A",version:7,semanticHash:"semantic-A",status:"unknown"})',h.s);
  h.s.current=fixture("B","semantic-B",2);h.s.instance=preview("instance-B",0,"Draft","B","semantic-B");h.server.value=fixture("B","semantic-B",2);h.s.renderRuntime();assert.equal(h.action("Submit").disabled,false);
  h.enqueue({duplicate:false,committed:true,instance:preview("instance-B",1,"Submitted","B","semantic-B"),effects:["Audit"]});await h.action("Submit").onclick();assert.equal(h.feedback().data.status,"committed");assert.equal(h.s.instance.case_id,"B");
  h.enqueue(preview("new-instance-B",0,"Draft","B","semantic-B"));await h.get("reset").onclick();assert.equal(h.feedback().data.status,"preview");assert.equal(h.s.instance.id,"new-instance-B");
  assert.deepEqual(h.requests.filter(item=>item.method==="POST").map(item=>item.path),["cases/B/execute","cases/B/preview"]);assert.equal(vm.runInContext('editNeedsRefresh.has("A")',h.s),true);assert.equal(vm.runInContext('editNeedsRefresh.has("B")',h.s),false);
});
test("counterexample oracle detects the old success-text retention pattern",async()=>{
  const begin="  renderRuntimeFeedback();return runtimeAttempt;",failure="  renderRuntimeFeedback();reportError(error,{reveal:false});return false;";
  assert.ok(source.includes(begin)&&source.includes(failure));const h=harness(source.replace(begin,"  return runtimeAttempt;").replace(failure,"  reportError(error,{reveal:false});return false;"));
  await succeed(h);h.enqueue({code:"ROLE_DENIED",message:"Wrong role"},409);await h.action("Approve").onclick();assert.match(h.feedback().text,/Committed: Submit/);assert.throws(()=>assert.equal(h.feedback().data.status,"refused"),assert.AssertionError);
});

// S07/US08: the route identifies the attempted action's model rule, not a solver witness.
function recoveryHarness(code=source,action="Save"){
  const h=harness(code),routes=[];
  h.s.current.case.candidate.transitions=[{id:"save-rule",action,role:"Agent",from_state:"Submitted",to_state:"Recommended",guards:[],required_effects:["Audit"],forbidden_effects:[]}];
  h.s.status.pack.actions=[action,"Other"];h.server.value=clone(h.s.current);
  h.s.workbench={pack:{id:"test-pack"},connection:{status:"unavailable"}};h.s.impactSequence=0;
  h.s.workingModel=()=>h.s.current?.case.candidate;
  h.s.selectedConcept=()=>h.s.workingModel()?.transitions.find(item=>item.id===h.s.inspectorSelection?.id);
  h.s.switchTab=name=>{h.s.tab=name;routes.push(["tab",name]);};
  h.s.EijaShell.reveal=name=>routes.push(["reveal",name]);h.s.EijaTree={reveal:(_,kind,id)=>routes.push(["tree",kind,id])};
  for(const [start,end]of [["function inspectWorkingTransition(","function openComparisonImpact("],["function renderSelectionDetail()","function followReference("]]){
    const from=code.indexOf(start),to=code.indexOf(end,from);assert.ok(from>=0&&to>from,start);vm.runInContext(code.slice(from,to),h.s);
  }
  h.s.renderWorkbench=()=>h.s.renderSelectionDetail();h.s.renderRuntime();
  const returnContext=()=>h.get("selection-detail").children.find(node=>node.dataset.runtimeRuleReturn==="true");
  return Object.assign(h,{routes,returnContext,ruleLink:()=>h.get("runtime-rule-navigation").children.find(node=>node.tag==="button"),backLink:()=>returnContext()?.children.find(node=>node.dataset.runtimeAttempt)});
}
async function refusedRule(h,action="Save"){
  h.enqueue({code:"ROLE_DENIED",message:"Actor has no required role",details:{refs:["law:role"],codes:["ROLE_DENIED"]}},409);
  await h.action(action).onclick();assert.equal(h.feedback().data.status,"refused");
}
function retainedRuntime(h){return JSON.stringify({current:h.s.current,instance:h.s.instance,runtime:h.state(),requests:h.requests,feedback:h.feedback(),diagnostic:h.get("error-json").textContent,attempt:h.get("runtime-attempt-identity").children.map(node=>node.textContent)});}

test("refused action opens its exact working rule and returns focus to the same retained attempt without requests",async()=>{
  const h=recoveryHarness();await refusedRule(h);const before=retainedRuntime(h),link=h.ruleLink();
  assert.equal(link.textContent,"Inspect Save rule");assert.equal(link.type,"button");assert.equal(link.dataset.runtimeRule,"save-rule");
  assert.match(h.get("runtime-rule-navigation").children[1].textContent,/Model rule for the attempted action · revision 7/);
  h.s.modelView="history";assert.equal(link.onclick(),true);assert.equal(h.s.tab,"model");assert.equal(h.s.modelView,"working");assert.equal(h.s.editId,"save-rule");
  assert.deepEqual(clone(h.s.inspectorSelection),{kind:"transition",id:"save-rule"});assert.equal(h.get("transition-select").focused,true);
  assert.deepEqual(h.routes,[["tab","model"],["reveal","inspector"],["tree","transition","save-rule"]]);
  assert.ok(h.returnContext().children.some(node=>/From the refused Save attempt · revision 7/.test(node.textContent)));
  const back=h.backLink();assert.equal(back.textContent,"Return to Save attempt");assert.equal(back.dataset.runtimeAttempt,"operation-1");
  assert.equal(back.onclick(),true);assert.equal(h.s.tab,"try");assert.equal(h.ruleLink().focused,true);assert.equal(retainedRuntime(h),before);
});

test("recovery label and transition binding use the captured action exactly, not Save or current actor",async()=>{
  const action="Submit review <candidate>",h=recoveryHarness(source,action);await refusedRule(h,action);h.get("actor").value="different actor";
  assert.equal(h.ruleLink().textContent,`Inspect ${action} rule`);assert.equal(h.ruleLink().onclick(),true);assert.equal(h.backLink().textContent,`Return to ${action} attempt`);
  assert.equal(h.state().runtimeAttempt.actorId,"actor-A");assert.equal(h.s.editId,"save-rule");
});

async function staleRecoveryOracle(code=source){
  const mutations=[
    ["case",h=>{h.s.current.case.id="B";}],
    ["revision",h=>{h.s.current.case.version=8;}],
    ["semantic",h=>{h.s.current.packet.subject.semantic="semantic-B";}],
    ["candidate bytes",h=>{h.s.current.case.candidate.transitions[0].role="Owner";}],
    ["no candidate",h=>{h.s.current.case.candidate=null;}],
    ["instance identity",h=>{h.s.instance.id="new-instance";}],
    ["instance version",h=>{h.s.instance.version=4;}],
    ["instance case",h=>{h.s.instance.case_id="B";}],
    ["instance semantic",h=>{h.s.instance.model_hash="semantic-B";}],
    ["pending edit reconciliation",h=>vm.runInContext('editNeedsRefresh.set("A",{})',h.s)],
    ["changed captured action",h=>vm.runInContext('runtimeAttempt.action="Other"',h.s)]
  ];
  for(const [name,mutate]of mutations){
    const h=recoveryHarness(code);await refusedRule(h);const link=h.ruleLink();assert.equal(link.onclick(),true);const back=h.backLink();mutate(h);
    const before=retainedRuntime(h),routes=clone(h.routes);assert.equal(link.onclick(),false,name+" forward blocked");assert.equal(back.onclick(),false,name+" return blocked");
    assert.equal(retainedRuntime(h),before);h.s.renderRuntimeFeedback();assert.equal(h.ruleLink(),undefined,name+" no link");assert.equal(h.get("runtime-rule-navigation").hidden,false);
    assert.match(h.get("runtime-rule-navigation").children[0].textContent,/Rule navigation unavailable/);assert.deepEqual(h.routes,routes);
    h.s.renderSelectionDetail();assert.equal(h.backLink(),undefined,name+" old return removed");
  }
}
test("stale or incoherent subject refuses both saved callbacks and removes their rendered routes",()=>staleRecoveryOracle());

async function ambiguousRuleOracle(code=source){
  const rows=[[],[{id:"one",action:"Save"},{id:"two",action:"Save"}],[{id:"same",action:"Save"},{id:"same",action:"Other"}],[{id:"",action:"Save"}],[{action:"Save"}]];
  for(const transitions of rows){const h=recoveryHarness(code);h.s.current.case.candidate.transitions=transitions;await refusedRule(h);assert.equal(h.ruleLink(),undefined);assert.match(h.get("runtime-rule-navigation").children[0].textContent,/one unique rule/);assert.equal(h.routes.length,0);}
  for(const hash of [null,""]){const h=recoveryHarness(code);h.s.current.packet.subject.semantic=hash;h.s.instance.model_hash=hash;h.s.renderRuntime();await refusedRule(h);assert.equal(h.ruleLink(),undefined);}
}
test("missing identities and ambiguous action or transition ID never produce a guessed model route",()=>ambiguousRuleOracle());

test("new attempts, reset and case changes invalidate prior recovery controls without hiding raw refusal",async()=>{
  for(const change of ["new attempt","reset","case switch"]){const h=recoveryHarness();await refusedRule(h);const old=h.ruleLink();old.onclick();const back=h.backLink();
    if(change==="new attempt"){await refusedRule(h);assert.equal(h.state().runtimeAttempt.requestId,"operation-2");}
    else if(change==="reset"){h.enqueue(preview("replacement"));await h.get("reset").onclick();}
    else {h.server.value=fixture("B","semantic-B",1);await h.s.load("B");}
    const before=retainedRuntime(h),routes=clone(h.routes);assert.equal(old.onclick(),false);assert.equal(back.onclick(),false);assert.equal(retainedRuntime(h),before);assert.deepEqual(h.routes,routes);
    assert.equal(h.backLink(),undefined,"the old return button is removed without a full inspector render");
    if(change==="new attempt"){assert.match(h.get("error-json").textContent,/ROLE_DENIED/);assert.match(h.get("runtime-attempt-identity").children.map(node=>node.textContent).join(" "),/ROLE_DENIED/);}
    else assert.equal(h.get("runtime-rule-navigation").hidden,true);
  }
});

test("pending, unknown and acknowledged outcomes do not claim a refusal rule route",async()=>{
  for(const outcome of ["pending","unknown","committed"]){const h=recoveryHarness();
    if(outcome==="pending"){const pending=deferred();h.posts.push(()=>pending.promise);const request=h.action("Save").onclick();assert.equal(h.get("runtime-rule-navigation").hidden,true);pending.resolve(response(committed()));await request;}
    else {if(outcome==="unknown")h.posts.push(()=>Promise.reject(Error("transport unavailable")));else h.enqueue(committed());await h.action("Save").onclick();}
    assert.equal(h.get("runtime-rule-navigation").hidden,true);assert.equal(h.ruleLink(),undefined);
  }
});

test("return belongs to the selected working rule and cannot switch from another inspector context",async()=>{
  for(const change of [h=>{h.s.inspectorSelection={kind:"state",id:"Draft"};},h=>{h.s.inspectorSelection={kind:"transition",id:"other"};},h=>{h.s.modelView="baseline";}]){
    const h=recoveryHarness();await refusedRule(h);h.ruleLink().onclick();const back=h.backLink();change(h);const routes=clone(h.routes),before=retainedRuntime(h);assert.equal(back.onclick(),false);assert.equal(retainedRuntime(h),before);assert.deepEqual(h.routes,routes);
  }
});

async function pinnedInspectorReturnOracle(code=source){
  for(const tab of ["code","evidence","try"]){const h=recoveryHarness(code);await refusedRule(h);h.ruleLink().onclick();const back=h.backLink(),before=retainedRuntime(h);
    h.s.switchTab(tab);assert.equal(h.backLink(),back,"presentation switch retains the visible inspector button");assert.equal(back.onclick(),true,tab);assert.equal(h.s.tab,"try");assert.equal(h.ruleLink().focused,true);assert.equal(retainedRuntime(h),before);
  }
}
test("a pinned inspector return works from other views while retaining the exact selected rule and attempt",()=>pinnedInspectorReturnOracle());

async function scopedInvalidationOracle(code=source){
  for(const change of ["new attempt","clear","edit reconciliation"]){const h=recoveryHarness(code);await refusedRule(h);h.ruleLink().onclick();const back=h.backLink();
    const unrelated=new Element("input");unrelated.value="unsent inspector draft";unrelated.focus();h.get("selection-detail").append(unrelated);h.get("edit-role").value="unsent field";
    h.s.renderRuntimeFeedback();assert.equal(h.backLink(),back,"unchanged recovery context preserves its original button");
    if(change==="new attempt")await refusedRule(h);
    else if(change==="clear")h.s.clearRuntime();
    else {vm.runInContext('editNeedsRefresh.set("A",{caseId:"A",version:7,status:"unknown"})',h.s);h.s.renderEditReconciliation();}
    assert.equal(h.backLink(),undefined);assert.equal(h.returnContext().hidden,true);assert.equal(back.onclick(),false);
    assert.ok(h.get("selection-detail").children.includes(unrelated));assert.equal(unrelated.value,"unsent inspector draft");assert.equal(unrelated.focused,true);assert.equal(h.get("edit-role").value,"unsent field");
  }
}
test("attempt invalidation updates only recovery controls and retains unrelated inspector input and focus",()=>scopedInvalidationOracle());

test("recovery oracles reject weak identity guards, dead visible returns and stale inspector controls",async()=>{
  const mutants=[
    ["attempt.caseVersion!==current.case.version||","",staleRecoveryOracle],
    ["JSON.stringify(candidate)!==attempt.candidateJSON||","",staleRecoveryOracle],
    ['return matches.length===1&&typeof target.id','return matches.length>=1&&typeof target.id',ambiguousRuleOracle],
    ['&&candidate.transitions.filter(item=>item.id===target.id).length===1',"",ambiguousRuleOracle],
    ['runtimeRuleInspection!==inspection||modelView','runtimeRuleInspection!==inspection||tab!=="model"||modelView',pinnedInspectorReturnOracle],
    ['  renderRuntimeRuleNavigation();renderRuntimeRuleReturn($("selection-detail"));\n  $("runtime-last-commit")','  renderRuntimeRuleNavigation();\n  $("runtime-last-commit")',scopedInvalidationOracle]
  ];
  for(const [before,after,oracle]of mutants){assert.equal(source.split(before).length,2,before);await assert.rejects(oracle(source.replace(before,after)),assert.AssertionError,before);}
});
