"use strict";
// Transport lifecycle of actual app source plus actual immutable-subject validator.
// DOM rendering has a separate component suite; these tests run no network or browser.
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const appPath=path.join(__dirname,"../../src/eija_studio/resources/web/app.js");
const app=fs.readFileSync(appPath,"utf8"),begin=app.indexOf("let repositoryReview=null"),end=app.indexOf("\nrenderRepositoryReview();",begin);
assert.ok(begin>=0&&end>begin,"extract the actual repository request lifecycle, including event bindings");
const source=app.slice(begin,end+"\nrenderRepositoryReview();".length);
const markup=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/index.html"),"utf8");
const review=require(process.env.EIJA_REPOSITORY_REVIEW_MODULE||path.join(__dirname,"../../src/eija_studio/resources/web/repository-review.js"));
const clone=value=>JSON.parse(JSON.stringify(value)),oid=char=>char.repeat(40),sha=char=>char.repeat(64);
class ApiError extends Error{constructor(code,message,details={}){super(message);this.code=code;this.details=details;}}
function fixture(base="a",head="b",id="comparison-1"){
  const subject=char=>({commit:oid(char),tree:oid(char),changed_source_hash:"sha256:"+sha(char)});
  const files=["src/雪 #.py","src/second.py"].map((name,index)=>{
    const side=char=>({status:"captured",blob:oid(char),mode:"100644",file_sha256:sha(char),byte_length:48+index});
    const symbols=["first","second"].map(fragment=>{
      const reference="repo://"+name.split("/").map(encodeURIComponent).join("/")+"#"+fragment;
      const fact={reference,kind:"function",syntax_digest:sha("7"),start_line:1,end_line:2};
      return {reference,kind:"function",status:"changed",before:clone(fact),after:{...fact,syntax_digest:sha("8")}};
    });
    return {path:name,status:"modified",before:side("1"),after:side("2"),symbols,extraction:{before:{status:"EXTRACTED",symbols:symbols.map(s=>s.before)},after:{status:"EXTRACTED",symbols:symbols.map(s=>s.after)}}};
  });
  return {schema:"eija.repository.change.v1",status:"available",read_only:true,comparison_id:id,base:subject(base),head:subject(head),files,coverage:{changed_paths_total:2,displayed_paths:2,excluded_by_reason:{},inventory_reconciles:true},gaps:[]};
}
function selection(comparison,index=0,symbol=null){const row=comparison.files[index];return review.selectionFor(comparison,row.path,symbol===null?null:row.symbols[symbol].reference);}
function detail(comparison,selected){
  const row=comparison.files.find(row=>row.path===selected.path),symbol=row.symbols.find(symbol=>symbol.reference===selected.reference);
  const side=name=>({...clone(row[name]),text:"def example():\n    return 1\n",range:{start:1,end:2},truncated:false,snippet_sha256:sha("9"),...(symbol?{symbol:clone(symbol[name])}:{})});
  return {schema:"eija.repository.change-file.v1",status:"available",read_only:true,comparison_id:comparison.comparison_id,base:clone(comparison.base),head:clone(comparison.head),path:selected.path,selected_reference:selected.reference,before:side("before"),after:side("after"),unified_diff:{status:"AVAILABLE",text:"-old\n+new\n",truncated:false},known_impact:{}};
}
function harness(code=source){
  const nodes=new Map(),requests=[],renders=[],reported=[],shellCalls=[],controls=new Map();let document;
  const classes=()=>{const values=new Set();return {add(...names){names.forEach(name=>values.add(name));},remove(...names){names.forEach(name=>values.delete(name));},contains:name=>values.has(name),toggle(name,force){const enabled=force===undefined?!values.has(name):force;enabled?values.add(name):values.delete(name);return enabled;}};};
  const get=id=>{if(!nodes.has(id))nodes.set(id,{id,textContent:"",value:"",dataset:{},attributes:{},listeners:{},classList:classes(),hidden:false,open:id==="repository-revisions",tagName:id==="repository-revisions"?"DETAILS":id==="repository-revisions-summary"?"SUMMARY":"DIV",disabled:false,isConnected:true,parent:null,children:[],setAttribute(k,v){this.attributes[k]=String(v);},addEventListener(k,fn){this.listeners[k]=fn;},contains(node){return this===node||this.children.some(child=>child.contains(node));},getClientRects(){for(let node=this;node;node=node.parent){if(!node.isConnected||node.hidden)return [];if(node.tagName==="DETAILS"&&!node.open&&!node.children.find(child=>child.tagName==="SUMMARY")?.contains(this))return [];}return [{}];},focus(){if(!this.disabled&&this.getClientRects().length){sandbox.focused=id;document.activeElement=this;}},querySelector(){return null;}});return nodes.get(id);};
  document={body:get("body"),documentElement:get("html"),activeElement:get("body")};
  const revisionDetails=get("repository-revisions"),revisionSummary=get("repository-revisions-summary"),revisionForm=get("repository-compare-form");
  revisionDetails.children=[revisionSummary,revisionForm];revisionSummary.parent=revisionDetails;revisionForm.parent=revisionDetails;
  for(const id of ["repository-base","repository-head","repository-loaded-base","repository-loaded-head"]){const node=get(id);node.parent=revisionForm;revisionForm.children.push(node);}

  const acceptedLabel=get("repository-loaded-pair");acceptedLabel.parent=revisionSummary;revisionSummary.children.push(acceptedLabel);
  const statusTag=markup.match(/<[^>]+\bid="repository-comparison-status"[^>]*>/)?.[0];assert.ok(statusTag);
  for(const match of statusTag.matchAll(/([\w-]+)="([^"]*)"/g))get("repository-comparison-status").setAttribute(match[1],match[2]);
  function redrawControls(){
    for(const id of ["repository-review","repository-change-navigator"]){const root=get(id);for(const node of root.children){if(node.contains(document.activeElement))document.activeElement=document.body;node.isConnected=false;node.parent=null;}root.children=[];}
    for(const [id,spec]of controls){nodes.delete(id);const node=get(id),root=get(spec.container);node.hidden=!!spec.hidden;node.disabled=!!spec.disabled;node.parent=root;root.children.push(node);}
  }
  const sandbox={URLSearchParams,ApiError,$:get,document,console,focused:null,
    api(route,...args){assert.ok(!args.length||args[0]==="GET","historical reads must not send mutation commands");let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});requests.push({route,args,resolve,reject});return promise;},
    EijaRepositoryReview:{inspect:review.inspect,render(root,options){redrawControls();const render={root,options,destroyed:false,symbolsOpen:!!options.symbolsOpen,symbolsFilter:options.symbolsFilter||"changed"};renders.push(render);return {destroy(){render.destroyed=true;},getState(){return {selection:options.selection,view:options.view,symbolsOpen:render.symbolsOpen,symbolsFilter:render.symbolsFilter};}};}},
    reportError(error){reported.push(error);vm.runInContext("lastDiagnostic = {}",sandbox);const target=vm.runInContext("lastDiagnostic",sandbox);Object.assign(target,{code:error.code||"REQUEST_FAILED",message:error.message,details:error.details||{}});sandbox.notice(error.message+(error.details?.codes?.length?" · "+error.details.codes.join("; "):""));},
    notice(message){get("notice").textContent=message;},
    clearDiagnostic(){vm.runInContext("lastDiagnostic=null",sandbox);},
    renderNavigator(){shellCalls.push("navigator");},EijaShell:{reveal(key){shellCalls.push(["reveal",key]);}},
    openSource(){throw new Error("Historical review must not request live source");},loadRepositoryImpact(){throw new Error("Historical review must not request live impact");}
  };
  vm.createContext(sandbox);
  vm.runInContext('let current={case:{id:"case-A",version:7}},instance={state:"Draft"},workbench={connection:{source_hash:"live-snapshot"}},modelView="history",sourceRecord={reference:"repo://live",data:{text:"retained live text"}},lastDiagnostic=null,navigatorMode="domain";',sandbox);
  get("q-authority").value="unsent owner answer";get("intent").value="unsent intent";
  vm.runInContext(code,sandbox,{filename:appPath});
  const state=()=>JSON.parse(vm.runInContext('JSON.stringify({comparison:repositoryComparison,file:repositoryFile,selection:repositorySelection,view:repositoryView,loading:repositoryLoading,pendingPair:repositoryPendingPair,pendingSelection:repositoryPendingSelection,error:repositoryError,diagnostic:lastDiagnostic})',sandbox));
  return {get,requests,renders,reported,shellCalls,sandbox,document,state,addControl(id,container="repository-review"){const spec={container};controls.set(id,spec);const node=get(id);node.parent=get(container);get(container).children.push(node);return spec;},latest:()=>renders.at(-1).options,
    compare:data=>sandbox.loadRepositoryComparison(data.base.commit,data.head.commit),file:value=>sandbox.loadRepositoryChangeFile(value),
    read:code=>vm.runInContext(code,sandbox),status:()=>get("repository-comparison-status").textContent,
    preserved:()=>JSON.parse(vm.runInContext('JSON.stringify({current,instance,workbench,modelView,sourceRecord})',sandbox)),
    async accept(data){const pending=this.compare(data);requests.at(-1).resolve(data);assert.equal(await pending,true);},
    async acceptFile(data,selected){const pending=this.file(selected);requests.at(-1).resolve(detail(data,selected));assert.equal(await pending,true);}
  };
}
async function wrongPairOracle(code=source){const h=harness(code),requested=fixture(),pending=h.compare(requested);h.requests[0].resolve(fixture("c","d","wrong-pair"));assert.equal(await pending,false);assert.equal(h.state().comparison,null);assert.equal(h.state().error.code,"CHANGE_SUBJECT_MISMATCH");}
async function reverseOracle(code=source,lateFailure=false){
  const h=harness(code),a=fixture(),b=fixture("c","d","comparison-B"),first=h.compare(a),second=h.compare(b);
  h.requests[1].resolve(b);assert.equal(await second,true);const accepted=h.state(),notice=h.status();
  if(lateFailure)h.requests[0].reject(new ApiError("OLD_FAILURE","old request failed"));else h.requests[0].resolve(a);
  assert.equal(await first,false);assert.deepEqual(h.state(),accepted);assert.equal(h.status(),notice);assert.equal(h.reported.length,0);
}

test("a well-formed comparison for a different requested commit pair is refused",()=>wrongPairOracle());
test("reverse comparison completion and late errors cannot replace newer data, notice or loading state",async()=>{await reverseOracle();await reverseOracle(source,true);});

test("editing commit fields invalidates pending success and failure without discarding retained data",async()=>{
  for(const rejects of [false,true]){const h=harness(),old=fixture(),next=fixture("c","d","next");await h.accept(old);const pending=h.compare(next);h.get("repository-head").listeners.input();const draft=h.state(),notice=h.status();
    if(rejects)h.requests.at(-1).reject(new ApiError("OLD_FAILURE","superseded"));else h.requests.at(-1).resolve(next);
    assert.equal(await pending,false);assert.deepEqual(h.state(),draft);assert.equal(h.status(),notice);assert.match(notice,/Commit fields changed/);assert.match(notice,/retained immutable pair/);assert.equal(h.latest().comparison.comparison_id,old.comparison_id);assert.equal(h.get("repository-compare-form").attributes["aria-busy"],"false");}
});

test("invalid submission cancels the earlier request and retains precise validation and focus",async()=>{
  const h=harness(),data=fixture(),pending=h.compare(data);assert.equal(await h.sandbox.loadRepositoryComparison("main",data.head.commit),false);
  assert.equal(h.requests.length,1);assert.equal(h.get("repository-base").attributes["aria-invalid"],"true");assert.equal(h.sandbox.focused,"repository-base");const refused=h.state();
  h.requests[0].resolve(data);assert.equal(await pending,false);assert.deepEqual(h.state(),refused);assert.equal(h.state().error.code,"CHANGE_REVISION_INVALID");
});

test("loading and failed new comparisons retain the old pair and file with explicit retained labels",async()=>{
  const h=harness(),old=fixture(),selected=selection(old);await h.accept(old);await h.acceptFile(old,selected);const next=fixture("c","d","next"),pending=h.compare(next);
  assert.equal(h.latest().comparison.comparison_id,old.comparison_id);assert.equal(h.latest().selection.path,selected.path);assert.equal(h.latest().loading,"comparison");assert.equal(h.latest().onSelectFile,undefined);assert.match(h.status(),/not the pending or refused result/);
  h.requests.at(-1).reject(new ApiError("READ_FAILED","exact comparison failure",{retry:true}));assert.equal(await pending,false);assert.equal(h.state().file.path,selected.path);assert.equal(h.latest().error.code,"READ_FAILED");assert.deepEqual(clone(h.latest().error.details),{retry:true});assert.match(h.status(),/retained immutable pair/);assert.equal(h.latest().loading,null);
});

test("file and same-file symbol races keep only the latest selection including late rejections",async()=>{
  for(const sameFile of [false,true])for(const rejects of [false,true]){
    const h=harness(),data=fixture();await h.accept(data);const x=selection(data,0,sameFile?0:null),y=selection(data,sameFile?0:1,sameFile?1:null),first=h.file(x),second=h.file(y);
    h.requests[2].resolve(detail(data,y));assert.equal(await second,true);const before=h.state(),notice=h.status();
    if(rejects)h.requests[1].reject(new ApiError("OLD_FILE","superseded file"));else h.requests[1].resolve(detail(data,x));
    assert.equal(await first,false);assert.deepEqual(h.state(),before);assert.equal(h.status(),notice);assert.equal(h.state().selection.reference,y.reference);assert.equal(h.reported.length,0);
  }
});

test("a refused file selection invalidates an earlier pending detail before it can clear the refusal",async()=>{
  const h=harness(),data=fixture();await h.accept(data);const selected=selection(data),pending=h.file(selected);assert.equal(await h.file({...selected,path:"not-in-inventory.py"}),false);assert.equal(h.requests.length,2);const refused=h.state();
  h.requests[1].resolve(detail(data,selected));assert.equal(await pending,false);assert.deepEqual(h.state(),refused);assert.equal(h.state().error.code,"CHANGE_REFERENCE_DENIED");assert.equal(h.state().loading,null);
});

test("comparison ID drift or changed historical identities refuse detail and preserve the last valid file",async()=>{
  const mutations=[data=>data.comparison_id="changed-policy",data=>data.base.changed_source_hash="sha256:"+sha("0"),data=>data.after.file_sha256=sha("0"),data=>data.selected_reference="repo://wrong#ref"];
  for(const mutate of mutations){const h=harness(),data=fixture(),old=selection(data),next=selection(data,1);await h.accept(data);await h.acceptFile(data,old);const pending=h.file(next),response=detail(data,next);mutate(response);h.requests.at(-1).resolve(response);assert.equal(await pending,false);assert.equal(h.state().file.path,old.path);assert.equal(h.state().selection.path,old.path);assert.equal(h.state().error.code,"CHANGE_SUBJECT_MISMATCH");assert.match(h.status(),/retained immutable pair/);}
});

test("starting another comparison cancels pending file work even while the old pair is retained",async()=>{
  const h=harness(),a=fixture(),b=fixture("c","d","next");await h.accept(a);const selected=selection(a),file=h.file(selected),comparison=h.compare(b);
  h.requests[1].resolve(detail(a,selected));assert.equal(await file,false);assert.equal(h.state().file,null);assert.equal(h.state().loading,"comparison");assert.equal(h.state().comparison.comparison_id,a.comparison_id);
  h.requests[2].resolve(b);assert.equal(await comparison,true);assert.equal(h.state().comparison.comparison_id,b.comparison_id);assert.equal(h.state().selection,null);
});

test("callbacks from destroyed renders cannot select files or change the current view",async()=>{
  const h=harness(),data=fixture();await h.accept(data);const old=h.latest(),selected=selection(data);h.sandbox.renderRepositoryReview();const count=h.requests.length;
  assert.equal(await old.onSelectFile(selected),false);old.onViewChange("after",selected);assert.equal(h.requests.length,count);assert.equal(h.state().view,"diff");
  await h.acceptFile(data,selected);const previous=h.latest();h.sandbox.renderRepositoryReview();previous.onViewChange("impact",selected);assert.equal(h.state().view,"diff");h.latest().onViewChange("before",selected);assert.equal(h.state().view,"before");assert.ok(h.renders.slice(0,-1).every(render=>render.destroyed));
});

test("unconfigured and unavailable envelopes remain failures and never become empty successful comparisons",async()=>{
  for(const status of ["unconfigured","unavailable"]){const h=harness(),data=fixture(),pending=h.compare(data);h.requests[0].resolve({schema:"eija.repository.change.v1",status,read_only:true,reason:"Exact capture limitation"});assert.equal(await pending,false);assert.equal(h.state().comparison,null);assert.equal(h.state().error.details.status,status);assert.match(h.status(),/Exact capture limitation/);assert.notEqual(h.get("repository-comparison-status").dataset.status,"captured");}
  const h=harness(),empty=fixture();empty.files=[];empty.coverage={changed_paths_total:0,displayed_paths:0,excluded_by_reason:{},inventory_reconciles:true};await h.accept(empty);assert.equal(h.state().comparison.files.length,0);assert.equal(h.state().error,null);assert.equal(h.get("repository-comparison-status").dataset.status,"captured");
});

test("file unavailable envelopes retain the prior file and its exact subject",async()=>{
  const h=harness(),data=fixture(),selected=selection(data);await h.accept(data);await h.acceptFile(data,selected);const pending=h.file(selection(data,1));h.requests.at(-1).resolve({schema:"eija.repository.change.v1",status:"unavailable",reason:"Capture changed; retry"});assert.equal(await pending,false);assert.equal(h.state().selection.path,selected.path);assert.equal(h.state().error.code,"REPOSITORY_CHANGE_FILE_UNAVAILABLE");assert.match(h.status(),/Capture changed; retry/);
});

test("requests use only historical GET routes with exact encoded file identity and no live snapshot substitution",async()=>{
  const h=harness(),data=fixture();await h.accept(data);await h.acceptFile(data,selection(data));await h.acceptFile(data,selection(data,0,0));
  const urls=h.requests.map(request=>new URL(request.route,"http://fixture.invalid/"));assert.deepEqual(urls.map(url=>url.pathname),["/repository/change","/repository/change/file","/repository/change/file"]);
  for(const url of urls){assert.equal(url.searchParams.get("base"),data.base.commit);assert.equal(url.searchParams.get("head"),data.head.commit);assert.equal(url.searchParams.has("expected_source_hash"),false);}
  assert.equal(urls[1].searchParams.get("path"),data.files[0].path);assert.equal(urls[1].searchParams.has("reference"),false);assert.equal(urls[2].searchParams.get("reference"),data.files[0].symbols[0].reference);assert.ok(h.requests.every(request=>request.args.length===0));assert.equal(h.latest().onOpenSide,undefined,"historical views must not be handed to the live-source reader");
});

test("review success and transport failures preserve case, runtime, live source and unsent edits",async()=>{
  const h=harness(),before=h.preserved(),data=fixture();await h.accept(data);await h.acceptFile(data,selection(data));const pending=h.file(selection(data,1));h.requests.at(-1).reject(new ApiError("FILE_FAILED","retry"));assert.equal(await pending,false);
  assert.deepEqual(h.preserved(),before);assert.equal(h.get("q-authority").value,"unsent owner answer");assert.equal(h.get("intent").value,"unsent intent");assert.deepEqual(h.shellCalls,[]);
});

test("successful retry clears only its own transport diagnostic and retains newer unrelated errors",async()=>{
  for(const unrelated of [false,true]){const h=harness(),data=fixture(),failed=h.compare(data);h.requests[0].reject(new ApiError("COMPARE_FAILED","first failure"));assert.equal(await failed,false);assert.equal(h.state().diagnostic.code,"COMPARE_FAILED");
    const retry=h.compare(data);if(unrelated)h.read('lastDiagnostic={code:"MODEL_BLOCKER",message:"Keep this newer blocker"}');h.requests[1].resolve(data);assert.equal(await retry,true);
    assert.equal(h.state().diagnostic?.code||null,unrelated?"MODEL_BLOCKER":null);assert.equal(h.state().error,null);}
});

test("request-pair oracle rejects removing the actual requested-identity guard",async()=>{
  const guard="!repositoryPairMatches(data,pair)||";assert.equal(source.split(guard).length,2);await assert.rejects(()=>wrongPairOracle(source.replace(guard,"")),assert.AssertionError);
});

test("reverse-completion oracle rejects removing actual async freshness guards",async()=>{
  const guard="if(!active())return false;";assert.ok(source.split(guard).length>=5);await assert.rejects(()=>reverseOracle(source.replaceAll(guard,"")),assert.AssertionError);
});


test("same-file symbol disclosure survives pending and accepted symbol reads and resets for a new file",async()=>{
  const h=harness(),data=fixture(),whole=selection(data);await h.accept(data);await h.acceptFile(data,whole);
  h.renders.at(-1).symbolsOpen=true;h.renders.at(-1).symbolsFilter="all";
  const symbol=selection(data,0,0),pending=h.file(symbol);assert.equal(h.latest().symbolsOpen,true,"pending same-file read retains expanded references");assert.equal(h.latest().symbolsFilter,"all");
  h.requests.at(-1).resolve(detail(data,symbol));assert.equal(await pending,true);assert.equal(h.latest().symbolsOpen,true,"accepted symbol read retains expanded references");assert.equal(h.latest().symbolsFilter,"all");
  const next=selection(data,1),nextRead=h.file(next);assert.equal(h.latest().symbolsOpen,true,"old file remains expanded while new file is pending");assert.equal(h.latest().symbolsFilter,"all");
  h.requests.at(-1).resolve(detail(data,next));assert.equal(await nextRead,true);assert.equal(h.latest().symbolsOpen,false,"new file starts with its own collapsed disclosure");assert.equal(h.latest().symbolsFilter,"changed");
});


test("rerender restores an equivalent in-review control and never steals focus moved outside during a request",async()=>{
  const h=harness(),data=fixture();await h.accept(data);await h.acceptFile(data,selection(data));h.addControl("review-symbol-control");const old=h.get("review-symbol-control");old.focus();
  h.sandbox.renderRepositoryReview();assert.equal(old.isConnected,false);assert.notEqual(h.document.activeElement,old);assert.equal(h.document.activeElement,h.get("review-symbol-control"));
  const selected=selection(data,0,0),pending=h.file(selected);h.get("q-authority").focus();const outside=h.document.activeElement;
  h.requests.at(-1).resolve(detail(data,selected));assert.equal(await pending,true);assert.equal(h.document.activeElement,outside);assert.equal(h.get("q-authority").value,"unsent owner answer");
});

test("hidden or disabled replacement controls use the visible summary when captured status is quiet",async()=>{
  for(const attribute of ["hidden","disabled"]){const h=harness(),data=fixture();await h.accept(data);const spec=h.addControl("review-control","repository-change-navigator");h.get("review-control").focus();spec[attribute]=true;h.sandbox.renderRepositoryReview();assert.equal(h.document.activeElement,h.get("repository-revisions-summary"));}
  const h=harness(),data=fixture();await h.accept(data);const spec=h.addControl("review-control");h.get("review-control").focus();spec.hidden=true;h.get("repository-comparison-status").hidden=true;h.get("repository-revisions-summary").hidden=true;h.sandbox.renderRepositoryReview();assert.equal(h.document.activeElement,h.document.body);
});

test("Show changed files is disabled without an available nonempty inventory",async()=>{
  const h=harness();assert.equal(h.get("repository-show-files").disabled,true);const data=fixture();await h.accept(data);assert.equal(h.get("repository-show-files").disabled,false);
  const empty=fixture("c","d","empty");empty.files=[];empty.coverage={changed_paths_total:0,displayed_paths:0,excluded_by_reason:{},inventory_reconciles:true};await h.accept(empty);assert.equal(h.get("repository-show-files").disabled,true);
});


test("actual task navigator keeps Code changes and model Changes roots distinct and respects Domain pin",()=>{
  const nodes=new Map(),writes=[],get=id=>{if(!nodes.has(id))nodes.set(id,{hidden:false,dataset:{},value:""});return nodes.get(id);};
  const context={$:get,workbench:{},navigatorMode:"task",tab:"review",EijaTree:{setVisible:(root,visible)=>root.hidden=!visible},sessionStorage:{setItem:(key,value)=>writes.push([key,value])}};
  const start=app.indexOf("function renderNavigator()"),finish=app.indexOf("function fillStates(",start);assert.ok(start>=0&&finish>start);vm.createContext(context);vm.runInContext(app.slice(start,finish),context);
  for(const tab of ["review","repository-changes","review"]){context.tab=tab;context.renderNavigator();assert.equal(get("task-navigator").hidden,tab!=="review");assert.equal(get("repository-change-navigator").hidden,tab!=="repository-changes");assert.equal(get("domain-tree").hidden,true);assert.equal(get("navigator-context").hidden,true);}
  get("navigator-mode").onchange({target:{value:"domain"}});for(const tab of ["repository-changes","review"]){context.tab=tab;context.renderNavigator();assert.equal(get("domain-tree").hidden,false);assert.equal(get("task-navigator").hidden,true);assert.equal(get("repository-change-navigator").hidden,true);}
  assert.deepEqual(writes,[["eija-ui-navigator","domain"]]);
});

test("six native primary destinations keep Changes at work-area level and comparison tabs keep local navigation",()=>{
  const html=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/index.html"),"utf8"),mainMarkup=html.match(/<nav\b[^>]*aria-label="Work views"[^>]*>[\s\S]*?<\/nav>/)?.[0];assert.ok(mainMarkup);
  const attributes=tag=>Object.fromEntries([...tag.matchAll(/([\w-]+)="([^"]*)"/g)].map(match=>[match[1],match[2]]));
  const primaryTags=[...mainMarkup.matchAll(/<button\b[^>]*>/g)].map(match=>attributes(match[0]));
  assert.deepEqual(primaryTags.map(tag=>tag["data-tab"]),["model","code","change","review","try","evidence"]);
  assert.equal(attributes(mainMarkup.match(/<nav\b[^>]*>/)[0]).role,undefined);
  for(const tag of primaryTags){assert.equal(tag.role,undefined);assert.equal(tag["aria-selected"],undefined);assert.ok(tag.tabindex===undefined||tag.tabindex==="0");assert.equal(tag["aria-current"],tag["data-tab"]==="model"?"page":undefined);}
  assert.equal(primaryTags.find(tag=>tag["data-tab"]==="review")["aria-controls"],"comparison-workspace");
  const localMarkup=html.match(/<nav\b[^>]*id="comparison-tabs"[^>]*>[\s\S]*?<\/nav>/)?.[0];assert.ok(localMarkup);
  assert.equal(attributes(localMarkup.match(/<nav\b[^>]*>/)[0]).role,"tablist");
  const localTags=[...localMarkup.matchAll(/<button\b[^>]*>/g)].map(match=>attributes(match[0]));
  assert.deepEqual(localTags.map(tag=>tag["data-comparison-tab"]),["review","repository-changes"]);
  for(const tag of localTags){const selected=tag["data-comparison-tab"]==="review";assert.equal(tag.role,"tab");assert.equal(tag["aria-controls"],tag["data-comparison-tab"]);assert.equal(tag["aria-selected"],String(selected));assert.equal(tag.tabindex,selected?"0":"-1");}
  let handler,localHandler,focused=null;const opened=[];
  const primary=primaryTags.map(tag=>({dataset:{tab:tag["data-tab"]},closest:selector=>{assert.equal(selector,'[role="tablist"]');return null;},focus(){focused=this;}}));
  const comparison=localTags.map(tag=>({dataset:{comparisonTab:tag["data-comparison-tab"]},focus(){focused=this;}}));
  const local={querySelectorAll:selector=>{assert.equal(selector,"[data-comparison-tab]");return comparison;},addEventListener:(name,fn)=>{assert.equal(name,"keydown");localHandler=fn;}};
  const context={document:{querySelector:selector=>{assert.equal(selector,".editor-navigation");return {addEventListener:(name,fn)=>{assert.equal(name,"keydown");handler=fn;}};},querySelectorAll:selector=>{assert.equal(selector,"[data-comparison-tab]");return comparison;}},$:id=>{assert.equal(id,"comparison-tabs");return local;},switchTab:tab=>opened.push(tab),openWorkTab:tab=>opened.push(tab)};
  const start=app.indexOf('document.querySelector(".editor-navigation").addEventListener("keydown"'),finish=app.indexOf("\nconst paletteCommands =",start);assert.ok(start>=0&&finish>start);vm.createContext(context);vm.runInContext(app.slice(start,finish),context);
  const press=(listener,target,key)=>{let prevented=false;listener({target,key,preventDefault(){prevented=true;}});return prevented;};
  for(const target of primary)for(const key of ["ArrowLeft","ArrowRight","Home","End","Tab","Enter"," "]){target.focus();const count=opened.length;assert.equal(press(handler,target,key),false);assert.equal(opened.length,count);assert.equal(focused,target);}
  for(const [name,key,expected]of [["review","ArrowLeft","repository-changes"],["review","ArrowRight","repository-changes"],["repository-changes","ArrowLeft","review"],["repository-changes","ArrowRight","review"],["repository-changes","Home","review"],["review","End","repository-changes"]]){const count=opened.length;assert.equal(press(localHandler,comparison.find(button=>button.dataset.comparisonTab===name),key),true);assert.equal(opened.length,count+1);assert.equal(opened.at(-1),expected);assert.equal(focused,comparison.find(button=>button.dataset.comparisonTab===expected));}
  const count=opened.length;assert.equal(press(localHandler,primary[0],"ArrowRight"),false);assert.equal(press(localHandler,comparison[0],"Tab"),false);assert.equal(opened.length,count);
  for(const button of comparison){button.onclick();assert.equal(opened.at(-1),button.dataset.comparisonTab);}
});


test("Show changed files focuses the selected second file before falling back to the first file",async()=>{
  const h=harness(),data=fixture();await h.accept(data);await h.acceptFile(data,selection(data,1));
  h.addControl("review-file-first","repository-change-navigator");h.addControl("review-file-selected","repository-change-navigator");const first=h.get("review-file-first"),selected=h.get("review-file-selected"),queries=[];let hasSelected=true;
  h.get("repository-change-navigator").querySelector=selector=>{queries.push(selector);if(selector==='button[aria-pressed="true"]')return hasSelected?selected:null;if(selector==="button"||selector.includes(","))return first;throw Error("Unexpected selector "+selector);};
  const count=h.requests.length;h.get("repository-show-files").onclick();assert.equal(h.document.activeElement,selected);assert.deepEqual(queries,['button[aria-pressed="true"]']);assert.equal(h.read("navigatorMode"),"task");assert.equal(h.requests.length,count);
  queries.length=0;hasSelected=false;h.get("repository-show-files").onclick();assert.equal(h.document.activeElement,first);assert.deepEqual(queries,['button[aria-pressed="true"]',"button"]);assert.deepEqual(h.shellCalls,["navigator",["reveal","explorer"],"navigator",["reveal","explorer"]]);
});


test("successful repository retry clears its own notice text and preserves unrelated newer notice or diagnostic",async()=>{
  for(const kind of ["own","own-with-codes","new-notice","new-diagnostic"]){
    const h=harness(),data=fixture(),codes=kind==="own-with-codes"?["RULE_A","RULE_B"]:[],pending=h.compare(data);
    h.requests[0].reject(new ApiError("COMPARE_FAILED","comparison failed",{codes}));assert.equal(await pending,false);
    const ownText="comparison failed"+(codes.length?" · RULE_A; RULE_B":"");assert.equal(h.get("notice").textContent,ownText);
    const retry=h.compare(data);
    if(kind==="new-notice")h.sandbox.notice("Draft saved elsewhere");
    if(kind==="new-diagnostic")h.read('lastDiagnostic={code:"MODEL_BLOCKER",message:"Keep this separate failure"}');
    h.requests[1].resolve(data);assert.equal(await retry,true);
    assert.equal(h.get("notice").textContent,kind==="new-notice"?"Draft saved elsewhere":kind==="new-diagnostic"?ownText:"");
    assert.equal(h.state().diagnostic?.code||null,kind==="new-diagnostic"?"MODEL_BLOCKER":null);
  }
});


function assertAcceptedRevisions(h,data){
  assert.equal(h.get("repository-loaded-base").textContent,data.base.commit);assert.equal(h.get("repository-loaded-head").textContent,data.head.commit);
  const node=h.get("repository-loaded-pair");assert.match(node.textContent,new RegExp(data.base.commit.slice(0,7)));assert.match(node.textContent,new RegExp(data.head.commit.slice(0,7)));
  assert.ok(!node.textContent.includes(data.base.commit),"compact pair label must not expand to full object IDs");
  for(const description of [node.title||node.attributes.title||"",node.attributes["aria-label"]||""])assert.ok(description.includes(data.base.commit)&&description.includes(data.head.commit),"title and accessible label both retain full accepted identities");
  assert.equal(h.get("repository-pair-details").hidden,false);
}

test("revision editor is native initially-open details and initial failure never collapses it",async()=>{
  const html=fs.readFileSync(path.join(__dirname,"../../src/eija_studio/resources/web/index.html"),"utf8"),details=html.match(/<details\b(?=[^>]*\bid="repository-revisions")[^>]*>/)?.[0];assert.ok(details);assert.match(details,/\bopen(?:\s|>|=)/);assert.match(html,/<summary\b[^>]*id="repository-revisions-summary"[^>]*>/);assert.match(html,/Change revisions/);
  const h=harness(),data=fixture();assert.equal(h.get("repository-revisions").open,true);const pending=h.compare(data);h.requests.at(-1).reject(new ApiError("READ_FAILED","first comparison unavailable"));assert.equal(await pending,false);assert.equal(h.get("repository-revisions").open,true);assert.equal(h.state().comparison,null);assert.ok(!h.get("repository-loaded-pair").textContent.includes(data.base.commit.slice(0,7)));
});

test("only the first accepted comparison automatically collapses revisions and moves in-editor focus to its summary",async()=>{
  const h=harness(),data=fixture();h.get("repository-base").value=data.base.commit;h.get("repository-head").value=data.head.commit;h.get("repository-base").focus();await h.accept(data);
  assert.equal(h.get("repository-revisions").open,false);assert.equal(h.document.activeElement,h.get("repository-revisions-summary"));assert.ok(h.document.activeElement.getClientRects().length);assertAcceptedRevisions(h,data);
  for(const next of [data,fixture("c","d","second-pair")]){h.get("repository-revisions").open=true;await h.accept(next);assert.equal(h.get("repository-revisions").open,true,"a deliberate reopening survives later accepted comparisons");assertAcceptedRevisions(h,next);}
  h.get("repository-revisions").open=false;await h.accept(fixture("e","f","third-pair"));assert.equal(h.get("repository-revisions").open,false,"a deliberate closure also survives later success");
});

test("pending requests retain disclosure preference and accepted identities distinct from draft revisions",async()=>{
  for(const open of [false,true]){const h=harness(),old=fixture(),next=fixture("c","d","next");await h.accept(old);h.get("repository-revisions").open=open;
    h.get("repository-base").value=next.base.commit;h.get("repository-head").value=next.head.commit;const pending=h.compare(next);
    assert.equal(h.get("repository-revisions").open,open);assertAcceptedRevisions(h,old);assert.equal(h.get("repository-base").value,next.base.commit);assert.equal(h.get("repository-head").value,next.head.commit);assert.match(h.status(),new RegExp(next.base.commit.slice(0,12)));assert.match(h.status(),new RegExp(old.base.commit.slice(0,12)));assert.match(h.status(),/retained immutable pair/);
    h.requests.at(-1).resolve(next);assert.equal(await pending,true);assert.equal(h.get("repository-revisions").open,open);assertAcceptedRevisions(h,next);
  }
});

test("draft edits, invalid revisions and file failures reopen details without relabeling the accepted pair",async()=>{
  const h=harness(),old=fixture();await h.accept(old);h.get("repository-base").value="draft-ref";h.get("repository-base").listeners.input();assert.equal(h.get("repository-revisions").open,true);assertAcceptedRevisions(h,old);assert.equal(h.get("repository-base").value,"draft-ref");
  h.get("repository-revisions").open=false;assert.equal(await h.sandbox.loadRepositoryComparison("main",old.head.commit),false);assert.equal(h.get("repository-revisions").open,true);assertAcceptedRevisions(h,old);assert.equal(h.document.activeElement,h.get("repository-base"));
  h.get("repository-revisions").open=false;const pending=h.file(selection(old));h.requests.at(-1).reject(new ApiError("FILE_UNAVAILABLE","selected historical file unavailable"));assert.equal(await pending,false);assert.equal(h.get("repository-revisions").open,true);assertAcceptedRevisions(h,old);assert.equal(h.get("repository-base").value,"draft-ref");
});

test("first accepted comparison never steals focus moved outside revision details while awaiting the response",async()=>{
  const h=harness(),data=fixture();h.get("repository-head").focus();const pending=h.compare(data);h.get("q-authority").focus();const outside=h.document.activeElement;
  h.requests.at(-1).resolve(data);assert.equal(await pending,true);assert.equal(h.get("repository-revisions").open,false);assert.equal(h.document.activeElement,outside);assert.equal(h.get("q-authority").value,"unsent owner answer");assertAcceptedRevisions(h,data);
});

test("stale success after a draft edit cannot collapse revisions or update accepted identity",async()=>{
  const h=harness(),old=fixture(),next=fixture("c","d","next");await h.accept(old);const pending=h.compare(next);h.get("repository-head").value="new unsent revision";h.get("repository-head").listeners.input();
  h.requests.at(-1).resolve(next);assert.equal(await pending,false);assert.equal(h.get("repository-revisions").open,true);assertAcceptedRevisions(h,old);assert.equal(h.get("repository-head").value,"new unsent revision");assert.match(h.status(),/Commit fields changed/);
});


test("manual-disclosure oracle rejects removing the actual first-comparison-only collapse guard",async()=>{
  const guard="if(initialComparison)closeInitialRepositoryRevisions();";assert.equal(source.split(guard).length,2);
  const mutated=source.replace(guard,"closeInitialRepositoryRevisions();");
  await assert.rejects(async()=>{const h=harness(mutated),data=fixture();await h.accept(data);h.get("repository-revisions").open=true;await h.accept(data);assert.equal(h.get("repository-revisions").open,true,"later success must preserve deliberate reopening");},assert.AssertionError);
});


function assertRepositoryStatus(h,state,quiet){
  const node=h.get("repository-comparison-status");assert.equal(node.dataset.status,state);assert.equal(node.classList.contains("sr-only"),quiet);assert.equal(node.hidden,false);assert.notEqual(node.attributes["aria-hidden"],"true");assert.equal(node.attributes.role,"status");assert.equal(node.attributes["aria-live"],"polite");assert.ok(node.textContent.length>0,"live-region text must remain available when visually quiet");
}

test("loaded toolbar keeps the accepted pair inside native Change revisions summary and retains the full editor",()=>{
  const summary=markup.match(/<summary\b[^>]*id="repository-revisions-summary"[^>]*>([\s\S]*?)<\/summary>/)?.[1];assert.ok(summary);assert.match(summary,/Change revisions/);assert.match(summary,/id="repository-loaded-pair"/);
  for(const id of ["repository-base","repository-head","repository-loaded-base","repository-loaded-head","repository-show-files","repository-introduction"])assert.equal((markup.match(new RegExp('id="'+id+'"',"g"))||[]).length,1,id+" retained exactly once");
  const h=harness();assert.equal(h.get("repository-introduction").hidden,false);assert.equal(h.get("repository-comparison-status").classList.contains("sr-only"),false);
});

test("accepted success becomes quiet but loading, failure and retry remain truthful visible states",async()=>{
  const h=harness(),old=fixture(),next=fixture("c","d","new-pair");await h.accept(old);assert.equal(h.get("repository-introduction").hidden,true);assertRepositoryStatus(h,"captured",true);assertAcceptedRevisions(h,old);
  h.get("repository-base").value=next.base.commit;h.get("repository-head").value=next.head.commit;const pending=h.compare(next);assertRepositoryStatus(h,"loading",false);assertAcceptedRevisions(h,old);assert.match(h.status(),/retained immutable pair/);
  h.requests.at(-1).reject(new ApiError("COMPARE_UNAVAILABLE","Exact capture refusal",{reason:"unreadable object",retry:true}));assert.equal(await pending,false);assertRepositoryStatus(h,"unavailable",false);assert.match(h.status(),/Exact capture refusal/);assert.deepEqual(clone(h.latest().error.details),{reason:"unreadable object",retry:true});assertAcceptedRevisions(h,old);assert.equal(h.get("repository-introduction").hidden,true);
  const retry=h.compare(next);assertRepositoryStatus(h,"loading",false);h.requests.at(-1).resolve(next);assert.equal(await retry,true);assertRepositoryStatus(h,"captured",true);assertAcceptedRevisions(h,next);assert.equal(h.get("repository-base").value,next.base.commit);assert.equal(h.get("repository-head").value,next.head.commit);
});

test("draft, invalid revision and unavailable file statuses stay visible while retaining accepted identity",async()=>{
  const h=harness(),data=fixture();await h.accept(data);h.get("repository-base").value="draft base";h.get("repository-base").listeners.input();assertRepositoryStatus(h,"draft",false);assertAcceptedRevisions(h,data);
  assert.equal(await h.sandbox.loadRepositoryComparison("invalid",data.head.commit),false);assertRepositoryStatus(h,"invalid",false);assertAcceptedRevisions(h,data);
  const pending=h.file(selection(data));assertRepositoryStatus(h,"loading-file",false);h.requests.at(-1).reject(new ApiError("FILE_FAILED","Exact historical file failure"));assert.equal(await pending,false);assertRepositoryStatus(h,"unavailable-file",false);assert.match(h.status(),/Exact historical file failure/);assertAcceptedRevisions(h,data);assert.equal(h.get("repository-base").value,"draft base");
  await h.acceptFile(data,selection(data));assertRepositoryStatus(h,"captured-file",true);assertAcceptedRevisions(h,data);
});

test("unconfigured or unavailable first comparisons keep introduction and failure status visible",async()=>{
  for(const status of ["unconfigured","unavailable"]){const h=harness(),data=fixture(),pending=h.compare(data);h.requests.at(-1).resolve({schema:"eija.repository.change.v1",status,read_only:true,reason:"Explicit capture limitation"});assert.equal(await pending,false);assert.equal(h.get("repository-introduction").hidden,false);assertRepositoryStatus(h,"unavailable",false);assert.match(h.status(),/Explicit capture limitation/);assert.equal(h.state().comparison,null);}
});

test("quieting a focused successful status relocates to visible summary and does not steal outside focus",async()=>{
  for(const outside of [false,true]){const h=harness(),data=fixture();await h.accept(data);const pending=h.file(selection(data));assertRepositoryStatus(h,"loading-file",false);h.get("repository-comparison-status").focus();if(outside)h.get("q-authority").focus();const prior=h.document.activeElement;
    h.requests.at(-1).resolve(detail(data,selection(data)));assert.equal(await pending,true);assertRepositoryStatus(h,"captured-file",true);assert.ok(h.get("repository-comparison-status").getClientRects().length,"sr-only text can still have layout rectangles");assert.equal(h.document.activeElement,outside?prior:h.get("repository-revisions-summary"));assert.ok(h.document.activeElement.getClientRects().length);assert.equal(h.document.activeElement.classList.contains("sr-only"),false);}
});

test("failed replacement of a focused control prefers status when loading makes it visible",async()=>{
  const h=harness(),data=fixture();await h.accept(data);const spec=h.addControl("review-pending-control");h.get("review-pending-control").focus();spec.disabled=true;const pending=h.file(selection(data));assertRepositoryStatus(h,"loading-file",false);assert.equal(h.document.activeElement,h.get("repository-comparison-status"));
  h.requests.at(-1).reject(new ApiError("FILE_FAILED","Cannot read file"));assert.equal(await pending,false);assertRepositoryStatus(h,"unavailable-file",false);assert.equal(h.document.activeElement,h.get("repository-comparison-status"));
});


test("visibility oracle rejects hiding pending status merely because an older comparison exists",async()=>{
  const guard='&&["captured","captured-file"].includes(state)';assert.equal(source.split(guard).length,2);
  await assert.rejects(async()=>{const h=harness(source.replace(guard,"")),old=fixture(),next=fixture("c","d","next");await h.accept(old);const pending=h.compare(next),quietWhilePending=h.get("repository-comparison-status").classList.contains("sr-only");h.requests.at(-1).resolve(next);await pending;assert.equal(quietWhilePending,false,"pending comparison feedback must stay visible despite retained accepted data");},assert.AssertionError);
});
