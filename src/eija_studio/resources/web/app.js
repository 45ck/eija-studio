"use strict";
const $ = id => document.getElementById(id);
const el = (tag, text, cls) => {const x=document.createElement(tag); if(text!==undefined)x.textContent=text; if(cls)x.className=cls; return x;};
let token = location.hash.slice(1) || sessionStorage.getItem("eija-session") || "";
if(location.hash){sessionStorage.setItem("eija-session",token); history.replaceState(null,"",location.pathname);}
let current=null, instance=null, status=null, tab="model", busy=false, editId=null, workbench=null, affordanceData=null, lastDiagnostic=null, modelView="working", sourceSequence=0, sourceHistory=[], sourceHistoryIndex=-1, caseHistory=null, historyModel=null, historyLabel="", canvasDirection="AUTO";
const caseViews = new Map();
let inspectorSelection = null;
function fillStates(id,states,value){$(id).replaceChildren(...states.map(s=>el("option",s)));$(id).value=value;}
const notice=(text,error=false)=>{$("notice").textContent=text;$("notice").className=error?"error":"";};
class ApiError extends Error {
  constructor(code, message, details = {}, httpStatus = null) {super(`${code}: ${message}`); this.name = "ApiError"; this.code = code; this.details = details; this.httpStatus = httpStatus;}
}
async function api(path, body) {
  const options = {headers: {Authorization: "Bearer " + token}};
  if (body !== undefined) {options.method = "POST"; options.headers["Content-Type"] = "application/json"; options.body = JSON.stringify(body);}
  const response = await fetch("/api/" + path, options);
  let data; try {data = await response.json();} catch {throw new ApiError("RESPONSE_INVALID", "The server did not return JSON", {}, response.status);}
  if (!response.ok) throw new ApiError(data.code || response.status, data.message || "Request failed", data.details || {}, response.status);
  return data;
}
function reportError(error) {
  lastDiagnostic = {code: error.code || "REQUEST_FAILED", message: error.message, details: error.details || {}};
  notice(error.message + (error.details?.codes?.length ? " · " + error.details.codes.join("; ") : ""), true);
  $("error-details").hidden = false; $("error-json").textContent = JSON.stringify(lastDiagnostic, null, 2);renderProblems();EijaShell.bottom("problems-pane");
}
function clearDiagnostic() {
  lastDiagnostic = null; $("error-details").hidden = true; $("error-json").textContent = ""; renderProblems();
}
function captureTaskFocus(){const target=document.activeElement;return {id:target?.id,action:target?.dataset?.action,meaning:target?.dataset?.meaning};}
function restoreTaskFocus(previous){
  if(!previous.id&&!previous.action&&!previous.meaning)return;
  if(document.activeElement!==document.body&&document.activeElement!==document.documentElement)return;
  const available=node=>node&&!node.disabled&&node.getClientRects().length>0;
  let target=previous.id?$(previous.id):null;
  if(!available(target)&&previous.action)target=[...document.querySelectorAll("[data-action]")].find(node=>node.dataset.action===previous.action);
  if(!available(target)&&previous.meaning)target=[...document.querySelectorAll("[data-meaning]")].find(node=>node.dataset.meaning===previous.meaning);
  if(!available(target)&&previous.id==="create")target=$("propose");
  if(!available(target)&&previous.id==="approve")target=$("apply");
  if(!available(target))target=$("case-title");
  if(available(target))target.focus();
}
async function task(fn,message="Working…"){if(busy)return;const previousFocus=captureTaskFocus();busy=true;notice(message);$("status-agent").textContent=message;document.body.setAttribute("aria-busy","true");try{await fn();}catch(e){reportError(e);}finally{busy=false;$("status-agent").textContent="Provider idle";document.body.removeAttribute("aria-busy");restoreTaskFocus(previousFocus);}}
async function cases() {
  const data=await api("cases"),list=$("case-list"),select=$("case-switcher");list.replaceChildren();select.replaceChildren();
  const empty=el("option",data.length?"Choose a change case…":"No change cases yet");empty.value="";select.append(empty);
  for(const c of data){const b=el("button",c.request.slice(0,90),current?.case.id===c.id?"selected":"");b.append(el("small",c.stage));if(current?.case.id===c.id)b.setAttribute("aria-current","true");b.title=c.request;b.onclick=()=>task(async()=>{await load(c.id);notice("");});list.append(b);
    const option=el("option",c.request.slice(0,65));option.value=c.id;select.append(option);}
  select.value=current?.case.id||"";
  if(!data.length)list.append(el("p","Start an intent to create a case.","muted"));
}
function switchTab(name) {
  tab = name;EijaShell.setArea(name); if (name === "visual") loadVisual();
  if(name === "change" && !current) $("create-panel").hidden=false;
  document.querySelectorAll(".tab-content").forEach(x => {x.hidden = x.id !== name; x.setAttribute("role", "tabpanel");});
  document.querySelectorAll("[data-tab]").forEach(x => {const selected = x.dataset.tab === name; x.classList.toggle("active", selected); x.setAttribute("aria-selected", String(selected)); x.tabIndex = selected ? 0 : -1;});
  for(const group of document.querySelectorAll('[role="tablist"]')){const tabs=[...group.querySelectorAll('[data-tab]')];if(tabs.length&&!tabs.some(button=>button.tabIndex===0))tabs[0].tabIndex=0;}
  const reference=$("reference-views"),selectedReference=reference.querySelector('[aria-selected="true"]');reference.dataset.active=String(!!selectedReference);reference.querySelector("summary").textContent=selectedReference?`Reference: ${selectedReference.textContent}`:"Reference views";
  if(name === "model" && workbench)EijaShell.mountCanvas(`${current?.case.id||workbench.pack.id}:${modelView}`);
}
function formalList(parent,title,items){if(!items||!items.length)return;parent.append(el("h4",title));const ul=el("ul");for(const x of items)ul.append(el("li",typeof x==="string"?x:JSON.stringify(x)));parent.append(ul);}
function explanation(root,x,lead){const box=el("div",undefined,"formal-explain");box.append(el("strong",lead+x.control+" ("+(x.source||"")+")"));box.append(el("p",(x.trace?"Counterexample trace: "+x.trace.map(s=>s.join(" ")).join(" -> ")+(x.final_state?" ends "+x.final_state:""):"Witness: "+JSON.stringify(x.witness))+". "+(x.note||"")));root.append(box);}
function renderFormal(p){const root=$("formal");root.replaceChildren();for(const m of p.blocked_meanings||[]){root.append(el("p","Blocked meaning: "+m.label+" ("+(m.policy_errors||[]).join(", ")+")","formal-blocked"));for(const x of m.explanations||[])explanation(root,x,"Why the policy refuses it: ");}
for(const x of p.explanations||[])explanation(root,x,"Why the policy blocks this: ");
for(const e of p.formal_evidence||[]){const d=el("details",undefined,"formal-item status-"+e.status.toLowerCase());d.append(el("summary",e.kind.replaceAll("_"," ")+": "+e.status+" ("+e.evidence_level.replaceAll("_"," ")+")"));d.append(el("p",e.establishes));formalList(d,"Why this status",e.reasons);formalList(d,"Does not establish",e.does_not_establish);formalList(d,"Assumptions",e.assumptions);if(e.bounds)formalList(d,"Bounds",[JSON.stringify(e.bounds)]);formalList(d,"Counterexamples",e.counterexamples);d.append(el("small","Needs: "+e.prerequisites));root.append(d);}}
async function load(id) {
  const switching=current?.case.id!==id;
  if(switching&&current)caseViews.set(current.case.id,{tab,editId,inspectorSelection,modelView,historyModel,historyLabel,canvasDirection});
  const [next,affordances,historyData]=await Promise.all([api("cases/"+id),api(`cases/${id}/affordances`),api(`cases/${id}/history`).catch(error=>({status:"unavailable",reason:error.code||"HISTORY_UNAVAILABLE"}))]);
  if(switching){instance=null;$("runtime-result").textContent="";const previous=caseViews.get(id);editId=previous?.editId||null;inspectorSelection=previous?.inspectorSelection||null;modelView=previous?.modelView||"working";historyModel=previous?.historyModel||null;historyLabel=previous?.historyLabel||"";canvasDirection=previous?.canvasDirection||"AUTO";if(previous)tab=previous.tab;}
  current=next;affordanceData=affordances;caseHistory=historyData;render();await cases();clearDiagnostic();
}
async function command(action,extra={}){const id=current.case.id;const result=await api(`cases/${id}/${action}`,{expected_version:current.case.version,...extra});await load(id);return result;}
function render(){const c=current.case,p=current.packet,closed=["APPLIED","DISCARDED"].includes(c.stage);$("create-panel").hidden=true;$("workspace").hidden=false;$("case-title").textContent=c.request;$("case-id").textContent=`CHANGE CASE ${c.id.slice(0,10)} / REVISION ${c.version} / BASELINE ${c.baseline_version}`;$("case-stage").textContent=c.stage;$("proposal-summary").textContent=c.proposal?.summary||"No interpretation has been requested. Your request is not yet a semantic change.";$("propose").disabled=!!c.candidate||closed;$("options").replaceChildren();
for(const a of c.proposal?.alternatives||[]){const canonical=current.options[a.interpretation],chosen=c.selected_meaning===a.interpretation;const card=el("article",undefined,"option"+(chosen?" selected":""));card.append(el("small",chosen?"SELECTED BY LOCAL OWNER":canonical.supported?"SUPPORTED MEANING":"BLOCKED / OUT OF SCOPE"),el("h3",canonical.label));for(const consequence of canonical.consequences)card.append(el("p",consequence));const d=el("details");d.append(el("summary","Untrusted provider explanation"),el("p",a.explanation));card.append(d);const b=el("button",chosen?"Meaning selected":canonical.supported?"Select this meaning":"Explain boundary",chosen?"secondary":"");b.dataset.meaning=a.interpretation;b.disabled=closed||!!c.candidate;b.onclick=()=>task(async()=>{await command("select",{interpretation:a.interpretation});notice("Meaning selected. The local baseline has not changed.");});card.append(b);$("options").append(card);}
$("proposal-unknowns").replaceChildren();for(const unknown of c.proposal?.unknowns||[])$("proposal-unknowns").append(el("p","Unresolved: "+unknown,"muted"));$("editor").hidden=!c.candidate;
for(const id of ["save","discard","edit-rule","edit-state","move-node","verify","reset"])$(id).disabled=!c.candidate||closed;
const model = c.candidate || c.baseline;
$("rule-table").replaceChildren();
for (const transition of model.transitions) {
  const row = el("tr"); row.dataset.eijaId = `${workbench?.pack.id || model.id}.rule.${transition.id}`;
  const action = el("td"), choose = el("button", transition.action, "text-button"); choose.onclick = () => {selectTransition(transition.id); switchTab("model");}; action.append(choose); row.append(action);
  [transition.role, transition.from_state, transition.to_state, transition.guards.join(", ")].forEach(value => row.append(el("td", value))); $("rule-table").append(row);
}
$("state-flow").replaceChildren(); $("layout-node").replaceChildren();
for (const state of model.states) {
  const node = el("div", undefined, "state-node"); node.dataset.eijaId = `${model.id}.state-card.${state}`; node.append(el("strong", state));
  for (const t of model.transitions.filter(t => t.from_state === state)) node.append(el("small", `${t.role}: ${t.action} → ${t.to_state}`));
  $("state-flow").append(node); $("layout-node").append(el("option", state));
}
$("impact-summary").textContent = p.impact ? `${p.impact.changed_actions.length} changed actions · ${p.impact.affected.length} modelled dependants · closure ${p.impact.complete ? "complete within this mapping" : "INCOMPLETE"}` : "Select a supported meaning before reviewing a candidate.";
$("impact-json").textContent = JSON.stringify({impact:p.impact, subject:p.subject}, null, 2);
$("journeys").replaceChildren(...(p.projections?.journeys || []).map(j => el("p", j, "muted")));
renderWorkbench(); EijaReview.render($("review-chapters"), current,{terms:workbench.language?.terms,inspectTransition:id=>{modelView="working";switchTab("model");selectTransition(id);},openReference:followReference,openEvidence:()=>switchTab("evidence")});
$("runtime-actions").replaceChildren();for(const action of status?.pack?.actions||[]){const b=el("button",action,"secondary");b.dataset.action=action;b.disabled=!instance||closed;b.onclick=()=>task(async()=>{const result=await api(`cases/${c.id}/execute`,{operation_id:crypto.randomUUID(),actor_id:$("actor").value,instance_id:instance.id,action,expected_version:instance.version});instance=result.instance;await load(c.id);$("runtime-result").textContent="Committed: "+action+". Effects: "+result.effects.join(", ");notice("Commit completed; the displayed state is persisted.");});$("runtime-actions").append(b);}$("runtime-state").textContent=instance?.state||"Not started";$("runtime-version").textContent=instance?`Instance ${instance.id.slice(0,8)} · version ${instance.version} · isolated candidate`:"No candidate state has been executed";$("trace").textContent=JSON.stringify(current.observations,null,2);
$("claims").replaceChildren();for(const [name,value]of Object.entries(p.technical_claims||{})){const card=el("div",undefined,"evidence-card");card.append(el("span",name.replaceAll("_"," ")),el("strong",value));$("claims").append(card);}renderFormal(p);renderProblems();$("blockers").textContent=p.blockers?.length?"Review blocked: "+p.blockers.join(", "):"Technical scope eligible. Human authorisation is still a separate decision.";$("packet").textContent=JSON.stringify(p,null,2);$("questions").replaceChildren();for(const q of p.questions||[]){const div=el("div",undefined,"question"),label=el("label",q.question);label.htmlFor="q-"+q.id;const input=el("input");input.id="q-"+q.id;input.name=q.id;input.autocomplete="off";input.required=true;div.append(label,input);$("questions").append(div);}$("approve").disabled=!p.eligible||closed||c.stage==="APPROVED";$("apply").disabled=c.stage!=="APPROVED"||!p.eligible;$("export").disabled=false;switchTab(tab);}
$("create").onclick=()=>task(async()=>{const c=await api("cases",{request:$("request").value});tab="change";editId=null;await load(c.id);notice("Case created. No provider call or baseline change has occurred.");});$("new-case").onclick=openIntent;document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>{switchTab(b.dataset.tab);if(b.closest("#reference-views")){$("reference-views").open=false;$("reference-views").querySelector("summary").focus();}});
$("propose").onclick=()=>task(async()=>{await command("propose",{consent:$("egress").checked});notice("Interpretations received. No meaning was selected automatically.");},"Requesting an untrusted proposal…");
$("save").onclick=()=>task(async()=>{await command("save");notice("Review checkpoint saved; the active baseline is unchanged.");});$("discard").onclick=()=>task(async()=>{await command("discard");instance=null;render();notice("Candidate closed. History is retained; the baseline is unchanged.");});
function edit(source) {return commitChoice(choiceFor("retarget_source", "state:" + source));}
$("edit-rule").onclick = () => edit($("rejection-source").value);
$("edit-state").onclick = () => edit($("diagram-source").value);
$("edit-target").onclick = () => commitChoice(choiceFor("retarget_target", "state:" + $("target-state").value));
$("edit-role").onclick = () => commitChoice(choiceFor("set_role", "role:" + $("transition-role").value));
$("move-node").onclick=()=>task(async()=>{await command("layout",{change:{node:$("layout-node").value,x:Number($("layout-x").value),y:Number($("layout-y").value)}});notice("Layout metadata changed. Domain receipts remain applicable; exact-presentation approval is cleared.");});
$("reset").onclick=()=>task(async()=>{instance=await command("preview");render();$("runtime-result").textContent="";notice(`Fresh isolated instance created in ${instance.state}.`);});
$("verify").onclick=()=>task(async()=>{await command("verify");notice("Bounded runtime verification finished. Human evidence remains UNKNOWN.");},"Executing the synthetic state / actor / action matrix…");
$("review-form").onsubmit=e=>{e.preventDefault();task(async()=>{const answers={};for(const q of current.packet.questions)answers[q.id]=$("q-"+q.id).value.trim();await command("approve",{subject_hash:current.packet.subject_hash,answers,acknowledge_unknowns:$("acknowledge").checked,scope:"local-demo"});notice("Exact local revision acknowledged. Apply remains a separate action.");});};
$("apply").onclick=()=>task(async()=>{await command("apply");status=await api("status");workbench=await api("workbench");renderWorkbench();notice("Applied to the local demo baseline only. No production system was touched.");});
$("export").onclick=()=>task(async()=>{const data=await api(`cases/${current.case.id}/export`),blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"}),url=URL.createObjectURL(blob),a=el("a");a.href=url;a.download=`eija-${current.case.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notice("Case exported with model, evidence, observations and integrity hash.");});
$("doctor").onclick=()=>task(async()=>{notice(JSON.stringify(await api("doctor")));});
function showPack(pack){if(!pack)return;$("pack-name").textContent=pack.name;if(!$("request").value)$("request").value=pack.demo_request;$("actor").replaceChildren(...pack.actors.map(a=>{const o=el("option",`${a.role} · ${a.assigned?"assigned":"unassigned"} / ${a.active?"active":"revoked"}`);o.value=a.id;return o;}));}
task(async () => {
  [status, workbench] = await Promise.all([api("status"), api("workbench")]);
  showPack(status.pack); $("connection").textContent = `${status.provider} · ${status.network_enabled ? "network enabled" : "local / offline"}`;
  renderWorkbench(); renderProblems(); EijaReview.render($("review-chapters"), null); switchTab("model"); await cases(); notice("");
});
// Visual view: diagram text is generated server-side from the executable model and drawn inside a sandboxed frame
// (see visual-frame.js and docs/SECURITY_AND_TRUST.md). This page never parses or inserts diagram markup itself.
let visual={data:null,ready:false,seq:0};
function diffItems(s){const at=x=>Array.isArray(x)?x.join(", ")||"none":String(x),out=[];if(!s)return out;if(s.initial_state)out.push(`Start state: ${s.initial_state.before} → ${s.initial_state.after}`);
for(const [label,list] of [["Added states",s.added_states],["Removed states",s.removed_states],["Added actions",s.added_actions],["Removed actions",s.removed_actions]])if(list.length)out.push(`${label}: ${list.join(", ")}`);
for(const [action,changes] of Object.entries(s.changed_actions))out.push(`Changed ${action}: `+changes.map(c=>`${c.field} ${at(c.before)} → ${at(c.after)}`).join("; "));
return out.length?out:["No semantic change between baseline and candidate."];}
function visualPanels(){const v=visual.data.views,d=visual.data,action=$("visual-action").value,list=[{id:"before",title:"Before (baseline)",note:"The active rules.",text:v.state_before,group:"row"}];
if(v.state_after){list.push({id:"after",title:"After (candidate)",note:"The rules if this candidate were applied.",text:v.state_after,group:"row"},{id:"diff",title:"Diff",note:"Nodes: green added, red removed (dashed outline), amber changed. Edges cannot be coloured in a state diagram, so a label starting + - or ~ marks an added, removed or changed transition and a ~ label names what changed; the list below repeats it as text.",text:v.diff,items:diffItems(d.summary),group:"row"},{id:"impact",title:"Ripple: what this change touches",note:d.impact.envelope,text:v.impact});}
if(v.sequences[action])list.push({id:"sequence",title:"Commit protocol: "+action,note:"Order of checks and writes in one atomic commit.",text:v.sequences[action]});
list.push({id:"journey",title:"Journeys by role",note:"Only transitions each role may perform.",text:v.journey});if(v.class)list.push({id:"class",title:"Domain contracts",note:"Introspected from the typed contracts.",text:v.class});return list;}
function postVisual(){const frame=$("visual-frame");if(!visual.ready||!visual.data||!frame.contentWindow)return;frame.contentWindow.postMessage({type:"eija.visual.render",panels:visualPanels()},"*");}
window.addEventListener("message",e=>{const frame=$("visual-frame");if(e.source!==frame.contentWindow)return;const m=e.data||{};if(m.type==="eija.visual.ready"){visual.ready=true;postVisual();}else if(m.type==="eija.visual.size"&&Number.isFinite(m.height))frame.style.height=Math.min(Math.max(m.height,240),16000)+"px";});
$("visual-action").onchange=postVisual;
async function loadVisual(){if(!current)return;const id=current.case.id,mine=++visual.seq,frame=$("visual-frame");if(!frame.getAttribute("src"))frame.setAttribute("src","/visual-frame");
try{const data=await api(`cases/${id}/diagrams`);if(mine!==visual.seq)return;visual.data=data;const select=$("visual-action"),previous=select.value,actions=Object.keys(data.views.sequences);select.replaceChildren(...actions.map(x=>el("option",x)));
const added=actions.find(x=>!current.case.baseline.transitions.some(t=>t.action===x));select.value=actions.includes(previous)?previous:added||actions[0]||"";
const subject=current.packet.subject?.semantic,candidate=data.sources.candidate;
$("visual-source").textContent=`Generated from workflow hash ${data.sources.baseline.slice(0,12)} (baseline)`+(candidate?` and ${candidate.slice(0,12)} (candidate) · ${candidate===subject?"matches the evidence subject":"DOES NOT MATCH the evidence subject"}`:" · no candidate yet: select a meaning to see the diff and ripple")+(data.policy_violations&&data.policy_violations.length?" · POLICY BLOCKED: "+data.policy_violations.join("; "):"");
postVisual();}catch(e){reportError(e);}}

function workingModel() {return current ? modelView === "history" && historyModel ? historyModel : modelView === "baseline" ? current.case.baseline : current.case.candidate || current.case.baseline : workbench?.model;}
function editable() {return modelView === "working" && !!current?.case.candidate && !["APPLIED", "DISCARDED"].includes(current.case.stage);}
function selectedTransition() {return workingModel()?.transitions.find(t => t.id === editId);}
function choiceFor(kind, target) {return EijaCanvas.entries(affordanceData?.affordances, editId, kind).find(a => a.target === target);}
function fillChoices(id, kind, currentValue) {
  const select = $(id), prefix = kind === "set_role" ? "role:" : "state:";
  select.replaceChildren();
  const unchanged = el("option", currentValue ? `${currentValue} (current)` : "Select a transition first"); unchanged.value = currentValue || ""; select.append(unchanged);
  for (const entry of EijaCanvas.entries(affordanceData?.affordances, editId, kind)) {
    const name = entry.target.slice(prefix.length), option = el("option", `${name} · ${entry.legal ? "allowed" : "refused: " + entry.codes.join(", ")}`);
    option.value = name; select.append(option);
  }
  select.value = currentValue || ""; select.disabled = !editable() || !selectedTransition();
}
function renderEditor() {
  const model = workingModel(), select = $("transition-select");
  select.replaceChildren(); const prompt = el("option", "Select a transition…"); prompt.value = ""; select.append(prompt);
  for (const transition of model?.transitions || []) {const option = el("option", `${transition.action} · ${transition.from_state} → ${transition.to_state}`); option.value = transition.id; select.append(option);}
  if (!model?.transitions.some(t => t.id === editId)) editId = null;
  select.value = editId || ""; const target = selectedTransition(), details = $("transition-details"); details.replaceChildren();
  if (target) {
    details.dataset.eijaId = `${workbench.pack.id}.transition-detail.${target.id}`;
    details.append(el("h3", target.action), el("p", `${target.id} · ${target.role}`));
    for (const [label, values] of [["Guards", target.guards], ["Required effects", target.required_effects], ["Forbidden effects", target.forbidden_effects]]) {
      const group=el("details"),list=el("ul");group.append(el("summary",`${label} · ${(values||[]).length}`));for(const value of values||[])list.append(el("li",value));
      if(!list.childElementCount)list.append(el("li","None declared"));group.append(list);details.append(group);
    }
  } else details.append(el("p", "Select an edge on the canvas or choose a transition above to inspect its guards and effects.", "muted"));
  $("edit-fields").hidden=!target;
  for (const id of ["rejection-source", "diagram-source", "model-source"]) fillChoices(id, "retarget_source", target?.from_state);
  fillChoices("target-state", "retarget_target", target?.to_state); fillChoices("transition-role", "set_role", target?.role);
  for (const id of ["edit-rule", "edit-state", "edit-source", "edit-target", "edit-role", "cancel-draft"]) $(id).disabled = !editable() || !target;
  $("rejection-label").textContent = target ? `${target.action} may start from` : "Select a transition in Model first";
  $("diagram-label").textContent = target ? `${target.action} source state` : "Select a transition in Model first";
}
function renderCanvas() {
  $("canvas-direction").value=canvasDirection;
  EijaCanvas.render($("model-canvas"), {model: workingModel(), layout: current?.case.layout || {}, pack: workbench.pack.id,
    direction:canvasDirection, selected: editId, affordances: affordanceData?.affordances, editable: editable(), onSelect: selectTransition, onDrop: commitChoice, onNotice: notice});
  EijaShell.mountCanvas(`${current?.case.id||workbench.pack.id}:${modelView}`);
}
function selectTransition(id) {const returnFocus=$("model-canvas").contains(document.activeElement);editId = id || null;inspectorSelection=editId?{kind:"transition",id:editId}:null;EijaShell.toggle("inspector",true);renderEditor();renderSelectionDetail();renderCanvas();if(returnFocus)$("model-canvas").querySelector(".model-edge.selected")?.focus();}
function cancelDraft() {
  if (busy || !editable() || !selectedTransition()) return;
  renderEditor(); notice("Unsent fields reset to the loaded model; no transaction was sent.");
}
$("cancel-draft").onclick = cancelDraft;
$("edit-fields").addEventListener("keydown", event => {
  if (event.key === "Escape" && !busy) {event.preventDefault(); event.stopPropagation(); cancelDraft();}
});
function renderWorkbench() {
  if (!workbench) return;
  const model = workingModel(), pack = workbench.pack;
  if (!current) {
    $("case-title").textContent = "Explore the loaded baseline"; $("case-id").textContent = "No change case selected"; $("case-stage").textContent = "BASELINE";
    for (const id of ["propose", "save", "discard", "move-node", "verify", "reset", "approve", "apply", "export"]) $(id).disabled = true;
  }
  $("explorer-pack").textContent = pack.name; $("model-title").textContent = pack.name;
  $("model-revision").textContent = current ? `r${current.case.version} · ${modelView==="history"?"history":modelView==="baseline"?"original":current.case.candidate?"candidate":"baseline"}` : `v${pack.version}`;
  $("model-empty").hidden=false;
  $("model-empty").textContent=modelView==="history"?`Read-only historical preview · ${historyLabel}. Choose Working model to return.`:modelView==="baseline"?"Original baseline · read only. Switch to Working model to edit the candidate.":editable()?"Drag an endpoint or use the inspector. Every edit is checked by the kernel.":"Select a transition to inspect it. Start an intent to change the model.";
  $("model-version").querySelector('option[value="history"]').hidden=!historyModel;$("model-version").value=modelView;$("model-version").querySelector('option[value="baseline"]').disabled=!current?.case.candidate;
  $("undo-edit").disabled=!caseHistory?.can_undo||!current||["APPLIED","DISCARDED"].includes(current.case.stage);
  $("redo-edit").disabled=!caseHistory?.can_redo||!current||["APPLIED","DISCARDED"].includes(current.case.stage);
  $("source-status").textContent = status?.trusted_fixture ? "Source identity matches its release fixture. This identifies reviewed bytes; it does not prove correctness." : "SOURCE_REVIEW_REQUIRED · implementation changed since the owner-stamped fixture. Verification and apply remain blocked pending source review.";
  $("source-status").classList.toggle("source-required", !status?.trusted_fixture);
  $("status-model").textContent = `Pack ${pack.id} · ${current ? "revision " + current.case.version : "baseline"} · ${String(affordanceData?.semantic_hash || pack.digest || "unknown").slice(0, 12)}`;
  $("repository-status").textContent = EijaSource.state(workbench.connection).title;
  EijaSource.render($("source-view"), workbench.connection);
  EijaTree.render($("domain-tree"), workbench, model, showSelection);renderEditor();renderSelectionDetail();renderCanvas();EijaShell.renderHistory(current,caseHistory,previewHistory);
}
function showSelection(kind, item) {
  inspectorSelection={kind,id:item.id};
  EijaShell.toggle("inspector",true);
  if(kind==="transition")selectTransition(item.id);else renderSelectionDetail();
  if(["transition","state"].includes(kind))switchTab("model");
}
function renderSelectionDetail() {
  const kind=inspectorSelection?.kind,id=inspectorSelection?.id,model=workingModel();
  const items=kind==="transition"?model?.transitions:kind==="state"?model?.states.map(value=>({id:value})):kind==="term"?workbench.language?.terms:kind==="law"?workbench.laws:kind==="role"?workbench.roles:[];
  const item=items?.find(value=>value.id===id),root=$("selection-detail");
  root.replaceChildren();$("inspector-impact").replaceChildren();delete root.dataset.eijaId;
  if(!item){inspectorSelection=null;root.append(el("h3","Explore a concept"),el("p","Select a term, state, role or law in the explorer.","muted"));return;}
  root.dataset.eijaId = `${workbench.pack.id}.detail.${kind}.${item.id}`;
  root.append(el("h3", item.label || item.action || item.id), el("p", kind==="transition"?`${item.from_state} → ${item.to_state}`:item.definition || item.description || `Model ${kind}`));
  for (const field of ["code", "kind", "role", "state", "action"]) if (item[field]) root.append(el("p", `${field}: ${item[field]}`));
  for (const field of ["refs", "binds"]) if (item[field]?.length) {
    root.append(el("h4", field === "refs" ? "Model references" : "Declared source bindings")); const list = el("ul");
    for (const ref of item[field]) {
      const li = el("li"), link = el("button", ref, "text-button"); link.onclick = () => followReference(ref); li.append(link); list.append(li);
    } root.append(list);
  }
  if (kind === "law") {const detail = el("details"); detail.append(el("summary", "Exact declared law"), el("pre", JSON.stringify(item, null, 2))); root.append(detail);}
  if (kind === "term" && workbench.connection?.status === "connected") {
    const impact = el("button", "Find repository references", "secondary");
    impact.onclick=()=>task(async()=>{const data=await api("repository/impact?term="+encodeURIComponent(item.id));EijaShell.renderImpact($("inspector-impact"),data,openSource);notice("Known dependency links loaded. Unknown dependencies remain outside this mapping.");});root.append(impact);
  }
}
function followReference(ref) {
  if(ref.startsWith("repo://")){openSource(ref);return;}
  const colon = ref.indexOf(":"), kind = ref.slice(0, colon), id = ref.slice(colon + 1), model = workingModel();
  const values = kind === "law" ? workbench.laws : kind === "state" ? model.states.map(value => ({id:value})) : kind === "transition" ? model.transitions : kind === "role" ? workbench.roles : [];
  const item = values.find(value => value.id === id);
  if(item)showSelection(kind,item);else notice(`Reference not found in the declared model: ${ref}`);
}
function renderProblems() {
  const problems = $("problems"); problems.replaceChildren();
  const p = current?.packet;
  const source = workbench?.connection;
  if (source && source.status !== "connected") problems.append(el("li", `Repository ${source.status || "unknown"}: ${source.reason || "No source snapshot available"}`, "diagnostic"));
  if (source?.status === "connected" && ["FAIL", "REVIEW", "NOT_RUN"].includes(source.lint?.verdict)) {
    const item = el("li"), button = el("button", `Source-link lint: ${source.lint.verdict} · ${source.lint.findings?.length || 0} findings. Inspect source checks.`, "text-button");
    button.onclick = () => switchTab("source"); item.append(button); problems.append(item);
  }
  if (!status?.trusted_fixture) problems.append(el("li", "SOURCE_REVIEW_REQUIRED · owner review of changed implementation is outstanding.", "diagnostic"));
  for (const code of p?.blockers || []) problems.append(el("li", String(code), "diagnostic"));
  if (lastDiagnostic) {
    problems.append(el("li", lastDiagnostic.message, "diagnostic"));
    for (const code of lastDiagnostic.details.codes || []) problems.append(el("li", code, "diagnostic"));
    for (const ref of lastDiagnostic.details.refs || []) {const li = el("li"), button = el("button", ref, "text-button"); button.onclick = () => followReference(ref); li.append(button); problems.append(li);}
  }
  if (!problems.childElementCount) problems.append(el("li", p ? "No review blockers reported by the current packet." : "No case selected; case checks have not run."));
  EijaShell.renderEvidence($("evidence-summary"),p);$("problem-count").textContent=problems.childElementCount;
  $("status-evidence").textContent = p ? `Technical eligibility: ${p.eligible ? "eligible" : "blocked"} · human UNKNOWN` : "Evidence: NOT_RUN · human UNKNOWN";
}
function commitChoice(choice) {
  if (!editable() || !choice) {notice("Choose a different server-listed destination for the selected transition."); return;}
  return task(async () => {
    const id = current.case.id, expectedVersion = current.case.version;
    const check = await api(`cases/${id}/edit/check`, {transaction: choice.transaction});
    if (!check.legal) {
      reportError(new ApiError("EDIT_REFUSED", "The kernel refused this edit; the model is unchanged", {codes: check.codes, refs: check.refs}));
      renderCanvas(); return;
    }
    await api(`cases/${id}/edit`, {expected_version: expectedVersion, transaction: choice.transaction});
    instance = null; lastDiagnostic = null; $("error-details").hidden = true;
    await load(id);
    notice("One typed transaction committed. The canvas has reloaded the server model; prior evidence and decisions must be reconsidered.");
  }, "Checking the typed edit…");
}
$("transition-select").onchange = event => selectTransition(event.target.value);
$("edit-source").onclick = () => edit($("model-source").value);
document.querySelector(".editor-navigation").addEventListener("keydown", event => {
  const group=event.target.closest('[role="tablist"]');if(!group)return;
  const tabs = [...group.querySelectorAll("[data-tab]")], index = tabs.indexOf(event.target); if (index < 0) return;
  const next = event.key === "ArrowRight" ? tabs[(index + 1) % tabs.length] : event.key === "ArrowLeft" ? tabs[(index + tabs.length - 1) % tabs.length] : event.key === "Home" ? tabs[0] : event.key === "End" ? tabs[tabs.length - 1] : null;
  if (next) {event.preventDefault(); switchTab(next.dataset.tab); next.focus();}
});

$("reference-views").addEventListener("keydown",event=>{if(event.key==="Escape"){$("reference-views").open=false;$("reference-views").querySelector("summary").focus();event.stopPropagation();}});
document.addEventListener("pointerdown",event=>{if(!$("reference-views").contains(event.target))$("reference-views").open=false;});
const paletteCommands = [
  ["New change case",openIntent],
  ["Toggle explorer",()=>EijaShell.toggle("explorer")],
  ["Toggle inspector",()=>EijaShell.toggle("inspector")],
  ["Show local case history",()=>EijaShell.bottom("history-pane")],
  ["Fit model overview",()=>{switchTab("model");EijaShell.fit();}],
  ...[...document.querySelectorAll("[data-tab]")].map(button => [`Open ${button.textContent}`, () => {switchTab(button.dataset.tab); button.focus();}]),
  ["Focus domain explorer", () => $("domain-tree").querySelector('[tabindex="0"]')?.focus()],
  ["Refresh current model", () => task(refreshCurrentModel)],
  ["Select a transition", () => {switchTab("model");EijaShell.toggle("inspector",true); $("transition-select").focus();}]
];
async function refreshCurrentModel() {
  if(current)await load(current.case.id);else{workbench=await api("workbench");renderWorkbench();clearDiagnostic();}
  notice("Current model refreshed from the server.");
}
function filterCommands() {
  const query = $("palette-search").value.toLowerCase(), root = $("palette-results"); root.replaceChildren();
  for (const [label, action] of paletteCommands.filter(([label]) => label.toLowerCase().includes(query))) {
    const button = el("button", label, "palette-command"); button.onclick = () => {$("command-palette").close(); action();}; root.append(button);
  }
  if (!root.childElementCount) root.append(el("p", "No matching commands."));
}
function openPalette() {$("palette-search").value = ""; filterCommands(); $("command-palette").showModal(); $("palette-search").focus();}
$("open-palette").onclick = openPalette; $("close-palette").onclick = () => $("command-palette").close();
$("palette-search").oninput = filterCommands;
$("palette-search").onkeydown = event => {if (["ArrowDown", "Enter"].includes(event.key)) {event.preventDefault(); $("palette-results").querySelector("button")?.focus();}};
document.addEventListener("keydown", event => {if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {event.preventDefault(); if($("command-palette").open) $("command-palette").close(); else openPalette();}});

$("open-source").onclick = () => switchTab("source");
$("refresh-source").onclick = () => task(async () => {
  [workbench, status] = await Promise.all([api("workbench"), api("status")]);
  renderWorkbench(); renderProblems();
  const connection = EijaSource.state(workbench.connection);
  notice(connection.connected ? "Repository snapshot refreshed. Source indexing did not execute project tests." : connection.title + ": " + connection.reason, !connection.connected);
}, "Reading the configured repository snapshot…");

function previewHistory(model,label){historyModel=model;historyLabel=label;modelView="history";editId=null;inspectorSelection=null;switchTab("model");renderWorkbench();notice("Historical model preview · read only. Use Working model to return to the current candidate.");}
function openIntent(){switchTab("change");$("create-panel").hidden=false;$("request").focus();notice("");}
$("case-switcher").onchange=event=>{const id=event.target.value;$("case-switcher").value=current?.case.id||"";if(id)task(async()=>{try{await load(id);notice("");}finally{$("case-switcher").value=current?.case.id||"";}});};
$("canvas-direction").onchange=event=>{canvasDirection=event.target.value;renderCanvas();EijaShell.readable();};
$("model-version").onchange=event=>{modelView=event.target.value;renderWorkbench();};
async function openSource(reference,record=true){
  const sequence=++sourceSequence;switchTab("code");EijaShell.sourceLoading(reference);
  try{
    const data=await api("repository/source?reference="+encodeURIComponent(reference));
    if(sequence!==sourceSequence)return;EijaShell.renderSource(data);
    if(record&&data.status==="connected"){sourceHistory=sourceHistory.slice(0,sourceHistoryIndex+1);sourceHistory.push(reference);sourceHistoryIndex=sourceHistory.length-1;}
    $("source-back").disabled=sourceHistoryIndex<=0;
  }catch(error){if(sequence===sourceSequence){EijaShell.sourceError(error.message,error.code);notice(error.message,true);}}
}
$("source-open-form").onsubmit=event=>{event.preventDefault();const ref=$("source-reference").value.trim();if(ref)openSource(ref);};
$("source-back").onclick=()=>{if(sourceHistoryIndex>0){sourceHistoryIndex--;openSource(sourceHistory[sourceHistoryIndex],false);}};
$("undo-edit").onclick=()=>task(async()=>{if(!caseHistory?.can_undo)return;await command("undo");instance=null;modelView="working";render();notice("Last semantic edit undone by the kernel. Earlier receipts are retained; eligibility is recomputed.");});
$("redo-edit").onclick=()=>task(async()=>{if(!caseHistory?.can_redo)return;await command("redo");instance=null;modelView="working";render();notice("Semantic edit reapplied by the kernel. The displayed model was reloaded from the server.");});
EijaShell.init({newIntent:openIntent,openTab:switchTab});
