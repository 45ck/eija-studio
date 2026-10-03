"use strict";
// Actual product picker, API, task, load, and selector handlers with controlled responses.
// DOM doubles establish application behavior; they do not claim browser/accessibility acceptance.
const {test}=require("node:test");
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(process.env.EIJA_CASE_PICKER_APP||path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
const clone=value=>JSON.parse(JSON.stringify(value));
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const row=(id,request=`Request ${id}`,stage="PREVIEW")=>({id,request,stage,version:7});
const fixture=id=>({case:row(id),packet:{subject:{semantic:`semantic-${id}`}},observations:{instances:[]}});
const response=(data,status=200)=>({ok:status>=200&&status<300,status,json:async()=>clone(data)});

function section(code,start,end){
  const first=code.indexOf(start),last=code.indexOf(end,first+start.length);
  assert.ok(first>=0&&last>first,`Actual source seam missing: ${start} -> ${end}`);
  return code.slice(first,last);
}

function harness({code=source,current=fixture("A")}={}){
  const nodes=new Map(),requests=[],errors=[],notices=[],renders=[],reconciliations=[];
  let pendingTask=null,diagnosticsCleared=0;
  const document={activeElement:null};
  class Element{
    constructor(tag="div"){
      this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.attributes={};
      this.hidden=false;this.disabled=false;this.ownText="";this.assignedValue=undefined;
    }
    set textContent(value){this.ownText=String(value);this.children=[];}
    get textContent(){return this.ownText+this.children.map(child=>child.textContent).join("");}
    get options(){return this.children.filter(child=>child.tagName==="OPTION");}
    get value(){
      if(this.tagName!=="SELECT")return this.assignedValue??(this.tagName==="OPTION"?this.textContent:"");
      return this.options.some(option=>option.value===this.assignedValue)?this.assignedValue:"";
    }
    set value(value){
      const next=String(value);
      this.assignedValue=this.tagName==="SELECT"&&!this.options.some(option=>option.value===next)?"":next;
    }
    append(...items){this.children.push(...items);}
    replaceChildren(...items){this.children=[...items];this.ownText="";this.assignedValue=undefined;}
    setAttribute(name,value){this.attributes[name]=String(value);}
    removeAttribute(name){delete this.attributes[name];}
    focus(){assert.equal(this.hidden,false,"Cannot focus a hidden control");assert.equal(this.disabled,false,"Cannot focus a disabled control");document.activeElement=this;}
  }
  const get=id=>{if(!nodes.has(id))nodes.set(id,new Element(id==="case-switcher"?"select":"div"));return nodes.get(id);};
  document.body=new Element("body");document.documentElement=new Element("html");document.activeElement=document.body;
  const s={current,instance:current?{id:`preview-${current.case.id}`,state:"Submitted",version:3}:null,
    busy:false,token:"fixture-token",caseViews:new Map(),editNeedsRefresh:new Map(),runtimeAttempt:null,
    tab:"try",editId:"TR-SUBMIT",inspectorSelection:{kind:"transition",id:"TR-SUBMIT"},
    modelView:"working",historyModel:null,historyLabel:"",canvasDirection:"AUTO",caseHistory:null,affordanceData:null,
    $:get,el:(tag,text)=>{const node=new Element(tag);if(text!==undefined)node.textContent=text;return node;},document,
    captureTaskFocus:()=>({}),restoreTaskFocus(){},cancelSourceRead(){},renderEditReconciliation(){},reconcileProposalRefresh(){},
    reconcileRuntime:next=>reconciliations.push(next.case.id),
    clearDiagnostic:()=>{diagnosticsCleared++;},reportError:error=>errors.push(error),notice:(text,error=false)=>notices.push({text,error}),
    fetch:(url,options)=>new Promise((resolve,reject)=>{
      const request={path:url.slice(5),method:options.method||"GET",body:options.body,settled:false};
      request.resolve=(data,status=200)=>{request.settled=true;resolve(response(data,status));};
      request.reject=error=>{request.settled=true;reject(error);};requests.push(request);
    })};
  s.render=()=>{renders.push(s.current.case.id);s.renderCasePicker();};
  vm.createContext(s);
  for(const [start,end]of [
    ["class ApiError","function reportError("],
    ["async function task(","let caseInventory="],
    ["let caseInventory=","let lastComparisonTab="],
    ["async function load(","let editNeedsRefresh="]
  ])vm.runInContext(section(code,start,end),s);
  for(const id of ["case-switcher","case-picker-retry"]){
    const binding=code.split(/\r?\n/).find(line=>line.startsWith(`$("${id}").${id==="case-switcher"?"onchange":"onclick"}=`));
    assert.ok(binding,`Actual ${id} binding missing`);vm.runInContext(binding,s);
  }
  const actualTask=s.task;
  s.task=(...args)=>{pendingTask=actualTask(...args);return pendingTask;};
  get("runtime-result").textContent="Committed: Submit. Effects: audit";
  s.renderCasePicker();
  const snapshot=()=>clone(vm.runInContext("({inventory:caseInventory,status:caseListState,sequence:caseListSequence})",s));
  return {s,get,nodes,requests,errors,notices,renders,reconciliations,document,snapshot,
    seed(inventory,state="ready"){
      s.fixtureInventory=inventory;s.fixtureListState=state;
      vm.runInContext("caseInventory=fixtureInventory;caseListState=fixtureListState;renderCasePicker();",s);
    },
    request(name){const request=requests.find(item=>item.path===name&&!item.settled);assert.ok(request,`Pending request missing: ${name}`);return request;},
    choices:()=>get("case-switcher").options.filter(option=>option.value!==""),
    choose(id){const select=get("case-switcher");select.value=id;assert.equal(select.value,id,"Test selection must exist as a native option");select.onchange({target:select});return pendingTask;},
    retry(){get("case-picker-retry").onclick();return pendingTask;},
    cleared:()=>diagnosticsCleared,
    assertReadOnly(){assert.ok(requests.every(request=>request.method==="GET"&&request.body===undefined),"Picker/navigation must not submit a mutation");}
  };
}

test("cold loading stays visible and disabled; only a successful empty list hides the picker",async()=>{
  const h=harness({current:null}),pending=h.s.cases();
  assert.equal(h.snapshot().status,"loading");assert.equal(h.snapshot().inventory,null);
  assert.equal(h.get("case-switcher").hidden,false);assert.equal(h.get("case-switcher").disabled,true);
  assert.equal(h.get("case-picker-label").hidden,false);assert.match(h.get("case-picker-status").textContent,/refresh|loading/i);
  h.s.focusCasePicker();assert.equal(h.document.activeElement,h.get("case-picker-status"));
  h.request("cases").resolve([]);await pending;
  assert.equal(h.snapshot().status,"ready");assert.deepEqual(h.snapshot().inventory,[]);
  assert.equal(h.get("case-switcher").hidden,true);assert.equal(h.get("case-picker-label").hidden,true);
  assert.equal(h.get("case-picker-retry").hidden,true);assert.equal(h.get("start-intent").disabled,false);
  h.s.focusCasePicker();assert.equal(h.document.activeElement,h.get("start-intent"));h.assertReadOnly();
});

test("native options keep literal request, stage and full case ID in one label",async()=>{
  const h=harness(),inventory=[row("A","<script>Draft & inspect</script>"),row("B-0123456789abcdef","Second request","SAVED")];
  h.s.current.case=clone(inventory[0]);
  const pending=h.s.cases();h.request("cases").resolve(inventory);await pending;
  assert.deepEqual(h.choices().map(option=>({value:option.value,label:option.textContent,title:option.title})),inventory.map(item=>({value:item.id,label:`${item.request} · ${item.stage} · ${item.id}`,title:item.request})));
  assert.ok(h.choices().every(option=>option.children.length===0),"Native options must not contain separate stage/id markup");
  assert.equal(h.get("case-switcher").value,"A");assert.equal(h.get("case-switcher").disabled,false);
  h.s.focusCasePicker();assert.equal(h.document.activeElement,h.get("case-switcher"));h.assertReadOnly();
});

test("active option describes the loaded case even when its inventory row has another stage or request",async()=>{
  const h=harness();h.s.current.case=row("A","Actually loaded request","VERIFIED");
  const inventory=[row("A","Cached older request","DRAFT"),row("B","Other listed request","SAVED")];
  const pending=h.s.cases();h.request("cases").resolve(inventory);await pending;
  assert.deepEqual(h.snapshot().inventory,inventory,"Rendering must not rewrite the server inventory");
  assert.deepEqual(h.choices().map(option=>option.textContent),["Actually loaded request · VERIFIED · A","Other listed request · SAVED · B"]);
  assert.equal(h.choices()[0].title,"Actually loaded request");assert.equal(h.get("case-switcher").value,"A");
});

test("list refresh keeps usable inventory and the actual current case while pending",async()=>{
  const h=harness(),inventory=[row("A"),row("B")];h.seed(inventory);
  const current=h.s.current,preview=h.s.instance,pending=h.s.cases();
  assert.deepEqual(h.snapshot().inventory,inventory);assert.equal(h.snapshot().status,"loading");
  assert.equal(h.get("case-switcher").value,"A");assert.equal(h.get("case-switcher").disabled,false);
  assert.match(h.get("case-picker-status").textContent,/retained/i);
  h.request("cases").resolve([row("B")]);await pending;
  assert.equal(h.s.current,current);assert.equal(h.s.instance,preview);assert.equal(h.get("case-switcher").value,"A");
  assert.deepEqual(h.choices().map(option=>option.value),["A","B"]);assert.match(h.get("case-picker-status").textContent,/absent.*latest case list/i);h.assertReadOnly();
});

test("an empty successful inventory never hides an actually loaded case",async()=>{
  const h=harness(),current=h.s.current,pending=h.s.cases();h.request("cases").resolve([]);await pending;
  assert.equal(h.snapshot().status,"ready");assert.deepEqual(h.snapshot().inventory,[]);
  assert.equal(h.s.current,current);assert.equal(h.get("case-switcher").hidden,false);assert.equal(h.get("case-switcher").disabled,false);
  assert.equal(h.get("case-picker-label").hidden,false);assert.equal(h.get("case-switcher").value,"A");
  assert.deepEqual(h.choices().map(option=>option.value),["A"]);assert.doesNotMatch(h.get("case-picker-status").textContent,/No change cases yet/);
});

test("failed GET retains old inventory and current selection, and exposes explicit retry",async()=>{
  const h=harness(),inventory=[row("A"),row("B")];h.seed(inventory);
  const current=h.s.current,preview=h.s.instance,pending=h.s.cases(),rejected=assert.rejects(pending,/Offline case list/);
  h.request("cases").reject(Error("Offline case list"));await rejected;
  assert.equal(h.snapshot().status,"unavailable");assert.deepEqual(h.snapshot().inventory,inventory);
  assert.equal(h.s.current,current);assert.equal(h.s.instance,preview);assert.equal(h.get("case-switcher").value,"A");
  assert.equal(h.get("case-switcher").hidden,false);assert.equal(h.get("case-picker-retry").hidden,false);
  assert.match(h.get("case-picker-status").textContent,/unavailable/i);assert.doesNotMatch(h.get("case-picker-status").textContent,/No change cases yet/);h.assertReadOnly();
});

test("failed initial list keeps unavailable distinct from empty and palette focuses recovery",async()=>{
  const h=harness({current:null}),pending=h.s.cases(),rejected=assert.rejects(pending,/Offline/);
  h.request("cases").reject(Error("Offline"));await rejected;
  assert.equal(h.snapshot().inventory,null);assert.equal(h.snapshot().status,"unavailable");
  assert.equal(h.get("case-switcher").hidden,false);assert.equal(h.get("case-switcher").disabled,true);assert.equal(h.get("case-picker-label").hidden,false);
  h.s.focusCasePicker();assert.equal(h.document.activeElement,h.get("case-picker-retry"));
  const retry=h.retry();assert.equal(h.snapshot().status,"loading");h.request("cases").resolve([row("B")]);await retry;
  assert.equal(h.snapshot().status,"ready");assert.equal(h.get("case-switcher").value,"");assert.equal(h.s.current,null,"Refreshing inventory must not choose a case");
  assert.equal(h.document.activeElement,h.get("case-switcher"));assert.equal(h.cleared(),1);assert.equal(h.errors.length,0);h.assertReadOnly();
});

test("actual retry completion preserves deliberate focus movement during the GET",async()=>{
  for(const moved of [false,true]){
    const h=harness({current:null});h.seed(null,"unavailable");h.get("case-picker-retry").focus();
    const pending=h.retry(),elsewhere=h.get("start-intent");
    if(moved)elsewhere.focus();
    h.request("cases").resolve([row("B")]);await pending;
    assert.equal(h.document.activeElement,moved?elsewhere:h.get("case-switcher"));
    assert.equal(h.snapshot().status,"ready");assert.equal(h.cleared(),1);h.assertReadOnly();
  }
});

test("malformed or duplicate inventory is unavailable and never substitutes an empty success",async()=>{
  for(const data of [null,{},"not a list",[null],[{id:"B"}],[row("B"),row("B")]]){
    const h=harness(),before=[row("A")];h.seed(before);
    const pending=h.s.cases(),rejected=assert.rejects(pending,error=>error.code==="CASE_LIST_INVALID");
    h.request("cases").resolve(data);await rejected;
    assert.equal(h.snapshot().status,"unavailable");assert.deepEqual(h.snapshot().inventory,before);
    assert.equal(h.get("case-switcher").value,"A");assert.equal(h.get("case-switcher").hidden,false);h.assertReadOnly();
  }
});

async function latestResponseOracle(code=source,oldFails=false){
  const h=harness({code,current:null}),old=h.s.cases(),oldRequest=h.request("cases"),newest=h.s.cases();
  const newestRequest=h.requests.at(-1);newestRequest.resolve([row("C")]);await newest;
  const accepted=h.snapshot(),status=h.get("case-picker-status").textContent;
  if(oldFails)oldRequest.reject(Error("Superseded failure"));else oldRequest.resolve([row("B")]);
  await old;
  assert.deepEqual(h.snapshot(),accepted,"A superseded completion must not replace the accepted inventory/status");
  assert.equal(h.get("case-picker-status").textContent,status);assert.deepEqual(h.choices().map(option=>option.value),["C"]);h.assertReadOnly();
}
test("latest list request wins over both stale success and stale failure",async()=>{
  await latestResponseOracle();await latestResponseOracle(source,true);
});
test("the stale-response oracle rejects removal of the actual sequence guards",async()=>{
  const guard="if(sequence!==caseListSequence)return false;";
  assert.ok(source.includes(guard),"Actual sequence guard must remain identifiable for this counterexample");
  await assert.rejects(latestResponseOracle(source.split(guard).join("")),/superseded completion/);
});

for(const failedPath of ["cases/B","cases/B/affordances"]){
  test(`actual selector preserves case A and preview when ${failedPath} fails`,async()=>{
    const h=harness();h.seed([row("A"),row("B")]);const current=h.s.current,preview=h.s.instance,feedback=h.get("runtime-result").textContent;
    const pending=h.choose("B");assert.equal(h.get("case-switcher").value,"A","Pending selection must still identify the displayed case");
    for(const request of h.requests){
      if(request.path===failedPath)request.reject(Error("Cannot load case B"));
      else request.resolve(request.path.endsWith("/history")?{status:"ready"}:request.path.endsWith("/affordances")?{affordances:[]}:fixture("B"));
    }
    await pending;
    assert.equal(h.s.current,current);assert.equal(h.s.instance,preview);assert.equal(h.get("runtime-result").textContent,feedback);
    assert.equal(h.get("case-switcher").value,"A");assert.deepEqual(h.renders,[]);assert.deepEqual(h.reconciliations,[]);
    assert.equal(h.errors.length,1);assert.match(h.errors[0].message,/Cannot load case B/);h.assertReadOnly();
  });
}

test("a successful B load remains selected when its following inventory GET fails",async()=>{
  const h=harness();h.seed([row("A"),row("B")]);
  const pending=h.choose("B");
  h.request("cases/B").resolve(fixture("B"));h.request("cases/B/affordances").resolve({affordances:[]});h.request("cases/B/history").resolve({status:"ready"});
  await tick();assert.equal(h.s.current.case.id,"B");assert.equal(h.get("case-switcher").value,"B");
  h.request("cases").reject(Error("Inventory refresh failed after acknowledged load"));await pending;
  assert.equal(h.s.current.case.id,"B");assert.equal(h.get("case-switcher").value,"B");assert.deepEqual(h.renders,["B"]);
  assert.equal(h.snapshot().status,"unavailable");assert.equal(h.errors.length,1);assert.match(h.errors[0].message,/after acknowledged load/);h.assertReadOnly();
});

test("loaded B gets a real fallback option when it was absent from the retained inventory",async()=>{
  const h=harness();h.seed([row("A")]);const pending=h.s.load("B"),rejected=assert.rejects(pending,/Inventory refresh failed/);
  h.request("cases/B").resolve(fixture("B"));h.request("cases/B/affordances").resolve({affordances:[]});h.request("cases/B/history").resolve({status:"ready"});
  await tick();h.request("cases").reject(Error("Inventory refresh failed"));await rejected;
  assert.deepEqual(h.snapshot().inventory,[row("A")]);assert.equal(h.s.current.case.id,"B");
  assert.equal(h.get("case-switcher").value,"B","A select cannot display a value without an actual matching option");
  assert.deepEqual(h.choices().map(option=>option.value),["B","A"]);assert.match(h.choices()[0].textContent,/Request B · PREVIEW · B/);h.assertReadOnly();
});

test("busy actual selector cannot start a second load or mislabel the displayed case",async()=>{
  const h=harness();h.seed([row("A"),row("B")]);h.s.busy=true;await h.choose("B");
  assert.equal(h.s.current.case.id,"A");assert.equal(h.get("case-switcher").value,"A");assert.equal(h.requests.length,0);assert.equal(h.errors.length,0);
});
