"use strict";
// Actual proposal projection, task, API and load seams. DOM/transport doubles are not browser proof.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(process.env.EIJA_PROPOSAL_APP||path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
const clone=value=>JSON.parse(JSON.stringify(value)),tick=()=>new Promise(resolve=>setImmediate(resolve));
const response=(data,status=200)=>({ok:status>=200&&status<300,status,json:async()=>clone(data)});
const deferred=()=>{let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return {promise,resolve,reject};};
const run=(overrides={})=>({id:"accepted-A",provider:"offline",model:"fixture-v1",live:false,usage:{},elapsed_seconds:0.01,timestamp:"2026-10-03T03:00:00Z",request_hash:"request-hash-A",egress:false,...overrides});
const event=(seq,kind,body={})=>({seq,kind,body:{case_id:"A",...body}});
function fixture(id="A",version=7,providerRun=run()){
  return {case:{id,version,baseline_version:0,stage:"PROPOSED",request:`Retained request ${id}`,candidate:null,selected_meaning:null,proposal:{summary:`Retained proposal ${id}`,alternatives:[],unknowns:[]},provider_run:providerRun},packet:{subject:{semantic:`semantic-${id}`}},observations:{events:[]}};
}
class Element{
  constructor(tag="div"){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.attributes={};this.hidden=false;this.disabled=false;this.open=false;this.value="";this.ownText="";this.checked=false;}
  set textContent(value){this.ownText=String(value);this.children=[];}get textContent(){return this.ownText+this.children.map(child=>child.textContent).join("\n");}
  append(...items){this.children.push(...items);}replaceChildren(...items){this.children=[...items];this.ownText="";}
  setAttribute(name,value){this.attributes[name]=String(value);}removeAttribute(name){delete this.attributes[name];}
  set innerHTML(_value){throw Error("Markup insertion is forbidden");}
}
function section(code,start,end){const a=code.indexOf(start),b=code.indexOf(end,a+start.length);assert.ok(a>=0&&b>a,`Actual source seam missing: ${start}`);return code.slice(a,b);}
function harness({code=source,current=fixture()}={}){
  const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);},requests=[],posts=[],errors=[],notices=[],server={value:clone(current),fail:null};
  const s={current,status:{provider:"codex",provider_networked:true,network_enabled:false},busy:false,token:"fixture-token",lastDiagnostic:null,
    caseViews:new Map(),editNeedsRefresh:new Map(),runtimeAttempt:null,editId:null,inspectorSelection:null,modelView:"working",historyModel:null,historyLabel:"",canvasDirection:"AUTO",tab:"change",caseHistory:null,affordanceData:null,
    $:get,el:(tag,text,cls)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;},document:{body:new Element("body")},
    captureTaskFocus:()=>({}),restoreTaskFocus(){},cancelSourceRead(){},renderEditReconciliation(){},reconcileRuntime(){},clearDiagnostic(){},reportError:error=>errors.push(error),notice:(message,error=false)=>notices.push({message,error}),
    fetch:async(url,options)=>{
      const request={path:url.slice(5),method:options.method||"GET",body:options.body?JSON.parse(options.body):undefined};requests.push(request);
      if(request.method==="POST"){assert.ok(posts.length,"Unexpected mutation");return posts.shift()(request);}
      if(server.fail===request.path)throw Error("Workspace refresh failed");
      if(request.path==="cases")return response([]);
      if(request.path.endsWith("/affordances"))return response({affordances:[]});
      if(request.path.endsWith("/history"))return response({events:[]});
      return response(server.value);
    }};
  s.cases=async()=>{await s.api("cases");return true;};s.render=()=>s.renderProposalProvenance();vm.createContext(s);
  for(const [start,end]of [["class ApiError","function reportError("],["async function task(","let caseInventory="],["async function load(","let editNeedsRefresh="],["let proposalAttempt=","async function command("]])vm.runInContext(section(code,start,end),s);
  const binding=code.split(/\r?\n/).find(line=>line.startsWith('$("propose").onclick='));assert.ok(binding);vm.runInContext(binding,s);
  get("request").value="Unsent request remains intact";s.renderProposalProvenance();
  return {s,get,requests,posts,errors,notices,server,text:id=>get(id).textContent,
    enqueue:(data,status=200)=>posts.push(()=>response(data,status)),
    attempt:()=>clone(vm.runInContext("proposalAttempt",s)),
    propose:()=>get("propose").onclick()};
}
function accepted(h,providerRun=run({id:"accepted-B",provider:"openrouter",model:"observed-model",live:true,egress:true})){
  const next=clone(h.s.current);next.case.version++;next.case.provider_run=providerRun;next.case.proposal.summary="New accepted proposal";return next;
}

test("loaded proposal identity is distinct from the configured provider and is read-only",()=>{
  const h=harness(),before=JSON.stringify(h.s.current);h.s.renderProposalProvenance();
  assert.match(h.text("proposal-provider"),/Configured for new requests: codex.*network disabled/);
  assert.match(h.text("proposal-origin"),/Loaded proposal: offline.*fixture-v1.*Offline fixture/);assert.doesNotMatch(h.text("proposal-origin"),/codex/);
  assert.match(h.text("proposal-subject"),/Loaded case A.*revision 7.*Untrusted interpretation/);
  assert.deepEqual({...h.get("proposal-provenance").dataset},{caseId:"A",revision:"7",runId:"accepted-A"});
  assert.match(h.text("proposal-metadata"),/accepted-A.*Provider.*offline.*Actual model.*fixture-v1/s);
  assert.equal(JSON.stringify(h.s.current),before);assert.equal(h.requests.length,0);
});

test("an unreported actual model and incomplete metadata stay unknown",()=>{
  const h=harness({current:fixture("A",7,run({provider:"codex",model:"",live:true,egress:true,usage:{accounting:"Check Codex; no inferred subscription cost"}}))});
  assert.match(h.text("proposal-origin"),/Actual model not supplied.*Live response reported/);assert.match(h.text("proposal-metadata"),/Actual model\nNot supplied/);
  assert.match(h.text("proposal-metadata"),/Accounting note.*no inferred subscription cost/s);
  h.s.current.case.provider_run={id:"partial"};h.s.renderProposalProvenance();
  assert.match(h.text("proposal-origin"),/Provider not supplied.*Actual model not supplied.*Run mode not supplied/);
  assert.match(h.text("proposal-metadata"),/Elapsed\nNot supplied.*Egress\nNot supplied.*Usage \/ accounting\nNot supplied/s);
  assert.doesNotMatch(h.text("proposal-origin"),/codex|Offline fixture/);
});

test("only allowlisted accounting is rendered and strings remain literal text",()=>{
  const h=harness({current:fixture("A",7,run({provider:"<img src=x onerror=alert(1)>",usage:{prompt_tokens:10,total_tokens:20,cost:0.2,output_tokens:-1,input_tokens:"invented",access_token:"fixture-secret-must-not-render",prompt:"private prompt fixture"},credentials:"fixture-secret-must-not-render"}))});
  assert.match(h.text("proposal-origin"),/<img src=x onerror=alert\(1\)>/);assert.equal(h.get("proposal-origin").children.length,0);
  assert.match(h.text("proposal-metadata"),/Prompt tokens\n10.*Total tokens\n20.*Reported cost \(unit not supplied\)\n0.2/s);
  assert.doesNotMatch(h.text("proposal-metadata"),/fixture-secret|private prompt|invented|Output tokens|Input tokens/);
});

test("missing proposal metadata is explicit and an orphan run is not presented as an accepted proposal",()=>{
  const h=harness({current:fixture("A",7,null)});assert.match(h.text("proposal-origin"),/provenance metadata not supplied/);
  h.s.current.case.proposal=null;h.s.current.case.provider_run=run();h.s.renderProposalProvenance();
  assert.equal(h.text("proposal-origin"),"No proposal loaded for this case.");assert.doesNotMatch(h.text("proposal-metadata"),/accepted-A|fixture-v1/);
  h.s.current=null;h.s.renderProposalProvenance();assert.equal(h.get("proposal-provenance").hidden,true);assert.equal(h.get("proposal-activity").hidden,true);assert.deepEqual({...h.get("proposal-activity").dataset},{});
});

test("recorded failure and unresolved activity stay separate from the accepted run and are case-filtered",()=>{
  const h=harness();h.s.current.observations.events=[event(5,"ProviderCallNotAccepted",{attempt_id:"failed-run",error_code:"PROVIDER_OUTPUT_INVALID"}),event(2,"ProposalReceived",{run:run()}),event(4,"ProviderCallStarted",{attempt_id:"failed-run",provider:"openrouter"}),event(9,"ProviderCallNotAccepted",{case_id:"B",attempt_id:"other-case",error_code:"OTHER_CASE"})];
  const before=JSON.stringify(h.s.current.observations);h.s.renderProposalProvenance();
  assert.match(h.text("proposal-activity"),/Latest recorded attempt was not accepted.*PROVIDER_OUTPUT_INVALID/);assert.match(h.text("proposal-origin"),/offline.*fixture-v1/);
  assert.doesNotMatch(h.text("proposal-events"),/OTHER_CASE|other-case/);assert.match(h.text("proposal-events"),/Event 2.*Event 4.*Event 5/s);assert.equal(JSON.stringify(h.s.current.observations),before);
  h.s.current.observations.events.push(event(6,"ProviderCallStarted",{attempt_id:"unresolved",provider:"codex"}));h.s.renderProposalProvenance();
  assert.match(h.text("proposal-activity"),/no completion is recorded.*outcome is unknown/);assert.doesNotMatch(h.text("proposal-activity"),/is running/);
});

test("native disclosure preserves openness only for the same loaded proposal and limits history honestly",()=>{
  const h=harness();h.get("proposal-record").open=true;h.s.current.case.version=8;h.s.renderProposalProvenance();assert.equal(h.get("proposal-record").open,true);
  h.s.current.case.provider_run=run({id:"different-run"});h.s.renderProposalProvenance();assert.equal(h.get("proposal-record").open,false);
  h.get("proposal-record").open=true;h.s.current=fixture("B",1);h.s.renderProposalProvenance();assert.equal(h.get("proposal-record").open,false);assert.equal(h.get("proposal-provenance").dataset.caseId,"B");
  h.s.current=fixture();h.s.current.observations.events=Array.from({length:7},(_,index)=>event(index+1,"ProviderCallStarted",{attempt_id:`run-${index}`,provider:"offline"}));h.s.renderProposalProvenance();
  assert.match(h.text("proposal-events"),/latest 5 of 7/);assert.equal(h.get("proposal-events").children.filter(child=>child.dataset.eventSeq).length,5);
});

test("pending requests retain previous provenance and capture consent once without duplicate submission",async()=>{
  const h=harness(),pending=deferred(),next=accepted(h);h.get("egress").checked=true;h.posts.push(()=>pending.promise);
  const first=h.propose();await tick();h.get("egress").checked=false;await h.propose();
  assert.equal(h.requests.length,1);assert.equal(h.get("propose").disabled,true);assert.match(h.text("proposal-activity"),/Requesting interpretations.*last loaded proposal/);assert.match(h.text("proposal-origin"),/offline/);
  assert.deepEqual(h.requests[0],{path:"cases/A/propose",method:"POST",body:{expected_version:7,consent:true}});
  h.server.value=next;pending.resolve(response(next.case));await first;
  assert.equal(h.attempt().status,"received");assert.equal(h.attempt().refresh,"current");assert.match(h.text("proposal-origin"),/openrouter.*observed-model.*Live response reported/);
  assert.equal(h.get("proposal-provenance").dataset.revision,"8");assert.match(h.text("proposal-activity"),/No meaning was selected automatically/);assert.equal(h.get("propose").disabled,false);
  assert.deepEqual(h.requests.map(request=>request.path),["cases/A/propose","cases/A","cases/A/affordances","cases/A/history","cases"]);
  assert.equal(h.requests.filter(request=>request.method==="POST").length,1);assert.equal(h.s.current.case.selected_meaning,null);assert.equal(h.get("request").value,"Unsent request remains intact");
});

test("authoritative refusal preserves request and accepted proposal without retry",async()=>{
  const h=harness(),before=JSON.stringify(h.s.current);h.enqueue({code:"PROVIDER_OUTPUT_INVALID",message:"Provider response was invalid",details:{}},409);await h.propose();
  assert.equal(h.attempt().status,"refused");assert.match(h.text("proposal-activity"),/Request refused \(PROVIDER_OUTPUT_INVALID\).*retained/);assert.match(h.text("proposal-origin"),/offline/);
  assert.equal(JSON.stringify(h.s.current),before);assert.equal(h.requests.length,1);assert.equal(h.errors.length,1);assert.equal(h.get("request").value,"Unsent request remains intact");
});

test("transport, malformed acknowledgement and server errors remain unknown without retry",async()=>{
  for(const failure of [()=>Promise.reject(Error("Transport lost")),()=>response({id:"A"}),()=>response({code:"PROVIDER_OUTPUT_INVALID",message:"Server failed",details:{}},500),()=>({ok:true,status:200,json:async()=>{throw Error("Bad JSON");}})]){
    const h=harness(),before=JSON.stringify(h.s.current);h.posts.push(failure);await h.propose();
    assert.equal(h.attempt().status,"unknown");assert.match(h.text("proposal-activity"),/outcome unknown.*last loaded proposal.*no automatic retry/);assert.equal(h.requests.length,1);assert.equal(JSON.stringify(h.s.current),before);assert.equal(h.errors.length,1);
  }
});

test("a proposal acknowledgement is retained across case, affordance or case-list refresh failures",async()=>{
  for(const failure of ["cases/A","cases/A/affordances","cases"]){
    const h=harness(),next=accepted(h);h.server.value=next;h.server.fail=failure;h.enqueue(next.case);await h.propose();
    assert.equal(h.attempt().status,"received");assert.equal(h.attempt().refresh,"failed");assert.match(h.text("proposal-activity"),/Proposal acknowledged.*refresh is incomplete/);assert.doesNotMatch(h.text("proposal-activity"),/outcome unknown|Request refused/);
    assert.equal(h.requests.filter(request=>request.method==="POST").length,1);assert.equal(h.get("request").value,"Unsent request remains intact");
    assert.match(h.text("proposal-origin"),failure==="cases"?/openrouter.*observed-model/:/offline.*fixture-v1/);
  }
});

test("late acknowledgement or failure cannot restore a different case or revision",async()=>{
  for(const failed of [false,true])for(const nextCurrent of [fixture("B",1),fixture("A",9)]){
    const h=harness(),pending=deferred(),next=accepted(h);h.posts.push(()=>pending.promise);const request=h.propose();await tick();h.s.current=nextCurrent;h.s.renderProposalProvenance();
    if(failed)pending.reject(Error("Old request failure"));else pending.resolve(response(next.case));await request;
    assert.equal(h.s.current,nextCurrent);assert.equal(h.requests.length,1);assert.equal(h.errors.length,0);assert.equal(h.get("proposal-activity").hidden,true);
  }
});

test("the existing case refresh reconciles proposal feedback without another proposal call",async()=>{
  const h=harness(),next=accepted(h);h.server.value=next;h.server.fail="cases/A";h.enqueue(next.case);await h.propose();
  assert.match(h.text("proposal-activity"),/Refresh current model in the command palette/);
  h.server.fail="cases";await assert.rejects(h.s.load("A"),/Workspace refresh failed/);assert.equal(h.attempt().refresh,"failed");assert.match(h.text("proposal-activity"),/refresh is incomplete/);
  h.server.fail=null;await h.s.load("A");assert.equal(h.attempt().refresh,"current");assert.match(h.text("proposal-activity"),/Interpretations received/);assert.doesNotMatch(h.text("proposal-activity"),/incomplete/);
  assert.equal(h.requests.filter(request=>request.method==="POST").length,1);
  const uncertain=harness();uncertain.posts.push(()=>Promise.reject(Error("Transport lost")));await uncertain.propose();
  assert.match(uncertain.text("proposal-activity"),/Refresh current model/);
  uncertain.server.value.observations.events=[event(9,"ProviderCallStarted",{attempt_id:"unresolved",provider:"offline"})];await uncertain.s.load("A");
  assert.match(uncertain.text("proposal-activity"),/outcome unknown.*case was refreshed.*still unconfirmed/);assert.match(uncertain.text("proposal-events"),/Started.*unresolved/);assert.equal(uncertain.requests.filter(request=>request.method==="POST").length,1);
});

test("candidate, closed case and edit reconciliation cannot submit proposals",async()=>{
  for(const modify of [h=>{h.s.current.case.candidate={states:[]};},h=>{h.s.current.case.stage="DISCARDED";},h=>{h.s.editNeedsRefresh.set("A",{});}]){
    const h=harness();modify(h);h.s.renderProposalProvenance();assert.equal(h.get("propose").disabled,true);await h.propose();assert.equal(h.requests.length,0);assert.equal(h.attempt(),null);
  }
});

test("acknowledgement must identify the exact captured request and next unselected proposal revision",async()=>{
  for(const mutate of [next=>{next.case.id="B";},next=>{next.case.version=9;},next=>{next.case.request="Different request";},next=>{next.case.stage="PREVIEW";next.case.selected_meaning="unsafe";next.case.candidate={};}]){
    const h=harness(),next=accepted(h);mutate(next);h.enqueue(next.case);await h.propose();assert.equal(h.attempt().status,"unknown");assert.equal(h.requests.length,1);assert.equal(h.s.current.case.id,"A");assert.equal(h.s.current.case.version,7);
  }
});

test("the feature is wired into actual render, startup and the existing proposal button",()=>{
  assert.match(section(source,"function render(){",'$("create").onclick='),/renderProposalProvenance\(\)/);
  assert.match(section(source,"task(async () => {","// Visual view:"),/renderProposalProvenance\(\)/);
  assert.ok(source.split(/\r?\n/).some(line=>line==='$("propose").onclick=()=>task(requestInterpretations,"Requesting an untrusted proposal…");'));
});
