"use strict";
// Actual presentation, task, request/API and provenance rendering; controlled DOM/transport/reload boundaries.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(process.env.EIJA_APP_MODULE||path.join(__dirname,"../../src/eija_studio/resources/web/app.js"),"utf8");
const clone=value=>JSON.parse(JSON.stringify(value));
function section(code,start,end){const a=code.indexOf(start),b=code.indexOf(end,a+start.length);assert.ok(a>=0&&b>a,start);return code.slice(a,b);}
const descend=node=>node.children.flatMap(child=>[child,...descend(child)]);
const visibleText=node=>node.tag==="details"&&!node.open?visibleText(node.children[0]):node.ownText+node.children.map(visibleText).join(" ");
const freeze=value=>{if(value&&typeof value==="object"){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
function fixture(){return {case:{id:"case-A",version:2,stage:"PROPOSED",request:"Fixture request",candidate:null,selected_meaning:null,proposal:{summary:"Fixture proposal",unknowns:[],alternatives:[
  {interpretation:"safe",explanation:"Untrusted recommendation"},{interpretation:"authority",explanation:"Untrusted authority request"},{interpretation:"external",explanation:"Untrusted external request"}]}},options:{
  safe:{supported:true,label:"Recommend only",consequences:["Teacher recommends; Registrar retains final approval."]},
  authority:{supported:false,label:"Teacher approves",consequences:["Transfers approval authority to Teacher.","Protected policy rejects this interpretation."]},
  external:{supported:false,label:"External workflow",consequences:["Requires an unsupported operator."]}}};}
function harness(code=source,{retainedDisclosureRects=false}={}){
  const document={},calls=[],roots=[],requests=[],reloads=[],errors=[];let acceptedCase=null;
  class Element{
    constructor(tag,text,cls){this.tag=tag;this.ownText=text===undefined?"":String(text);this.className=cls||"";this.children=[];this.dataset={};this.open=false;this.disabled=false;this.checked=false;this.id="";this.hidden=false;this.attributes={};}
    get disabled(){return !!this.isDisabled;}
    set disabled(value){this.isDisabled=!!value;if(value&&document.activeElement===this)document.activeElement=document.body;}
    setAttribute(key,value){this.attributes[key]=String(value);}
    removeAttribute(key){delete this.attributes[key];}
    get textContent(){return this.ownText+this.children.map(node=>node.textContent).join(" ");}
    set textContent(text){this.ownText=String(text);this.replaceChildren();}
    append(...nodes){for(const node of nodes){node.parent=this;this.children.push(node);}}
    replaceChildren(...nodes){if(this!==document.activeElement&&this.contains(document.activeElement))document.activeElement=document.body;for(const child of this.children)child.parent=null;this.children=[];this.append(...nodes);}
    contains(node){return node===this||this.children.some(child=>child.contains(node));}
    querySelectorAll(selector){assert.equal(selector,"button[data-meaning]");return descend(this).filter(node=>node.tag==="button"&&node.dataset.meaning);}
    hiddenByDisclosure(){for(let node=this;node.parent;node=node.parent)if(node.parent.tag==="details"&&!node.parent.open&&node!==node.parent.children[0])return true;return false;}
    getClientRects(){return this.hidden||(!retainedDisclosureRects&&this.hiddenByDisclosure())?[]:[1];}
    focus(){if(!this.disabled&&!this.hidden&&!this.hiddenByDisclosure())document.activeElement=this;}
  }
  const el=(...args)=>new Element(...args),root=(id,tag="div")=>{const node=el(tag);node.id=id;roots.push(node);return node;};
  const body=root("body");document.body=body;document.documentElement=root("html");document.activeElement=body;
  const controls=root("proposal-controls","details"),summary=el("summary","Request interpretations"),propose=el("button","Get interpretations"),egress=el("input");
  summary.id="proposal-controls-summary";propose.id="propose";egress.id="egress";controls.open=true;controls.append(summary,propose,egress);
  const options=root("options"),interpretations=root("interpretation-panel","details"),intentSummary=el("summary","Interpretations");
  intentSummary.id="interpretation-summary";interpretations.open=true;interpretations.append(intentSummary,controls,options);root("case-title","h1");
  for(const id of ["status-agent","proposal-provenance","proposal-record","proposal-provider","proposal-activity","proposal-subject","proposal-origin","proposal-metadata","proposal-events","proposal-events-heading"])root(id);
  const get=id=>roots.flatMap(node=>[node,...descend(node)]).find(node=>node.id===id)||null;
  const s={document,$:get,el,current:fixture(),editNeedsRefresh:new Map(),token:"fixture-token",
    busy:false,status:{provider:"offline",provider_networked:false},reportError:error=>errors.push(error),
    command:async(action,body)=>{calls.push({action,body});},notice:()=>{},
    fetch:async(url,options)=>{
      const request={path:url.slice(5),method:options.method||"GET",body:options.body?JSON.parse(options.body):undefined};requests.push(request);
      assert.equal(request.path,`cases/${s.current.case.id}/propose`);assert.equal(request.method,"POST");
      acceptedCase=clone(s.current.case);acceptedCase.version++;acceptedCase.stage="PROPOSED";acceptedCase.proposal??=fixture().case.proposal;
      return {ok:true,status:200,json:async()=>clone(acceptedCase)};
    },
    load:async(id,canPublish)=>{assert.equal(id,acceptedCase.id);assert.equal(canPublish(),true);reloads.push(id);s.current={...s.current,case:clone(acceptedCase)};s.renderProposals(s.current.case,false);return true;}};
  const start=code.indexOf("function renderProposals("),end=code.indexOf("function render(){",start);assert.ok(start>=0&&end>start);
  vm.createContext(s);vm.runInContext(code.slice(start,end),s);
  for(const [from,to]of [["class ApiError","function reportError("],["function captureTaskFocus()","let caseInventory="],
    ["let proposalAttempt=","async function command("]])vm.runInContext(section(code,from,to),s);
  const binding=code.split(/\r?\n/).find(line=>line.startsWith('$("propose").onclick='));assert.ok(binding);vm.runInContext(binding,s);
  return {s,get,document,calls,requests,reloads,errors,render:closed=>s.renderProposals(s.current.case,!!closed),cards:()=>descend(get("options")).filter(node=>node.className.split(" ").includes("option")),
    button:meaning=>get("options").querySelectorAll("button[data-meaning]").find(node=>node.dataset.meaning===meaning)};
}
function assertComplete(h){
  const current=h.s.current;assert.equal(h.cards().length,current.case.proposal.alternatives.length);
  const shown=visibleText(h.get("options"));
  for(const option of Object.values(current.options)){assert.ok(shown.includes(option.label),option.label);for(const consequence of option.consequences)assert.ok(shown.includes(consequence),consequence);}
  assert.ok(h.button("safe").getClientRects().length,"Supported choice remains directly reachable");
  assert.match(visibleText(h.get("proposal-alternatives")),/Unsupported interpretations \(2\)/);
}
test("completed controls collapse but all three meanings and every canonical boundary remain visible",()=>{
  const h=harness();freeze(h.s.current);const before=JSON.stringify(h.s.current);h.get("propose").focus();h.render();
  assertComplete(h);assert.equal(h.get("proposal-controls").open,false);assert.equal(h.get("proposal-alternatives").open,false);
  assert.equal(h.document.activeElement,h.get("proposal-controls-summary"));assert.equal(JSON.stringify(h.s.current),before);assert.deepEqual(h.calls,[]);
  assert.ok(!visibleText(h.get("options")).includes("Untrusted authority request"));
});
test("unsupported explanations remain inspectable with their actual unchanged boundary action",async()=>{
  const h=harness();h.render();const group=h.get("proposal-alternatives");group.open=true;
  assert.ok(h.button("authority").getClientRects().length);const card=h.cards().find(node=>node.contains(h.button("authority")));
  card.children.find(node=>node.tag==="details").open=true;assert.ok(visibleText(card).includes("Untrusted authority request"));
  await h.button("authority").onclick();assert.deepEqual(JSON.parse(JSON.stringify(h.calls)),[{action:"select",body:{interpretation:"authority"}}]);
});
test("closing completed controls recovers egress focus but never takes focus from another control",()=>{
  const h=harness();h.get("egress").focus();h.render();assert.equal(h.document.activeElement,h.get("proposal-controls-summary"));
  const other=harness();other.get("case-title").focus();other.render();assert.equal(other.document.activeElement,other.get("case-title"));
});
test("retry controls retain exact consent and deliberate opening across same-proposal refresh",async()=>{
  const h=harness();h.render();h.get("proposal-controls").open=true;h.get("egress").checked=true;h.get("propose").focus();h.render();
  assert.equal(h.get("proposal-controls").open,true);assert.equal(h.get("egress").checked,true);assert.equal(h.document.activeElement,h.get("propose"));
  await h.get("propose").onclick();
  assert.deepEqual(clone(h.requests),[{path:"cases/case-A/propose",method:"POST",body:{expected_version:2,consent:true}}]);
  assert.deepEqual(h.reloads,["case-A"]);assert.deepEqual(h.calls,[]);assert.equal(h.s.current.case.version,3);
  assert.equal(h.get("proposal-controls").open,true);assert.equal(h.get("egress").checked,true);
});
test("discovery state persists for the same proposal but cannot leak to a new proposal or case",()=>{
  const h=harness();h.render();h.get("proposal-alternatives").open=true;h.get("proposal-alternatives-summary").focus();h.render();
  assert.equal(h.get("proposal-alternatives").open,true);assert.equal(h.document.activeElement,h.get("proposal-alternatives-summary"));
  h.s.current.case.proposal.summary="New proposal";h.render();assert.equal(h.get("proposal-alternatives").open,false);
  h.get("proposal-controls").open=true;h.s.current.case.id="case-B";h.render();assert.equal(h.get("proposal-controls").open,false);
});
test("before proposals the request controls stay open; an all-unsupported result states that limit",()=>{
  const h=harness();h.s.current.case.proposal=null;h.render();assert.equal(h.get("proposal-controls").open,true);assert.equal(h.cards().length,0);
  h.s.current=fixture();h.s.current.case.proposal.alternatives=h.s.current.case.proposal.alternatives.slice(1);h.render();
  assert.match(visibleText(h.get("options")),/No supported interpretation was proposed/);assert.match(visibleText(h.get("options")),/Teacher approves/);
});
test("the selected intent has a named disclosure retaining every consequence and disabled selection action",()=>{
  const h=harness();h.s.current.case.selected_meaning="safe";h.s.current.case.candidate={id:"candidate"};h.render();
  assert.equal(h.get("interpretation-panel").open,false);assert.equal(h.get("interpretation-summary").textContent,"Selected intent: Recommend only");
  h.get("interpretation-panel").open=true;
  assertComplete(h);assert.ok(h.button("safe").getClientRects().length);assert.equal(h.button("safe").textContent,"Meaning selected");
  assert.ok(h.get("options").querySelectorAll("button[data-meaning]").every(button=>button.disabled));
  h.render();assert.equal(h.get("interpretation-panel").open,true,"A deliberate disclosure opening survives same-case refresh");
  h.s.current.case.id="case-B";h.render();assert.equal(h.get("interpretation-panel").open,false,"A new candidate does not inherit the prior disclosure state");
  h.s.current=fixture();h.render(true);assert.ok(h.get("options").querySelectorAll("button[data-meaning]").every(button=>button.disabled));
});
test("the comparison oracle rejects hiding boundaries or supported choices under the unsupported disclosure",()=>{
  for(const [marker,replacement]of [["for(const {canonical} of unsupported)","for(const {canonical} of [])"],["canonical.supported||chosen","chosen"]]){
    assert.ok(source.includes(marker));const h=harness(source.replace(marker,replacement));h.render();
    assert.throws(()=>assertComplete(h),assert.AssertionError);
  }
});


test("a candidate arriving while request content has focus returns to the visible intent summary",()=>{
  for(const focusId of ["egress","propose","proposal-controls-summary"])for(const collapseClearsFocus of [false,true]){
    const h=harness();h.render();const panel=h.get("interpretation-panel");h.get("proposal-controls").open=true;h.get(focusId).focus();
    if(collapseClearsFocus){
      // A DOM variant clears focus as the ancestor closes; capture must happen before closing.
      let opened=panel.open;Object.defineProperty(panel,"open",{get:()=>opened,set:value=>{opened=value;if(!value&&panel.contains(h.document.activeElement)&&h.document.activeElement!==h.get("interpretation-summary"))h.document.activeElement=h.document.body;}});
    }
    h.s.current.case.candidate={id:"candidate"};h.s.current.case.selected_meaning="safe";const before=JSON.stringify(h.s.current);h.render();
    assert.equal(panel.open,false);assert.equal(h.document.activeElement,h.get("interpretation-summary"),focusId);
    assert.ok(h.document.activeElement.getClientRects().length);assert.equal(JSON.stringify(h.s.current),before);assert.deepEqual(h.calls,[]);assert.deepEqual(h.requests,[]);
  }
});

test("candidate collapse preserves external navigation and native intent-summary focus",()=>{
  for(const focusId of ["case-title","interpretation-summary"]){
    const h=harness();h.render();h.get(focusId).focus();h.s.current.case.candidate={id:"candidate"};h.s.current.case.selected_meaning="safe";h.render();
    assert.equal(h.document.activeElement,h.get(focusId));assert.ok(h.document.activeElement.getClientRects().length);
    h.render();assert.equal(h.document.activeElement,h.get(focusId),"Refreshing an already collapsed intent must not steal focus");
  }
});

test("explicit meaning selection keeps its existing case-title focus destination",()=>{
  const h=harness();h.render();h.button("safe").focus();h.s.current.case.candidate={id:"candidate"};h.s.current.case.selected_meaning="safe";h.render();
  assert.equal(h.document.activeElement,h.get("case-title"));assert.ok(h.document.activeElement.getClientRects().length);assert.equal(h.get("interpretation-panel").open,false);
});

async function firstRequestFocus(code=source,retainedDisclosureRects=false){
  const h=harness(code,{retainedDisclosureRects});h.s.current.case.proposal=null;h.render();h.get("egress").checked=true;
  const fetch=h.s.fetch;let release;const gate=new Promise(resolve=>{release=resolve;});
  h.s.fetch=async(...args)=>{const response=await fetch(...args);await gate;return response;};
  h.get("propose").focus();const pending=h.get("propose").onclick();
  assert.equal(h.get("propose").disabled,true,"Actual provenance disables the in-flight request button");
  assert.equal(h.document.activeElement,h.document.body,"Native disable blur must precede the response render");
  await h.get("propose").onclick();assert.equal(h.requests.length,1,"Actual task blocks duplicate activation");
  release();await pending;return h;
}
function assertFirstRequestFocus(h){
  assert.deepEqual(h.errors,[]);assert.equal(h.get("proposal-controls").open,false);assert.equal(h.get("interpretation-panel").open,true);
  assert.equal(h.get("propose").disabled,false);assert.equal(h.document.activeElement,h.get("proposal-controls-summary"));
  assert.ok(!h.document.activeElement.hiddenByDisclosure());assert.equal(h.s.busy,false);assert.equal(h.s.current.case.selected_meaning,null);
  assert.deepEqual(clone(h.requests),[{path:"cases/case-A/propose",method:"POST",body:{expected_version:2,consent:true}}]);
  assert.deepEqual(h.reloads,["case-A"]);assert.deepEqual(h.calls,[]);
}
test("actual request task restores native-disable blur to the closed controls summary",async t=>{
  // Retained layout boxes must never make content under closed details a focus destination.
  for(const retainedRects of [false,true])await t.test(`retained disclosure boxes: ${retainedRects}`,async()=>{
    assertFirstRequestFocus(await firstRequestFocus(source,retainedRects));
  });
});
test("actual retry task restores the deliberately open request button",async()=>{
  const h=harness();h.render();h.get("proposal-controls").open=true;h.get("propose").focus();
  await h.get("propose").onclick();
  assert.deepEqual(h.errors,[]);assert.equal(h.get("proposal-controls").open,true);assert.equal(h.get("interpretation-panel").open,true);
  assert.equal(h.document.activeElement,h.get("propose"));assert.equal(h.get("propose").disabled,false);
  assert.equal(h.requests.length,1);assert.equal(h.s.current.case.selected_meaning,null);
});
test("pending request completion preserves deliberate external focus and collapsed intent",async()=>{
  for(const externalFocus of [false,true]){
    const h=harness(source,{retainedDisclosureRects:true});h.s.current.case.proposal=null;h.render();
    const fetch=h.s.fetch;let release;const gate=new Promise(resolve=>{release=resolve;});
    h.s.fetch=async(...args)=>{const response=await fetch(...args);await gate;return response;};
    h.get("propose").focus();const pending=h.get("propose").onclick();
    h.get("interpretation-panel").open=false;if(externalFocus)h.get("case-title").focus();
    release();await pending;
    assert.deepEqual(h.errors,[]);assert.equal(h.get("interpretation-panel").open,false,"Completion must not reopen the owner's disclosure");
    assert.equal(h.document.activeElement,h.get(externalFocus?"case-title":"interpretation-summary"));
    assert.ok(!h.document.activeElement.hiddenByDisclosure());assert.equal(h.s.current.case.selected_meaning,null);assert.equal(h.requests.length,1);
  }
});
test("request refusal restores the open request button without changing the loaded proposal",async()=>{
  const h=harness();h.s.current.case.proposal=null;h.render();const before=JSON.stringify(h.s.current),fetch=h.s.fetch;
  h.s.fetch=async(...args)=>{await fetch(...args);return {ok:false,status:409,json:async()=>({code:"STALE_VERSION",message:"Refresh required",details:{}})};};
  h.get("propose").focus();await h.get("propose").onclick();
  assert.equal(h.errors.length,1);assert.equal(h.errors[0].code,"STALE_VERSION");assert.equal(h.get("proposal-controls").open,true);
  assert.equal(h.get("propose").disabled,false);assert.equal(h.document.activeElement,h.get("propose"));assert.equal(JSON.stringify(h.s.current),before);
  assert.deepEqual(h.reloads,[]);assert.equal(h.requests.length,1);
});
test("focus oracle rejects removing async disclosure recovery independently of provider success",async()=>{
  const recovery='  if(previous.id==="propose"&&!$("interpretation-panel").open)target=$("interpretation-summary");\n  else if(previous.id==="propose"&&!$("proposal-controls").open)target=$("proposal-controls-summary");\n';
  assert.equal(source.split(recovery).length,2,"Mutation anchor must identify exactly one scoped recovery");
  const h=await firstRequestFocus(source.replace(recovery,""),true);
  assert.deepEqual(h.errors,[]);assert.equal(h.s.current.case.version,3);assert.equal(h.cards().length,3);
  assert.throws(()=>assertFirstRequestFocus(h),assert.AssertionError,"A successful proposal must not mask lost focus");
});
