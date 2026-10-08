"use strict";
// Actual DOM renderer and immutable-subject checks; no browser or human acceptance claim.
const {test}=require("node:test"),assert=require("node:assert/strict"),path=require("node:path");
class Element{
  constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.attributes={};this.listeners={};this.ownText="";this.className="";this.classList={add:value=>{this.className+=(this.className?" ":"")+value;}};}
  set textContent(value){this.ownText=String(value);this.children=[];}
  get textContent(){return this.ownText+this.children.map(child=>child.textContent).join("");}
  append(...nodes){for(const node of nodes){node.remove();node.parent=this;this.children.push(node);}}
  replaceChildren(...nodes){for(const child of this.children)child.parent=null;this.children=[];this.ownText="";this.append(...nodes);}
  remove(){if(this.parent){this.parent.children=this.parent.children.filter(child=>child!==this);this.parent=null;}}
  setAttribute(key,value){this.attributes[key]=String(value);}
  getAttribute(key){return this.attributes[key];}
  addEventListener(kind,callback){this.listeners[kind]=callback;}
  focus(){document.activeElement=this;}
}
global.document={createElement:tag=>new Element(tag)};
const review=require(process.env.EIJA_REPOSITORY_REVIEW_MODULE||path.join(__dirname,"../../src/eija_studio/resources/web/repository-review.js"));
const clone=value=>JSON.parse(JSON.stringify(value)),freeze=value=>{if(value&&typeof value==="object"){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
const all=node=>[node,...node.children.flatMap(all)],find=(root,predicate)=>all(root).find(predicate);
const objectId=char=>char.repeat(40),sha=char=>char.repeat(64),captured=char=>({commit:objectId(char),tree:objectId(char==="a"?"c":"d"),changed_source_hash:"sha256:"+sha(char)});
function fixture(){
  const ref="repo://src/%E9%9B%AA%23.py#run",filePath="src/雪#.py";
  const before={status:"captured",blob:objectId("1"),mode:"100644",file_sha256:sha("1"),byte_length:48};
  const after={status:"captured",blob:objectId("2"),mode:"100644",file_sha256:sha("2"),byte_length:61};
  const old={reference:ref,kind:"function",syntax_digest:"ast-old",start_line:10,end_line:11},next={...old,syntax_digest:"ast-new",start_line:20,end_line:22};
  const row={path:filePath,status:"modified",before,after,extraction:{before:{status:"EXTRACTED",method:"python_ast_ast-v2",symbols:[old],gaps:[]},after:{status:"PARTIAL",method:"python_ast_ast-v2",symbols:[next],gaps:[{reason:"UNPARSEABLE",message:"One definition was not extracted"}]}},symbols:[{reference:ref,kind:"function",status:"changed",before:old,after:next}]};
  const comparison={schema:"eija.repository.change.v1",status:"partial",read_only:true,comparison_id:"comparison-1",base:captured("a"),head:captured("b"),files:[row],coverage:{changed_paths_total:2,displayed_paths:1,excluded_by_reason:{private_path:1},inventory_reconciles:true},capture_policy:{id:"changed-only",ignore:"current configured checkout policy"},pack:{id:"sample",digest:"pack-1"},tools:{git_version:"git fixture",python_version:"3.fixture"},scope:{capture:"Changed blobs only",behavior:"NOT_RUN by source comparison",semantic_complete:false,working_tree:"Not compared or executed."},gaps:[]};
  const selection=review.selectionFor(comparison,filePath,ref);
  const file={schema:"eija.repository.change-file.v1",status:"partial",read_only:true,comparison_id:comparison.comparison_id,base:clone(comparison.base),head:clone(comparison.head),path:filePath,selected_reference:ref,
    before:{...before,text:"def run():\r\n    return '雪'\r\n",range:{start:7,end:8},truncated:false,snippet_sha256:sha("3"),symbol:old},
    after:{...after,text:"def run():\n    return '<script>'\n",range:{start:17,end:18},truncated:true,snippet_sha256:sha("4"),symbol:next},
    unified_diff:{status:"AVAILABLE",text:"diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -10 +20 @@\n-return 'old'\n+return '<script>'\n",context_lines:3,truncated:false},
    known_impact:{before:{status:"PARTIAL",complete:false,uncaptured_inventory_count:90,captured_source_hash:comparison.base.changed_source_hash,graph_hash:"graph-old",impact:{target:ref,count:1,affected:[{id:"repo://dependent",type:"function",rank:1,witness:[ref,"repo://dependent"]}]}},after:{status:"UNKNOWN_TARGET",complete:false,reason:"No declared graph target for this syntax reference.",uncaptured_inventory_count:91}}};
  return {comparison,file,selection};
}
function render(data=fixture(),extras={}){const root=new Element("div"),controller=review.render(root,{...data,...extras});return {root,controller,view:value=>find(root,node=>node.dataset.repositoryView===value).onclick()};}
test("actual renderer retains exact commit pair, Git text, exclusions and bounded side source",()=>{
  const data=freeze(fixture()),original=JSON.stringify(data),h=render(data);
  assert.equal(find(h.root,node=>node.dataset.comparisonId).dataset.comparisonId,data.comparison.comparison_id);
  for(const value of [data.comparison.base.commit,data.comparison.head.commit,data.comparison.base.tree,data.comparison.head.tree,data.comparison.base.changed_source_hash,data.comparison.head.changed_source_hash])assert.ok(h.root.textContent.includes(value));
  assert.equal(find(h.root,node=>node.dataset.repositoryDiff==="git").textContent,data.file.unified_diff.text);assert.match(h.root.textContent,/2 changed paths · 1 displayed · 1 excluded/);assert.match(h.root.textContent,/private_path/);
  h.view("before");assert.equal(find(h.root,node=>node.dataset.repositorySource==="before").textContent,data.file.before.text);assert.match(h.root.textContent,/Lines 7–8/);assert.ok(h.root.textContent.includes(data.file.before.snippet_sha256));
  h.view("after");assert.equal(find(h.root,node=>node.dataset.repositorySource==="after").textContent,data.file.after.text);assert.match(h.root.textContent,/excerpt truncated/);assert.equal(JSON.stringify(data),original);
});
test("every identity dimension rejects stale detail without displaying its diff or source",()=>{
  const mutations=[d=>d.file.comparison_id="other",d=>d.file.base.commit=objectId("9"),d=>d.file.head.tree=objectId("9"),d=>d.file.base.changed_source_hash="other",d=>d.file.path="other.py",d=>d.file.selected_reference="repo://other",d=>d.file.after.blob=objectId("9"),d=>d.file.before.file_sha256=sha("9"),d=>d.selection.comparison_id="other",d=>d.selection.head_commit=objectId("9"),d=>{d.file.after.symbol={...d.file.after.symbol,reference:"repo://another#definition"};},d=>{d.file.after.symbol={...d.file.after.symbol,syntax_digest:"wrong-symbol"};},d=>{d.file.after.symbol={...d.file.after.symbol,start_line:999};}];
  for(const mutate of mutations){const data=fixture();mutate(data);const h=render(data);assert.equal(find(h.root,node=>node.className==="repository-review").dataset.repositoryStatus,"mismatch");assert.match(h.root.textContent,/does not match selection/);assert.ok(!find(h.root,node=>node.dataset.repositoryDiff));assert.ok(!find(h.root,node=>node.dataset.repositorySource));}
});
test("missing file, unavailable blob, ambiguous reference and incomplete extraction are distinct",()=>{
  const absent=fixture();absent.comparison.files[0].before=null;absent.file.before=null;let h=render(absent);h.view("before");assert.match(h.root.textContent,/This file is not present in the before commit/);
  const unavailable=fixture();unavailable.comparison.files[0].before.status="unavailable";unavailable.file.before={status:"unavailable",blob:unavailable.comparison.files[0].before.blob};h=render(unavailable);h.view("before");assert.match(h.root.textContent,/not captured as permitted text/);
  for(const status of ["ambiguous","not_present"]){const data=fixture(),row=data.comparison.files[0];row.extraction.after.symbols=status==="ambiguous"?[row.symbols[0].after,row.symbols[0].after]:[];row.symbols[0].after=null;row.symbols[0].status=status==="ambiguous"?"ambiguous":"removed";data.file.after={status,blob:row.after.blob,reference:data.selection.reference};h=render(data);h.view("after");assert.ok(!find(h.root,node=>node.dataset.repositorySource));assert.match(h.root.textContent,status==="ambiguous"?/Multiple extracted definitions/:/No matching reference was extracted.*PARTIAL/);if(status==="not_present")assert.match(h.root.textContent,/not proof of absence/);h.view("syntax");assert.match(h.root.textContent,/No unique extracted match · PARTIAL/);}
});
test("zero changed paths differ from an excluded inventory and unavailable or empty Git diff",()=>{
  const data=fixture();data.comparison.files=[];data.comparison.coverage={changed_paths_total:0,displayed_paths:0,excluded_by_reason:{},inventory_reconciles:true};data.selection=null;data.file=null;let h=render(data);assert.match(h.root.textContent,/No changed paths between these commits/);assert.match(h.root.textContent,/does not establish behavioral equivalence/);
  data.comparison.coverage={changed_paths_total:2,displayed_paths:0,excluded_by_reason:{private_path:2},inventory_reconciles:true};h=render(data);assert.match(h.root.textContent,/No changed files available within capture scope/);assert.doesNotMatch(h.root.textContent,/No changed paths between/);
  const blocked=fixture();blocked.file.unified_diff={status:"NOT_RUN",text:"",reason:"Bounded Git output unavailable"};h=render(blocked);assert.match(h.root.textContent,/Diff · NOT_RUN/);assert.match(h.root.textContent,/Bounded Git output unavailable/);assert.doesNotMatch(h.root.textContent,/No textual hunks/);
  blocked.file.unified_diff={status:"AVAILABLE",text:""};h=render(blocked);assert.match(h.root.textContent,/No textual hunks/);assert.doesNotMatch(h.root.textContent,/No changed paths/);
});
test("literal file/reference navigation carries only the pinned historical selection",()=>{
  const data=fixture(),files=[],symbols=[],sides=[];const h=render(data,{onSelectFile:value=>files.push(value),onSelectSymbol:value=>symbols.push(value),onOpenSide:value=>sides.push(value)});
  find(h.root,node=>node.dataset.repositoryPath).onclick();assert.deepEqual(files,[{...data.selection,reference:null}]);
  find(h.root,node=>node.dataset.repositoryReference).onclick();assert.deepEqual(symbols,[data.selection]);
  h.view("after");find(h.root,node=>node.dataset.repositoryAction==="open-after").onclick();assert.equal(sides[0].commit,data.comparison.head.commit);assert.equal(sides[0].tree,data.comparison.head.tree);assert.equal(sides[0].text,data.file.after.text);assert.equal(sides[0].snippet_sha256,data.file.after.snippet_sha256);assert.deepEqual(sides[0].selection,data.selection);assert.equal(sides[0].read_only,true);
  assert.ok(!all(h.root).some(node=>["SCRIPT","IMG","IFRAME"].includes(node.tagName)));assert.match(h.root.textContent,/<script>/);assert.equal(sides[0].source_hash,undefined);
});
test("syntax and known impact remain scoped observations with exact unknowns and witnesses",()=>{
  const h=render();h.view("syntax");assert.match(h.root.textContent,/Syntactic observations/);assert.match(h.root.textContent,/Partial extraction can make definitions appear added or removed/);assert.match(h.root.textContent,/UNPARSEABLE/);assert.match(h.root.textContent,/ast-old/);assert.match(h.root.textContent,/ast-new/);
  h.view("impact");assert.match(h.root.textContent,/Before · PARTIAL/);assert.match(h.root.textContent,/After · UNKNOWN_TARGET/);assert.match(h.root.textContent,/repo:\/\/dependent/);assert.match(h.root.textContent,/Unmodified files and runtime dependencies are omitted/);assert.match(h.root.textContent,/Behavior · NOT_RUN/);assert.match(h.root.textContent,/model receipts do not cover this code comparison/);assert.doesNotMatch(h.root.textContent,/behavior.*PASS/i);
});
test("loading, retained requests, unavailable envelopes and exact retry errors cannot mint subjects",()=>{
  let h=render({comparison:null,file:null,selection:null},{loading:"comparison"});assert.match(h.root.textContent,/Loading repository comparison/);assert.ok(!find(h.root,node=>node.dataset.comparisonId));
  h=render(fixture(),{loading:"comparison",error:{code:"REQUEST_FAILED",message:"Temporary failure",details:{retryable:true}}});assert.match(h.root.textContent,/Retained comparison while loading/);assert.match(h.root.textContent,/not the pending result/);assert.match(h.root.textContent,/REQUEST_FAILED/);assert.match(h.root.textContent,/retryable/);assert.equal(find(h.root,node=>node.dataset.comparisonId).dataset.comparisonId,"comparison-1");
  for(const status of ["unconfigured","unavailable"]){h=render({comparison:{status,reason:"No configured local repository"}});assert.ok(!find(h.root,node=>node.dataset.comparisonId));assert.match(h.root.textContent,/No configured local repository/);assert.match(h.root.textContent,/Behavior · NOT_RUN/);}
  const data=fixture();data.file={schema:"eija.repository.change.v1",status:"unavailable",reason:"Capture policy changed; retry"};h=render(data);assert.match(h.root.textContent,/Historical file unavailable/);assert.match(h.root.textContent,/Capture policy changed/);assert.ok(!find(h.root,node=>node.dataset.repositoryDiff));
});
test("actual keyboard tab navigation and external navigator cleanup preserve unrelated content",()=>{
  const external=new Element("aside"),unrelated=new Element("p");unrelated.textContent="Owned elsewhere";external.append(unrelated);const changes=[],h=render(fixture(),{navigatorRoot:external,onSelectFile:()=>{},onViewChange:(...args)=>changes.push(args)});
  const tabs=find(h.root,node=>node.className==="repository-view-tabs"),first=find(h.root,node=>node.dataset.repositoryView==="diff");let prevented=false;
  tabs.listeners.keydown({key:"ArrowRight",target:first,preventDefault(){prevented=true;}});assert.ok(prevented);assert.equal(document.activeElement.dataset.repositoryView,"before");assert.equal(document.activeElement.getAttribute("aria-selected"),"true");assert.equal(h.controller.getState().view,"before");assert.equal(changes[0][0],"before");
  assert.equal(h.controller.openSide("after"),true);assert.equal(h.controller.getState().view,"after");assert.equal(h.controller.openSide("live"),false);
  assert.equal(external.children.length,2);h.controller.destroy();assert.equal(external.children.length,1);assert.equal(external.children[0],unrelated);assert.equal(h.controller.openSide("before"),false);
});
test("presentation-only diff rows preserve exact Git bytes including metadata and no-newline markers",()=>{
  const raw="diff --git a/x b/x\r\n--- a/x\r\n+++ b/x\r\n@@ -1 +1 @@\r\n-old\r\n+new\r\n\\ No newline at end of file";const rows=review.diffRows(raw);assert.equal(rows.map(row=>row.text).join(""),raw);assert.deepEqual(rows.map(row=>row.kind),["header","header","header","header","removed","added","header"]);
});
test("coverage oracle rejects omitted displayed files even when a server completeness flag remains true",()=>{
  const data=fixture();assert.equal(review.coverage(data.comparison).reconciles,true);data.comparison.files=[];assert.equal(review.coverage(data.comparison).reconciles,false);const h=render({...data,selection:null,file:null});assert.match(h.root.textContent,/Inventory does not reconcile/);assert.doesNotMatch(h.root.textContent,/No changed paths between/);
});
test("a detail cannot claim missing or ambiguous syntax when the summary has one exact fact",()=>{
  for(const status of ["not_present","ambiguous"]){const data=fixture();data.file.after={status,reference:data.selection.reference,blob:data.comparison.files[0].after.blob};assert.equal(review.inspect(data.comparison,data.file,data.selection).status,"mismatch");}
});
test("symbol-identity oracle rejects an implementation mutant that accepts another definition",()=>{
  const fs=require("node:fs"),vm=require("node:vm"),filename=process.env.EIJA_REPOSITORY_REVIEW_MODULE||path.join(__dirname,"../../src/eija_studio/resources/web/repository-review.js"),source=fs.readFileSync(filename,"utf8");
  const marker="&&sameSymbol(row,file[side],side,selection.reference)";assert.ok(source.includes(marker));const sandbox={module:{exports:{}},document};vm.createContext(sandbox);vm.runInContext(source.replace(marker,""),sandbox);
  const data=fixture();data.file.after.symbol={...data.file.after.symbol,reference:"repo://same-file#wrong-definition"};
  assert.equal(review.inspect(data.comparison,data.file,data.selection).status,"mismatch");
  assert.throws(()=>assert.equal(sandbox.module.exports.inspect(data.comparison,data.file,data.selection).status,"mismatch"),assert.AssertionError);
});
function populatedFixture(){
  const data=fixture(),row=data.comparison.files[0];
  for(let i=1;i<73;i++){
    const reference=`repo://src/app.js#js/function/${i===72?"task":`helper_${i}`}`,fact={reference,kind:"function",syntax_digest:`syntax-${i}`,start_line:100+i,end_line:100+i};
    const symbol={reference,kind:"function",status:i<4?"changed":"unchanged",before:fact,after:{...fact,syntax_digest:i<4?`updated-${i}`:fact.syntax_digest}};
    row.symbols.push(symbol);row.extraction.before.symbols.push(symbol.before);row.extraction.after.symbols.push(symbol.after);
  }
  return data;
}
const referenceButtons=root=>all(root).filter(node=>node.dataset.repositoryReference!==undefined);
test("changed-first filter preserves complete 73-reference inventory and exact unchanged navigation",()=>{
  const data=freeze(populatedFixture()),before=JSON.stringify(data),selections=[],h=render(data,{symbolsOpen:true,onSelectSymbol:value=>selections.push(value)});
  const symbols=data.comparison.files[0].symbols,changed=symbols.filter(item=>item.status!=="unchanged").map(item=>item.reference),filter=find(h.root,node=>node.dataset.repositorySymbolFilter!==undefined);
  assert.deepEqual(referenceButtons(h.root).map(node=>node.dataset.repositoryReference),changed);assert.equal(changed.length,4);
  filter.value="all";filter.onchange();const visible=referenceButtons(h.root).map(node=>node.dataset.repositoryReference);
  assert.equal(visible.length,73);assert.equal(new Set(visible).size,73);assert.deepEqual(visible,symbols.map(item=>item.reference));
  assert.equal(h.controller.getState().symbolsFilter,"all");
  const task=symbols.at(-1);find(h.root,node=>node.dataset.repositoryReference===task.reference).onclick();
  assert.deepEqual(selections,[{...data.selection,reference:task.reference}]);assert.equal(h.controller.getState().symbolsOpen,false);
  assert.match(document.activeElement.id,/-symbols-summary$/);assert.equal(document.activeElement.textContent,"73 extracted syntax references");
  assert.equal(JSON.stringify(data),before);
});
test("compact file labels retain the full path for identity, accessible name and navigation",()=>{
  const data=fixture(),selections=[],h=render(data,{onSelectFile:value=>selections.push(value)}),button=find(h.root,node=>node.dataset.repositoryPath!==undefined);
  assert.equal(find(button,node=>node.className==="repository-filename").textContent,"雪#.py");assert.equal(find(button,node=>node.className==="repository-parent-path").textContent,"src");
  assert.equal(button.dataset.repositoryPath,data.selection.path);assert.equal(button.title,`◇ Modified · ${data.selection.path}`);assert.equal(button.getAttribute("aria-label"),button.title);
  button.onclick();assert.deepEqual(selections,[{...data.selection,reference:null}]);
});
test("display decoding never rewrites selected reference or callback identity and exposes collisions",()=>{
  const data=fixture(),row=data.comparison.files[0],reference="repo://src/app.js#js/assignment/%24(%22create%22).onclick";
  assert.equal(review.referenceLabel(reference),'$("create").onclick');assert.equal(review.referenceLabel("repo://x.py#Studio.verify"),"Studio.verify");assert.equal(review.referenceLabel("repo://x.js#js/function/bad%ZZ"),"bad%ZZ");
  row.symbols[0].reference=reference;row.symbols[0].kind="assignment";for(const side of ["before","after"]){row.symbols[0][side].reference=reference;row.symbols[0][side].kind="assignment";row.extraction[side].symbols[0]=row.symbols[0][side];data.file[side].symbol=clone(row.symbols[0][side]);}
  data.selection.reference=reference;data.file.selected_reference=reference;const selected=[],h=render(data,{onSelectSymbol:value=>selected.push(value)}),choice=referenceButtons(h.root)[0];
  assert.ok(choice.textContent.includes('$("create").onclick'));assert.ok(!choice.textContent.includes("%24"));assert.equal(choice.title,reference);assert.ok(choice.getAttribute("aria-label").includes(reference));
  choice.onclick();assert.equal(selected[0].reference,reference);const identity=find(h.root,node=>node.dataset.repositorySelectedReference!==undefined);assert.equal(identity.dataset.repositorySelectedReference,reference);assert.equal(find(identity,node=>node.tagName==="CODE").textContent,reference);
  const duplicate=clone(row.symbols[0]);duplicate.reference="repo://src/app.js#js/assignment/$(%22create%22).onclick";row.symbols.push(duplicate);
  const collision=render(data);assert.ok(referenceButtons(collision.root)[0].textContent.includes(reference));assert.ok(referenceButtons(collision.root)[1].textContent.includes(duplicate.reference));
});
test("selected unchanged identity remains reachable under changed filter and retains chosen view state",()=>{
  const data=populatedFixture(),symbol=data.comparison.files[0].symbols.at(-1);data.selection.reference=symbol.reference;data.file.selected_reference=symbol.reference;
  for(const side of ["before","after"])data.file[side].symbol=clone(symbol[side]);
  const h=render(data,{view:"after",symbolsFilter:"changed",symbolsOpen:false});assert.equal(referenceButtons(h.root).length,4);
  const identity=find(h.root,node=>node.dataset.repositorySelectedReference===symbol.reference);assert.ok(identity);assert.match(identity.children[0].textContent,/Selected · task · = Unchanged/);assert.equal(find(identity,node=>node.tagName==="CODE").textContent,symbol.reference);
  assert.equal(find(h.root,node=>node.dataset.repositorySource==="after").textContent,data.file.after.text);const state=h.controller.getState(),retained=render(data,{...state,symbolsFilter:"all",symbolsOpen:true});assert.equal(referenceButtons(retained.root).length,73);assert.equal(retained.controller.getState().view,"after");assert.equal(retained.controller.getState().symbolsOpen,true);
});
test("all-unchanged extraction offers All explicitly without suggesting empty file or no changes",()=>{
  const data=fixture();data.comparison.files[0].symbols[0].status="unchanged";const h=render(data);assert.equal(referenceButtons(h.root).length,0);assert.match(h.root.textContent,/No changed or unresolved references reported/);assert.ok(find(h.root,node=>node.dataset.repositoryDiff==="git"));
  const filter=find(h.root,node=>node.dataset.repositorySymbolFilter!==undefined);filter.value="all";filter.onchange();assert.equal(referenceButtons(h.root).length,1);assert.equal(h.controller.getState().symbolsFilter,"all");
});
const visibleText=node=>node.ownText+(node.tagName==="DETAILS"&&!node.open?node.children.filter(child=>child.tagName==="SUMMARY"):node.children).map(visibleText).join("");
test("compact metadata keeps limits visible while native disclosures retain exact identity and exclusions",()=>{
  const data=freeze(fixture()),original=JSON.stringify(data),h=render(data,{view:"after"}),visible=visibleText(h.root);
  assert.equal((visible.match(/Behavior · NOT_RUN/g)||[]).length,1);assert.match(visible,/known impact is incomplete/);assert.match(visible,/PARTIAL · read-only/);
  assert.match(visible,/2 changed paths · 1 displayed · 1 excluded/);assert.match(visible,/Capture exclusions and gaps \(1 excluded; 0 gaps\)/);assert.match(visible,/Syntax before: EXTRACTED · after: PARTIAL/);assert.match(visible,/Selected · run · ◇ Changed/);
  assert.ok(!visible.includes(data.comparison.base.changed_source_hash));assert.ok(!visible.includes(data.selection.reference));
  const identities=find(h.root,node=>node.className==="repository-identity-disclosure"),exclusions=find(h.root,node=>node.tagName==="DETAILS"&&node.children[0].textContent.startsWith("Capture exclusions and gaps")),selected=find(h.root,node=>node.dataset.repositorySelectedReference===data.selection.reference);
  identities.open=true;exclusions.open=true;selected.open=true;const expanded=visibleText(h.root);
  for(const value of [data.comparison.base.commit,data.comparison.head.commit,data.comparison.base.tree,data.comparison.head.tree,data.comparison.base.changed_source_hash,data.comparison.head.changed_source_hash,data.selection.reference,"private_path","model receipts do not cover this code comparison"])assert.ok(expanded.includes(value),value);
  assert.equal(find(h.root,node=>node.dataset.repositorySource==="after").textContent,data.file.after.text);assert.equal(JSON.stringify(data),original);assert.deepEqual(h.controller.getState().selection,data.selection);
});
test("grouping never discloses away an inventory inconsistency or historical-source truncation",()=>{
  const data=fixture();data.comparison.coverage.displayed_paths=99;const h=render(data,{view:"after"});assert.match(visibleText(h.root),/Inventory does not reconcile/);assert.match(visibleText(h.root),/Completeness is unknown/);assert.match(visibleText(h.root),/Lines 17–18 · excerpt truncated/);assert.match(visibleText(h.root),/read-only historical source/);
  assert.equal(find(h.root,node=>node.dataset.repositorySource==="after").textContent,data.file.after.text);
  const identities=find(h.root,node=>node.tagName==="DETAILS"&&node.children[0].textContent==="After blob and excerpt identities");identities.open=true;
  for(const value of [data.comparison.head.commit,data.file.after.blob,data.file.after.file_sha256,data.file.after.snippet_sha256])assert.ok(visibleText(h.root).includes(value));
});
