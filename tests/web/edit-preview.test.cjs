"use strict";
// Actual API, task and edit-preview handlers with controlled HTTP/render boundaries; no browser claim.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
const clone=value=>JSON.parse(JSON.stringify(value));
const transaction={kind:"retarget_transition",transition:"T",end:"target",state:"Done"};
function model(target="Review"){return {id:"workflow",states:["Draft","Review","Done"],initial_state:"Draft",transitions:[{id:"T",action:"Submit",role:"Owner",from_state:"Draft",to_state:target,guards:["authorized"],required_effects:["Audit"],forbidden_effects:[]}]};}
function fixture(){return {case:{id:"case-A",version:7,stage:"PREVIEW",candidate:model(),baseline:model()},packet:{subject:{semantic:"semantic-before"}},observations:[{kind:"retained"}]};}
function checked(overrides={}){return {scope:"semantic-edit-preview",applied:false,persisted:false,case_id:"case-A",version:7,stage:"PREVIEW",semantic_hash:"semantic-before",current:model(),transaction:clone(transaction),legal:true,codes:[],refs:[],candidate:model("Done"),candidate_semantic_hash:"semantic-after",...overrides};}
const response=(data,status=200)=>({ok:status>=200&&status<300,status,json:async()=>clone(data)});
const deferred=()=>{let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return {promise,resolve,reject};};
class Element{
  constructor(document,id=""){this.document=document;this.id=id;this.children=[];this.dataset={};this.attributes={};this.events={};this.textContent="";this.disabled=false;this.hidden=false;this.open=false;this.isConnected=true;}
  append(...items){this.children.push(...items);}replaceChildren(...items){this.children=[...items];this.textContent="";}
  setAttribute(name,value){this.attributes[name]=String(value);}removeAttribute(name){delete this.attributes[name];}
  addEventListener(name,fn){this.events[name]=fn;}getClientRects(){return this.hidden?[]:[{}];}focus(){this.document.activeElement=this;}
  showModal(){this.open=true;}close(){this.open=false;}
  dispatch(type,values={}){const event={prevented:false,stopped:false,preventDefault(){this.prevented=true;},stopPropagation(){this.stopped=true;},...values};this.events[type]?.(event);return event;}
}
function slice(code,start,end){const from=code.indexOf(start),to=code.indexOf(end,from);assert.ok(from>=0&&to>from,start);return code.slice(from,to);}
function harness(code=source){
  const nodes=new Map(),document={activeElement:null},get=id=>{if(!nodes.has(id))nodes.set(id,new Element(document,id));return nodes.get(id);};document.body=new Element(document,"body");
  const requests=[],queue=[],notices=[],comparisons=[],reloads=[],bottom=[],reload={error:null,pending:null};let clears=0,canvas=0,refreshes=0;
  const s={current:fixture(),modelView:"working",busy:false,lastDiagnostic:null,instance:{id:"retained-runtime"},token:"test",document,$:get,
    captureTaskFocus:()=>({}),restoreTaskFocus(){},renderProblems(){},EijaShell:{bottom:(...args)=>bottom.push(args)},
    notice:(message,error=false)=>notices.push({message,error}),renderCanvas:()=>{canvas++;},renderEditor(){},refreshCurrentModel:async()=>{refreshes++;},
    clearRuntime:()=>{clears++;s.instance=null;},
    fetch:async(url,options)=>{const request={path:url.slice(5),method:options.method||"GET",body:options.body?JSON.parse(options.body):undefined};requests.push(request);assert.ok(queue.length,"Unexpected HTTP request: "+request.path);return queue.shift()(request);},
    load:async(id,canPublish)=>{reloads.push({id,canPublish});if(reload.pending)await reload.pending.promise;if(reload.error)throw reload.error;return !canPublish||canPublish();},
    EijaCompare:{render:(root,current,options)=>{const record={root,current:clone(current),options:clone(options),selected:null,destroyed:false};comparisons.push(record);return {select:value=>{record.selected=clone(value);return true;},destroy:()=>{record.destroyed=true;}};}}};
  vm.createContext(s);
  vm.runInContext(slice(code,"class ApiError","function captureTaskFocus("),s);
  vm.runInContext(slice(code,"async function task(","async function cases("),s);
  vm.runInContext(slice(code,"function editable()","function selectedTransition()"),s);
  vm.runInContext(slice(code,"let editNeedsRefresh=","let runtimeAttempt="),s);
  vm.runInContext(slice(code,"let editPreview=null","$(\"transition-select\").onchange"),s);
  get("edit-source").focus();
  return {s,get,requests,notices,comparisons,reloads,bottom,reload,queue,
    enqueue:(data,status=200)=>queue.push(()=>response(data,status)),
    propose:(value=transaction)=>s.commitChoice({transaction:value}),
    confirm:()=>get("edit-preview-apply").onclick(),close:()=>get("edit-preview-cancel").onclick(),
    phase:()=>get("edit-preview-status").dataset.status,counts:()=>({clears,canvas,refreshes}),
    read:expression=>vm.runInContext(expression,s),writes:()=>requests.filter(request=>request.path.endsWith("/edit"))};
}
async function ready(h,check=checked()){h.enqueue(check);assert.equal(await h.propose(),true);assert.equal(h.phase(),"ready");}

function assertCapturedSubject(h){
  assert.equal(h.get("edit-preview-subject").textContent,`Case case-A · Captured revision 7 · before ${"semantic-before".slice(0,12)} → proposed ${"semantic-after".slice(0,12)}. Exact identities are in the server preview below.`);
}

test("comparison title and footer describe captured snapshots without asserting a submission outcome",()=>{
  const html=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/index.html"),"utf8");
  const dialog=slice(html,'<dialog id="edit-preview"',"</dialog>");
  assert.match(dialog,/<h2 id="edit-preview-title">Captured edit comparison<\/h2>/);
  assert.match(dialog,/<span>Captured snapshots; see submission outcome above\. This comparison does not verify behavior\.<\/span>/);
  assert.doesNotMatch(dialog,/Only Apply edit submits|Uncommitted edit preview/);
});

test("preview alone renders exact server snapshots without a write; explicit Apply sends one original request",async()=>{
  const h=harness(),before=JSON.stringify(h.s.current);await ready(h);assertCapturedSubject(h);assert.match(h.get("edit-preview-status").textContent,/No model has changed/);
  assert.deepEqual(h.requests,[{path:"cases/case-A/edit/preview",method:"POST",body:{transaction}}]);
  assert.equal(JSON.stringify(h.s.current),before);assert.equal(h.s.instance.id,"retained-runtime");assert.equal(h.s.busy,false);assert.equal(h.get("edit-preview").open,true);
  assert.deepEqual(h.comparisons[0].current.case,{id:"case-A",version:7,baseline:model(),candidate:model("Done")});assert.deepEqual(h.comparisons[0].options,{preview:true});assert.deepEqual(h.comparisons[0].selected,{kind:"transition",id:"T"});
  h.enqueue({id:"case-A",version:8,candidate:model("Done")});await h.confirm();
  assert.deepEqual(h.writes().map(item=>item.body),[{expected_version:7,transaction}]);assert.equal(h.reloads.length,1);assert.equal(h.reloads[0].id,"case-A");assert.equal(h.counts().clears,1);assert.equal(h.get("edit-preview").open,false);assert.equal(h.s.busy,false);assert.match(h.notices.at(-1).message,/transaction committed/);
});

test("Cancel, Escape and native cancel close pending checks and silence late success or failure",async()=>{
  for(const method of ["button","Escape","cancel"])for(const reject of [false,true]){
    const h=harness(),pending=deferred();h.queue.push(()=>pending.promise);const run=h.propose();assert.equal(h.s.busy,false);assert.equal(h.get("edit-preview-cancel").disabled,false);
    if(method==="button")h.close();else {const event=h.get("edit-preview").dispatch(method==="Escape"?"keydown":"cancel",{key:method});assert.equal(event.prevented,true);if(method==="Escape")assert.equal(event.stopped,true);}
    const retained={notices:h.notices.length,phase:h.phase(),diagnostic:h.s.lastDiagnostic};assert.equal(h.get("edit-preview").open,false);assert.equal(h.s.document.activeElement,h.get("edit-source"));
    if(reject)pending.reject(Error("late discarded failure"));else pending.resolve(response(checked()));await run;
    assert.equal(h.requests.length,1);assert.equal(h.writes().length,0);assert.equal(h.comparisons.length,0);assert.equal(h.notices.length,retained.notices);assert.equal(h.phase(),retained.phase);assert.equal(h.s.lastDiagnostic,retained.diagnostic);assert.equal(h.get("edit-preview").open,false);
  }
});

test("a replaced preview owns readiness and old responses cannot repaint its subject",async()=>{
  for(const reject of [false,true]){const h=harness(),pending=deferred();h.queue.push(()=>pending.promise);const old=h.propose();const next={...transaction,state:"Draft"};h.enqueue(checked({transaction:next,candidate:model("Draft"),candidate_semantic_hash:"semantic-next"}));await h.propose(next);
    const text=h.get("edit-preview-json").textContent;if(reject)pending.reject(Error("old failure"));else pending.resolve(response(checked()));await old;
    assert.equal(h.phase(),"ready");assert.equal(h.get("edit-preview-json").textContent,text);assert.equal(h.get("edit-preview").dataset.proposedSemanticHash,"semantic-next");assert.equal(h.comparisons.length,1);assert.equal(h.s.lastDiagnostic,null);assert.equal(h.writes().length,0);
  }
});

test("case revision semantic model stage and inspection changes during checking or before Apply refuse stale intent",async()=>{
  const changes=[s=>{s.current.case.id="case-B";},s=>{s.current.case.version=8;},s=>{s.current.packet.subject.semantic="other-semantic";},s=>{s.current.case.candidate.transitions[0].to_state="Draft";},s=>{s.current.case.stage="APPROVED";},s=>{s.current.case.stage="DISCARDED";},s=>{s.current.case.candidate=null;},s=>{s.modelView="history";},s=>{s.modelView="baseline";},s=>{s.current=null;}];
  for(const change of changes)for(const when of ["pending","ready"]){const h=harness();if(when==="pending"){const pending=deferred();h.queue.push(()=>pending.promise);const run=h.propose();change(h.s);pending.resolve(response(checked()));await run;}else {await ready(h);change(h.s);await h.confirm();}
    assert.equal(h.phase(),"stale");assert.equal(h.get("edit-preview-apply").disabled,true);assert.equal(h.writes().length,0);assert.equal(h.reloads.length,0);assert.equal(h.counts().clears,0);
  }
});

test("server check identity cannot name a different case revision semantic model or stage",async()=>{
  const mismatches=[{case_id:"case-B"},{version:8},{semantic_hash:"other-semantic"},{current:model("Done")},{stage:"APPROVED"}];
  for(const mismatch of mismatches){const h=harness(),serverCheck=checked(mismatch);h.enqueue(serverCheck);await h.propose();assert.equal(h.phase(),"stale");assert.equal(h.s.lastDiagnostic.code,"EDIT_PREVIEW_STALE");assert.deepEqual(JSON.parse(h.get("edit-preview-json").textContent),serverCheck);assert.equal(h.writes().length,0);assert.equal(h.comparisons.length,0);}
});

test("unknown or malformed check contract cannot enable Apply",async()=>{
  const malformed=[null,{legal:true},checked({scope:"other"}),checked({applied:true}),checked({persisted:true}),checked({legal:"true"}),checked({codes:[4]}),checked({refs:null}),checked({transaction:{...transaction,state:"Draft"}}),checked({candidate:null}),checked({candidate_semantic_hash:""}),checked({legal:false,candidate:model()}),checked({legal:false,candidate:null,candidate_semantic_hash:"unexpected-proposed-identity"})];
  for(const check of malformed){const h=harness();h.enqueue(check);await h.propose();await h.confirm();assert.equal(h.phase(),"failed");assert.equal(h.s.lastDiagnostic.code,"RESPONSE_INVALID");assert.equal(h.get("edit-preview-apply").disabled,true);assert.equal(h.writes().length,0);assert.equal(h.reloads.length,0);}
});

test("kernel refusal retains exact diagnostics and captured model without repairing a request",async()=>{
  const h=harness(),before=JSON.stringify(h.s.current),codes=["LAW:requires-step"],refs=["law:requires-step","state:Done"];
  h.enqueue(checked({legal:false,candidate:null,candidate_semantic_hash:null,codes,refs}));await h.propose();await h.confirm();
  assert.equal(h.phase(),"refused");assert.deepEqual(clone(h.s.lastDiagnostic.details),{codes,refs});assert.equal(JSON.stringify(h.s.current),before);assert.equal(h.s.instance.id,"retained-runtime");assert.equal(h.comparisons.length,0);assert.equal(h.writes().length,0);assert.equal(h.reloads.length,0);assert.deepEqual(h.bottom,[]);
});

test("preview transport failures or unusable comparison output cannot submit or enable Apply",async()=>{
  const failures=[()=>Promise.reject(Error("Preview disconnected")),()=>({ok:true,status:200,json:async()=>{throw Error("invalid JSON");}})];
  for(const fail of failures){const h=harness(),before=JSON.stringify(h.s.current);h.queue.push(fail);await h.propose();await h.confirm();assert.equal(h.phase(),"failed");assert.equal(h.writes().length,0);assert.equal(JSON.stringify(h.s.current),before);assert.equal(h.get("edit-preview-apply").disabled,true);assert.deepEqual(h.bottom,[]);}
  const h=harness();h.s.EijaCompare.render=()=>({destroy(){}});h.enqueue(checked());await h.propose();await h.confirm();assert.equal(h.phase(),"failed");assert.equal(h.s.lastDiagnostic.code,"RESPONSE_INVALID");assert.equal(h.writes().length,0);
});

test("original transaction is captured before asynchronous checking and Apply does not reread controls",async()=>{
  const h=harness(),original=clone(transaction),pending=deferred();h.queue.push(()=>pending.promise);const run=h.propose(original);original.state="Draft";original.extra={changed:true};h.get("target-state").value="Draft";
  pending.resolve(response(checked()));await run;h.enqueue({id:"case-A",version:8,candidate:model("Done")});await h.confirm();assert.deepEqual(h.requests[0].body.transaction,transaction);assert.deepEqual(h.writes()[0].body.transaction,transaction);
});

test("double Apply and close during submission cannot send twice or claim cancellation",async()=>{
  const h=harness();await ready(h);const pending=deferred();h.queue.push(()=>pending.promise);const run=h.confirm();assert.equal(h.phase(),"submitting");assert.equal(h.s.busy,true);assert.equal(h.get("edit-preview-cancel").disabled,true);await h.confirm();assert.equal(h.close(),false);
  h.get("edit-preview").dispatch("keydown",{key:"Escape"});assert.equal(h.get("edit-preview").open,true);assert.equal(h.writes().length,1);assert.doesNotMatch(h.notices.at(-1).message,/No edit was submitted/);
  pending.resolve(response({id:"case-A",version:8,candidate:model("Done")}));await run;assert.equal(h.writes().length,1);assert.equal(h.counts().clears,1);
});

test("Escape cannot abandon an acknowledged edit while its authoritative reload is pending",async()=>{
  for(const fail of [false,true]){const h=harness();await ready(h);h.reload.pending=deferred();if(fail)h.reload.error=Error("Reload failed");h.enqueue({id:"case-A",version:8,candidate:model("Done")});const run=h.confirm();await new Promise(resolve=>setImmediate(resolve));
    assert.equal(h.phase(),"committed");assert.equal(h.reloads.length,1);assert.equal(h.get("edit-preview-cancel").disabled,true);assert.equal(h.close(),false);const escape=h.get("edit-preview").dispatch("keydown",{key:"Escape"});assert.equal(escape.prevented,true);assert.equal(h.get("edit-preview").open,true);assert.equal(h.writes().length,1);assert.equal(h.counts().clears,1);
    h.reload.pending.resolve();await run;assert.equal(h.s.busy,false);assert.equal(h.writes().length,1);
    if(fail){assert.equal(h.phase(),"committed");assert.match(h.get("edit-preview-status").textContent,/refresh failed/);assert.equal(h.get("edit-preview-cancel").disabled,false);h.close();assert.equal(h.get("edit-preview").open,false);}else assert.equal(h.get("edit-preview").open,false);
  }
});

test("late write acknowledgement cannot clear a newer subject or strand an unclosable preview",async()=>{
  for(const change of [s=>{s.current.case.id="case-B";},s=>{s.current.case.version=8;},s=>{s.current.packet.subject.semantic="newer-semantic";}]){const h=harness();await ready(h);const pending=deferred();h.queue.push(()=>pending.promise);const run=h.confirm();change(h.s);h.s.instance={id:"newer-runtime"};const retained=JSON.stringify(h.s.current);
    pending.resolve(response({id:"case-A",version:8,candidate:model("Done")}));await run;assert.equal(h.phase(),"committed");assert.match(h.get("edit-preview-status").textContent,/subject changed/);assert.equal(JSON.stringify(h.s.current),retained);assert.equal(h.s.instance.id,"newer-runtime");assert.equal(h.counts().clears,0);assert.equal(h.reloads.length,0);assert.equal(h.get("edit-preview-cancel").disabled,false);assert.equal(h.close(),true);assert.equal(h.get("edit-preview").open,false);
  }
});

test("an unrelated busy task leaves a ready preview intact and does not submit",async()=>{
  const h=harness();await ready(h);h.s.busy=true;await h.confirm();assert.equal(h.phase(),"ready");assert.equal(h.get("edit-preview").open,true);assert.equal(h.writes().length,0);assert.equal(h.read("editPreview.submitted"),false);
});

test("structured stale write refusal preserves previous runtime and never reports success",async()=>{
  const h=harness();await ready(h);h.enqueue({code:"STALE_VERSION",message:"Version changed",details:{codes:["STALE_VERSION"],refs:["case:case-A"]}},409);await h.confirm();
  assert.equal(h.phase(),"refused");assert.equal(h.counts().clears,0);assert.equal(h.s.instance.id,"retained-runtime");assert.equal(h.reloads.length,0);assert.equal(h.writes().length,1);assert.equal(h.s.lastDiagnostic.code,"STALE_VERSION");assert.equal(h.get("edit-preview-apply").disabled,true);assert.deepEqual(h.bottom,[]);
});

test("acknowledged write survives refresh failure and clears obsolete runtime immediately",async()=>{
  const h=harness();await ready(h);h.reload.error=Error("Reload failed");h.enqueue({id:"case-A",version:8,candidate:model("Done")});await h.confirm();
  assert.equal(h.phase(),"committed");assertCapturedSubject(h);assert.match(h.get("edit-preview-status").textContent,/committed.*refresh failed/);assert.doesNotMatch(h.get("edit-preview-status").textContent,/No model has changed/);assert.equal(h.counts().clears,1);assert.equal(h.s.instance,null);assert.equal(h.writes().length,1);assert.equal(h.get("edit-preview-apply").disabled,true);assert.equal(h.get("edit-preview-cancel").disabled,false);await h.confirm();assert.equal(h.writes().length,1);
  h.close();assert.equal(h.get("edit-reconciliation").hidden,false);assert.deepEqual(h.get("edit-reconciliation").dataset,{caseId:"case-A",revision:"7",status:"committed"});assert.match(h.get("edit-reconciliation-status").textContent,/acknowledged at revision 8.*last loaded snapshot/);assert.equal(h.s.editable(),false);
  for(const id of ["propose","save","discard","move-node","verify","reset","approve","apply","undo-edit","redo-edit","history-undo","history-redo"])assert.equal(h.get(id).disabled,true,id+" remains disabled after closing acknowledged preview");
  const count=h.requests.length;await h.propose();assert.equal(h.requests.length,count,"authoritative refresh is required before a new proposal");
});

test("uncertain writes never retry automatically or allow another proposal before refresh",async()=>{
  const failures=[()=>Promise.reject(Error("Failed to fetch")),()=>({ok:true,status:200,json:async()=>{throw Error("broken JSON");}}),()=>response({id:"other-case",version:8,candidate:model("Done")}),()=>response({id:"case-A",version:7,candidate:model("Done")}),()=>response({id:"case-A",version:8,candidate:model("Draft")}),()=>response({id:"case-A",version:8}),()=>response({code:"SERVER_ERROR",message:"Unavailable"},500),()=>response({code:"STALE_VERSION"},409),()=>response({code:"RESPONSE_INVALID",message:"Malformed acknowledgement"},409),()=>response({code:"REQUEST_FAILED",message:"Uncertain transport"},400)];
  for(const fail of failures){const h=harness();await ready(h);h.queue.push(fail);await h.confirm();assert.equal(h.phase(),"unknown");assertCapturedSubject(h);assert.match(h.get("edit-preview-status").textContent,/may have committed.*no automatic retry/i);assert.doesNotMatch(h.get("edit-preview-status").textContent,/No model has changed/);assert.equal(h.counts().clears,0);assert.equal(h.s.instance.id,"retained-runtime");assert.equal(h.reloads.length,0);assert.equal(h.writes().length,1);await h.confirm();assert.equal(h.writes().length,1);
    h.get("edit-preview").dispatch("keydown",{key:"Escape"});assert.equal(h.get("edit-preview").open,false);assert.equal(h.get("edit-reconciliation").hidden,false);assert.equal(h.get("edit-reconciliation").dataset.status,"unknown");assert.match(h.get("edit-reconciliation-status").textContent,/outcome unknown.*may have committed.*last loaded snapshot/);assert.equal(h.s.editable(),false);
    for(const id of ["propose","save","discard","move-node","verify","reset","approve","apply","undo-edit","redo-edit","history-undo","history-redo"])assert.equal(h.get(id).disabled,true,id+" remains disabled after closing unknown preview");
    const count=h.requests.length;await h.propose();assert.equal(h.requests.length,count);
  }
});

test("unresolved edits retain separate case records and the visible banner follows its current subject",async()=>{
  const h=harness();await ready(h);h.queue.push(()=>Promise.reject(Error("A response lost")));await h.confirm();h.close();
  h.s.current=fixture();Object.assign(h.s.current.case,{id:"case-B",version:3});h.s.current.packet.subject.semantic="semantic-B";h.s.renderEditReconciliation();assert.equal(h.get("edit-reconciliation").hidden,true);assert.equal(h.s.editable(),true);
  await ready(h,checked({case_id:"case-B",version:3,semantic_hash:"semantic-B"}));h.reload.error=Error("B reload failed");h.enqueue({id:"case-B",version:4,candidate:model("Done")});await h.confirm();h.close();
  assert.deepEqual(clone(h.read("Array.from(editNeedsRefresh.keys())")),["case-A","case-B"]);assert.equal(h.get("edit-reconciliation").dataset.caseId,"case-B");assert.equal(h.get("edit-reconciliation").dataset.status,"committed");assert.match(h.get("edit-reconciliation-status").textContent,/revision 4/);
  h.s.current=fixture();h.s.renderEditReconciliation();assert.equal(h.get("edit-reconciliation").dataset.caseId,"case-A");assert.equal(h.get("edit-reconciliation").dataset.status,"unknown");assert.match(h.get("edit-reconciliation-status").textContent,/revision 7/);assert.equal(h.s.editable(),false);
  await h.get("edit-reconcile-refresh").onclick();assert.equal(h.counts().refreshes,1);assert.equal(h.writes().length,2);assert.equal(h.get("edit-reconciliation").hidden,false,"requesting refresh does not itself erase an unresolved outcome");
});

test("missing choice candidate identity read-only view and global busy do not request a check",async()=>{
  for(const setup of [h=>()=>h.s.commitChoice(undefined),h=>{h.s.current.packet.subject.semantic=null;return()=>h.propose();},h=>{h.s.modelView="history";return()=>h.propose();},h=>{h.s.current.case.stage="APPLIED";return()=>h.propose();},h=>{h.s.current=null;return()=>h.propose();},h=>{h.s.busy=true;return()=>h.propose();}]){const h=harness();await setup(h)();assert.equal(h.requests.length,0);assert.equal(h.writes().length,0);}
});

test("dialog shortcuts stay local and closing falls back when its invoking control disappears",async()=>{
  const h=harness();await ready(h);assert.equal(h.s.document.activeElement,h.get("edit-preview-cancel"));
  for(const values of [{key:"k",ctrlKey:true},{key:"K",metaKey:true},{key:"b",ctrlKey:true}]){const event=h.get("edit-preview").dispatch("keydown",values);assert.equal(event.prevented,true);assert.equal(event.stopped,true);}
  h.get("edit-source").isConnected=false;h.close();assert.equal(h.s.document.activeElement,h.get("transition-select"));assert.equal(h.comparisons[0].destroyed,true);assert.equal(h.writes().length,0);
  await ready(h);h.get("transition-select").hidden=true;h.get("edit-source").isConnected=false;h.close();assert.equal(h.s.document.activeElement,h.get("case-title"),"a collapsed inspector still leaves visible workspace focus");
});

test("negative control: removing the expected subject guard is caught for a reused transition ID",async()=>{
  const marker='current.case.version===preview.version&&';assert.ok(source.includes(marker));const h=harness(source.replace(marker,""));await ready(h);h.s.current.case.version=8;h.enqueue({id:"case-A",version:8,candidate:model("Done")});await h.confirm();assert.throws(()=>assert.equal(h.writes().length,0),assert.AssertionError);
});

async function readyWithObserver(h, onCommitted, check=checked()){
  h.enqueue(check);await h.s.commitChoice({transaction:clone(transaction)},{onCommitted});
}
function useAuthoritativeReload(h){
  const previous=h.s.load;
  h.s.load=async(id,canPublish)=>{
    const value=await h.s.api(`cases/${id}`);
    if(canPublish&&!canPublish())return false;
    h.s.current=value;
    await previous(id,()=>true);
    return true;
  };
}
function reloadedCandidate(){
  const value=fixture();Object.assign(value.case,{version:8,stage:"DRAFT",candidate:model("Done")});value.packet.subject.semantic="semantic-after";return value;
}

test("owner edit observer runs once only after acknowledged edit and exact authoritative GET reload",async()=>{
  const h=harness(),observed=[];useAuthoritativeReload(h);
  await readyWithObserver(h,value=>observed.push({value:clone(value),current:clone(h.s.current),requests:clone(h.requests)}));
  assert.deepEqual(observed,[]);h.enqueue({id:"case-A",version:8,candidate:model("Done")});h.enqueue(reloadedCandidate());await h.confirm();
  assert.equal(observed.length,1);assert.deepEqual(observed[0].value,{caseId:"case-A",previousVersion:7,version:8,semanticHash:"semantic-after",transaction});
  assert.deepEqual(observed[0].current,reloadedCandidate());assert.deepEqual(observed[0].requests.map(item=>[item.method,item.path]),[["POST","cases/case-A/edit/preview"],["POST","cases/case-A/edit"],["GET","cases/case-A"]]);
  assert.equal(h.get("edit-preview").open,false);await h.confirm();assert.equal(observed.length,1);assert.equal(h.writes().length,1);
});

test("Close kernel refusal uncertain writes and refresh failure never notify an edit observer",async()=>{
  for(const failure of ["close","refused","unknown","refresh"]){
    const h=harness(),observed=[];
    await readyWithObserver(h,value=>observed.push(value),failure==="refused"?checked({legal:false,candidate:null,candidate_semantic_hash:null,codes:["PROTECTED_AUTHORITY"],refs:["law:owner"]}):checked());
    if(failure==="close")h.close();
    else if(failure==="refused")await h.confirm();
    else if(failure==="unknown"){h.queue.push(()=>Promise.reject(Error("Acknowledgement lost")));await h.confirm();}
    else{useAuthoritativeReload(h);h.enqueue({id:"case-A",version:8,candidate:model("Done")});h.queue.push(()=>Promise.reject(Error("GET reload unavailable")));await h.confirm();}
    assert.deepEqual(observed,[],failure);assert.equal(h.writes().length,["unknown","refresh"].includes(failure)?1:0);
  }
});

test("stale workspace and mismatched authoritative case revision semantic or model never notify an observer",async()=>{
  for(const change of [s=>{s.current.case.id="case-B";},s=>{s.current.case.version=8;},s=>{s.current.packet.subject.semantic="newer";}]){
    const h=harness(),observed=[],pending=deferred();await readyWithObserver(h,value=>observed.push(value));
    h.queue.push(()=>pending.promise);const run=h.confirm();change(h.s);pending.resolve(response({id:"case-A",version:8,candidate:model("Done")}));await run;
    assert.deepEqual(observed,[]);assert.equal(h.reloads.length,0);
  }
  for(const change of [value=>{value.case.id="case-B";},value=>{value.case.version=9;},value=>{value.packet.subject.semantic="newer";},value=>{value.case.candidate=model("Draft");}]){
    const h=harness(),observed=[],value=reloadedCandidate();change(value);useAuthoritativeReload(h);await readyWithObserver(h,result=>observed.push(result));
    h.enqueue({id:"case-A",version:8,candidate:model("Done")});h.enqueue(value);await h.confirm();assert.deepEqual(observed,[]);
  }
});

test("observer UI exception cannot turn an acknowledged reloaded edit into an uncertain mutation",async()=>{
  const h=harness();useAuthoritativeReload(h);let calls=0;await readyWithObserver(h,()=>{calls++;throw Error("panel rendering failed");});
  h.enqueue({id:"case-A",version:8,candidate:model("Done")});h.enqueue(reloadedCandidate());await h.confirm();
  assert.equal(calls,1);assert.equal(h.writes().length,1);assert.equal(h.get("edit-preview").open,false);assert.deepEqual(clone(h.read("Array.from(editNeedsRefresh.keys())")),[]);
  assert.equal(h.phase(),"committed");assert.equal(h.s.current.case.version,8);assert.match(h.notices.at(-1).message,/Edit committed.*proposal panel could not update/);assert.doesNotMatch(h.notices.at(-1).message,/unknown|may have committed/);
});
