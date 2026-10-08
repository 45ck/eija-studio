"use strict";
// Real lifecycle functions and source/impact renderers; controlled promises are the transport boundary.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const web=path.join(__dirname,"../../src/eija_studio/resources/web"),app=fs.readFileSync(path.join(web,"app.js"),"utf8"),shell=fs.readFileSync(path.join(web,"shell.js"),"utf8");
const A="a".repeat(64),B="b".repeat(64),X="repo://src/x.py#X",Y="repo://src/y.py#Y";
class Element{
  constructor(tag="div"){this.tag=tag;this.children=[];this.dataset={};this.attributes={};this.value="";this.ownText="";this.hidden=false;const classes=new Set();this.classList={toggle:(key,on)=>on?classes.add(key):classes.delete(key),add:key=>classes.add(key),remove:key=>classes.delete(key),contains:key=>classes.has(key)};}
  set textContent(value){this.ownText=String(value);this.children=[];}get textContent(){return this.ownText+this.children.map(node=>node.textContent).join("\n");}
  append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.ownText="";this.children=[...nodes];}
  setAttribute(key,value){this.attributes[key]=String(value);}getAttribute(key){return this.attributes[key];}removeAttribute(key){delete this.attributes[key];}
  querySelectorAll(){return [];}get childElementCount(){return this.children.length;}
}
const all=node=>[node,...node.children.flatMap(all)],tick=()=>new Promise(resolve=>setImmediate(resolve));
function data(hash=A,reference=X,text="def unchanged():\n    pass\n"){
  return {status:"connected",reference,path:reference===X?"src/x.py":"src/y.py",symbol:reference===X?"X":"Y",source_hash:hash,file_hash:"file-"+hash[0],snippet_hash:"snippet-"+hash[0],graph_hash:"graph-"+hash[0],lines:{start:4,end:5},symbol_lines:{start:4,end:5},text,scope:"Captured tracked source only",fragment_resolution:"python_ast"};
}
function impact(hash=A,term="T"){return {status:"connected",source_hash:hash,graph_hash:"graph-"+hash[0],scope:"Known links only",impact:{target:term,count:1,certificate:"certificate-"+hash[0],affected:[{id:X,type:"function",rank:1,witness:["term:"+term,X]}]}};}
function harness(code=app){
  const nodes=new Map(),requests=[],notices=[],bottom=[],renders=[],get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
  const sandbox={module:{exports:{}},document:{createElement:tag=>new Element(tag),getElementById:get},console};vm.createContext(sandbox);vm.runInContext(shell,sandbox);const actualShell=sandbox.module.exports;actualShell.bottom=id=>bottom.push(id);
  const sourceState=connection=>({connected:connection?.status==="connected",title:connection?.status==="connected"?"Snapshot "+connection.source_hash:"Unavailable repository",reason:connection?.reason||"No source"});
  Object.assign(sandbox,{
    $:get,el:(tag,text,cls)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;},
    sourceSequence:0,impactSequence:0,sourcePending:false,sourceRecord:null,sourceHistory:[],sourceHistoryIndex:-1,
    workbench:{connection:{status:"connected",source_hash:A},pack:{id:"pack-A"},model:{id:"declared-model-A"}},status:{trusted_fixture:false},
    current:{case:{id:"case-A",version:7},packet:{subject_hash:"packet-A"}},instance:{id:"instance-A",version:3,state:"Submitted"},inspectorSelection:{kind:"term",id:"T"},
    modelView:"history",historyModel:{id:"prior-model"},historyLabel:"Protected initial model",editId:"Save",canvasDirection:"LR",comparison:null,caseViews:new Map(),caseHistory:{version:7},affordanceData:{},tab:"evidence",lastDiagnostic:null,
    EijaShell:actualShell,EijaSource:{state:sourceState,render:(root,connection)=>root.replaceChildren(new Element("p"))},
    api:(request,body)=>new Promise((resolve,reject)=>requests.push({request,body,resolve,reject,settled:false})),
    notice:(message,error=false)=>notices.push({message,error}),switchTab:name=>{sandbox.tab=name;},renderProblems:()=>{},render:()=>renders.push("render"),cases:async()=>{},clearDiagnostic:()=>{},
    renderWorkbench:()=>{throw Error("Repository refresh must not rebuild unsent model fields");},task:fn=>fn()
  });
  for(const [start,end]of [["class ApiError", "async function api("],["function reportError(","function clearDiagnostic("],["async function load(","async function command("],["async function refreshCurrentModel()","function filterCommands("],["function sourceSnapshot()","function previewHistory("],["async function openSource(",'$("source-open-form").onsubmit']]){
    const from=code.indexOf(start),to=code.indexOf(end,from);assert.ok(from>=0&&to>from,start);vm.runInContext(code.slice(from,to),sandbox);
  }
  const previousStart=code.indexOf("async function previousSource()");if(previousStart>=0)vm.runInContext(code.slice(previousStart,code.indexOf('$("source-back").onclick=',previousStart)),sandbox);
  const find=prefix=>requests.find(item=>!item.settled&&item.request.startsWith(prefix));
  return {get,sandbox,requests,notices,bottom,renders,find,
    resolve(prefix,value){const req=find(prefix);assert.ok(req,"pending request "+prefix);req.settled=true;req.resolve(value);return req;},
    reject(prefix,code,message=code){const req=find(prefix);assert.ok(req,"pending request "+prefix);req.settled=true;const error=new Error(message);error.code=code;req.reject(error);return req;},
    snapshot(){return {text:get("source-reader").textContent,hash:get("source-reader").dataset.sourceHash,freshness:get("source-freshness").dataset.status,message:get("source-freshness").textContent,notice:notices.at(-1)};}
  };
}
async function seed(h,record=data()){const run=h.sandbox.openSource(record.reference);h.resolve("repository/source",record);await run;return h.snapshot();}
async function completeRefreshConnection(h,hash=B){h.resolve("workbench",{connection:{status:"connected",source_hash:hash},model:{id:"must-not-replace-model"}});h.resolve("status",{trusted_fixture:false,provider:"offline"});await tick();}
function query(request){return new URL(request,"http://fixture.invalid/api/").searchParams;}
function assertBoundRequest(h){const run=h.sandbox.openSource(X);const request=h.find("repository/source");assert.equal(query(request.request).get("reference"),X);assert.equal(query(request.request).get("expected_source_hash"),A);h.resolve("repository/source",data());return run;}

test("source requests bind the selected snapshot and render only the returned matching identity",async()=>{
  const h=harness();await assertBoundRequest(h);assert.equal(h.snapshot().hash,A);assert.equal(h.snapshot().freshness,"captured");assert.match(h.get("source-metadata").textContent,new RegExp(A));assert.ok(h.requests.every(req=>req.body===undefined));
});
test("an absent connection identity fails before transport and exposes a refresh action",async()=>{
  const h=harness();h.sandbox.workbench.connection={status:"unavailable"};await h.sandbox.openSource(X);assert.equal(h.requests.length,0);assert.equal(h.snapshot().freshness,"unavailable");assert.match(h.snapshot().message,/SOURCE_SNAPSHOT_UNAVAILABLE/);assert.ok(all(h.get("source-freshness")).some(node=>node.dataset.sourceRefresh));
});
test("a response for another snapshot cannot replace the previously captured source",async()=>{
  const h=harness(),before=await seed(h);const run=h.sandbox.openSource(Y);h.resolve("repository/source",data(B,Y,"unexpected B bytes"));await run;
  assert.equal(h.snapshot().text,before.text);assert.equal(h.snapshot().hash,A);assert.equal(h.snapshot().freshness,"unavailable");assert.match(h.snapshot().message,/SOURCE_SNAPSHOT_MISMATCH/);assert.doesNotMatch(h.snapshot().text,/unexpected/);
});
test("a stale refusal retains exact prior bytes, identity and a real Refresh source action",async()=>{
  const h=harness(),before=await seed(h);const run=h.sandbox.openSource(X);h.reject("repository/source","SOURCE_SNAPSHOT_STALE","Captured source changed");await run;
  assert.equal(h.snapshot().text,before.text);assert.equal(h.snapshot().hash,A);assert.equal(h.snapshot().freshness,"stale");assert.match(h.snapshot().message,/not a current filesystem read/);assert.ok(all(h.get("source-freshness")).some(node=>node.tag==="button"&&node.dataset.sourceRefresh&&typeof node.onclick==="function"));
});
test("later source navigation wins over an older success or refusal",async()=>{
  for(const rejectOld of [false,true]){
    const h=harness();const older=h.sandbox.openSource(X),first=h.find("repository/source"),newer=h.sandbox.openSource(Y),second=h.requests.at(-1);second.settled=true;second.resolve(data(A,Y,"new Y bytes"));await newer;const retained=h.snapshot();
    first.settled=true;if(rejectOld){const e=new Error("obsolete stale refusal");e.code="SOURCE_SNAPSHOT_STALE";first.reject(e);}else first.resolve(data(A,X,"old X bytes"));await older;assert.deepEqual(h.snapshot(),retained);
  }
});
test("refresh retains prior bytes with a non-current label until the bound reopening succeeds",async()=>{
  const h=harness(),before=await seed(h);h.get("model-source").value="unsent source";h.get("target-state").value="unsent target";h.get("q-authority").value="draft answer";
  const saved={current:h.sandbox.current,instance:h.sandbox.instance,historyModel:h.sandbox.historyModel,model:h.sandbox.workbench.model,selection:h.sandbox.inspectorSelection,modelView:h.sandbox.modelView,historyLabel:h.sandbox.historyLabel,tab:h.sandbox.tab};
  const run=h.sandbox.refreshSource();await completeRefreshConnection(h);assert.equal(h.sandbox.workbench.connection.source_hash,B);assert.equal(h.snapshot().text,before.text);assert.equal(h.snapshot().hash,A);assert.notEqual(h.snapshot().freshness,"captured");assert.match(h.snapshot().message,/Previous captured source/);
  const req=h.find("repository/source");assert.equal(query(req.request).get("expected_source_hash"),B);h.resolve("repository/source",data(B,X));await run;assert.equal(h.snapshot().hash,B);assert.equal(h.snapshot().freshness,"captured");assert.equal(h.snapshot().text,before.text,"identical content must not mask changed identity");
  for(const key of ["current","instance","historyModel","selection","modelView","historyLabel","tab"])assert.equal(h.sandbox[key==="selection"?"inspectorSelection":key],saved[key],key);assert.equal(h.sandbox.workbench.model,saved.model);assert.equal(h.get("model-source").value,"unsent source");assert.equal(h.get("target-state").value,"unsent target");assert.equal(h.get("q-authority").value,"draft answer");assert.deepEqual(h.renders,[]);assert.ok(h.requests.every(req=>req.body===undefined));
});
test("refresh clears both prior impact witnesses and their obsolete identity",async()=>{
  const h=harness();const old=h.sandbox.loadRepositoryImpact("T");h.resolve("repository/impact",impact());await old;assert.equal(h.get("inspector-impact").dataset.sourceHash,A);assert.match(h.get("inspector-impact").textContent,/certificate-a/);
  const run=h.sandbox.refreshSource();await completeRefreshConnection(h);await run;assert.doesNotMatch(h.get("inspector-impact").textContent,/certificate-a|term:T/);assert.equal(h.get("inspector-impact").dataset.sourceHash,undefined);
});
test("refresh cancels old pending source success and error without repainting or newer feedback loss",async()=>{
  for(const rejectOld of [false,true]){
    const h=harness();await seed(h);const obsolete=h.sandbox.openSource(Y),old=h.find("repository/source"),refresh=h.sandbox.refreshSource();await completeRefreshConnection(h);const reopened=h.requests.at(-1);assert.equal(query(reopened.request).get("expected_source_hash"),B);reopened.settled=true;reopened.resolve(data(B,X));await refresh;const retained=h.snapshot();
    old.settled=true;if(rejectOld){const error=new Error("old denial");error.code="SOURCE_SNAPSHOT_STALE";old.reject(error);}else old.resolve(data(A,Y,"obsolete bytes"));await obsolete;assert.deepEqual(h.snapshot(),retained);
  }
});
test("case and same-case revision loads invalidate pending reads even with the same source snapshot",async()=>{
  for(const [id,version]of [["case-B",1],["case-A",8]]){
    const h=harness(),pending=h.sandbox.openSource(X),old=h.find("repository/source"),load=h.sandbox.load(id);
    h.resolve("cases/"+id,{case:{id,version},packet:{subject_hash:"new-packet"}});h.resolve("cases/"+id+"/affordances",{affordances:[]});h.resolve("cases/"+id+"/history",{version});await load;const retained=h.snapshot();old.settled=true;old.resolve(data(A,X,"late old context"));await pending;
    assert.deepEqual(h.snapshot(),retained);assert.equal(h.sandbox.current.case.id,id);assert.equal(h.sandbox.current.case.version,version);assert.equal(h.snapshot().freshness,"cancelled");assert.doesNotMatch(h.snapshot().text,/late old context/);
  }
});
test("impact requests bind their snapshot and later selection or connection changes reject stale completions",async()=>{
  for(const change of [h=>{h.sandbox.inspectorSelection={kind:"term",id:"U"};},h=>{h.sandbox.workbench.connection.source_hash=B;}]){
    const h=harness(),run=h.sandbox.loadRepositoryImpact("T");const req=h.find("repository/impact");assert.equal(query(req.request).get("expected_source_hash"),A);assert.equal(query(req.request).get("term"),"T");change(h);h.get("inspector-impact").textContent="new selection context";h.resolve("repository/impact",impact());await run;assert.equal(h.get("inspector-impact").textContent,"new selection context");assert.equal(h.notices.length,0);
  }
});
test("a wrong impact snapshot is refused without rendering its witness and keeps exact diagnostic",async()=>{
  const h=harness(),run=h.sandbox.loadRepositoryImpact("T");h.resolve("repository/impact",impact(B));await run;assert.doesNotMatch(h.get("inspector-impact").textContent,/certificate-b/);assert.equal(JSON.parse(h.get("error-json").textContent).code,"SOURCE_SNAPSHOT_MISMATCH");assert.deepEqual(h.bottom,["problems-pane"]);assert.ok(all(h.get("inspector-impact")).some(node=>node.dataset.sourceRefresh));
});
test("an obsolete refresh reopening cannot overwrite feedback from newer failed navigation",async()=>{
  const h=harness();await seed(h);const refresh=h.sandbox.refreshSource();await completeRefreshConnection(h);const old=h.find("repository/source"),newer=h.sandbox.openSource(Y),newReq=h.requests.at(-1);newReq.settled=true;const error=new Error("New selected reference is stale");error.code="SOURCE_SNAPSHOT_STALE";newReq.reject(error);await newer;const retained=h.snapshot();old.settled=true;old.resolve(data(B,X));await refresh;assert.deepEqual(h.snapshot(),retained);
});
test("failed reopening after refresh retains stale status and does not overwrite the actual read error",async()=>{
  const h=harness();await seed(h);const refresh=h.sandbox.refreshSource();await completeRefreshConnection(h);h.reject("repository/source","SOURCE_SNAPSHOT_STALE","Changed again during reopening");await refresh;assert.equal(h.snapshot().hash,A);assert.equal(h.snapshot().freshness,"stale");assert.equal(h.notices.at(-1).error,true);assert.match(h.notices.at(-1).message,/Changed again during reopening/);
});
test("no-case Refresh current model cannot retain captured source A as current against connection B",async()=>{
  const h=harness();await seed(h);h.sandbox.current=null;h.sandbox.renderWorkbench=()=>h.renders.push("renderWorkbench");const refresh=h.sandbox.refreshCurrentModel();h.resolve("workbench",{connection:{status:"connected",source_hash:B},model:{id:"declared-model-A"}});if(h.find("status"))h.resolve("status",{trusted_fixture:false});await tick();
  const reopen=h.find("repository/source");if(reopen){assert.equal(query(reopen.request).get("expected_source_hash"),B);h.resolve("repository/source",data(B,X));}
  await refresh;assert.ok(h.snapshot().hash===B||h.snapshot().freshness!=="captured","old snapshot A must not be labelled captured/current after connection B");
});
test("no-case current-model refresh invalidates an earlier pending source read without stuck loading",async()=>{
  const h=harness();h.sandbox.current=null;h.sandbox.renderWorkbench=()=>h.renders.push("renderWorkbench");const pending=h.sandbox.openSource(X),old=h.find("repository/source"),refresh=h.sandbox.refreshCurrentModel();h.resolve("workbench",{connection:{status:"connected",source_hash:B},model:{id:"declared-model-A"}});if(h.find("status"))h.resolve("status",{trusted_fixture:false});await refresh;old.settled=true;old.resolve(data(A,X));await pending;
  assert.notEqual(h.snapshot().freshness,"loading");assert.notEqual(h.snapshot().hash,A);
});
test("repository refresh updates the source-review banner from actual refreshed status without model rerender",async()=>{
  const h=harness();h.sandbox.status={trusted_fixture:true};h.get("source-status").textContent="Source identity matches its release fixture.";h.get("source-status").classList.toggle("source-required",false);
  const refresh=h.sandbox.refreshSource();await completeRefreshConnection(h);await refresh;assert.match(h.get("source-status").textContent,/SOURCE_REVIEW_REQUIRED/);assert.equal(h.get("source-status").classList.contains("source-required"),true);assert.deepEqual(h.renders,[]);
});
test("a refused Back navigation cannot consume a source history entry",async()=>{
  const h=harness(),Z="repo://src/z.py#Z";await seed(h,data(A,X));await seed(h,data(A,Y));await seed(h,data(A,Z));
  const start=app.indexOf('$("source-back").onclick='),end=app.indexOf('$("undo-edit").onclick=',start);assert.ok(start>=0&&end>start);vm.runInContext(app.slice(start,end),h.sandbox);
  h.get("source-back").onclick();assert.equal(query(h.find("repository/source").request).get("reference"),Y);h.reject("repository/source","SOURCE_SNAPSHOT_STALE","Back reference changed");await tick();assert.equal(h.sandbox.sourceRecord.reference,Z);
  h.get("source-back").onclick();assert.equal(query(h.find("repository/source").request).get("reference"),Y,"retry must still target Y, not skip it for X");h.resolve("repository/source",data(A,Y));await tick();
});
test("request-binding oracle kills omission of expected_source_hash from actual sourceQuery",async()=>{
  const marker='&expected_source_hash=${encodeURIComponent(hash)}';assert.ok(app.includes(marker));const h=harness(app.replace(marker,""));await assert.rejects(async()=>assertBoundRequest(h),assert.AssertionError);
});
test("stale-paint oracle kills source identity validation removal",async()=>{
  const line='    if(data.source_hash!==hash)throw new ApiError("SOURCE_SNAPSHOT_MISMATCH","The source response does not describe the selected snapshot.");';assert.ok(app.includes(line));const h=harness(app.replace(line,""));await seed(h);const run=h.sandbox.openSource(Y);h.resolve("repository/source",data(B,Y));await run;assert.throws(()=>assert.equal(h.snapshot().hash,A),assert.AssertionError);
});
