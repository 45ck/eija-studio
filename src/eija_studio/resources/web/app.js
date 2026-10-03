"use strict";
const $ = id => document.getElementById(id);
const el = (tag, text, cls) => {const x=document.createElement(tag); if(text!==undefined)x.textContent=text; if(cls)x.className=cls; return x;};
let token = location.hash.slice(1) || sessionStorage.getItem("eija-session") || "";
if(location.hash){sessionStorage.setItem("eija-session",token); history.replaceState(null,"",location.pathname);}
let current=null, instance=null, status=null, tab="model", busy=false, editId=null, workbench=null, affordanceData=null, lastDiagnostic=null, modelView="working", sourceSequence=0, sourceHistory=[], sourceHistoryIndex=-1, caseHistory=null, historyModel=null, historyLabel="", canvasDirection="AUTO";
const caseViews = new Map(), comparisonViews = new Map();
let comparison = null, comparisonSelection = null, sourceRecord = null, sourcePending = false, impactSequence = 0;
function renderChanges(){
  comparison?.destroy();comparisonSelection=null;
  const origin=current?{id:current.case.id,version:current.case.version}:null, key=JSON.stringify([origin?.id,origin?.version]);
  comparison=EijaCompare.render($("review-chapters"),current,{terms:workbench?.language?.terms,state:comparisonViews.get(key),navigatorRoot:$("task-navigator"),
    onStateChange:value=>comparisonViews.set(key,value),onSelection:rememberComparisonSelection,
    openNavigator:()=>{navigatorMode="task";renderNavigator();EijaShell.reveal("explorer");$("task-navigator").querySelector("button.selected,button")?.focus();},
    inspectTransition:(id,selection)=>{if(selection?.case===origin?.id&&selection?.revision===origin?.version&&selection?.kind==="transition"&&selection.id===id&&rememberComparisonSelection(selection))inspectWorkingTransition(id,origin);},
    openImpact:(navigation,selection)=>openComparisonImpact(navigation,selection),
    openReference:(ref,selection)=>{if(!selection||rememberComparisonSelection(selection))followReference(ref);},
    openEvidence:selection=>{if(rememberComparisonSelection(selection))switchTab("evidence");}});
}
let inspectorSelection = null;
let navigatorMode="task";
try{if(sessionStorage.getItem("eija-ui-navigator")==="domain")navigatorMode="domain";}catch{/* Optional UI preference. */}
function selectedConcept(){
  const kind=inspectorSelection?.kind,id=inspectorSelection?.id,model=workingModel();
  const items=kind==="transition"?model?.transitions:kind==="state"?model?.states.map(value=>({id:value})):kind==="term"?workbench?.language?.terms:kind==="law"?workbench?.laws:kind==="role"?workbench?.roles:[];
  return items?.find(value=>value.id===id)||null;
}
function renderNavigator(){
  EijaShell.setNavigatorPinned?.(navigatorMode === "domain");
  if(!workbench)return;
  const domain=navigatorMode==="domain"||tab==="model";
  $("navigator-mode").value=navigatorMode;EijaTree.setVisible($("domain-tree"),domain);
  $("task-navigator").hidden=domain||tab!=="review";
  $("repository-change-navigator").hidden=domain||tab!=="repository-changes";
  const root=$("navigator-context");root.hidden=domain||["review","repository-changes"].includes(tab);if(root.hidden)return;
  const selectedChange=currentComparisonSelection();
  const contextKey=JSON.stringify([workbench.pack.digest,tab,current?.case.id,current?.case.version,modelView,historyLabel,inspectorSelection,selectedChange]);
  if(root.dataset.contextKey===contextKey)return;root.dataset.contextKey=contextKey;root.replaceChildren();
  root.append(el("h3",{evidence:"Review context",code:"Source context",change:"Intent context",try:"Preview context"}[tab]||"Workspace context"));
  root.append(el("p",current?`Case revision ${current.case.version} · ${current.case.stage}`:"Loaded baseline · no change case"));
  if(selectedChange){
    root.append(el("strong",`Selected change: ${selectedChange.kind} · ${selectedChange.id}`));
    const back=el("button","Return to selected change","text-button");back.onclick=()=>openComparisonSelection();root.append(back);
  }
  const item=selectedConcept();
  if(item){
    const context=selectedChange?el("details"):root;
    if(selectedChange){context.append(el("summary",`Model inspector: ${inspectorSelection.kind} · ${item.id}`));root.append(context);}
    context.append(el("strong",item.label||item.action||item.id),el("p",`${inspectorSelection.kind} · ${item.id}`));
    const refs=[...new Set([...(item.refs||[]),...(item.binds||[])])];
    const detail=el("details"),list=el("ul");detail.append(el("summary",`Related model / source · ${refs.length}`));
    for(const ref of refs){const li=el("li"),button=el("button",ref,"text-button");button.onclick=()=>followReference(ref);li.append(button);list.append(li);}detail.append(list);
    if(!refs.length)detail.append(el("p","No direct references declared for this concept.","muted"));context.append(detail);
    const inspect=el("button","Inspect selected concept","text-button");inspect.onclick=()=>{EijaShell.reveal("inspector");renderSelectionDetail();};context.append(inspect);
  }else if(!selectedChange)root.append(el("p","No model concept selected. Pin Domain to explore concepts.","muted"));
  if(modelView!=="working")root.append(el("p",modelView==="history"?`Historical model preview · ${historyLabel}`:"Original baseline preview","subject-warning"));
  if(tab==="evidence")root.append(el("p","Checks in the editor describe the exact candidate subject, not a per-concept verdict.","muted"));
}
$("navigator-mode").onchange=event=>{
  navigatorMode=event.target.value==="domain"?"domain":"task";
  try{sessionStorage.setItem("eija-ui-navigator",navigatorMode);}catch{/* Optional UI preference. */}
  renderNavigator();
};
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
  if (!response.ok) {
    if(typeof data?.code!=="string"||typeof data?.message!=="string")throw new ApiError("RESPONSE_INVALID","The server did not return a structured refusal.",{},response.status);
    const error=new ApiError(data.code,data.message,data.details||{},response.status);error.responseValid=true;throw error;
  }
  return data;
}
function reportError(error,{reveal=true}={}) {
  lastDiagnostic = {code: error.code || "REQUEST_FAILED", message: error.message, details: error.details || {}};
  notice(error.message + (error.details?.codes?.length ? " · " + error.details.codes.join("; ") : ""), true);
  $("error-details").hidden = false; $("error-json").textContent = JSON.stringify(lastDiagnostic, null, 2);renderProblems();if(reveal)EijaShell.bottom("problems-pane",{temporary:true});
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
let caseInventory=null, caseListState="loading", caseListSequence=0;
function renderCasePicker(){
  const select=$("case-switcher"),message=$("case-picker-status"),active=current?.case;
  const entries=(caseInventory||[]).map(item=>item.id===active?.id?active:item),retained=active&&!entries.some(item=>item.id===active.id);
  if(retained)entries.unshift(active);
  const empty=caseListState==="ready"&&!entries.length,options=[];
  const placeholder=el("option",empty?"No change cases yet":caseListState==="loading"&&!entries.length?"Loading change cases…":caseListState==="unavailable"&&!entries.length?"Case list unavailable":"Choose a change case…");placeholder.value="";options.push(placeholder);
  for(const item of entries){const option=el("option",`${item.request} · ${item.stage} · ${item.id}`);option.value=item.id;option.title=item.request;options.push(option);}
  select.replaceChildren(...options);select.value=active?.id||"";select.hidden=empty;select.disabled=!entries.length;
  select.dataset.listState=caseListState;$("case-picker-label").hidden=empty;
  const retainedMessage=entries.length?" Retained choices are shown; their list status may be older.":"";
  message.textContent=caseListState==="loading"?`Refreshing case list…${retainedMessage}`:caseListState==="unavailable"?`Case list unavailable.${retainedMessage} Refresh the list to try again.`:empty?"No change cases yet.":retained?"The current case is the last loaded snapshot; it is absent from the latest case list.":"";
  message.hidden=!message.textContent;$("case-picker-retry").hidden=caseListState!=="unavailable";
}
function focusCasePicker(){
  const select=$("case-switcher");
  const target=!select.hidden&&!select.disabled?select:caseListState==="unavailable"?$("case-picker-retry"):caseListState==="ready"?$("start-intent"):$("case-picker-status");target.focus();
}
async function cases() {
  const sequence=++caseListSequence;caseListState="loading";renderCasePicker();
  try{
    const data=await api("cases");if(sequence!==caseListSequence)return false;
    if(!Array.isArray(data)||data.some(item=>!item||typeof item.id!=="string"||!item.id||typeof item.request!=="string"||typeof item.stage!=="string")||new Set(data.map(item=>item.id)).size!==data.length)throw new ApiError("CASE_LIST_INVALID","The server did not provide a valid change case list.");
    caseInventory=data;caseListState="ready";renderCasePicker();return true;
  }catch(error){if(sequence!==caseListSequence)return false;caseListState="unavailable";renderCasePicker();throw error;}
}

let lastComparisonTab="review";
const workDestinations = [["model","Model"],["code","Source"],["change","Intent"],["review","Changes"],["try","Run"],["evidence","Evidence"],["impact","Rules & ripple"],["visual","Diagrams"],["source","Repository"]];
function openWorkTab(name){switchTab(name==="review"?lastComparisonTab:name);}
function openWorkDestination(name){
  if(!workDestinations.some(([id])=>id===name))return;
  openWorkTab(name);
  const primary=["review","repository-changes"].includes(tab)?"review":tab;
  const target=document.querySelector(`[data-tab="${primary}"]`)||$(tab);
  if(target?.getClientRects().length)target.focus();
}
function switchTab(name) {
  const focused=document.activeElement;
  const comparing=["review","repository-changes"].includes(name),primary=comparing?"review":name;
  const hidingComparisonFocus=comparing?["review","repository-changes"].some(id=>id!==name&&$(id).contains(focused)):$("comparison-workspace").contains(focused);
  if(comparing)lastComparisonTab=name;
  tab = name;EijaShell.setArea(name); if (name === "visual") loadVisual();
  if(name === "change" && !current) $("create-panel").hidden=false;
  document.querySelectorAll(".tab-content").forEach(x => {x.hidden = x.id !== (comparing?"comparison-workspace":name); x.setAttribute("role", "region");});
  document.querySelectorAll("[data-tab], [data-workspace-view]").forEach(x => {
    const selected=(x.dataset.tab||x.dataset.workspaceView)===primary;x.classList.toggle("active",selected);
    if(selected)x.setAttribute("aria-current","page");else x.removeAttribute("aria-current");
  });
  document.querySelectorAll("[data-comparison-tab]").forEach(button=>{
    const selected=button.dataset.comparisonTab===lastComparisonTab;button.setAttribute("aria-selected",String(selected));button.tabIndex=selected?0:-1;
    $(button.dataset.comparisonTab).hidden=button.dataset.comparisonTab!==name;
  });
  $("comparison-workspace").dataset.comparisonView=lastComparisonTab;
  const secondary=!document.querySelector(`[data-tab="${primary}"]`),destination=$("workspace-destination");
  destination.hidden=!secondary;destination.textContent=secondary?` · ${workDestinations.find(([id])=>id===primary)?.[1]||primary}`:"";
  if(name === "model" && workbench)EijaShell.mountCanvas(`${current?.case.id||workbench.pack.id}:${modelView}`);
  if(name === "evidence")renderEvidenceContext();
  renderNavigator();
  if(hidingComparisonFocus&&[focused,document.body,document.documentElement].includes(document.activeElement)){
    const target=document.querySelector(comparing?`[data-comparison-tab="${name}"]`:`[data-tab="${primary}"]`);
    if(target?.getClientRects().length)target.focus();else if($(name)?.getClientRects().length)$(name).focus();
  }
}
function formalList(parent,title,items){if(!items||!items.length)return;parent.append(el("h4",title));const ul=el("ul");for(const x of items)ul.append(el("li",typeof x==="string"?x:JSON.stringify(x)));parent.append(ul);}
function explanation(root,x,lead){const box=el("div",undefined,"formal-explain");box.append(el("strong",lead+x.control+" ("+(x.source||"")+")"));box.append(el("p",(x.trace?"Counterexample trace: "+x.trace.map(s=>s.join(" ")).join(" -> ")+(x.final_state?" ends "+x.final_state:""):"Witness: "+JSON.stringify(x.witness))+". "+(x.note||"")));root.append(box);}
function evidenceValue(value){return typeof value==="string"?value:JSON.stringify(value);}
function evidenceKey(p){return typeof p.subject_hash==="string"&&p.subject_hash?JSON.stringify([current?.case.id||"no-case",p.subject_hash]):"";}
function evidenceSubjectIssue(p,e){
  if(!evidenceKey(p))return "Subject unavailable; reported result is not bound to an identified packet.";
  if(e.subject_hash!==undefined&&e.subject_hash!==p.subject_hash)return "Subject mismatch; reported result is not evidence for this packet.";
  if(e.subject!==undefined&&(!e.subject||typeof e.subject!=="object"||Array.isArray(e.subject)||!Object.keys(e.subject).length||Object.keys(e.subject).length!==Object.keys(p.subject||{}).length||Object.entries(e.subject).some(([name,value])=>p.subject?.[name]!==value)))return "Subject mismatch or incomplete identity; reported result dimensions do not match this packet.";
  return "";
}
function evidenceSummary(row,name,status,scope,issue){
  const summary=el("summary");summary.append(el("span",name,"evidence-name"),el("strong",evidenceValue(status),"evidence-status"),el("span",scope,"evidence-scope"));
  if(issue)summary.append(el("span",issue,"evidence-warning"));
  row.append(summary);
}
function inspectionDisclosure(parent,label,key,opened){
  const details=el("details",undefined,"formal-inspection-detail");details.append(el("summary",label));
  details.dataset.evidenceKey=key;details.open=opened.has(key);parent.append(details);return details;
}
function inspectionRaw(parent,label,value,key,opened){
  const details=inspectionDisclosure(parent,label,key,opened),raw=el("pre",typeof value==="string"?value:JSON.stringify(value,null,2),"formal-inspection-raw");
  raw.tabIndex=0;raw.setAttribute("role","region");raw.setAttribute("aria-label",label);details.append(raw);return details;
}
function inspectionMetadata(parent,fields){
  const list=el("dl",undefined,"evidence-metadata");
  for(const [label,value]of fields)list.append(el("dt",label),el("dd",value==null?"Not supplied":evidenceValue(value)));
  parent.append(list);
}
function inspectionIssue(p,e,x){
  const subjectIssue=evidenceSubjectIssue(p,e);if(subjectIssue)return subjectIssue;
  if(!x||x.schema_version!=="eija.formal-inspection.v1"||x.display_only!==true||x.scope!=="formal-record-inspection")return "Inspection format is unavailable; retain the raw data without assigning it to this check.";
  if(x.kind!==e.kind||x.status!==e.status||JSON.stringify(x.reasons)!==JSON.stringify(e.reasons))return "Inspection and formal record differ; no recorded items are assigned to this check.";
  const review=x.review;
  if(!review||review.case_id!==current?.case.id||review.case_version!==current?.case.version||review.scope!==p.scope||review.subject_hash!==p.subject_hash||review.candidate_semantic_hash!==p.subject?.semantic)return "Inspection belongs to a different or incomplete review identity; it is not the current check's inspection.";
  try{if(evidenceSubjectIssue(p,{subject:JSON.parse(review.subject_json)}))return "Inspection subject dimensions do not match this review packet.";}catch{return "Inspection subject is not readable JSON; no current association is made.";}
  if(workbench?.pack&&(review.pack_id!==workbench.pack.id||review.pack_digest!==workbench.pack.digest))return "Inspection pack identity differs from the loaded pack.";
  if(!["available","unavailable"].includes(x.availability)||!Array.isArray(x.records)||x.record_count!==x.records.length||!Array.isArray(x.availability_reasons)||!Array.isArray(x.projection_reasons))return "Inspection inventory is incomplete or inconsistent; inspect the retained raw data.";
  if(x.availability==="available"&&(!x.receipt||typeof x.artifact_json!=="string"))return "Inspection artifact identity is incomplete; inspect the retained raw data.";
  if(x.availability==="available"&&x.receipt.id!==e.receipt_id)return "Inspection identifies a different deciding receipt; no recorded items are assigned to this check.";
  if(x.availability==="unavailable"&&(x.records.length||x.artifact_json!==null||x.receipt!==null))return "Unavailable inspection contains conflicting artifact data; no recorded items are assigned to this check.";
  return "";
}
function inspectionRecord(parent,record,index,key,opened){
  const origins={counterexample:"Counterexample",negative_control:"Negative control",diagnostic:"Diagnostic"};
  if(!record||!Object.hasOwn(origins,record.origin)||typeof record.artifact_path!=="string"||!Array.isArray(record.steps)||!record.model){
    const invalid=el("div");invalid.append(el("p",`Record ${index+1} has an unsupported shape; raw data is retained.`,"evidence-warning"));inspectionRaw(invalid,"Raw recorded item",record,key+":invalid:"+index,opened);parent.append(invalid);return;
  }
  const recordKey=JSON.stringify([key,record.artifact_path,index]),details=inspectionDisclosure(parent,`${origins[record.origin]} · ${record.label||record.artifact_path}`,recordKey,opened);
  details.dataset.inspectionPath=record.artifact_path;details.dataset.inspectionOrigin=record.origin;details.dataset.inspectionIndex=String(index);
  if(record.origin==="negative_control")details.append(el("p","Seeded control; this is not a reported failure of the current candidate.","muted"));
  if(record.invariant!==null&&record.invariant!==undefined)details.append(el("p","Invariant: "+record.invariant));
  const steps=el("ol",undefined,"formal-inspection-steps");
  for(const step of record.steps){const item=el("li",typeof step?.text==="string"?step.text:step?.raw_json??"Recorded step text not supplied");item.dataset.stepIndex=String(step?.index??"");steps.append(item);}
  if(record.steps.length){details.append(el("p","Recorded steps · literal producer text", "muted"),steps);}else details.append(el("p","No recorded steps are supplied.","muted"));
  const model=record.model,modelLabels={valid_workflow:"A validated Workflow specimen is supplied; it is separate from the current candidate.",raw_invalid:"The supplied specimen is not a valid Workflow. Its raw data and validation errors are retained.",not_provided:"No Workflow specimen is supplied. The current candidate is not substituted."};
  details.append(el("p",modelLabels[model.availability]||"Specimen availability is not recognised; raw data is retained.","formal-inspection-model"));
  formalList(details,"Specimen validation errors",model.validation_errors);
  details.append(el("p","Model and source navigation are not available in this inspection view.","muted"));
  const identities=inspectionDisclosure(details,"Record and specimen identity",recordKey+":identity",opened);
  inspectionMetadata(identities,[["Artifact path",record.artifact_path],["Origin",record.origin],["Model slot",model.slot],["Supplied semantic hash",model.supplied_semantic_hash],["Computed specimen semantic hash",model.computed_semantic_hash],["Model availability",model.availability],["Navigation",record.navigation]]);
  if(model.raw_json!==null&&model.raw_json!==undefined)inspectionRaw(identities,"Raw model specimen",model.raw_json,recordKey+":model",opened);
  inspectionRaw(details,"Raw recorded item",record.raw_json,recordKey+":raw",opened);
}
function renderFormalInspection(row,e,p,opened){
  if(e.inspection===undefined)return;
  const x=e.inspection,issue=inspectionIssue(p,e,x),key=JSON.stringify(["inspection",current?.case.id,current?.case.version,p.subject_hash,x?.review,x?.receipt,e.kind,row.dataset.evidenceIndex]);
  const box=inspectionDisclosure(row,issue?"Inspection association unavailable":x.availability==="available"?`Inspect recorded evidence · ${x.record_count} records`:"Recorded artifact unavailable",key,opened);
  box.className+=" formal-inspection";box.dataset.inspectionAvailability=issue?"unassociated":x.availability;
  if(issue)box.append(el("p",issue,"evidence-warning"));
  else{
    box.append(el("p","Display-only inspection of this deciding record; the check status and review scope are unchanged.","muted"));
    formalList(box,"Artifact availability",x.availability_reasons);
    if(x.availability==="available"){
      if(x.receipt.subject_matches_review!==true)box.append(el("p","The deciding receipt subject differs from this review packet. Its recorded items remain separate from the current candidate.","evidence-warning"));
      if(!x.records.length)box.append(el("p","No structured records are supplied. The retained artifact and verdict reasons remain available."));
      x.records.forEach((record,index)=>inspectionRecord(box,record,index,key,opened));
      formalList(box,"Projection limits",x.projection_reasons);
    }else box.append(el("p","No admitted recorded artifact is available for this inspection. The reported status is unchanged."));
    const identities=inspectionDisclosure(box,"Review and deciding receipt identity",key+":identity",opened);
    inspectionMetadata(identities,[["Review case",x.review.case_id],["Review revision",x.review.case_version],["Review scope",x.review.scope],["Review subject hash",x.review.subject_hash],["Current candidate semantic hash",x.review.candidate_semantic_hash],["Pack",x.review.pack_id],["Pack digest",x.review.pack_digest],["Deciding receipt",x.receipt?.id],["Artifact hash",x.receipt?.artifact_hash],["Producer",x.receipt?.producer],["Method",x.receipt?.method],["Receipt subject matches review",x.receipt?.subject_matches_review]]);
    inspectionRaw(identities,"Full review subject",x.review.subject_json,key+":review",opened);
    if(x.receipt)inspectionRaw(identities,"Original receipt subject",x.receipt.subject_json,key+":receipt",opened);
    if(x.artifact_json!==null)inspectionRaw(box,"Complete recorded artifact",x.artifact_json,key+":artifact",opened);
  }
  inspectionRaw(box,"Raw inspection data",x,key+":raw",opened);
}
function formalDetails(row,e,p,opened){
  if(e.establishes!==undefined)row.append(el("p",evidenceValue(e.establishes)));
  formalList(row,"Why this status",e.reasons);renderFormalInspection(row,e,p,opened);formalList(row,"Does not establish",e.does_not_establish);formalList(row,"Assumptions",e.assumptions);
  if(e.bounds!==undefined)formalList(row,"Bounds",[evidenceValue(e.bounds)]);
  formalList(row,"Counterexamples",e.counterexamples);row.append(el("p","Needs: "+evidenceValue(e.prerequisites===undefined?"Not reported":e.prerequisites)));
  const alreadyShown=new Set(["establishes","reasons","does_not_establish","assumptions","bounds","counterexamples","prerequisites","inspection"]),metadata=el("dl",undefined,"evidence-metadata");
  for(const [name,value]of Object.entries(e))if(!alreadyShown.has(name)||value===null||(Array.isArray(value)&&!value.length))metadata.append(el("dt",name.replaceAll("_"," ")),el("dd",evidenceValue(value)));
  row.append(metadata);
}
function renderFormal(p){
  const root=$("formal"),key=evidenceKey(p),opened=new Set(key&&root.dataset.subjectKey===key?[...root.querySelectorAll("details[data-evidence-key][open]")].map(node=>node.dataset.evidenceKey):[]);
  root.replaceChildren();root.dataset.subjectKey=key;
  for(const m of p.blocked_meanings||[]){root.append(el("p","Blocked meaning: "+m.label+" ("+(m.policy_errors||[]).join(", ")+")","formal-blocked"));for(const x of m.explanations||[])explanation(root,x,"Why the policy refuses it: ");}
  for(const x of p.explanations||[])explanation(root,x,"Why the policy blocks this: ");
  const entries=Object.entries(p.technical_claims||{}),records=p.formal_evidence||[],paired=new Map(),notes=new Map(),counts=new Map();
  for(const e of records)if(typeof e.kind==="string"&&e.kind)counts.set(e.kind,(counts.get(e.kind)||0)+1);
  for(const [name,value]of entries){
    if(!name.startsWith("formal_"))continue;
    const matches=records.filter(e=>typeof e.kind==="string"&&e.kind&&name==="formal_"+e.kind);
    if(matches.length===1&&typeof value==="string"&&value===matches[0].status&&!evidenceSubjectIssue(p,matches[0]))paired.set(matches[0],name);
    else notes.set(name,!matches.length?"No formal record declares this exact kind.":matches.length>1?"Multiple formal records declare this kind; kept separate.":evidenceSubjectIssue(p,matches[0])||"Claim and formal record statuses differ or are not both reported; kept separate.");
  }
  for(const [name,value]of entries){
    if([...paired.values()].includes(name))continue;
    const d=el("details",undefined,"formal-item evidence-result"),rowKey="claim:"+name;
    d.dataset.claim=name;d.dataset.status=evidenceValue(value);d.dataset.evidenceKey=rowKey;d.open=opened.has(rowKey);
    evidenceSummary(d,name.replaceAll("_"," "),value,"Case-wide technical claim",[...new Set([evidenceSubjectIssue(p,{}),notes.get(name)].filter(Boolean))].join(" "));
    d.append(el("p",notes.get(name)||"Reported by the current packet. This claim is not an element-specific verdict."));
    const metadata=el("dl",undefined,"evidence-metadata");metadata.append(el("dt","Technical claim"),el("dd",name));d.append(metadata);root.append(d);
  }
  records.forEach((e,index)=>{
    const status=e.status??"NOT_REPORTED",kind=typeof e.kind==="string"&&e.kind?e.kind:"Kind not reported",d=el("details",undefined,"formal-item evidence-result status-"+String(status).toLowerCase());
    const rowKey=counts.get(e.kind)===1?"formal:"+e.kind:JSON.stringify(["record",index,e]);
    d.dataset.evidenceKind=e.kind??"";d.dataset.evidenceIndex=String(index);d.dataset.status=status;d.dataset.evidenceKey=rowKey;d.open=opened.has(rowKey)||(paired.has(e)&&opened.has("claim:"+paired.get(e)));
    if(paired.has(e))d.dataset.claim=paired.get(e);
    const claimName="formal_"+e.kind,note=counts.get(e.kind)>1?"Multiple formal records declare this kind; kept separate.":notes.get(claimName)||(!paired.has(e)?"No matching technical claim is reported for this formal record.":"");
    const issue=[...new Set([evidenceSubjectIssue(p,e),note].filter(Boolean))].join(" ");
    evidenceSummary(d,kind.replaceAll("_"," "),status,`${String(e.evidence_level||"scope not reported").replaceAll("_"," ")} · case-wide`,issue);
    if(paired.has(e))d.append(el("p","Technical claim: "+paired.get(e)));
    else if(note)d.append(el("p",note,"evidence-warning"));
    formalDetails(d,e,p,opened);root.append(d);
  });
  if(!entries.length)root.append(el("p","Technical claims: not reported for this packet.","muted"));
  if(!records.length)root.append(el("p","Formal evidence: not reported for this packet.","muted"));
}
function currentComparisonSelection(){
  return comparisonSelection&&comparisonSelection.case===current?.case.id&&comparisonSelection.revision===current?.case.version?comparisonSelection:null;
}
function rememberComparisonSelection(selection){
  if(!current||selection?.case!==current.case.id||selection.revision!==current.case.version||!["state","transition","initial"].includes(selection.kind)||typeof selection.id!=="string"||!selection.id)return false;
  comparisonSelection={case:selection.case,revision:selection.revision,kind:selection.kind,id:selection.id};
  renderEvidenceContext();return true;
}
function renderEvidenceContext(){
  const p=current?.packet,c=current?.case,root=$("evidence-subject");root.replaceChildren();
  root.dataset.subjectHash=p?.subject_hash||"";root.dataset.caseId=c?.id||"";root.dataset.displayedModel=modelView;root.dataset.revision=String(c?.version??"");
  root.append(el("p",c?`Case ${c.id} · revision ${c.version} · baseline revision ${c.baseline_version}`:"No case selected; evidence has not been requested."));
  root.append(el("p",p?.subject?.semantic?`Evidence subject: current candidate · semantic ${p.subject.semantic.slice(0,12)}`:"Evidence subject: not available. Select a supported meaning first."));
  if(modelView==="history")root.append(el("p",`Displayed model: historical preview · ${historyLabel||"recorded model"}. This packet is not evidence for that preview.`,"subject-warning"));
  else if(modelView==="baseline")root.append(el("p","Displayed model: original baseline. This packet describes the current candidate, not the baseline.","subject-warning"));
  else root.append(el("p","Displayed model: working model"));
  const selected=currentComparisonSelection();
  root.dataset.comparisonCaseId=selected?.case||"";root.dataset.comparisonRevision=String(selected?.revision??"");root.dataset.comparisonKind=selected?.kind||"";root.dataset.comparisonId=selected?.id||"";
  if(selected){
    root.append(el("p",`Comparison selection: ${selected.kind} · ${selected.id}`));
    root.append(el("p","Evidence scope: case-wide for the current candidate. The comparison selection is navigation context; it is not an element-specific result.","muted"));
  }
  if(inspectorSelection)root.append(el("p",`Model inspector selection: ${inspectorSelection.kind} · ${inspectorSelection.id}`));
  const identities=$("evidence-identities");identities.replaceChildren();
  if(p?.subject_hash)identities.append(el("dt","Review subject hash"),el("dd",p.subject_hash));
  for(const [name,value]of Object.entries(p?.subject||{}))identities.append(el("dt",name),el("dd",evidenceValue(value)));
  if(!identities.childElementCount)identities.append(el("dt","Subject"),el("dd","Not available"));
}
function evidenceBlockerDescription(code){
  const known={
    SOURCE_REVIEW_REQUIRED:["Source review required","Owner review of changed implementation is outstanding."],
    POLICY_BLOCKED:["Declared policy blocks review","The candidate does not satisfy the declared policy."],
    IMPACT_INCOMPLETE:["Dependency coverage is incomplete","The model's explicit dependency mapping is incomplete."],
    MEANING_REQUIRED:["Interpretation required","Choose a supported interpretation before reviewing a candidate."],
    STALE_BASELINE:["Baseline revision has changed","This case uses an older baseline revision."],
    HUMAN_FIELD_EVIDENCE_REQUIRED:["Human field evidence required","This review scope requires human field evidence beyond the local demo."],
    CASE_DISCARDED:["Case is closed","This case is unavailable for review."]
  };
  if(Object.hasOwn(known,code))return known[code];
  if(code.startsWith("RUNTIME_EVIDENCE_"))return ["Runtime evidence · "+code.slice(17),"The packet does not establish a passing runtime matrix."];
  const formal=code.match(/^FORMAL_EVIDENCE_(FAIL|CONFLICT):(.+)$/);
  return formal?[`Formal check ${formal[2]} · ${formal[1]}`,"Inspect the reported check, its reasons and scope."]:[code,"The packet reports this review restriction; no specific check is identified."];
}
function evidenceBlockerTarget(p,code){
  if(code==="SOURCE_REVIEW_REQUIRED"){
    const matches=[...$("problems").children].filter(node=>node.id==="source-review-problem"&&node.dataset.problemCode===code);
    return matches.length===1?{node:matches[0],kind:"problem",label:"Inspect source restriction"}:null;
  }
  if(evidenceSubjectIssue(p,{}))return null;
  let claim=null,expected=null;
  if(code==="POLICY_BLOCKED"){claim="schema_policy";expected="FAIL";}
  if(code==="IMPACT_INCOMPLETE"){claim="modelled_impact_closure";expected="UNKNOWN";}
  if(code.startsWith("RUNTIME_EVIDENCE_")&&!code.endsWith("_PASS")){claim="runtime_matrix";expected=code.slice(17);}
  const formal=code.match(/^FORMAL_EVIDENCE_(FAIL|CONFLICT):(.+)$/);
  if(formal){
    const records=(p.formal_evidence||[]).filter(record=>record.kind===formal[2]);
    if(records.length!==1||records[0].status!==formal[1]||evidenceSubjectIssue(p,records[0]))return null;
    claim="formal_"+formal[2];expected=formal[1];
  }
  if(!claim||p.technical_claims?.[claim]!==expected)return null;
  const matches=[...$("formal").children].filter(node=>node.dataset.claim===claim&&node.dataset.status===expected&&(!formal||node.dataset.evidenceKind===formal[2]));
  return matches.length===1?{node:matches[0],kind:"check",label:formal?"Inspect "+formal[2].replaceAll("_"," "):claim==="runtime_matrix"?"Inspect runtime check":claim==="schema_policy"?"Inspect policy check":"Inspect dependency check"}:null;
}
function openEvidenceBlocker(p,code,identity){
  const same=JSON.stringify([current?.case.id,current?.case.version,p.subject_hash,p.subject])===identity;
  const target=same&&current?.packet===p&&p.blockers?.includes(code)?evidenceBlockerTarget(p,code):null;
  if(!target){notice("Evidence changed. Use the current review restrictions.",true);return false;}
  if(target.kind==="problem"){
    EijaShell.bottom("problems-pane",{temporary:true});target.node.tabIndex=-1;target.node.focus();target.node.scrollIntoView({block:"nearest"});
  }else{
    switchTab("evidence");target.node.open=true;target.node.querySelector("summary").focus();target.node.scrollIntoView({block:"nearest"});
  }
  return true;
}
function renderEvidenceTriage(p){
  const root=$("evidence-triage"),identity=JSON.stringify([current?.case.id,current?.case.version,p.subject_hash,p.subject]);root.replaceChildren();
  root.dataset.caseId=current?.case.id||"";root.dataset.revision=String(current?.case.version??"");root.dataset.subjectHash=p.subject_hash||"";
  if(!p.blockers?.length){root.append(el("p",p.eligible?"No blockers are reported for this technical scope. Human authorisation remains separate.":"Review is blocked, but the packet does not identify a reason."));return;}
  const list=el("ul");
  for(const code of p.blockers){
    const [title,reason]=evidenceBlockerDescription(code),row=el("li"),copy=el("div"),target=evidenceBlockerTarget(p,code);
    row.dataset.blockerCode=code;copy.append(el("strong",title),el("p",reason));row.append(copy);
    if(target){const button=el("button",target.label,"secondary");button.type="button";button.dataset.blockerCode=code;button.onclick=()=>openEvidenceBlocker(p,code,identity);row.append(button);}
    list.append(row);
  }
  root.append(list);
}
function renderEvidencePacket(p){
  renderFormal(p);renderProblems();renderEvidenceContext();renderEvidenceTriage(p);
  $("blockers").textContent=p.blockers?.length?"Review blocked: "+p.blockers.join(", "):p.eligible?"Technical scope eligible. Human authorisation is still a separate decision.":"Review blocked. No blocker codes were reported.";
  $("packet").textContent=JSON.stringify(p,null,2);
  const decision=$("review-decision"),key=evidenceKey(p),sameSubject=!!key&&decision.dataset.subjectKey===key;
  const previous=sameSubject?new Map([...$("questions").querySelectorAll("input")].map(input=>[input.name,input.value])):new Map();
  if(!sameSubject){decision.open=false;$("acknowledge").checked=false;}
  decision.dataset.subjectKey=key;
  $("review-subject").textContent=`Review this exact subject · ${p.eligible?"eligible for local review":"blocked"} · ${p.subject_hash?p.subject_hash.slice(0,12):"subject not available"}`;
  $("questions").replaceChildren();
  for(const q of p.questions||[]){const div=el("div",undefined,"question"),label=el("label",q.question);label.htmlFor="q-"+q.id;const input=el("input");input.id="q-"+q.id;input.name=q.id;input.autocomplete="off";input.required=true;input.value=previous.get(q.id)||"";div.append(label,input);$("questions").append(div);}
}
async function load(id,canPublish=null) {
  const switching=current?.case.id!==id;
  if(switching&&current)caseViews.set(current.case.id,{tab,editId,inspectorSelection,modelView,historyModel,historyLabel,canvasDirection});
  const [next,affordances,historyData]=await Promise.all([api("cases/"+id),api(`cases/${id}/affordances`),api(`cases/${id}/history`).catch(error=>({status:"unavailable",reason:error.code||"HISTORY_UNAVAILABLE"}))]);
  if(canPublish&&!canPublish())return false;
  reconcileRuntime(next);
  if(switching){const previous=caseViews.get(id);editId=previous?.editId||null;inspectorSelection=previous?.inspectorSelection||null;modelView=previous?.modelView||"working";historyModel=previous?.historyModel||null;historyLabel=previous?.historyLabel||"";canvasDirection=previous?.canvasDirection||"AUTO";if(previous)tab=previous.tab;}
  if(current?.case.id!==next.case.id||current?.case.version!==next.case.version)cancelSourceRead();
  current=next;affordanceData=affordances;caseHistory=historyData;renderEditReconciliation();render();await cases();if(canPublish&&!canPublish())return false;
  if(runtimeAttempt&&runtimeOwns(runtimeAttempt)&&runtimeAttempt.refresh==="failed"){runtimeAttempt.refresh="current";renderRuntimeFeedback();}
  if(editNeedsRefresh.delete(id))render();
  renderEditReconciliation();
  clearDiagnostic();return true;
}
let editNeedsRefresh=new Map();
function renderEditReconciliation(){
  const root=$("edit-reconciliation"),pending=editNeedsRefresh.get(current?.case.id);root.hidden=!pending;
  if(!pending){$("edit-reconciliation-status").textContent="";for(const key of ["caseId","revision","status"])delete root.dataset[key];return;}
  Object.assign(root.dataset,{caseId:pending.caseId,revision:String(pending.version),status:pending.status});
  const outcome=pending.status==="committed"?`Edit acknowledged at revision ${pending.version+1}.`:`Edit outcome unknown for revision ${pending.version}; it may have committed.`;
  $("edit-reconciliation-status").textContent=`${outcome} Revision ${current.case.version} and its evidence are the last loaded snapshot. Refresh this case to reconcile before changing it or its runtime.`;
  for(const id of ["propose","save","discard","move-node","verify","reset","approve","apply","undo-edit","redo-edit","history-undo","history-redo"])$(id).disabled=true;
  for(const button of $("runtime-actions").children)button.disabled=true;
}
let runtimeAttempt=null,runtimeCommit=null,runtimeEpoch=0,runtimeUncertain=false;
function runtimeSemantic(data=current){return data?.packet?.subject?.semantic??null;}
function clearRuntime(){
  ++runtimeEpoch;runtimeAttempt=null;runtimeCommit=null;runtimeUncertain=false;instance=null;
  $("runtime-state").textContent="Not started";
  $("runtime-version").textContent="No preview instance has been acknowledged";
  for(const button of $("runtime-actions").children)button.disabled=true;
  renderRuntimeFeedback();
}
function reconcileRuntime(next){
  if(current?.case.id!==next.case.id||runtimeSemantic()!==runtimeSemantic(next))clearRuntime();
}
function runtimeOwns(attempt){
  return runtimeAttempt===attempt&&attempt.epoch===runtimeEpoch&&attempt.caseId===current?.case.id&&attempt.semanticHash===runtimeSemantic()&&
    (instance?.id??null)===(attempt.result?.instance.id??attempt.instanceId);
}
function runtimeRefused(error){
  const boundaries={HOST_DENIED:403,SESSION_REQUIRED:401,ORIGIN_DENIED:403,CONTENT_TYPE:415,BODY_TOO_LARGE:413,CONTRACT_REJECTED:422,NOT_FOUND:404};
  const domain=["CASE_SCHEMA_OLD","CASE_CLOSED","MEANING_REQUIRED","POLICY_BLOCKED","STALE_INSTANCE","ACTION_DENIED","UNKNOWN_ACTOR","ACTOR_REVOKED","ROLE_DENIED","ASSIGNMENT_DENIED","OPERATION_CONFLICT","STALE_VERSION","STATE_DENIED","EFFECT_DENIED","INVALID_STATE"];
  return error instanceof ApiError&&error.responseValid===true&&error.httpStatus===(boundaries[error.code]??(domain.includes(error.code)?409:null));
}
function beginRuntimeAttempt(kind,action){
  const requestId=crypto.randomUUID(),c=current.case;
  runtimeAttempt={epoch:++runtimeEpoch,requestId,operationId:kind==="execute"?requestId:null,kind,caseId:c.id,caseVersion:c.version,
    semanticHash:runtimeSemantic(),subjectHash:current.packet?.subject_hash??null,actorId:kind==="execute"?$("actor").value:null,action,
    instanceId:instance?.id??null,instanceVersion:instance?.version??null,status:"pending",refresh:"not requested"};
  runtimeAttempt.command=kind==="execute"?{operation_id:requestId,actor_id:runtimeAttempt.actorId,instance_id:runtimeAttempt.instanceId,action,expected_version:runtimeAttempt.instanceVersion}:{expected_version:c.version};
  renderRuntimeFeedback();return runtimeAttempt;
}
function runtimeInstanceValid(value,attempt){
  return value&&typeof value.id==="string"&&value.id.length>0&&value.case_id===attempt.caseId&&value.model_hash===attempt.semanticHash&&
    typeof value.state==="string"&&value.state.length>0&&Number.isInteger(value.version)&&value.version>=0;
}
function validateRuntimeResult(result,attempt){
  const validInstance=runtimeInstanceValid(result?.instance,attempt)&&result.instance.id===attempt.instanceId;
  const effects=Array.isArray(result?.effects)&&result.effects.every(value=>typeof value==="string");
  const committed=result?.committed===true&&result.duplicate===false&&result.instance?.version===attempt.instanceVersion+1;
  const original=result?.original_result;
  const duplicate=result?.duplicate===true&&result.committed===false&&result.effects?.length===0&&original?.committed===true&&original.duplicate===false&&
    runtimeInstanceValid(original.instance,attempt)&&original.instance.id===attempt.instanceId&&original.instance.version===attempt.instanceVersion+1&&result.instance.version>=original.instance.version&&Array.isArray(original.effects)&&original.effects.every(value=>typeof value==="string");
  if(!validInstance||!effects||(!committed&&!duplicate))throw new ApiError("RESPONSE_INVALID","The runtime response did not identify a valid outcome for this request.");
}
function runtimeFailure(attempt,error){
  if(!runtimeOwns(attempt))return false;
  attempt.status=runtimeRefused(error)?"refused":"unknown";attempt.error={code:error.code||"REQUEST_FAILED",message:error.message,details:error.details||{}};
  runtimeUncertain=runtimeUncertain||attempt.status==="unknown"||["STALE_VERSION","STALE_INSTANCE","NOT_FOUND"].includes(error.code);
  renderRuntimeFeedback();reportError(error,{reveal:false});return false;
}
async function refreshRuntime(attempt){
  if(!runtimeOwns(attempt))return false;
  attempt.refresh="pending";renderRuntimeFeedback();
  try{
    await load(attempt.caseId,()=>runtimeOwns(attempt));
    if(!runtimeOwns(attempt))return false;
    attempt.refresh="current";renderRuntimeFeedback();notice(attempt.kind==="preview"?"Fresh isolated instance acknowledged; case observations refreshed.":"Runtime outcome acknowledged; case observations refreshed.");return true;
  }catch(error){
    if(!runtimeOwns(attempt))return false;
    attempt.refresh="failed";attempt.refreshError={code:error.code||"REQUEST_FAILED",message:error.message,details:error.details||{}};renderRuntimeFeedback();
    reportError(new ApiError("RUNTIME_REFRESH_FAILED","The runtime outcome was acknowledged, but case observations could not be refreshed.",{cause:attempt.refreshError}),{reveal:false});return false;
  }
}
async function executeRuntime(action,origin){
  if(!current||editNeedsRefresh.has(current.case.id)||origin.caseId!==current.case.id||origin.revision!==current.case.version||origin.semanticHash!==runtimeSemantic()||!instance||origin.instanceId!==instance.id||origin.instanceVersion!==instance.version)return false;
  const attempt=beginRuntimeAttempt("execute",action);
  let result;
  try{result=await api(`cases/${attempt.caseId}/execute`,attempt.command);validateRuntimeResult(result,attempt);}catch(error){return runtimeFailure(attempt,error);}
  if(!runtimeOwns(attempt))return false;
  instance=result.instance;runtimeUncertain=false;attempt.status=result.committed?"committed":"duplicate";attempt.result=result;
  if(result.committed)runtimeCommit={caseId:attempt.caseId,semanticHash:attempt.semanticHash,operationId:attempt.operationId,action:attempt.action,actorId:attempt.actorId,result};
  renderRuntime();return refreshRuntime(attempt);
}
async function startRuntimePreview(){
  if(!current||editNeedsRefresh.has(current.case.id))return false;
  const attempt=beginRuntimeAttempt("preview","Start / reset preview");let result;
  try{
    result=await api(`cases/${attempt.caseId}/preview`,attempt.command);
    if(!runtimeInstanceValid(result,attempt)||result.version!==0)throw new ApiError("RESPONSE_INVALID","The preview response did not identify a new instance for this candidate.");
  }catch(error){return runtimeFailure(attempt,error);}
  if(!runtimeOwns(attempt))return false;
  instance=result;runtimeCommit=null;runtimeUncertain=false;attempt.status="preview";attempt.result={instance:result};
  renderRuntime();return refreshRuntime(attempt);
}
function renderRuntimeFeedback(){
  const root=$("runtime-result"),attempt=runtimeAttempt,identity=$("runtime-attempt-identity");
  root.textContent="";identity.replaceChildren();
  for(const key of ["status","operationId","requestId","caseId","caseRevision","semanticHash","actorId","action","instanceId","expectedVersion","refresh"])delete root.dataset[key];
  if(attempt){
    Object.assign(root.dataset,{status:attempt.status,operationId:attempt.operationId||"",requestId:attempt.requestId,caseId:attempt.caseId,caseRevision:String(attempt.caseVersion),semanticHash:attempt.semanticHash||"",actorId:attempt.actorId||"",action:attempt.action,instanceId:attempt.instanceId||"",expectedVersion:String(attempt.instanceVersion??""),refresh:attempt.refresh});
    const effects=attempt.result?.effects||[],actor=attempt.kind==="execute"?` Actor: ${attempt.actorId}.`:"";
    const message={pending:`Pending: ${attempt.action}.${actor} No outcome has been acknowledged.`,committed:`Committed: ${attempt.action}.${actor} Effects: ${effects.join(", ")||"none"}.`,
      duplicate:`Previously committed operation acknowledged: ${attempt.action}.${actor} This request added no effects.`,preview:`New isolated preview acknowledged: ${attempt.result?.instance.state}.`,
      refused:`Refused: ${attempt.action}.${actor} ${attempt.error?.message}. This request did not commit. See Attempt details and diagnostic.`,unknown:`Outcome unknown: ${attempt.action}.${actor} ${attempt.error?.message}. The request may have committed; no automatic retry was sent. See Attempt details and diagnostic.`}[attempt.status];
    root.textContent=message+(attempt.refresh==="failed"?" Case observations refresh failed; the acknowledged runtime outcome is retained.":attempt.refresh==="pending"?" Refreshing case observations…":"")+(runtimeUncertain?" The last confirmed state may be stale.":"");
    const values={"Client request ID":attempt.requestId,"Operation ID":attempt.operationId||"Not supplied by preview endpoint","Case":attempt.caseId,"Case revision at request":attempt.caseVersion,"Candidate semantic hash":attempt.semanticHash||"Not reported","Review subject hash at request":attempt.subjectHash||"Not reported","Actor":attempt.actorId||"Not applicable","Action":attempt.action,"Instance at request":attempt.instanceId||"None","Instance version at request":attempt.instanceVersion??"None","Latest status":attempt.status,"Case observations":attempt.refresh,"Exact request":JSON.stringify(attempt.command||{}),"Acknowledged instance":attempt.result?.instance?JSON.stringify(attempt.result.instance):"Not acknowledged"};
    if(attempt.error)values["Request diagnostic"]=JSON.stringify(attempt.error);if(attempt.refreshError)values[attempt.refresh==="current"?"Earlier refresh diagnostic (later refresh succeeded)":"Refresh diagnostic"]=JSON.stringify(attempt.refreshError);
    for(const [name,value]of Object.entries(values))identity.append(el("dt",name),el("dd",String(value)));
  }
  $("runtime-last-commit").textContent=runtimeCommit?`Last acknowledged commit: ${runtimeCommit.action} · actor ${runtimeCommit.actorId} · instance ${runtimeCommit.result.instance.id} · version ${runtimeCommit.result.instance.version}. Effects: ${runtimeCommit.result.effects.join(", ")||"none"}. This is separate from the latest attempt.`:"";
}
function renderRuntime(){
  const c=current?.case,closed=!c||editNeedsRefresh.has(c.id)||["APPLIED","DISCARDED"].includes(c.stage),origin={caseId:c?.id,revision:c?.version,semanticHash:runtimeSemantic(),instanceId:instance?.id,instanceVersion:instance?.version};
  $("runtime-actions").replaceChildren();
  for(const action of status?.pack?.actions||[]){const button=el("button",action,"secondary");button.dataset.action=action;button.disabled=!instance||closed;button.onclick=()=>task(()=>executeRuntime(action,origin));$("runtime-actions").append(button);}
  $("runtime-state").textContent=instance?.state||"Not started";
  $("runtime-version").textContent=instance?`Last confirmed instance ${instance.id.slice(0,8)} · version ${instance.version} · isolated candidate${runtimeUncertain?" · may be stale":""}`:"No preview instance has been acknowledged";
  $("trace").textContent=JSON.stringify(current?.observations??[],null,2);renderRuntimeFeedback();
}

async function command(action,extra={}){
  const id=current.case.id;
  if(editNeedsRefresh.has(id))throw new ApiError("EDIT_RECONCILIATION_REQUIRED","Refresh this case before changing it or its runtime; the previous edit submission needs reconciliation.",{case_id:id});
  const result=await api(`cases/${id}/${action}`,{expected_version:current.case.version,...extra});
  if(["undo","redo","discard"].includes(action))clearRuntime();await load(id);return result;
}
function renderProposals(c,closed){
  const interpretationPanel=$("interpretation-panel"),interpretationKey=JSON.stringify([c.id,!!c.candidate]);
  if(interpretationPanel.dataset.caseState!==interpretationKey){interpretationPanel.open=!c.candidate;interpretationPanel.dataset.caseState=interpretationKey;}
  $("interpretation-summary").textContent=c.candidate?`Selected intent: ${current.options[c.selected_meaning]?.label||c.selected_meaning}`:"Interpretations";
  const options=$("options"),controls=$("proposal-controls"),active=document.activeElement;
  const key=JSON.stringify([c.id,c.proposal]),previous=$("proposal-alternatives");
  const retainOpen=previous?.dataset.proposalKey===key&&previous.open;
  const optionFocused=options.contains(active),controlsFocused=active===$("propose")||active===$("egress"),meaning=active?.dataset?.meaning;
  const unsupported=[],direct=[];options.replaceChildren();
  for(const a of c.proposal?.alternatives||[]){
    const canonical=current.options[a.interpretation],chosen=c.selected_meaning===a.interpretation;
    const card=el("article",undefined,"option"+(chosen?" selected":""));
    card.append(el("small",chosen?"SELECTED BY LOCAL OWNER":canonical.supported?"SUPPORTED MEANING":"BLOCKED / OUT OF SCOPE"),el("h3",canonical.label));
    for(const consequence of canonical.consequences)card.append(el("p",consequence));
    const explanation=el("details");explanation.append(el("summary","Untrusted provider explanation"),el("p",a.explanation));card.append(explanation);
    const button=el("button",chosen?"Meaning selected":canonical.supported?"Select this meaning":"Explain boundary",chosen?"secondary":"");
    button.dataset.meaning=a.interpretation;button.disabled=closed||!!c.candidate;
    button.onclick=()=>task(async()=>{await command("select",{interpretation:a.interpretation});notice("Meaning selected. The local baseline has not changed.");});card.append(button);
    if(canonical.supported||chosen)direct.push(card);else unsupported.push({card,canonical});
  }
  options.append(...direct);
  if(unsupported.length){
    if(!direct.length)options.append(el("p","No supported interpretation was proposed. Inspect the boundaries or request another proposal.","muted"));
    const disclosure=el("details"),summary=el("summary"),cards=el("div",undefined,"options");
    summary.append(el("strong",`Unsupported interpretations (${unsupported.length}) · inspect explanations`));
    for(const {canonical} of unsupported)summary.append(el("span",`${canonical.label} — ${canonical.consequences.join(" ")}`,"proposal-boundary"));
    disclosure.id="proposal-alternatives";disclosure.dataset.proposalKey=key;disclosure.open=!!retainOpen;
    summary.id="proposal-alternatives-summary";cards.append(...unsupported.map(item=>item.card));disclosure.append(summary,cards);options.append(disclosure);
  }
  const controlKey=JSON.stringify([c.id,!!c.proposal]);
  if(controls.dataset.proposalKey!==controlKey){controls.open=!c.proposal;controls.dataset.proposalKey=controlKey;}
  $("proposal-controls-summary").textContent=c.proposal?"Interpretations received · proposal controls":"Request interpretations";
  if(controlsFocused&&!controls.open){$("proposal-controls-summary").focus();}
  else if(optionFocused){
    const retained=active?.id&&$(active.id);
    const same=[...options.querySelectorAll("button[data-meaning]")].find(button=>button.dataset.meaning===meaning&&!button.disabled&&button.getClientRects().length);
    const first=[...options.querySelectorAll("button[data-meaning]")].find(button=>!button.disabled&&button.getClientRects().length);
    (retained&&!retained.disabled&&retained.getClientRects().length?retained:same||first||(c.candidate?$("case-title"):$("proposal-alternatives-summary"))||$("proposal-controls-summary")).focus();
  }
}
function render(){const c=current.case,p=current.packet,closed=editNeedsRefresh.has(c.id)||["APPLIED","DISCARDED"].includes(c.stage);$("create-panel").hidden=true;$("workspace").hidden=false;$("case-heading").hidden=false;$("case-title").textContent=c.request;$("case-id").textContent=`CHANGE CASE ${c.id.slice(0,10)} / REVISION ${c.version} / BASELINE ${c.baseline_version}`;$("case-stage").textContent=c.stage;$("proposal-summary").textContent=c.proposal?.summary||"No interpretation has been requested. Your request is not yet a semantic change.";$("propose").disabled=!!c.candidate||closed;renderProposals(c,closed);
$("proposal-unknowns").replaceChildren();for(const unknown of c.proposal?.unknowns||[])$("proposal-unknowns").append(el("p","Unresolved: "+unknown,"muted"));$("editor").hidden=!c.candidate;
for(const id of ["save","discard","edit-rule","edit-state","move-node","verify","reset"])$(id).disabled=!c.candidate||closed;
renderWorkbench(); renderChanges();
globalThis.eijaAgentEdits?.update();
renderRuntime();
renderEvidencePacket(p);$("approve").disabled=!p.eligible||closed||c.stage==="APPROVED";$("apply").hidden=c.stage!=="APPROVED";$("apply").disabled=c.stage!=="APPROVED"||!p.eligible;$("export").disabled=false;switchTab(tab);}
$("create").onclick=()=>task(async()=>{const c=await api("cases",{request:$("request").value});tab="change";editId=null;await load(c.id);notice("Case created. No provider call or baseline change has occurred.");});document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>openWorkDestination(b.dataset.tab));
$("propose").onclick=()=>task(async()=>{await command("propose",{consent:$("egress").checked});notice("Interpretations received. No meaning was selected automatically.");},"Requesting an untrusted proposal…");
$("save").onclick=()=>task(async()=>{await command("save");notice("Review checkpoint saved; the active baseline is unchanged.");});$("discard").onclick=()=>task(async()=>{await command("discard");clearRuntime();render();notice("Candidate closed. History is retained; the baseline is unchanged.");});
function edit(source) {return commitChoice(choiceFor("retarget_source", "state:" + source));}
$("edit-rule").onclick = () => edit($("rejection-source").value);
$("edit-state").onclick = () => edit($("diagram-source").value);
$("edit-target").onclick = () => commitChoice(choiceFor("retarget_target", "state:" + $("target-state").value));
$("edit-role").onclick = () => commitChoice(choiceFor("set_role", "role:" + $("transition-role").value));
$("move-node").onclick=()=>task(async()=>{await command("layout",{change:{node:$("layout-node").value,x:Number($("layout-x").value),y:Number($("layout-y").value)}});notice("Layout metadata changed. Domain receipts remain applicable; exact-presentation approval is cleared.");});
$("reset").onclick=()=>task(startRuntimePreview,"Starting an isolated preview…");
async function verifyForReview(){
  const origin={id:current.case.id,version:current.case.version,subject:JSON.stringify(current.packet?.subject),hash:current.packet?.subject_hash,decision:!!current.case.decision};
  const result=await command("verify");
  notice("Bounded runtime verification finished. Human evidence remains UNKNOWN.");
  const c=current?.case,p=current?.packet,decision=$("review-decision"),active=document.activeElement;
  if(tab!=="evidence"||origin.decision||c?.decision||result?.id!==origin.id||result.version!==origin.version+1||result.stage!=="VERIFIED"||
    c?.id!==result.id||c.version!==result.version||c.stage!=="VERIFIED"||!origin.hash||p?.subject_hash!==origin.hash||JSON.stringify(p.subject)!==origin.subject||
    p.eligible!==true||!Array.isArray(p.blockers)||p.blockers.length||decision.dataset.subjectKey!==evidenceKey(p)||
    active!==$("verify"))return false;
  decision.open=true;
  const unanswered=[...$("questions").querySelectorAll("input")].find(input=>!input.disabled&&!input.value.trim());
  (unanswered||$("review-subject")).focus();return true;
}
$("verify").onclick=()=>task(verifyForReview,"Executing the synthetic state / actor / action matrix…");
$("review-form").onsubmit=e=>{e.preventDefault();task(async()=>{const answers={};for(const q of current.packet.questions)answers[q.id]=$("q-"+q.id).value.trim();await command("approve",{subject_hash:current.packet.subject_hash,answers,acknowledge_unknowns:$("acknowledge").checked,scope:"local-demo"});notice("Exact local revision acknowledged. Apply remains a separate action.");});};
$("apply").onclick=()=>task(async()=>{await command("apply");status=await api("status");workbench=await api("workbench");renderWorkbench();notice("Applied to the local demo baseline only. No production system was touched.");});
$("export").onclick=()=>task(async()=>{const data=await api(`cases/${current.case.id}/export`),blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"}),url=URL.createObjectURL(blob),a=el("a");a.href=url;a.download=`eija-${current.case.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notice("Case exported with model, evidence, observations and integrity hash.");});
$("doctor").onclick=()=>task(async()=>{notice(JSON.stringify(await api("doctor")));});
function showPack(pack){if(!pack)return;$("pack-name").textContent=pack.name;if(!$("request").value)$("request").value=pack.demo_request;$("actor").replaceChildren(...pack.actors.map(a=>{const o=el("option",`${a.role} · ${a.assigned?"assigned":"unassigned"} / ${a.active?"active":"revoked"}`);o.value=a.id;return o;}));}
task(async () => {
  [status, workbench] = await Promise.all([api("status"), api("workbench")]);
  showPack(status.pack); $("connection").textContent = `${status.provider} · ${status.network_enabled ? "network enabled" : "local / offline"}`;
  renderWorkbench(); renderProblems(); renderChanges(); switchTab("model"); await cases(); notice("");
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
function editable() {return !editNeedsRefresh.has(current?.case.id) && modelView === "working" && !!current?.case.candidate && !["APPLIED", "DISCARDED"].includes(current.case.stage);}
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
    details.setAttribute("aria-label",`Declared constraints for ${target.id}`);
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
  const c=current?.case;
  $("rules-edit-help").textContent=editNeedsRefresh.has(c?.id)?"An edit submission needs reconciliation. Refresh this case before editing the last loaded model.":!c?.candidate?"The baseline is read only. Choose a supported meaning in Intent to create a candidate.":["APPLIED","DISCARDED"].includes(c.stage)?`This case is ${c.stage}; its model is read only. Open another case to make changes.`:modelView!=="working"?"The Model workspace shows a read-only preview. Choose a rule above to open the current candidate before editing.":target?`Editing ${target.action} (${target.id}) in the current candidate · revision ${c.version}. The kernel checks each submitted change.`:"Choose a rule above to select the current candidate transition to edit.";
}
function renderCanvas() {
  $("canvas-direction").value=canvasDirection;
  EijaCanvas.render($("model-canvas"), {model: workingModel(), layout: current?.case.layout || {}, pack: workbench.pack.id,
    direction:canvasDirection, selected: editId, affordances: affordanceData?.affordances, editable: editable(), onSelect: selectTransition, onDrop: commitChoice, onNotice: notice});
  EijaShell.mountCanvas(`${current?.case.id||workbench.pack.id}:${modelView}`);
}
function selectTransition(id) {const returnFocus=$("model-canvas").contains(document.activeElement);editId = id || null;inspectorSelection=editId?{kind:"transition",id:editId}:null;EijaShell.reveal("inspector");EijaTree.reveal($("domain-tree"),"transition",editId);renderEditor();renderSelectionDetail();renderCanvas();renderEvidenceContext();renderNavigator();if(returnFocus)$("model-canvas").querySelector(".model-edge.selected")?.focus();}
function openTransitionPicker(){
  switchTab("model");inspectorSelection=selectedTransition()?{kind:"transition",id:editId}:null;
  renderSelectionDetail();renderEvidenceContext();renderNavigator();EijaShell.reveal("inspector");
  $("transition-inspector").hidden=false;$("transition-select").focus();
}
function openComparisonSelection(target){
  switchTab("review");
  if(target&&!comparison?.select(target))return false;
  const selected=$("task-navigator").querySelector("button.selected");
  (selected?.getClientRects().length?selected:$("comparison-model-tab")).focus();return true;
}
function cancelDraft() {
  if (busy || !editable() || !selectedTransition()) return;
  renderEditor(); notice("Unsent fields reset to the loaded model; no transaction was sent.");
}
$("cancel-draft").onclick = cancelDraft;
$("edit-fields").addEventListener("keydown", event => {
  if (event.key === "Escape" && !busy) {event.preventDefault(); event.stopPropagation(); cancelDraft();}
});
function renderRules() {
  const c=current?.case,p=current?.packet,model=c?(c.candidate||c.baseline):workbench?.model;
  const origin=c?{id:c.id,version:c.version}:null;
  const subject=$("rules-subject"),kind=c?(c.candidate?"candidate":"case baseline"):"loaded baseline";
  subject.dataset.caseId=c?.id||"";subject.dataset.revision=String(c?.version??workbench?.baseline_version??"");subject.dataset.modelSubject=kind;
  subject.textContent=c?`Current ${kind} · case ${c.id} · revision ${c.version}.`:`Loaded baseline · no change case · revision ${workbench?.baseline_version??workbench?.pack.version??"not reported"}.`;
  subject.dataset.semanticHash=c?.candidate?p?.subject?.semantic||"":"";
  if(subject.dataset.semanticHash)subject.append(el("span",` Semantic ${subject.dataset.semanticHash.slice(0,12)}.`));
  if(c&&modelView!=="working")subject.append(el("span",` Model workspace shows ${modelView==="history"?"a historical preview":"the original baseline"}; choose a rule to inspect this current ${kind}.`,"subject-warning"));
  $("rules-evidence").disabled=!c;
  const table=$("rule-table"),changes=c?.candidate?new Map(EijaReview.compare(c.baseline,c.candidate).transitions.map(item=>[item.id,item.status])):new Map();
  table.replaceChildren();
  for(const transition of model?.transitions||[]){
    const row=el("tr"),action=el("td"),choose=el("button",transition.action,"text-button"),change=changes.get(transition.id)||"baseline";
    row.dataset.eijaId=`${workbench?.pack.id||model.id}.rule.${transition.id}`;row.dataset.transitionId=transition.id;row.dataset.changeStatus=change;
    choose.onclick=()=>inspectWorkingTransition(transition.id,origin);action.append(choose);
    if(["added","changed"].includes(change))action.append(el("span",change==="added"?"Added":"Changed","diff-tag "+change));
    row.append(action);[transition.role,transition.from_state,transition.to_state,transition.guards.join(", ")].forEach(value=>row.append(el("td",value)));table.append(row);
  }
  if(!table.childElementCount){const row=el("tr"),cell=el("td",model?"No transitions are declared in this model.":"The baseline model is unavailable.");cell.colSpan=5;row.append(cell);table.append(row);}
  const selectedLayout=$("layout-node").value;$("state-flow").replaceChildren();$("layout-node").replaceChildren();
  for(const state of model?.states||[]){
    const node=el("div",undefined,"state-node");node.dataset.eijaId=`${model.id}.state-card.${state}`;node.append(el("strong",state));
    for(const transition of model.transitions.filter(item=>item.from_state===state))node.append(el("small",`${transition.role}: ${transition.action} → ${transition.to_state}`));
    $("state-flow").append(node);$("layout-node").append(el("option",state));
  }
  if(model?.states.includes(selectedLayout))$("layout-node").value=selectedLayout;
  $("impact-summary").textContent=p?.impact?`${p.impact.changed_actions.length} changed actions · ${p.impact.affected.length} modelled dependants · closure ${p.impact.complete?"complete within this mapping":"INCOMPLETE"}`:c?"Select a supported meaning before reviewing a candidate.":"Baseline rules only. Open a change case to inspect candidate impact and evidence.";
  $("impact-json").textContent=JSON.stringify({impact:p?.impact??null,subject:p?.subject??null},null,2);
  const journeys=p?.projections?.journeys||[];$("journeys").replaceChildren(...journeys.map(value=>el("p",value,"muted")));
  if(!journeys.length)$("journeys").append(el("p","No generated journeys have been reported for this subject.","muted"));
}
function openCaseEvidence(section="overview") {
  if(!current)return false;
  switchTab("evidence");
  if(section==="decision"){$("review-decision").open=true;$("review-subject").focus();}
  else{$("evidence-subject").tabIndex=-1;$("evidence-subject").focus();}
  return true;
}
$("rules-evidence").onclick=()=>openCaseEvidence();
function inspectWorkingTransition(id,origin) {
  if((origin?.id??null)!==(current?.case.id??null)||origin?.version!==current?.case.version)return false;
  const model=current?(current.case.candidate||current.case.baseline):workbench?.model;
  if(!model?.transitions.some(item=>item.id===id)){notice("This transition is not present in the current working model.");return false;}
  modelView="working";editId=id;inspectorSelection={kind:"transition",id};
  switchTab("model");renderWorkbench();EijaShell.reveal("inspector");EijaTree.reveal($("domain-tree"),"transition",id);EijaShell.readable?.();$("transition-select").focus();return true;
}
function openComparisonImpact(navigation,selection) {
  if(!current||selection?.case!==current.case.id||selection.revision!==current.case.version)return false;
  const route=EijaCompare.impactNavigation(navigation?.reference,current.case.baseline,current.case.candidate),target=route.target;
  if(!target){notice(route.reason||"No declared destination is available for this reference.");return false;}
  if(!rememberComparisonSelection(selection))return false;
  if(target.view==="review"){
    if(!openComparisonSelection(target))return false;
  }else if(target.view==="evidence")openCaseEvidence(target.section);
  else if(target.view==="try"){
    switchTab("try");
    const action=[...$("runtime-actions").children].find(button=>button.dataset.action===target.action&&!button.disabled);
    const destination=action||(!$("reset").disabled?$("reset"):$("runtime-state"));
    if(destination===$("runtime-state"))destination.tabIndex=-1;
    destination.focus();
  }else if(target.view==="impact"){
    switchTab("impact");renderRules();$("rules-journeys").open=true;$("rules-journeys").querySelector("summary").focus();
  }
  notice(route.scope);return true;
}
function renderWorkbench() {
  if (!workbench) return;
  const model = workingModel(), pack = workbench.pack;
  renderRules();
  if (!current) {
    $("case-heading").hidden = true; $("case-title").textContent = "Explore the loaded baseline"; $("case-id").textContent = "No change case selected"; $("case-stage").textContent = "BASELINE";
    for (const id of ["propose", "save", "discard", "move-node", "verify", "reset", "approve", "apply", "export"]) $(id).disabled = true;
  }
  $("explorer-pack").textContent = pack.name; $("model-title").textContent = pack.name;
  $("model-revision").textContent = current ? `r${current.case.version} · ${modelView==="history"?"history":modelView==="baseline"?"original":current.case.candidate?"candidate":"baseline"}` : `v${pack.version}`;
  $("model-empty").hidden=false;
  $("model-empty").textContent=modelView==="history"?`Read-only historical preview · ${historyLabel}. Choose Working model to return.`:modelView==="baseline"?"Original baseline · read only. Switch to Working model to edit the candidate.":editable()?"Drag an endpoint or use the inspector. Every edit is checked by the kernel.":"Select a transition to inspect it. Start an intent to change the model.";
  $("model-version").querySelector('option[value="history"]').hidden=!historyModel;$("model-version").value=modelView;$("model-version").querySelector('option[value="baseline"]').disabled=!current?.case.candidate;
  $("undo-edit").disabled=!caseHistory?.can_undo||!current||editNeedsRefresh.has(current.case.id)||["APPLIED","DISCARDED"].includes(current.case.stage);
  $("redo-edit").disabled=!caseHistory?.can_redo||!current||editNeedsRefresh.has(current.case.id)||["APPLIED","DISCARDED"].includes(current.case.stage);
  $("history-undo").disabled=$("undo-edit").disabled;$("history-redo").disabled=$("redo-edit").disabled;
  $("source-status").textContent = status?.trusted_fixture ? "Source identity matches its release fixture. This identifies reviewed bytes; it does not prove correctness." : "SOURCE_REVIEW_REQUIRED · implementation changed since the owner-stamped fixture. Verification and apply remain blocked pending source review.";
  $("source-status").classList.toggle("source-required", !status?.trusted_fixture);
  $("status-model").textContent = `Pack ${pack.id} · ${current ? "revision " + current.case.version : "baseline"} · ${String(affordanceData?.semantic_hash || pack.digest || "unknown").slice(0, 12)}`;
  $("repository-status").textContent = EijaSource.state(workbench.connection).title;
  EijaSource.render($("source-view"), workbench.connection);
  EijaTree.render($("domain-tree"), workbench, model, showSelection,{key:JSON.stringify([pack.digest,current?.case.id||"baseline",modelView]),selection:inspectorSelection});renderNavigator();renderEditor();renderSelectionDetail();renderCanvas();EijaShell.renderHistory(current,caseHistory,previewHistory);renderEvidenceContext();globalThis.eijaAgentEdits?.update();
}
function showSelection(kind, item) {
  inspectorSelection={kind,id:item.id};
  if(["transition","state"].includes(kind))switchTab("model");
  EijaShell.reveal("inspector");EijaTree.reveal($("domain-tree"),kind,item.id);
  if(kind==="transition")selectTransition(item.id);else renderSelectionDetail();
  renderEvidenceContext();renderNavigator();
}
function renderSelectionDetail() {
  const kind=inspectorSelection?.kind,id=inspectorSelection?.id,model=workingModel();
  const item=selectedConcept(),root=$("selection-detail");
  $("transition-inspector").hidden=!!item&&kind!=="transition";
  root.replaceChildren();++impactSequence;$("inspector-impact").replaceChildren();delete $("inspector-impact").dataset.sourceHash;delete root.dataset.eijaId;
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
    impact.onclick=()=>task(()=>loadRepositoryImpact(item.id));root.append(impact);
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
  const problems=$("problems");problems.replaceChildren();
  const p=current?.packet,source=workbench?.connection,issues=new Map();
  const add=(code,message,origin)=>{
    if(!issues.has(code))issues.set(code,{code,messages:new Set(),origins:new Set()});
    const issue=issues.get(code);if(message)issue.messages.add(message);issue.origins.add(origin);return issue;
  };
  if(source&&source.status!=="connected")add("REPOSITORY_UNAVAILABLE",`Repository ${source.status||"unknown"}: ${source.reason||"No source snapshot available"}`,"Repository connection");
  if(source?.status==="connected"&&["FAIL","REVIEW","NOT_RUN"].includes(source.lint?.verdict))add("SOURCE_LINK_LINT",`Source-link lint: ${source.lint.verdict} · ${source.lint.findings?.length||0} findings`,"Source snapshot");
  if(!status?.trusted_fixture)add("SOURCE_REVIEW_REQUIRED","Owner review of changed implementation is outstanding.","Implementation identity");
  for(const code of p?.blockers||[])add(String(code),null,"Current packet blocker");
  if(lastDiagnostic){
    add(lastDiagnostic.code,lastDiagnostic.message,"Latest refused operation");
    for(const code of lastDiagnostic.details.codes||[])add(String(code),null,"Server diagnostic");
  }
  for(const issue of issues.values()){
    const li=el("li",undefined,"diagnostic");li.dataset.problemCode=issue.code;li.dataset.problemOrigins=JSON.stringify([...issue.origins]);if(issue.code==="SOURCE_REVIEW_REQUIRED")li.id="source-review-problem";
    li.append(el("strong",issue.code));for(const message of issue.messages)li.append(el("span",` · ${message}`));
    const detail=el("details");detail.append(el("summary","Issue origins"),el("p",[...issue.origins].join(" · ")));li.append(detail);
    if(issue.code==="SOURCE_LINK_LINT"){const button=el("button","Inspect source checks","text-button");button.onclick=()=>switchTab("source");li.append(button);}
    problems.append(li);
  }
  if(lastDiagnostic?.details.refs?.length){
    const item=el("li",undefined,"diagnostic-references");item.append(el("span","Refused operation references"));
    for(const ref of lastDiagnostic.details.refs){const button=el("button",ref,"text-button");button.onclick=()=>followReference(ref);item.append(button);}problems.append(item);
  }
  if(!issues.size)problems.append(el("li",p?"No review blockers reported by the current packet.":"No case selected; case checks have not run."));
  EijaShell.renderEvidence($("evidence-summary"),p);$("problem-count").textContent=issues.size;
  $("focus-problem-count").textContent=issues.size;
  $("status-evidence").textContent=p?`Technical eligibility: ${p.eligible?"eligible":"blocked"} · human UNKNOWN`:"Evidence: NOT_RUN · human UNKNOWN";
}
let editPreview=null,editPreviewSequence=0;
function markEditReconciliation(preview,status){
  editNeedsRefresh.set(preview.caseId,{caseId:preview.caseId,version:preview.version,semanticHash:preview.semanticHash,status});
  renderEditReconciliation();if(current?.case.id===preview.caseId){renderEditor();renderCanvas();}
}
function editPreviewCurrent(preview){
  return editPreview===preview&&editable()&&current?.case.id===preview.caseId&&current.case.version===preview.version&&
    current.case.stage===preview.stage&&current.packet?.subject?.semantic===preview.semanticHash&&JSON.stringify(current.case.candidate)===preview.originalModel;
}
function editPreviewStatus(preview,phase,message){
  if(editPreview!==preview)return;
  preview.phase=phase;const root=$("edit-preview-status");root.dataset.status=phase;root.textContent=message;
  $("edit-preview-apply").disabled=phase!=="ready";$("edit-preview-cancel").disabled=phase==="submitting"||!!preview.refreshPending;
  $("edit-preview-cancel").textContent="Close preview";
  $("edit-preview").setAttribute("aria-busy",String(["checking","submitting"].includes(phase)||!!preview.refreshPending));
  if(!$("edit-preview-cancel").disabled&&!["checking","ready"].includes(phase)&&[document.body,$("edit-preview-apply")].includes(document.activeElement))$("edit-preview-cancel").focus();
}
function closeEditPreview(){
  const preview=editPreview;if(!preview)return true;
  if(preview.phase==="submitting"||preview.refreshPending)return false;
  ++editPreviewSequence;editPreview=null;preview.comparison?.destroy();$("edit-preview").close();
  const target=preview.invoker;
  if(target?.isConnected&&!target.disabled&&target.getClientRects().length)target.focus();else if($("transition-select").getClientRects().length)$("transition-select").focus();else if($("case-title").getClientRects().length)$("case-title").focus();
  if(!preview.submitted)notice("Edit preview closed. No edit was submitted.");return true;
}
function validateEditPreview(check,preview){
  const strings=value=>Array.isArray(value)&&value.every(item=>typeof item==="string");
  if(!check||check.scope!=="semantic-edit-preview"||check.applied!==false||check.persisted!==false||typeof check.legal!=="boolean"||!strings(check.codes)||!strings(check.refs)||JSON.stringify(check.transaction)!==JSON.stringify(preview.transaction))throw new ApiError("RESPONSE_INVALID","The edit check did not identify this exact proposed transaction.");
  if(check.case_id!==preview.caseId||check.version!==preview.version||check.stage!==preview.stage||check.semantic_hash!==preview.semanticHash||JSON.stringify(check.current)!==preview.originalModel)throw new ApiError("EDIT_PREVIEW_STALE","The checked model is no longer the candidate selected for this edit. Close and refresh the current model.");
  if(check.legal&&(!check.candidate||typeof check.candidate_semantic_hash!=="string"||!check.candidate_semantic_hash))throw new ApiError("RESPONSE_INVALID","The edit check supplied no identified proposed candidate.");
  if(!check.legal&&(check.candidate!==null||check.candidate_semantic_hash!==null))throw new ApiError("RESPONSE_INVALID","A refused edit cannot supply an applicable proposed candidate.");
}
async function checkEditPreview(preview){
  const active=()=>editPreview===preview&&preview.sequence===editPreviewSequence;
  try{
    const check=await api(`cases/${preview.caseId}/edit/preview`,{transaction:preview.transaction});
    if(!active())return false;
    $("edit-preview-json").textContent=JSON.stringify(check,null,2);
    validateEditPreview(check,preview);preview.check=check;
    if(!editPreviewCurrent(preview))throw new ApiError("EDIT_PREVIEW_STALE","The workspace subject changed while checking. Close and choose the edit again.");
    if(!check.legal){
      const error=new ApiError("EDIT_REFUSED","The kernel refused this edit; no model was changed",{codes:check.codes,refs:check.refs});
      editPreviewStatus(preview,"refused",`${error.message} · ${check.codes.join("; ")}`);$("edit-preview-diagnostic").textContent=JSON.stringify(error.details,null,2);reportError(error,{reveal:false});renderCanvas();return false;
    }
    preview.comparison=EijaCompare.render($("edit-preview-comparison"),{case:{id:preview.caseId,version:preview.version,baseline:check.current,candidate:check.candidate},packet:{}},{preview:true});
    if(typeof preview.comparison.select!=="function")throw new ApiError("RESPONSE_INVALID","The checked snapshots could not be rendered. No edit was submitted.");
    preview.comparison.select({kind:"transition",id:preview.transaction.transition});
    $("edit-preview").dataset.proposedSemanticHash=check.candidate_semantic_hash;
    $("edit-preview-subject").textContent=`Case ${preview.caseId} · Captured revision ${preview.version} · before ${preview.semanticHash.slice(0,12)} → proposed ${check.candidate_semantic_hash.slice(0,12)}. Exact identities are in the server preview below.`;
    editPreviewStatus(preview,"ready","Kernel check accepted this proposed edit. Review the exact differences, then Apply edit or close this preview. No model has changed.");return true;
  }catch(error){
    if(!active())return false;
    editPreviewStatus(preview,error.code==="EDIT_PREVIEW_STALE"?"stale":"failed",error.message);
    $("edit-preview-diagnostic").textContent=JSON.stringify({code:error.code||"REQUEST_FAILED",message:error.message,details:error.details||{}},null,2);reportError(error,{reveal:false});return false;
  }
}
function commitChoice(choice,options={}){
  if(busy||editPreview?.phase==="submitting")return;
  if(editNeedsRefresh.has(current?.case.id)){notice("Refresh this case before proposing another edit: the previous submission needs reconciliation.",true);return;}
  if(!editable()||!choice?.transaction){notice("Choose a different server-listed destination for the selected transition.");return;}
  if(editPreview&&!closeEditPreview())return;
  const c=current.case,preview={sequence:++editPreviewSequence,caseId:c.id,version:c.version,stage:c.stage,semanticHash:current.packet?.subject?.semantic,
    transaction:JSON.parse(JSON.stringify(choice.transaction)),originalModel:JSON.stringify(c.candidate),invoker:document.activeElement,phase:"checking",submitted:false,onCommitted:options.onCommitted};
  editPreview=preview;$("edit-preview-comparison").replaceChildren();$("edit-preview-diagnostic").textContent="";$("edit-preview-json").textContent=JSON.stringify({transaction:preview.transaction},null,2);
  const dialog=$("edit-preview");Object.assign(dialog.dataset,{caseId:preview.caseId,revision:String(preview.version),semanticHash:preview.semanticHash||"",proposedSemanticHash:""});
  $("edit-preview-subject").textContent=`Case ${preview.caseId} · Captured revision ${preview.version} · before ${preview.semanticHash||"identity unavailable"}`;
  editPreviewStatus(preview,"checking","Checking the proposed edit without changing the model…");dialog.showModal();$("edit-preview-cancel").focus();
  if(!preview.semanticHash){editPreviewStatus(preview,"stale","Candidate identity is unavailable. Close and refresh the model before editing.");return;}
  return checkEditPreview(preview);
}
function confirmEditPreview(){
  const preview=editPreview;
  if(busy||!preview||preview.phase!=="ready")return;
  if(!editPreviewCurrent(preview)){editPreviewStatus(preview,"stale","The case, model or inspection view changed. Close and choose the edit again.");return;}
  editPreviewStatus(preview,"submitting","Submitting this exact checked edit. The request can no longer be cancelled.");preview.submitted=true;
  return task(async()=>{
    let acknowledged=false;
    try{
      const result=await api(`cases/${preview.caseId}/edit`,{expected_version:preview.version,transaction:preview.transaction});
      if(!result||result.id!==preview.caseId||result.version!==preview.version+1||JSON.stringify(result.candidate)!==JSON.stringify(preview.check.candidate))throw new ApiError("RESPONSE_INVALID","The edit response did not acknowledge the expected case revision.");
      acknowledged=true;
      if(editPreview!==preview)return;
      if(!editPreviewCurrent(preview)){markEditReconciliation(preview,"committed");editPreviewStatus(preview,"committed","Edit acknowledged, but the workspace subject changed. Close and refresh this case to reconcile.");return;}
      preview.refreshPending=true;clearRuntime();editPreviewStatus(preview,"committed","Edit committed. Refreshing the workspace…");$("edit-preview-cancel").disabled=true;
      await load(preview.caseId,()=>editPreview===preview&&current?.case.id===preview.caseId);
      preview.refreshPending=false;
      if(editPreview!==preview||current?.case.id!==preview.caseId)return;
      closeEditPreview();notice("One typed transaction committed. The server model has reloaded; matching evidence and decisions must be reconsidered.");
      if(current.case.version===preview.version+1&&current.packet?.subject?.semantic===preview.check.candidate_semantic_hash&&JSON.stringify(current.case.candidate)===JSON.stringify(preview.check.candidate)){
        try{preview.onCommitted?.({caseId:preview.caseId,previousVersion:preview.version,version:current.case.version,semanticHash:current.packet.subject.semantic,transaction:preview.transaction});}
        catch{notice("Edit committed. The proposal panel could not update; inspect the current model and history.",true);}
      }
    }catch(error){
      preview.refreshPending=false;
      if(editPreview!==preview)return;
      const refused=!acknowledged&&error.responseValid===true&&!["REQUEST_FAILED","RESPONSE_INVALID"].includes(error.code)&&[400,401,403,404,409,413,415,422].includes(error.httpStatus);
      const phase=acknowledged?"committed":refused?"refused":"unknown";
      if(acknowledged||!refused)markEditReconciliation(preview,phase);
      editPreviewStatus(preview,phase,acknowledged?"Edit committed, but the workspace refresh failed. Close and refresh the current model.":refused?`${error.message}. This edit was refused; the last loaded model is retained.`:`Edit outcome unknown: ${error.message}. It may have committed. Close and refresh before proposing another edit; no automatic retry was sent.`);
      $("edit-preview-diagnostic").textContent=JSON.stringify({code:error.code||"REQUEST_FAILED",message:error.message,details:error.details||{}},null,2);reportError(error,{reveal:false});
    }
  },"Submitting the checked edit…");
}
$("edit-reconcile-refresh").onclick=()=>task(refreshCurrentModel,"Refreshing the case to reconcile its edit…");
$("edit-preview-cancel").onclick=closeEditPreview;
$("edit-preview-apply").onclick=confirmEditPreview;
$("edit-preview").addEventListener("cancel",event=>{event.preventDefault();closeEditPreview();});
$("edit-preview").addEventListener("keydown",event=>{
  if(event.key==="Escape"){event.preventDefault();event.stopPropagation();closeEditPreview();}
  else if((event.ctrlKey||event.metaKey)&&["k","b"].includes(event.key.toLowerCase())){event.preventDefault();event.stopPropagation();}
});
$("transition-select").onchange = event => selectTransition(event.target.value);
$("edit-source").onclick = () => edit($("model-source").value);
document.querySelector(".editor-navigation").addEventListener("keydown", event => {
  const group=event.target.closest('[role="tablist"]');if(!group)return;
  const tabs = [...group.querySelectorAll("[data-tab]")], index = tabs.indexOf(event.target); if (index < 0) return;
  const next = event.key === "ArrowRight" ? tabs[(index + 1) % tabs.length] : event.key === "ArrowLeft" ? tabs[(index + tabs.length - 1) % tabs.length] : event.key === "Home" ? tabs[0] : event.key === "End" ? tabs[tabs.length - 1] : null;
  if (next) {event.preventDefault(); openWorkTab(next.dataset.tab); next.focus();}
});

document.querySelectorAll("[data-comparison-tab]").forEach(button=>button.onclick=()=>switchTab(button.dataset.comparisonTab));
$("comparison-tabs").addEventListener("keydown",event=>{
  const tabs=[...$("comparison-tabs").querySelectorAll("[data-comparison-tab]")],index=tabs.indexOf(event.target);if(index<0)return;
  const next=event.key==="ArrowRight"?tabs[(index+1)%tabs.length]:event.key==="ArrowLeft"?tabs[(index+tabs.length-1)%tabs.length]:event.key==="Home"?tabs[0]:event.key==="End"?tabs[tabs.length-1]:null;
  if(next){event.preventDefault();switchTab(next.dataset.comparisonTab);next.focus();}
});

const paletteCommands = [
  ["New change case",openIntent],
  ["Switch change case",focusCasePicker],
  ["Toggle explorer",()=>EijaShell.toggle("explorer")],
  ["Toggle inspector",()=>EijaShell.toggle("inspector")],
  ["Toggle lower panel",()=>EijaShell.toggle("panel")],
  ["Focus work area",()=>EijaShell.focusWorkspace()],
  ["Restore workspace",()=>EijaShell.focusWorkspace(false)],
  ["Show local case history",()=>EijaShell.bottom("history-pane")],
  ["Fit model overview",()=>{switchTab("model");EijaShell.fit();}],
  ...workDestinations.map(([name,label])=>[`Open ${label}`,()=>openWorkDestination(name)]),
  ["Open Model changes",()=>{switchTab("review");$("comparison-model-tab").focus();}],
  ["Open Code changes",()=>{switchTab("repository-changes");$("comparison-code-tab").focus();}],
  ["Focus domain explorer", () => {navigatorMode="domain";renderNavigator();EijaShell.reveal("explorer");$("domain-tree").querySelector('[tabindex="0"]')?.focus();}],
  ["Refresh current model", () => task(refreshCurrentModel)],
  ["Select a transition", openTransitionPicker]
];
async function refreshCurrentModel() {
  if(current)await load(current.case.id);else{if(!await refreshSource(true))return;renderWorkbench();clearDiagnostic();}
  notice("Current model refreshed from the server.");
}
function filterCommands() {
  const query = $("palette-search").value.toLowerCase(), root = $("palette-results"); root.replaceChildren();
  for (const [label, action] of paletteCommands.filter(([label]) => label.toLowerCase().includes(query))) {
    const button = el("button", label, "palette-command"); button.onclick = () => {$("command-palette").close(); action();}; root.append(button);
  }
  if (!root.childElementCount) root.append(el("p", "No matching commands."));
}
function openPalette() {if(document.querySelector("dialog[open]"))return;$("palette-search").value = ""; filterCommands(); $("command-palette").showModal(); $("palette-search").focus();}
$("open-palette").onclick = openPalette; $("close-palette").onclick = () => $("command-palette").close();
$("palette-search").oninput = filterCommands;
$("palette-search").onkeydown = event => {if (["ArrowDown", "Enter"].includes(event.key)) {event.preventDefault(); $("palette-results").querySelector("button")?.focus();}};
document.addEventListener("keydown", event => {if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {event.preventDefault(); if($("command-palette").open) $("command-palette").close(); else openPalette();}});

$("open-source").onclick = () => switchTab("source");
$("refresh-source").onclick = () => task(refreshSource, "Reading the configured repository snapshot…");
function sourceSnapshot(){return workbench?.connection?.source_hash||null;}
function sourceQuery(path,key,value,hash){
  if(!hash)throw new ApiError("SOURCE_SNAPSHOT_UNAVAILABLE","Refresh the repository connection before following source links.");
  return `repository/${path}?${key}=${encodeURIComponent(value)}&expected_source_hash=${encodeURIComponent(hash)}`;
}
function cancelSourceRead(){
  ++sourceSequence;++impactSequence;
  if(!sourcePending)return;
  sourcePending=false;
  if(sourceRecord)EijaShell.renderSource(sourceRecord);
  else EijaShell.sourceError("The pending source request was cancelled because the displayed case changed.","SOURCE_REQUEST_CANCELLED");
  EijaShell.sourceFreshness("cancelled","Source navigation cancelled by a case revision change. Choose a reference again.");
}
async function loadRepositoryImpact(term){
  const sequence=++impactSequence,hash=sourceSnapshot(),selection=JSON.stringify(inspectorSelection);
  const active=()=>sequence===impactSequence&&hash===sourceSnapshot()&&selection===JSON.stringify(inspectorSelection);
  try{
    const data=await api(sourceQuery("impact","term",term,hash));
    if(!active())return;
    if(data.status==="connected"&&data.source_hash!==hash)throw new ApiError("SOURCE_SNAPSHOT_MISMATCH","Impact response does not describe the selected source snapshot.");
    EijaShell.renderImpact($("inspector-impact"),data,openSource);
    notice("Known dependency links loaded for the captured snapshot. Unknown dependencies remain outside this mapping.");
  }catch(error){
    if(!active())return;
    const root=$("inspector-impact");delete root.dataset.sourceHash;root.replaceChildren(el("p",error.message,"diagnostic"));
    const retry=el("button","Refresh source","secondary");retry.dataset.sourceRefresh="true";retry.onclick=()=>task(refreshSource);root.append(retry);
    reportError(error);
  }
}
async function refreshSource(refreshBaseline=false){
  cancelSourceRead();const sequence=sourceSequence;
  const [next,nextStatus]=await Promise.all([api("workbench"),api("status")]);
  if(sequence!==sourceSequence)return false;
  workbench=refreshBaseline?next:{...workbench,connection:next.connection};status=nextStatus;
  $("source-status").textContent=status?.trusted_fixture?"Source identity matches its release fixture. This identifies reviewed bytes; it does not prove correctness.":"SOURCE_REVIEW_REQUIRED · implementation changed since the owner-stamped fixture. Verification and apply remain blocked pending source review.";
  $("source-status").classList.toggle("source-required",!status?.trusted_fixture);
  $("repository-status").textContent=EijaSource.state(workbench.connection).title;
  EijaSource.render($("source-view"),workbench.connection);
  $("inspector-impact").replaceChildren(el("p","Source snapshot refreshed. Find repository references again to calculate its known links.","muted"));
  delete $("inspector-impact").dataset.sourceHash;
  renderProblems();
  if(sourceRecord){
    EijaShell.renderSource(sourceRecord);
    EijaShell.sourceFreshness("previous","Previous captured source remains visible while its reference is reopened in the refreshed snapshot.");
    if(!await openSource(sourceRecord.reference,false,false)||sequence+1!==sourceSequence)return false;
  }
  const connection=EijaSource.state(workbench.connection);
  notice(connection.connected?"Repository snapshot refreshed. The model, unsent edits and runtime were preserved; indexing did not execute project tests.":connection.title+": "+connection.reason,!connection.connected);
  return connection.connected;
}

function previewHistory(model,label){historyModel=model;historyLabel=label;modelView="history";editId=null;inspectorSelection=null;switchTab("model");renderWorkbench();notice("Historical model preview · read only. Use Working model to return to the current candidate.");}
function openIntent(){switchTab("change");$("create-panel").hidden=false;$("request").focus();notice("");}
$("case-switcher").onchange=event=>{const id=event.target.value;$("case-switcher").value=current?.case.id||"";if(id)task(async()=>{try{await load(id);notice("");}finally{$("case-switcher").value=current?.case.id||"";}});};
$("case-picker-retry").onclick=()=>task(async()=>{const invoker=document.activeElement;if(await cases()){clearDiagnostic();notice("Case list refreshed from the server.");if(invoker===$("case-picker-retry")&&[invoker,document.body,document.documentElement].includes(document.activeElement))focusCasePicker();}},"Refreshing case list…");
$("canvas-direction").onchange=event=>{canvasDirection=event.target.value;renderCanvas();EijaShell.readable();};
$("model-version").onchange=event=>{modelView=event.target.value;renderWorkbench();};
async function openSource(reference,record=true,navigate=true){
  const sequence=++sourceSequence,hash=sourceSnapshot();sourcePending=true;
  if(navigate)switchTab("code");
  if(sourceRecord){EijaShell.renderSource(sourceRecord);EijaShell.sourceFreshness("loading",`Reading ${reference}. Previous captured source remains visible until this request finishes.`);}
  else {EijaShell.sourceLoading(reference);EijaShell.sourceFreshness("loading","Reading the selected repository snapshot…");}
  try{
    const data=await api(sourceQuery("source","reference",reference,hash));
    if(sequence!==sourceSequence||hash!==sourceSnapshot())return false;
    if(data.status!=="connected")throw new ApiError("SOURCE_UNAVAILABLE",data.reason||"No source snapshot is available.");
    if(data.source_hash!==hash)throw new ApiError("SOURCE_SNAPSHOT_MISMATCH","The source response does not describe the selected snapshot.");
    sourceRecord=data;EijaShell.renderSource(data);
    EijaShell.sourceFreshness("captured","Source and repository connection describe the same captured bytes. Later filesystem changes require another check.");
    if(record){sourceHistory=sourceHistory.slice(0,sourceHistoryIndex+1);sourceHistory.push(reference);sourceHistoryIndex=sourceHistory.length-1;}
    $("source-back").disabled=sourceHistoryIndex<=0;
    return true;
  }catch(error){if(sequence===sourceSequence){
    if(sourceRecord)EijaShell.renderSource(sourceRecord);else EijaShell.sourceError(error.message,error.code);
    const code=error.code||"SOURCE_UNAVAILABLE",message=error.message.startsWith(code+":")?error.message:`${code}: ${error.message}`;
    EijaShell.sourceFreshness(error.code=== "SOURCE_SNAPSHOT_STALE"?"stale":"unavailable",`${message}${sourceRecord?" Previous captured source is retained; it is not a current filesystem read.":""}`,()=>task(refreshSource));
    notice(error.message,true);
  }return false;}finally{if(sequence===sourceSequence)sourcePending=false;}
}
$("source-open-form").onsubmit=event=>{event.preventDefault();const ref=$("source-reference").value.trim();if(ref)openSource(ref);};
async function previousSource(){
  const previous=sourceHistoryIndex-1;
  if(previous<0)return;
  if(await openSource(sourceHistory[previous],false)){sourceHistoryIndex=previous;$("source-back").disabled=previous<=0;}
}
$("source-back").onclick=previousSource;
$("undo-edit").onclick=()=>task(async()=>{if(!current||editNeedsRefresh.has(current.case.id)||!caseHistory?.can_undo||["APPLIED","DISCARDED"].includes(current.case.stage))return;await command("undo");clearRuntime();modelView="working";render();notice("Last semantic edit undone by the kernel. Earlier receipts are retained; eligibility is recomputed.");});
$("redo-edit").onclick=()=>task(async()=>{if(!current||editNeedsRefresh.has(current.case.id)||!caseHistory?.can_redo||["APPLIED","DISCARDED"].includes(current.case.stage))return;await command("redo");clearRuntime();modelView="working";render();notice("Semantic edit reapplied by the kernel. The displayed model was reloaded from the server.");});
$("history-undo").onclick=$("undo-edit").onclick;$("history-redo").onclick=$("redo-edit").onclick;
EijaShell.init({newIntent:openIntent,openTab:openWorkDestination});
let repositoryReview=null,repositoryComparison=null,repositoryFile=null,repositorySelection=null,repositoryView="diff";
let repositoryGeneration=0,repositoryFileGeneration=0,repositoryRenderGeneration=0;
let repositoryLoading=null,repositoryPendingPair=null,repositoryPendingSelection=null,repositoryError=null,repositoryDiagnostic=null;
const repositoryObjectId=value=>typeof value==="string"&&/^(?:[0-9a-f]{40}|[0-9a-f]{64})$/.test(value);
const repositoryPairMatches=(data,pair)=>data?.base?.commit===pair?.base&&data?.head?.commit===pair?.head;
const repositorySameSelection=(left,right)=>!!left&&!!right&&["comparison_id","base_commit","head_commit","path"].every(key=>left[key]===right[key])&&(left.reference??null)===(right.reference??null);
const repositoryPairLabel=(base,head)=>`${base.slice(0,12)}… → ${head.slice(0,12)}…`;
function updateRepositoryRevisionHeader(){
  const comparison=repositoryComparison,node=$("repository-loaded-pair");
  const full=comparison?`Before ${comparison.base.commit}; After ${comparison.head.commit}`:"No immutable comparison loaded.";
  node.textContent=comparison?repositoryPairLabel(comparison.base.commit,comparison.head.commit):full;
  node.hidden=!comparison;$("repository-introduction").hidden=!!comparison;
  node.title=full;node.setAttribute("aria-label",full);node.dataset.comparisonId=comparison?.comparison_id||"";
  $("repository-pair-details").hidden=!comparison;
  $("repository-loaded-base").textContent=comparison?.base.commit||"Not loaded";
  $("repository-loaded-head").textContent=comparison?.head.commit||"Not loaded";
}
function closeInitialRepositoryRevisions(){
  const editor=$("repository-revisions"),summary=$("repository-revisions-summary"),focused=document.activeElement;
  const restore=editor.contains(focused)&&focused!==summary;
  editor.open=false;
  if(restore&&summary.getClientRects().length)summary.focus({preventScroll:true});
}
function repositoryRequestStatus(message,state){
  const node=$("repository-comparison-status");node.textContent=message;node.dataset.status=state;
  node.dataset.comparisonId=repositoryComparison?.comparison_id||"";
  const quiet=!!repositoryComparison&&["captured","captured-file"].includes(state);
  node.classList.toggle("sr-only",quiet);
  const summary=$("repository-revisions-summary");
  if(quiet&&document.activeElement===node&&summary.getClientRects().length)summary.focus({preventScroll:true});
  $("repository-compare-form").setAttribute("aria-busy",String(!!repositoryLoading));
}
function repositoryRetainedLabel(){
  if(!repositoryComparison)return "No successful repository comparison is displayed.";
  const selected=repositorySelection?` · ${repositorySelection.path}${repositorySelection.reference?" · "+repositorySelection.reference:""}`:"";
  return `Displaying retained immutable pair ${repositoryPairLabel(repositoryComparison.base.commit,repositoryComparison.head.commit)}${selected}. This is not the pending or refused result.`;
}
function restoreRepositoryFocus(previous){
  if(!previous)return;
  const active=document.activeElement;
  if(active!==document.body&&active!==document.documentElement&&active!==previous.node)return;
  const available=node=>node&&!node.disabled&&node.getClientRects().length>0;
  const equivalent=previous.id?$(previous.id):null,status=$("repository-comparison-status");
  const fallback=status.classList.contains("sr-only")?$("repository-revisions-summary"):status;
  const target=available(equivalent)?equivalent:fallback;
  if(available(target))target.focus({preventScroll:true});
}
function renderRepositoryReview(){
  updateRepositoryRevisionHeader();
  const root=$("repository-review"),navigator=$("repository-change-navigator"),focused=document.activeElement;
  const previousFocus=focused&&(root.contains(focused)||navigator.contains(focused))?{id:focused.id,node:focused}:null;
  const presentation=repositoryReview?.getState();
  const previous=presentation?.selection,selectedFile=repositorySelection;
  const sameFile=previous&&selectedFile&&["comparison_id","base_commit","head_commit","path"].every(key=>previous[key]===selectedFile[key]);
  const symbolsOpen=!!(sameFile&&presentation.symbolsOpen);
  const symbolsFilter=sameFile&&presentation.symbolsFilter==="all"?"all":"changed";
  repositoryReview?.destroy();
  const render=++repositoryRenderGeneration,generation=repositoryGeneration;
  const identity=repositoryComparison?.comparison_id,selected=repositorySelection;
  const active=()=>render===repositoryRenderGeneration&&generation===repositoryGeneration&&identity===repositoryComparison?.comparison_id;
  const select=value=>{if(active()&&!repositoryPendingPair)return loadRepositoryChangeFile(value);return false;};
  repositoryReview=EijaRepositoryReview.render(root,{
    comparison:repositoryComparison,file:repositoryFile,selection:repositorySelection,view:repositoryView,
    loading:repositoryLoading,error:repositoryError,symbolsOpen,symbolsFilter,navigatorRoot:navigator,
    onSelectFile:repositoryPendingPair?undefined:select,onSelectSymbol:repositoryPendingPair?undefined:select,
    onViewChange:(view,selection)=>{if(active()&&repositorySameSelection(selected,selection)&&repositorySameSelection(repositorySelection,selection))repositoryView=view;}
  });
  $("repository-show-files").disabled=!repositoryComparison?.files?.length;
  restoreRepositoryFocus(previousFocus);
}
function invalidateRepositoryRequest(){
  $("repository-revisions").open=true;
  ++repositoryGeneration;++repositoryFileGeneration;repositoryPendingPair=null;repositoryPendingSelection=null;repositoryLoading=null;
  repositoryRequestStatus(`Commit fields changed. Choose Compare commits to load them. ${repositoryRetainedLabel()}`,"draft");
  renderRepositoryReview();
}
function repositoryFailure(error,state){
  $("repository-revisions").open=true;
  repositoryError={code:error.code||"REQUEST_FAILED",message:error.message||"Repository comparison request failed",details:error.details||{}};
  const message=repositoryError.message.startsWith(repositoryError.code+":")?repositoryError.message:`${repositoryError.code}: ${repositoryError.message}`;
  repositoryRequestStatus(`${message} ${repositoryRetainedLabel()}`,state);
  renderRepositoryReview();reportError(error);repositoryDiagnostic=lastDiagnostic;
}
function clearRepositoryDiagnostic(){
  if(repositoryDiagnostic&&lastDiagnostic===repositoryDiagnostic){
    const expected=repositoryDiagnostic.message+(repositoryDiagnostic.details?.codes?.length?" · "+repositoryDiagnostic.details.codes.join("; "):"");
    clearDiagnostic();if($("notice").textContent===expected)notice("");
  }
  repositoryDiagnostic=null;
}
async function loadRepositoryComparison(base,head){
  const initialComparison=!repositoryComparison;
  const generation=++repositoryGeneration;++repositoryFileGeneration;
  repositoryPendingPair=null;repositoryPendingSelection=null;repositoryLoading=null;repositoryError=null;
  const pair={base,head},validBase=repositoryObjectId(base),validHead=repositoryObjectId(head);
  $("repository-base").setAttribute("aria-invalid",String(!validBase));$("repository-head").setAttribute("aria-invalid",String(!validHead));
  if(!validBase||!validHead){
    repositoryFailure(new ApiError("CHANGE_REVISION_INVALID","Use full 40- or 64-character lowercase hexadecimal local commit IDs for Before and After."),"invalid");
    $(validBase?"repository-head":"repository-base").focus();return false;
  }
  repositoryPendingPair=pair;repositoryLoading="comparison";
  const active=()=>generation===repositoryGeneration&&repositoryPendingPair?.base===base&&repositoryPendingPair?.head===head;
  repositoryRequestStatus(`Loading requested commits ${repositoryPairLabel(base,head)}. ${repositoryRetainedLabel()}`,"loading");renderRepositoryReview();
  try{
    const data=await api(`repository/change?${new URLSearchParams(pair)}`);
    if(!active())return false;
    if(!["available","partial"].includes(data?.status))throw new ApiError(data?.status==="unconfigured"?"REPOSITORY_CHANGE_UNCONFIGURED":"REPOSITORY_CHANGE_UNAVAILABLE",data?.reason||"No immutable repository comparison is available.",{status:data?.status||"not_reported"});
    if(!repositoryPairMatches(data,pair)||EijaRepositoryReview.inspect(data,null,null).status!=="select_file")throw new ApiError("CHANGE_SUBJECT_MISMATCH","The comparison response does not describe the requested immutable commit pair.");
    repositoryComparison=data;repositoryFile=null;repositorySelection=null;repositoryView="diff";
    repositoryPendingPair=null;repositoryLoading=null;repositoryError=null;clearRepositoryDiagnostic();
    repositoryRequestStatus(`Comparison loaded · ${data.status.toUpperCase()}. Choose a changed file.`,"captured");renderRepositoryReview();if(initialComparison)closeInitialRepositoryRevisions();return true;
  }catch(error){
    if(!active())return false;
    repositoryPendingPair=null;repositoryLoading=null;repositoryFailure(error,"unavailable");return false;
  }
}
async function loadRepositoryChangeFile(selection){
  if(repositoryPendingPair||!repositoryComparison)return false;
  const sequence=++repositoryFileGeneration;
  const selected=selection&&{comparison_id:selection.comparison_id,base_commit:selection.base_commit,head_commit:selection.head_commit,path:selection.path,reference:selection.reference??null};
  if(EijaRepositoryReview.inspect(repositoryComparison,null,selected).status!=="select_file"||!selected){
    repositoryPendingSelection=null;repositoryLoading=null;
    repositoryFailure(new ApiError("CHANGE_REFERENCE_DENIED","Choose a file or extracted reference from the displayed immutable comparison."),"unavailable");return false;
  }
  const generation=repositoryGeneration,comparison=repositoryComparison;
  repositoryPendingSelection=selected;repositoryLoading="file";repositoryError=null;
  const active=()=>generation===repositoryGeneration&&sequence===repositoryFileGeneration&&comparison===repositoryComparison&&repositorySameSelection(repositoryPendingSelection,selected)&&repositoryPairMatches(repositoryComparison,{base:selected.base_commit,head:selected.head_commit});
  repositoryRequestStatus(`Loading ${selected.path}${selected.reference?" · "+selected.reference:""} from the displayed commits. ${repositoryRetainedLabel()}`,"loading-file");renderRepositoryReview();
  try{
    const query=new URLSearchParams({base:selected.base_commit,head:selected.head_commit,path:selected.path});if(selected.reference!==null)query.set("reference",selected.reference);
    const data=await api(`repository/change/file?${query}`);
    if(!active())return false;
    const result=EijaRepositoryReview.inspect(comparison,data,selected);
    if(result.status!=="ready")throw new ApiError(result.status==="file_unavailable"?"REPOSITORY_CHANGE_FILE_UNAVAILABLE":"CHANGE_SUBJECT_MISMATCH",result.reason||"Historical file identity does not match the displayed comparison.");
    repositoryFile=data;repositorySelection=selected;repositoryPendingSelection=null;repositoryLoading=null;repositoryError=null;clearRepositoryDiagnostic();
    repositoryRequestStatus(`Captured ${selected.path}${selected.reference?" · "+selected.reference:""} at ${repositoryPairLabel(selected.base_commit,selected.head_commit)}.`,"captured-file");renderRepositoryReview();return true;
  }catch(error){
    if(!active())return false;
    repositoryPendingSelection=null;repositoryLoading=null;repositoryFailure(error,"unavailable-file");return false;
  }
}
$("repository-compare-form").onsubmit=event=>{event.preventDefault();loadRepositoryComparison($("repository-base").value,$("repository-head").value);};
for(const id of ["repository-base","repository-head"])$(id).addEventListener("input",invalidateRepositoryRequest);
$("repository-show-files").onclick=()=>{
  navigatorMode="task";renderNavigator();EijaShell.reveal("explorer");
  const root=$("repository-change-navigator");(root.querySelector('button[aria-pressed="true"]')||root.querySelector("button"))?.focus();
};
renderRepositoryReview();


// Suggestions never write a model. Owner confirmation remains in the existing edit preview.
function agentEditContext(){
  const c=current?.case;if(!c?.candidate)return null;
  return {caseId:c.id,version:c.version,stage:c.stage,semanticHash:current.packet?.subject?.semantic,
    model:c.candidate,packId:workbench?.pack.id,packDigest:workbench?.pack.digest,editable:editable(),selectedTransition:editId};
}
function navigateAgentEdit(kind,transaction){
  const c=current?.case;if(!c?.candidate||!c.candidate.transitions.some(item=>item.id===transaction.transition))return false;
  const origin={id:c.id,version:c.version};
  if(kind==="model")return inspectWorkingTransition(transaction.transition,origin);
  if(!["changes","rules"].includes(kind))return false;
  editId=transaction.transition;inspectorSelection={kind:"transition",id:editId};modelView="working";
  if(kind==="changes"){renderWorkbench();return openComparisonSelection({kind:"transition",id:transaction.transition});}
  if(kind==="rules"){
    switchTab("impact");renderWorkbench();
    const row=[...$("rule-table").children].find(item=>item.dataset.transitionId===transaction.transition),target=row?.querySelector("button");
    target?.scrollIntoView({block:"nearest"});target?.focus();return !!target;
  }
  return false;
}
globalThis.eijaAgentEdits=EijaAgentEdit.mount($("agent-edit-panel"),{
  getContext:agentEditContext,
  propose:(request,context)=>{if(busy)throw new ApiError("WORKSPACE_BUSY","Wait for the current workspace action to finish.");return api(`cases/${context.caseId}/edit/propose`,{request,expected_version:context.version});},
  previewChoice:(choice,onCommitted)=>commitChoice(choice,{onCommitted}),
  navigate:navigateAgentEdit
});
globalThis.eijaAgentEdits.update();
