"use strict";
/* Presentation-only fixture navigation. No fetch, runtime, policy, persistence, or source-writing engine. */
const $ = id => document.getElementById(id);
const el = (tag, text, className) => {const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (className) node.className = className; return node;};
const copy = value => JSON.parse(JSON.stringify(value));
const surfaces = {
  model:{id:"S01",title:"Understand the working model",stories:"US02 · US06 · US10",states:["ready","loading","empty","layout failed","stale"]},
  intent:{id:"S02",title:"Describe the intended change",stories:"US03 · US04 · US11",states:["ready","loading","failed","unknown"]},
  changes:{id:"S03",title:"See exactly what changes",stories:"US04 · US05 · US07",states:["ready","empty","loading","stale","removed element"]},
  source:{id:"S04",title:"Inspect the declared source",stories:"US01 · US05 · US10",states:["ready","loading","stale","missing binding","unsupported"]},
  edit:{id:"S05",title:"Preview a precise rule edit",stories:"US06 · US09 · US11",states:["ready","checking","refused","stale","unknown","acknowledged"]},
  evidence:{id:"S06",title:"Understand the evidence boundary",stories:"US07 · US10 · US11",states:["ready","loading","missing","stale","counterexample"]},
  run:{id:"S07",title:"Observe the latest attempt",stories:"US08 · US11",states:["ready","pending","refused","unknown","committed","refresh failed"]},
  history:{id:"S08",title:"Revisit without rewriting history",stories:"US09 · US10",states:["ready","empty","loading","stale","historical"]},
  factory:{id:"S09",title:"Coordinate work by meaning",stories:"US13 · US14 · PLANNED",states:["overlap","unknown","stale base","failed landing"]},
  connection:{id:"S10",title:"Connect, inspect, recover",stories:"US01 · US10 · US11 · US12",states:["ready","empty","loading","unavailable","partial"]}
};
const transition = (id, action, from, to, role, guards=[]) => ({id,action,from_state:from,to_state:to,role,guards,required_effects:[],forbidden_effects:[]});
const baseline = {states:["DRAFT","PREVIEW","SAVED","VERIFIED"],initial_state:"DRAFT",transitions:[
  transition("TR-SELECT","SelectMeaning","DRAFT","PREVIEW","Owner"),
  transition("TR-SAVE","Save","PREVIEW","SAVED","Owner"),
  transition("TR-VERIFY","Verify","PREVIEW","VERIFIED","Owner",["authenticated","assigned"]),
  transition("TR-VERIFY-SAVED","VerifySaved","SAVED","VERIFIED","Owner",["authenticated"])
]};
const candidate = copy(baseline);
candidate.transitions.find(t=>t.id==="TR-SAVE").role="Agent";
candidate.transitions.find(t=>t.id==="TR-VERIFY").from_state="SAVED";
candidate.transitions.find(t=>t.id==="TR-VERIFY").guards=["authenticated"];
const cases = {
  review:{id:"DESIGN-A",name:"Save checkpoint before verification",revision:8,before:baseline,after:candidate,selected:{kind:"transition",id:"TR-SAVE"}},
  missing:{id:"DESIGN-B",name:"A change with an unresolved binding",revision:3,before:baseline,after:{...copy(baseline),transitions:baseline.transitions.map(t=>t.id==="TR-SAVE"?{...copy(t),to_state:"VERIFIED"}:copy(t))},selected:{kind:"transition",id:"TR-SAVE"}}
};
const viewState = new Map(), caseState = new Map(), scrollState = new Map(), disclosureState = new Map();
let caseKey="review", view="changes", origin=null, renderer=null, previewRenderer=null, previewInvoker=null, variant="role", selectedWitness=0;
const sourceRecords = {
  "TR-SAVE":{name:"Studio.save",file:"example/studio.py",ref:"fixture://example/studio.py#Studio.save",start:42,lines:[
    "# Illustrative pseudocode; not captured repository source.",
    "def save(case, actor):", "    require_declared_actor(case, actor)", "    transaction = SaveCheckpoint(case.id)", "    return record_checkpoint(transaction)"]},
  "TR-VERIFY":{name:"Studio.verify",file:"example/studio.py",ref:"fixture://example/studio.py#Studio.verify",start:73,lines:[
    "# Illustrative pseudocode; not captured repository source.","def verify(case, actor):","    require_declared_actor(case, actor)","    subject = candidate_subject(case)","    return collect_bounded_checks(subject)"]}
};
const terms=Object.entries(sourceRecords).map(([id,record])=>({id:record.name,label:record.name,refs:[`transition:${id}`],binds:[record.ref]}));
function current(){
  const base=cases[caseKey],scenario=caseState.get(caseKey)?.scenario;
  if(scenario==="empty")return {...base,id:`${base.id}:unchanged-scene`,after:base.before};
  if(scenario==="removed")return {...base,id:`${base.id}:removed-scene`,after:{...base.after,transitions:base.after.transitions.filter(t=>t.id!=="TR-SAVE")}};
  return base;
}
function state(){return viewState.get(`${caseKey}:${view}`)||surfaces[view].states[0];}
function selection(){return caseState.get(caseKey)?.selected||current().selected;}
function afterSnapshot(){return current().after;}
function item(){return EijaCompare.inventory(current().before,afterSnapshot()).items.find(value=>value.kind===selection().kind&&value.id===selection().id);}
function selectedSource(){return caseKey==="missing"?null:sourceRecords[selection().id]||null;}
function button(text,action,className=""){const node=el("button",text,className);node.type="button";node.addEventListener("click",action);return node;}
function badge(text,tone="amber"){return el("span",text,`pill ${tone}`);}
function card(title,tag){const node=el("section",undefined,"card"),header=el("div",undefined,"card-heading");header.append(el("h2",title));if(tag)header.append(badge(tag));node.append(header);return node;}
function details(title,content){const node=el("details");node.append(el("summary",title),typeof content==="string"?el("p",content):content);return node;}
function exactRecord(label,record){const node=el("pre",JSON.stringify(record,null,2),"exact-record");node.tabIndex=0;node.setAttribute("role","region");node.setAttribute("aria-label",label);return node;}
function field(name,value){const row=el("div",undefined,"field-line");row.append(el("span",name),el("span",value));return row;}
function prose(text,className){return el("p",text,className);}
function announce(text){$("announcement").textContent=text;}
function setState(next){if(view==="changes"&&["ready","empty","removed element"].includes(next))caseState.set(caseKey,{...(caseState.get(caseKey)||{}),scenario:next==="empty"?"empty":next==="removed element"?"removed":null});viewState.set(`${caseKey}:${view}`,next);render();$("surface-title").focus();announce(`${surfaces[view].id}: ${next} illustration. No backend operation occurred.`);}
function navigate(next,remember=true){
  if(!surfaces[next])return;
  scrollState.set(`${caseKey}:${view}`,$("surface").scrollTop);
  disclosureState.set(`${caseKey}:${view}`,[...$("surface").querySelectorAll("details[open]")].map(node=>node.querySelector("summary")?.textContent));
  // Arrival at the originating view ends the detour; do not immediately create a reverse origin.
  if(origin?.view===next)origin=null;
  else if(remember&&next!==view&&!origin)origin={view,selected:{...selection()},focus:document.activeElement?.dataset.designFocusKey};
  view=next;document.body.classList.remove("nav-open");syncNavigation();render();$("surface-title").focus();
  $("surface").scrollTop=scrollState.get(`${caseKey}:${view}`)||0;
  announce(`${surfaces[view].title}. ${current().id}, revision ${current().revision}. Selection retained.`);
}
function setSelection(reference){caseState.set(caseKey,{...(caseState.get(caseKey)||{}),selected:{kind:reference.kind,id:reference.id}});renderSelection();renderContext();}
function sourceRoute(){if(!selectedSource())viewState.set(`${caseKey}:source`,"missing binding");navigate("source");}
function addActions(node,actions){const row=el("div",undefined,"row");for(const [label,action]of actions)row.append(button(label,action));node.append(row);return row;}
function renderSelection(){
  if(view==="factory"){$("selected-title").textContent="Planned combined review";$("selected-delta").textContent="No merged subject exists. Branch overlap is an illustration, not a verdict.";$("nav-selected").textContent="Shared checkpoint journey";$("nav-subject").textContent="Planned branch fixtures";$("status-subject").textContent="Factory concept · planned";return;}
  const value=item(),action=value?.after?.action||value?.before?.action||value?.id||"No element";
  $("selected-title").textContent=action;
  $("selected-delta").textContent=value?value.fields.filter(f=>f.changed).map(f=>`${f.label}: ${literal(f.before)} → ${literal(f.after)}`).join(" · ")||"Unchanged in these fixture snapshots":"No model element selected.";
  $("nav-selected").textContent=action;$("nav-subject").textContent=selection().id;
  $("status-subject").textContent=view==="factory"?"Factory concept · planned":"Local illustration · no network or writes";
}
function literal(value){return value===undefined?"Not present":Array.isArray(value)?JSON.stringify(value):String(value);}
function renderContext(){
  const target=$("context");target.replaceChildren(el("h2","Trace this change"));
  if(view==="factory"){target.append(el("h3","No combined subject"),badge("PLANNED"),prose("No merged revision or combined-result evidence exists in this design. The open case is parked while this concept is inspected."),details("Future evidence boundary",prose("Actual merged commit/model identity, exact base, coverage and owner authority are required before branch checks can support a landing decision.")));return;}
  const source=el("section",undefined,"context-card"),record=selectedSource();
  source.append(el("h3",record?record.name:"Source mapping unknown"),badge(record?"FIXTURE BINDING":"UNMAPPED"),prose(record?`${record.file} · lines ${record.start}–${record.start+record.lines.length-1}${item()?.after===undefined?" · Before snapshot only":""}`:"No source location is declared for this selected element.","muted"));
  source.append(button(record?"Open declared source":"Inspect mapping limit",sourceRoute));target.append(source);
  const evidence=el("section",undefined,"context-card");evidence.append(el("h3","Evidence boundary"),badge("NOT_RUN"),prose("No checks run. Repository behavior beyond this fixture remains unknown."),button("Inspect evidence boundary",()=>navigate("evidence")));target.append(evidence);
  const ripple=details("Known path and coverage limit",prose("Selected rule → declared fixture binding → separate example property. The binding is not proof of source conformance; no complete behavioral impact is claimed."));target.append(ripple);
  const actions=el("div",undefined,"context-card");actions.append(button("Explore prepared edit examples",()=>navigate("edit")),button("Inspect history",()=>navigate("history")));target.append(actions);
}
function stateNotice(host){
  const status=state();if(["ready","counterexample","historical","overlap","partial","removed element"].includes(status))return;
  const copy={loading:["Loading illustration","The prior subject stays readable. This is a chosen pending state, not a timed request."],checking:["Check pending illustration","The unsubmitted fields remain intact. There is no verdict yet."],pending:["Attempt pending illustration","The last acknowledged state stays visible. A second submission is unavailable in this state."],stale:["This subject is stale","The retained view is still readable. Current evidence and new writes cannot be attributed to it."],failed:["Request failed illustration","The request text and selection are retained. No automatic retry occurs."],unknown:["Outcome unknown illustration","A missing response does not establish refusal or success. Preserve the operation identity and reconcile explicitly."],refused:["Refused illustration","The last valid model/state is retained. Read the reason before correcting the request."],"refresh failed":["Acknowledged, refresh failed","The operation was acknowledged in this fixture. The displayed packet is older; do not relabel the commit as a refusal."],unavailable:["Connection unavailable","The last captured snapshot remains available. This does not mean the connection is current."],"missing binding":["No declared binding","No source location is inferred from an action name. Return to the selected model element."],unsupported:["Unsupported source scope","This fixture has no source view for binary or dynamic behavior. No project code is executed."],missing:["Evidence missing","A missing result is NOT_RUN, not a successful check."],empty:["No content for this subject","Choose the relevant entry action. Existing context is retained."],"stale base":["Planned: base changed","The example combined-result checks no longer apply. A fresh merged subject would be required."],"failed landing":["Planned: landing interrupted","No real landing occurred. Preserve branch identities and distinguish known commit from unknown outcome."]};
  const [title,message]=copy[status]||[`${status} illustration`,"Inspect the chosen design state."];const notice=el("section",undefined,`notice ${["refused","failed","unknown","unavailable"].includes(status)?"danger":""}`);
  notice.append(el("h2",title),prose(message));
  const label=["loading","checking","pending"].includes(status)?"Show completion illustration":status==="unknown"?"Show reconciliation illustration":status==="refused"?"Return to correction":"Show recovered illustration";
  notice.append(button(label,()=>setState(surfaces[view].states[0])));host.append(notice);
}
function render(){
  renderer?.destroy?.();renderer=null;$("change-navigator").replaceChildren();
  document.body.dataset.view=view;document.body.classList.toggle("taskless",!["model","changes","factory"].includes(view));$("navigation-toggle").hidden=!["model","changes","factory"].includes(view);syncNavigation();
  const config=surfaces[view];$("surface-title").textContent=view==="changes"?"Model changes":config.title;$("surface-kicker").textContent=config.id;
  $("task-nav-title").textContent=view==="factory"?"PLANNED BRANCH FIXTURES":view==="model"?"MODEL ELEMENTS":"MODEL CHANGES";
  $("case-caption").textContent=view==="factory"?"Open case parked · no merged subject":`${current().id} · r${current().revision}`;$("case-select").value=caseKey;
  $("identities").replaceChildren();for(const [name,value]of [["Fixture case",current().id],["Revision",String(current().revision)],["Selected element",`${selection().kind}:${selection().id}`],["Before model key",`illustration:model:${current().id}:baseline`],["After model key",`illustration:model:${current().id}:candidate`],["Source key","illustration:source:fixed-1"],["Evidence","NOT_RUN in this artifact; example cards do not certify these inputs"]])$("identities").append(el("dt",name),el("dd",value));
  document.querySelectorAll("[data-view]").forEach(node=>{node.classList.toggle("active",node.dataset.view===view);if(node.dataset.view===view)node.setAttribute("aria-current","page");else node.removeAttribute("aria-current");});
  $("return-origin").hidden=!origin||origin.view===view;$("return-origin").textContent=origin?`Return to ${surfaces[origin.view].id} selection`:"Return";
  $("surface").replaceChildren();stateNotice($("surface"));renderers[view]($("surface"));renderSelection();renderContext();renderLab();
  if(view!=="changes")renderSimpleNavigator();
  const opened=disclosureState.get(`${caseKey}:${view}`)||[];$("surface").querySelectorAll("details").forEach(node=>{if(opened.includes(node.querySelector("summary")?.textContent))node.open=true;});
  document.querySelectorAll("main button,#change-navigator button").forEach((node,index)=>{node.dataset.designFocusKey=`${view}:${node.id||node.dataset.compareKey||node.dataset.compareReference||node.textContent}:${index}`;});
}
function renderSimpleNavigator(){
  const list=$("change-navigator");if(view==="factory"){for(const title of ["Session A · Save rule","Session B · verification path","Combined result · unavailable"]){const group=el("div",undefined,"planned-nav-item");group.append(prose(title),badge("PLANNED"));list.append(group);}list.append(prose("No case-change inventory or merged result is attributed to these branch illustrations.","muted"));return;}
  const changes=EijaCompare.inventory(current().before,current().after);list.append(prose(`${changes.changes.length} changes in this example`,"muted"));
  for(const value of changes.changes){const node=button(`${value.after?.action||value.before?.action||value.id} · ${value.status}`,()=>{setSelection(value);render();});node.className="filter-choice";node.setAttribute("aria-pressed",String(value.id===selection().id&&value.kind===selection().kind));list.append(node);}
  if(view==="model"){const rest=details(`${changes.items.length-changes.changes.length} unchanged items`,el("div"));const content=rest.lastElementChild;for(const value of changes.items.filter(entry=>entry.status==="unchanged"))content.append(button(value.after?.action||value.id,()=>{setSelection(value);render();}));list.append(rest);}
}
function frameComparison(host,controller){
  const shell=host.querySelector(".paired-compare");if(!shell)return controller;
  const live=shell.querySelector(".compare-announcement");if(live)live.classList.add("sr-only");
  const exact=details("Exact fields and review context",el("div",undefined,"exact-content"));exact.className="exact-comparison";
  for(const node of [...shell.querySelectorAll(":scope > .compare-selection,:scope > .compare-context")])exact.lastElementChild.append(node);
  if(host.id==="preview-graph"){
    const navigator=shell.querySelector(".compare-navigator");
    if(navigator){const changed=navigator.querySelector(".compare-inventory")?.textContent||"Model items",unchanged=navigator.querySelector("details>summary")?.textContent||"";exact.querySelector("summary").textContent=`Exact fields and inventory · ${changed}${unchanged?` · ${unchanged}`:""}`;exact.lastElementChild.prepend(navigator);}
  }
  for(const summary of exact.querySelectorAll("summary"))if(summary.textContent.includes("typed transactions retained by the server"))summary.textContent="Prepared fixture transactions · none; no server history fetched";
  shell.append(exact);const heading=shell.querySelector(".compare-header h2");if(heading)heading.textContent="Selected change";
  const focus=shell.querySelector('[data-compare-action="focus"]');if(focus){focus.textContent="Focus 100%";focus.title="Center the selected path at natural text size. Pan if the available viewport cannot show all endpoints; Overview is an explicit reduced-scale alternative.";}
  let stopped=false;
  const readable=()=>{if(stopped||!host.isConnected)return;const saved=controller.getState?.();if(saved?.viewMode==="focus"&&saved.viewport?.scale<1){controller.setViewport({...saved.viewport,scale:1});const hint=shell.querySelector(".compare-scale-hint");if(hint)hint.textContent="100% focus · pan if the path exceeds this pane";}};
  const observer=new MutationObserver(readable);observer.observe(shell,{attributes:true,attributeFilter:["data-compare-view"]});
  if(focus)focus.onclick=()=>{controller.focus?.();readable();};
  requestAnimationFrame(()=>{if(!stopped){if(controller.getState?.().viewMode==="focus")controller.focus?.();readable();}});
  return {...controller,destroy(){stopped=true;observer.disconnect();controller.destroy?.();}};
}
function comparison(host,before,after,{preview=false}={}){
  const board=el("div",undefined,"compare-host");host.append(board);
  const saved=caseState.get(caseKey)?.comparison;
  const controller=EijaCompare.render(board,{case:{id:current().id,version:current().revision,baseline:before,candidate:after,transactions:[]},packet:{eligible:false,blockers:["DESIGN_ONLY","SOURCE_REVIEW_REQUIRED"],formal_evidence:[],impact:{complete:false,affected:[]}}},{
    preview,terms:caseKey==="missing"?[]:terms,navigatorRoot:preview?undefined:$("change-navigator"),
    state:{...(saved?.subject?.case===current().id?saved:{}),subject:{case:current().id,revision:current().revision},selected:selection()},
    onStateChange:s=>caseState.set(caseKey,{...(caseState.get(caseKey)||{}),comparison:s}),onSelection:reference=>setSelection(reference),
    openReference:sourceRoute,openEvidence:()=>navigate("evidence"),inspectTransition:()=>navigate("model")
  });
  renderer=frameComparison(board,controller);
  return board;
}
function renderModel(host){
  if(state()==="empty"){const empty=el("div",undefined,"empty");empty.append(el("h2","No selected meaning"),prose("Inspect the loaded baseline or describe a scoped change. There is no onboarding sequence to complete."));addActions(empty,[["Open Intent",()=>navigate("intent")],["Show populated model",()=>setState("ready")]]);host.append(empty);return;}
  const heading=el("div",undefined,"toolbar");heading.append(badge("WORKING CANDIDATE","green"),prose(`Fixture revision ${current().revision} · read-only illustration`,"muted"),button("Review an edit",()=>navigate("edit")));host.append(heading);
  if(state()!=="layout failed"){
    const board=el("div",undefined,"model-board");board.tabIndex=0;board.setAttribute("role","region");board.setAttribute("aria-label","Illustrative model diagram, keyboard transition controls inside");host.append(board);
    EijaCanvas.render(board,{model:current().after,layout:{},pack:"design-fixture",selected:selection().id,affordances:[],editable:false,direction:"TB",onSelect:id=>{setSelection({kind:"transition",id});render();},onNotice:announce});
    board.querySelector("svg").setAttribute("aria-label","Illustrative working model; no execution or validation");board.querySelector("desc").textContent="Existing EIJA Canvas and Dagre render this fixture. Select a transition or use the table below. No server or edits are connected.";
  }else host.append(prose("Diagram layout unavailable in this illustrated state. The rule table remains usable.","notice"));
  const info=details("Exact rules and keyboard alternative",ruleTable());info.open=state()==="layout failed";host.append(info);
}
function ruleTable(){const wrap=el("div",undefined,"table-scroll");wrap.tabIndex=0;wrap.setAttribute("role","region");wrap.setAttribute("aria-label","Fixture rule table");const table=el("table"),head=el("tr");for(const title of ["Action","Source → target","Role","Inspect"])head.append(el("th",title));table.append(head);for(const t of current().after.transitions){const row=el("tr");row.append(el("td",t.action),el("td",`${t.from_state} → ${t.to_state}`),el("td",t.role));const cell=el("td");cell.append(button(`Select ${t.action}`,()=>{setSelection({kind:"transition",id:t.id});render();}));row.append(cell);table.append(row);}wrap.append(table);return wrap;}
function renderChanges(host){
  if(state()==="empty"){const box=card("No semantic differences","UNCHANGED");box.append(prose("Before and after fixtures are identical in this state. No change is inferred from a different layout or heading."));addActions(box,[["Inspect model",()=>navigate("model")],["Show changed example",()=>setState("ready")]]);host.append(box);return;}
  const after=afterSnapshot();
  if(state()==="removed element")caseState.set(caseKey,{...(caseState.get(caseKey)||{}),selected:{kind:"transition",id:"TR-SAVE"}});
  comparison(host,current().before,after);
}
function renderIntent(host){
  const box=card("One intention, explicit scope","OFFLINE FIXTURE");box.append(prose("Ask the agent for a proposal; the engineer still selects meaning. This prototype sends nothing."));
  const label=el("label","Change request");label.htmlFor="intent-text";const input=el("textarea");input.id="intent-text";input.value=caseState.get(caseKey)?.prompt||(caseKey==="review"?"Let an agent save a checkpoint, while owner decisions remain owner-only.":"Show Save targeting VERIFIED instead of SAVED, keeping the Owner role. Source mapping is unresolved.");
  input.addEventListener("input",()=>caseState.set(caseKey,{...(caseState.get(caseKey)||{}),prompt:input.value}));box.append(label,input,prose("Scope: declared model only. Source transformation and factory execution are unavailable.","muted"));
  const controls=addActions(box,[["Show proposal illustration",()=>setState("ready")],["Show request pending",()=>setState("loading")],["Show interrupted request",()=>setState("unknown")]]);if(state()==="loading")controls.firstElementChild.textContent="Show completed proposal";host.append(box);
  if(state()==="ready"){const choices=el("div",undefined,"two-col"),isRole=caseKey==="review";const option=card(isRole?"Permit Save for Agent":"Save targets VERIFIED","PROPOSED");option.append(field(isRole?"Role":"Target state",isRole?"Owner → Agent":"SAVED → VERIFIED"),prose(isRole?"Owner approval authority is unchanged. This prepared case also contains Verify source/guard changes; inspect the complete inventory.":"Owner role is unchanged. There is no declared source mapping or proof that this destination is intended."),button("Inspect proposed meaning",()=>{setSelection({kind:"transition",id:"TR-SAVE"});navigate("changes");},"primary"));const alternative=card(isRole?"Keep owner-only Save":"Keep SAVED as the target","ALTERNATIVE");alternative.append(prose("No model change. Retain the request for clarification rather than selecting meaning automatically."),button("Return to request",()=>input.focus()));choices.append(option,alternative);host.append(choices);}
}
function renderSource(host){
  const record=selectedSource();if(!record||["missing binding","unsupported"].includes(state())){const box=el("div",undefined,"empty");box.append(el("h2",record?"No supported excerpt":"No source location is declared"),prose("The selected model element is known. Its repository implementation is not inferred from a matching name. Model review can continue with this limit visible."));addActions(box,[["Return to selected change",()=>navigate("changes")],["Inspect connection scope",()=>navigate("connection")]]);host.append(box);return;}
  const top=el("div",undefined,"source-heading");top.append(el("h2",record.name),badge("READ-ONLY FIXTURE"));host.append(top,prose(`${record.file} · lines ${record.start}–${record.start+record.lines.length-1}`,"muted"));
  const code=el("div",undefined,"source-code");code.tabIndex=0;code.setAttribute("role","region");code.setAttribute("aria-label",`${record.name} illustrative source with line numbers`);
  record.lines.forEach((text,index)=>{const line=el("div",undefined,`code-line${index===2?" highlight":""}`);line.append(el("span",String(record.start+index),"line-number"),el("span",text));code.append(line);});host.append(code);
  const disclosure=el("dl");for(const [name,value]of [["Declared fixture reference",record.ref],["Snapshot key","illustration:source:fixed-1"],["Line resolution","Explicit fixture range; no repository capture was performed"],["Coverage","One declared binding, not complete behavioral impact"]])disclosure.append(el("dt",name),el("dd",value));host.append(details("Exact source identity and scope",disclosure));
  addActions(host,[["Return to selected change",()=>navigate("changes")],["Inspect evidence",()=>navigate("evidence")],["Show stale source",()=>setState("stale")]]);
  host.append(details("Immutable Code changes · separate subject",prose("The product has a separate commit-pair Code changes view. This handoff does not reuse model receipts for a source diff. A future connected state must show both full commit IDs, each side's exact file hash, Git's diff and extraction limits; this artifact has no Git comparison.")));
}
const editVariants={
  role:{id:"TR-SAVE",label:"Save · Role: Owner → Agent",make:()=>{const after=copy(baseline);after.transitions.find(t=>t.id==="TR-SAVE").role="Agent";return after;}},
  source:{id:"TR-VERIFY",label:"Verify · Source state: PREVIEW → SAVED",make:()=>{const after=copy(baseline);after.transitions.find(t=>t.id==="TR-VERIFY").from_state="SAVED";return after;}},
  target:{id:"TR-SAVE",label:"Save · Target state: SAVED → VERIFIED",make:()=>{const after=copy(baseline);after.transitions.find(t=>t.id==="TR-SAVE").to_state="VERIFIED";return after;}},
  guards:{id:"TR-VERIFY",label:'Verify · Guards: ["authenticated","assigned"] → ["authenticated"]',make:()=>{const after=copy(baseline);after.transitions.find(t=>t.id==="TR-VERIFY").guards=["authenticated"];return after;}}
};
function renderEdit(host){
  const box=card("Inspect an unsubmitted change","PREPARED EDIT FIXTURE");box.append(prose("Choose a prepared edit example. Its Before is the owner-only fixture, independently of the open case's candidate. These fixed snapshots demonstrate the preview interaction; they are not server affordances for the current case."));
  const label=el("label","Edit example");label.htmlFor="edit-kind";const select=el("select");select.id="edit-kind";for(const[key,value]of Object.entries(editVariants)){const option=el("option",value.label);option.value=key;select.append(option);}select.value=variant;select.addEventListener("change",()=>{variant=select.value;render();$("edit-kind").focus();});box.append(label,select,prose("Previewing changes nothing. The real application requires a server-derived preview, captured subject/version and a separate Apply edit.","flow-note"));
  const launch=button("Open edit preview",openPreview,"primary");launch.disabled=["unknown","acknowledged"].includes(state());box.append(launch);host.append(box);
  if(["unknown","acknowledged"].includes(state())){const recovery=card(state()==="unknown"?"Prepared edit scene needs reconciliation":"Prepared edit acknowledged; captured view older",state()==="unknown"?"UNKNOWN":"REFRESH REQUIRED");recovery.append(prose(state()==="unknown"?"For prepared subject DESIGN-UNSUBMITTED r8, a missing response could hide a commit. Further submissions in this illustration remain unavailable until reconciliation.":"Prepared subject DESIGN-UNSUBMITTED r9 was acknowledged; its captured r8 view is older. Closing a preview must not hide this recovery state."),prose(`The open ${current().id} r${current().revision} fixture was not edited. This is an independent recovery scene.`),button("Show authoritative refresh outcome",()=>setState("ready")));host.append(recovery);}
  const contract=details("Interaction boundary and unsupported refactors",prose("Close preview or Escape before Apply sends no edit. During submission, close cannot discard an acknowledged outcome. Refusal preserves inputs; stale subjects must be refreshed. Rename, split, merge and source rewrite are planned adapter work, not controls in this design."));host.append(contract);
}
function openPreview(){
  previewInvoker=document.activeElement;previewRenderer?.destroy?.();const config=editVariants[variant],dialog=$("preview-dialog");dialog.showModal();
  const phase=state();$("preview-outcome").textContent="Prepared subject DESIGN-UNSUBMITTED · r8. "+(phase==="refused"?"Illustrative refusal: CASE_CLOSED. The model remains unchanged; no permission repair is suggested.":phase==="stale"?"Illustrative stale revision: preview r8 does not match the current r9. Apply is unavailable.":phase==="checking"?"Illustrative check pending. There is no verdict or applied change.":"Ready illustration, not a kernel verdict. Nothing is submitted.");
  $("preview-apply").disabled=["checking","refused","stale"].includes(phase);$("preview-apply").textContent="Show apply outcome";
  previewRenderer=frameComparison($("preview-graph"),EijaCompare.render($("preview-graph"),{case:{id:"DESIGN-UNSUBMITTED",version:8,baseline:copy(baseline),candidate:config.make()}},{preview:true,state:{subject:{case:"DESIGN-UNSUBMITTED",revision:8},selected:{kind:"transition",id:config.id}}}));
  $("preview-close").focus();
}
function closePreview(){previewRenderer?.destroy?.();previewRenderer=null;$("preview-dialog").close();(previewInvoker?.isConnected?previewInvoker:$("surface-title")).focus();announce("Preview closed. No edit or source write was sent.");}
function renderEvidence(host){
  host.append(prose("Checks, witnesses and applicability stay distinct. Every record below is an illustration; this artifact has run no checker.","muted"));
  const ledger=card("Evidence for the selected subject","NOT_RUN IN ARTIFACT");ledger.append(field("Subject",`${current().id} r${current().revision} · ${selection().id}`),field("Scope","Declared model only; repository behavior unproven"),field("Required review","SOURCE_REVIEW_REQUIRED"),field("Human benefit","UNKNOWN · no participant study"));host.append(ledger);
  const record=card("Separate witness example · SelectMeaning",state()==="stale"?"STALE EXAMPLE":"ILLUSTRATIVE FINDING");record.append(prose("This prepared witness concerns TR-SELECT, not the selected change's evidence. Property: the requested action satisfies its declared actor requirement. It does not prove complete source conformance."));
  const witness=el("div",undefined,"witness");["DRAFT","Agent requests SelectMeaning","Refused · ROLE_DENIED"].forEach((label,index)=>{const node=button(label,()=>{selectedWitness=index;render();});node.setAttribute("aria-pressed",String(selectedWitness===index));node.append(el("small",`Step ${index+1} · example only`));witness.append(node);});record.append(witness,prose(["Retained synthetic state before the illustrated attempt.","Captured actor/action is shown separately from the current actor selection.","This example attempt produced no effects. It does not establish that every later server state is still current."][selectedWitness]));
  if(state()==="stale")record.append(prose("Witness navigation unavailable: this stale example has no declared matching model revision or runtime instance. Refresh before navigating; do not substitute the current candidate.","notice"));
  else addActions(record,[["Inspect corresponding rule",()=>{setSelection({kind:"transition",id:"TR-SELECT"});navigate("model");}],["Open Run illustration",()=>navigate("run")]]);
  record.append(details("Exact example record and assumptions",exactRecord("Illustrative witness record and assumptions JSON",{kind:"illustrative_actor_witness",status:"DESIGN_ONLY",subject:{case:current().id,revision:current().revision,model:`illustration:model:${current().id}:candidate`,transition:"TR-SELECT"},property:"declared_actor_requirement",bounds:"single prepared attempt",assumptions:["fixture workflow only"],applicable_as_actual_evidence:false})));host.append(record);
}
function renderRun(host){
  host.append(prose("Synthetic candidate preview in the product. This design only switches among prepared outcome examples.","muted"));
  const acknowledged=["committed","refresh failed"].includes(state());const currentState=card("Last acknowledged state","EXAMPLE");currentState.append(el("p",acknowledged?"PREVIEW":"DRAFT","metric"),prose(acknowledged?"Instance fixture-run-1 · version 1 · SelectMeaning by Owner":"Instance fixture-run-1 · version 0 · initial preview creation", "muted"));host.append(currentState);
  const attempt=card("Latest attempt",state()==="ready"?"NO NEW ATTEMPT":state().toUpperCase());
  const outcomes={ready:"Choose an outcome illustration below. No server operation will occur.",pending:"SelectMeaning · actor Agent · awaiting response. Last acknowledged state remains DRAFT.",refused:"SelectMeaning · actor Agent · refused: ROLE_DENIED. This attempt produced no effects; the previous acknowledgement is retained.",unknown:"SelectMeaning · actor Agent · outcome UNKNOWN. A transport failure cannot prove no commit. No automatic retry with a new operation ID.",committed:"SelectMeaning · actor Owner · acknowledgement received in this example. The latest attempt and current instance agree.","refresh failed":"SelectMeaning · actor Owner · acknowledgement received, observations refresh failed. The commit remains acknowledged; the displayed observations are older."};attempt.append(prose(outcomes[state()]||outcomes.ready));
  const row=el("div",undefined,"row");for(const name of ["pending","refused","unknown","committed"])row.append(button(`Show ${name}`,()=>setState(name)));attempt.append(row,details("Attempt identity and diagnostic",exactRecord("Latest attempt identity and diagnostic JSON",{status:"DESIGN_ONLY",operation:"fixture-operation-2",case:current().id,revision:current().revision,action:"SelectMeaning",actor:acknowledged?"Owner":"Agent",instance:"fixture-run-1",code:state()==="refused"?"ROLE_DENIED":state()==="unknown"?"OUTCOME_UNKNOWN":null})));host.append(attempt);
  addActions(host,[["Inspect rule",()=>{setSelection({kind:"transition",id:"TR-SELECT"});navigate("model");}],["Inspect evidence scope",()=>navigate("evidence")],["Show fresh preview",()=>setState("ready")]]);
  host.append(details("Audit and effects · example",prose(acknowledged?"SelectMeaning by Owner acknowledged at instance version 1 in this example. No runtime, outbox or audit storage exists in this artifact.":"Preview creation acknowledged at instance version 0 in this example. No later commit is confirmed. This artifact has no runtime, outbox or audit storage.")));
}
function renderHistory(host){
  if(caseState.get(caseKey)?.scenario){const box=card("No history supplied for this snapshot variant","NOT PROVIDED");box.append(prose(`The ${current().id} comparison is a distinct prepared scene. It has no historical revisions to inspect; the ordinary example's timeline must not be attributed to it.`),button("Return to this comparison",()=>navigate("changes")));host.append(box);return;}
  if(state()==="empty"){host.append(prose("No semantic edit history in this illustrated case. Initial meaning remains protected; there is nothing to undo.","empty"));return;}
  if(state()==="historical")host.append(prose(`Inspecting fixture revision ${caseState.get(caseKey)?.historyRevision??current().revision-2}. Current revision ${current().revision} remains the working subject; its evidence does not attach to this historical preview.`,"notice"));
  const entries=caseKey==="review"?[["Initial meaning selected","Protected starting model; not an undoable edit."],["Save role changed","Owner → Agent · before/after retained."],["Verification path edited","Source PREVIEW → SAVED · guards shown explicitly."]]:[["Initial meaning selected","Protected starting model."],["Source scope recorded","Binding remains unresolved; this is not a semantic edit."],["Save target edited","SAVED → VERIFIED · owner role unchanged."]];
  const box=card("Case timeline","READ-ONLY INSPECTION");entries.forEach(([title,note],index)=>{const rev=current().revision-2+index,row=el("div",undefined,"history-row");row.append(el("small",`Fixture revision ${rev}`),el("h3",title),prose(note),button(index===2?"Inspect current comparison":`Inspect revision ${rev}`,()=>{if(index===2)navigate("changes");else{caseState.set(caseKey,{...(caseState.get(caseKey)||{}),historyRevision:rev});setState("historical");}}));box.append(row);});host.append(box);
  const actions=card("Inspecting is not restoring","NO WRITES");actions.append(prose("The product has audited semantic Undo/Redo. This prototype does not call those commands or pretend to restore a revision."));addActions(actions,[["Return to current comparison",()=>navigate("changes")],["Show stale undo state",()=>setState("stale")]]);host.append(actions);
}
function renderFactory(host){
  host.append(el("p","PLANNED FACTORY · illustrative worktrees and contracts · no agents, queue or landing service connected","planned-label"));
  const grid=el("div",undefined,"factory-grid");for(const [name,scope,identity]of [["Session A","Save checkpoint rule","branch example/save · base fixture-base-1"],["Session B","Verification source path","branch example/verify · base fixture-base-1"],["Combined result","Not computed","merge subject unavailable"]]){const box=card(name,"PLANNED");box.append(prose(scope),prose(identity,"fixture-identity"));grid.append(box);}host.append(grid);
  const contract=details("Contract needed before factory implementation",prose("Real session/worktree ownership, exact base and merged subject, detected overlap witness and unsupported coverage, combined-result checks, stale-decision refusal, recoverable failure and explicit owner landing authority. Existing Git and verification tools should be reused; this design supplies none of those services. No merged subject exists here, so current case evidence cannot be offered as combined-result evidence."));
  const branchFields=el("div");branchFields.append(field("Session A","Save · Role: Owner → Agent"),field("Session B","Verify · Source state: PREVIEW → SAVED"),prose("These are prepared branch descriptions. No merged model, combined source subject or conflict verdict exists."));const prepared=details("Prepared overlap fields",branchFields);
  const overlap=el("section",undefined,"factory-overlap");overlap.append(el("h2","Shared meaning requires inspection"),prose("Both examples touch the checkpoint-to-verification journey. A shared abstraction is a review lead, not proof of conflict or a safe merge."),field("Text overlap","Not assessed in this design"),field("Semantic overlap","Illustrative shared journey · coverage unknown"),field("Landing authority","Owner boundary unchanged; no landing control"));addActions(overlap,[["Inspect overlap fields",()=>{prepared.open=true;prepared.querySelector("summary").focus();}],["Read combined-result contract",()=>{contract.open=true;contract.querySelector("summary").focus();}]]);host.append(overlap,prepared,contract);
}
function renderConnection(host){
  if(state()==="empty"){const box=el("div",undefined,"empty");box.append(el("h2","Start with a subject you can inspect"),prose("Connect a local repository read-only, or inspect a declared model before connecting source. No forced onboarding path."));addActions(box,[["Show connection illustration",()=>setState("ready")],["Explore model fixture",()=>navigate("model")],["Describe intent",()=>navigate("intent")]]);host.append(box);return;}
  const box=card("Connection scope","DESIGN ONLY");box.append(field("Repository","Illustrative EIJA workspace; no filesystem access"),field("Snapshot","illustration:source:fixed-1"),field("Included","Two explicit pseudocode bindings in this artifact"),field("Excluded","Actual repository files, secrets, binaries and target execution"),field("Coverage","PARTIAL · unknown links remain unknown"));host.append(box);
  const recovery=card("One explicit recovery action","CONTEXT RETAINED");recovery.append(prose("When a provider or source capture is unavailable, keep the last valid subject, selection and request text. Say whether a write is acknowledged, refused or unknown."));addActions(recovery,[["Show unavailable connection",()=>setState("unavailable")],["Return to source",sourceRoute],["Show first entry",()=>setState("empty")]]);host.append(recovery);
  host.append(details("Keyboard and panel help",prose("Ctrl K opens surface search; Escape closes native dialogs. Tab visits the native navigation buttons; the reused comparison navigator also supports arrow keys. The comparison supports arrow-key pan, +/− zoom and Home focus. At compact widths Navigation is an explicit drawer; close returns focus to its opener. Browser, screen-reader and reflow acceptance are still NOT_RUN for this design.")));
}
const renderers={model:renderModel,intent:renderIntent,changes:renderChanges,source:renderSource,edit:renderEdit,evidence:renderEvidence,run:renderRun,history:renderHistory,factory:renderFactory,connection:renderConnection};
const handoffs={
 model:"Entry: selected rule or source return. Keyboard alternative: exact rule table. Layout failure retains rules. Selection and diagram presentation remain case-owned.",
 intent:"Request text remains on failed/unknown states. Pending has no invented percentage. Explicit retry is a separate illustration; no provider is contacted.",
 changes:"Select change → Source/Evidence → Return retains case/revision/item. Before/after use existing comparison and Dagre. Exact values lead; shared positions do not imply behavioral equivalence.",
 source:"Focus source heading on arrival. Read-only line region scrolls independently. Stale/missing binding never opens a guessed file. Return preserves the selected change.",
 edit:"Preview receives prepared before/after fixtures; Close/Escape submits nothing and restores its invoker. Apply outcome is an illustration. Unknown/acknowledged recovery survives dialog closure.",
 evidence:"Case/model identity and scope remain visible. Witness selections open declared destinations only; this example finding is not executed evidence. Raw record remains one disclosure away.",
 run:"Latest attempt and last acknowledgement are separate. Refusal, unknown, commit and failed refresh have different meanings. Inspect captured actor/action rather than the currently selected actor.",
 history:"Read-only historical inspection never restores silently. Return explicitly selects current review. Real Undo/Redo must use server commands and invalidate stale evidence.",
 factory:"Planned session/base/overlap/combined-result contract. Navigation demonstrates investigation only; no start, merge, approve or land action is offered.",
 connection:"No-case, unconfigured/unavailable and partial states preserve useful context. One relevant recovery action; no automatic retry or source execution. Explicit first-entry routes remain optional."
};
function renderLab(){
  $("state-select").replaceChildren();for(const name of surfaces[view].states){const option=el("option",name);option.value=name;$("state-select").append(option);}$("state-select").value=state();$("state-label").textContent=`${surfaces[view].id} · ${state()}`;$("state-handoff").textContent=handoffs[view];renderPersona();
}
function renderPersona(){const tasks={reviewer:"Reviewer task: identify the exact changed field, find its declared source, and decide what the available evidence does not establish.",modeller:"Modeller task: compare role, source/target and guard entries; close an unsubmitted preview, then revisit the same rule without losing context.",ai:"AI-assisted engineer task: preserve a scoped request through an interrupted proposal, inspect its meaning, and keep owner decisions separate.",factory:"Factory operator task (planned): trace an overlapping abstraction to the exact combined-result requirement without treating branch checks as landing authority."};$("persona-task").textContent=tasks[$("persona-select").value];}
function commandResults(){const query=$("command-query").value.toLowerCase();$("command-results").replaceChildren();for(const[key,value]of Object.entries(surfaces))if(`${value.title} ${value.id} ${key}`.toLowerCase().includes(query))$("command-results").append(button(`${value.id} · ${value.title}`,()=>{$("commands").close();navigate(key,false);}));}
document.querySelectorAll("[data-view]").forEach(node=>node.addEventListener("click",()=>navigate(node.dataset.view,false)));
$("case-select").addEventListener("change",()=>{scrollState.set(`${caseKey}:${view}`,$("surface").scrollTop);caseKey=$("case-select").value;origin=null;render();$("surface-title").focus();announce(`Changed to ${current().id}. This case's own selection restored.`);});
$("return-origin").onclick=()=>{const target=origin;if(!target)return;setSelection(target.selected);origin=null;navigate(target.view,false);const control=[...document.querySelectorAll("[data-design-focus-key]")].find(node=>node.dataset.designFocusKey===target.focus);if(control)control.focus();};
$("state-select").onchange=()=>setState($("state-select").value);$("persona-select").onchange=renderPersona;
$("reset-design").onclick=()=>{caseState.clear();viewState.clear();scrollState.clear();disclosureState.clear();origin=null;caseKey="review";view="changes";render();$("surface-title").focus();announce("Design fixtures reset. No product state was changed.");};
$("preview-close").onclick=closePreview;$("preview-dialog").addEventListener("cancel",event=>{event.preventDefault();closePreview();});
$("preview-apply").onclick=()=>{closePreview();viewState.set(`${caseKey}:edit`,"acknowledged");navigate("edit",false);announce("Acknowledged-but-unrefreshed illustration shown. No actual edit was submitted.");};
function openCommands(){if($("commands").open){$("command-query").focus();return;}if($("workspace-menu").open){$("workspace-menu").close();$("command-open").focus();}$("commands").showModal();$("command-query").value="";commandResults();$("command-query").focus();}
$("command-open").onclick=openCommands;$("command-close").onclick=()=>{$("commands").close();$("command-open").focus();};$("command-query").oninput=commandResults;
$("commands").addEventListener("close",()=>{if(document.activeElement===document.body)$("command-open").focus();});
const compactNavigation=window.matchMedia("(max-width:720px)");
function syncNavigation(){const shown=["model","changes","factory"].includes(view)&&(compactNavigation.matches?document.body.classList.contains("nav-open"):!document.body.classList.contains("nav-hidden"));$("navigation-toggle").setAttribute("aria-expanded",String(shown));}
$("navigation-toggle").onclick=()=>{if(compactNavigation.matches){document.body.classList.toggle("nav-open");if(document.body.classList.contains("nav-open"))$("navigation-close").focus();}else document.body.classList.toggle("nav-hidden");syncNavigation();};
$("navigation-close").onclick=()=>{document.body.classList.remove("nav-open");if(!compactNavigation.matches)document.body.classList.add("nav-hidden");syncNavigation();$("navigation-toggle").focus();};
compactNavigation.addEventListener("change",()=>{document.body.classList.remove("nav-open");syncNavigation();});
$("workspace-open").onclick=()=>{$("workspace-menu").showModal();$("workspace-close").focus();};$("workspace-close").onclick=()=>{$("workspace-menu").close();$("workspace-open").focus();};
$("workspace-menu").querySelectorAll("[data-view]").forEach(node=>node.addEventListener("click",()=>{$("workspace-menu").close();$("surface-title").focus();}));
document.addEventListener("keydown",event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="k"){event.preventDefault();if(!$("preview-dialog").open)openCommands();}if(event.key==="Escape"&&document.body.classList.contains("nav-open"))$("navigation-close").click();});
syncNavigation();render();
