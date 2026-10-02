"use strict";
// UI preferences and read-only projections. This module has no API or model mutation port.
const EijaShell = (() => {
  const get = id => document.getElementById(id);
  const make = (tag, text, cls) => {const n = document.createElement(tag); if (text !== undefined) n.textContent = String(text); if (cls) n.className = cls; return n;};
  const clamp = (n, low, high) => Math.min(high, Math.max(low, n));
  let settings = {explorer:230, inspector:288, panel:160, explorerOpen:true, inspectorOpen:true, panelOpen:true};
  let compact = false, compactOpen = {explorer:false, inspector:false, panel:false};
  let area="model";const contextualInspector=new Map();
  const paneOpen=key=>compact?compactOpen[key]:key==="inspector"&&!['model','code'].includes(area)?contextualInspector.get(area)===true:settings[key+"Open"];
  const views = new Map(); let canvas = null, canvasKey = "", baseBox = null, view = null, panHeld = false;
  function persist() {try {sessionStorage.setItem("eija-ui-layout", JSON.stringify(settings));} catch { /* Preferences are optional. */ }}
  function applySettings() {
    const style = document.documentElement.style;
    for (const key of ["explorer", "inspector", "panel"]) style.setProperty(`--${key}-size`, settings[key] + "px");
    for (const key of ["explorer", "inspector", "panel"]) {
      const open=paneOpen(key);
      document.body.classList.toggle(key + "-collapsed", !open);
      get(key === "panel" ? "toggle-bottom" : "toggle-" + key).setAttribute("aria-expanded", String(open));
    }
    document.body.dataset.compactExplorer=String(compact&&compactOpen.explorer);
    document.body.dataset.compactInspector=String(compact&&compactOpen.inspector);
    get("drawer-backdrop").hidden=!(compact&&(compactOpen.explorer||compactOpen.inspector));
    get("explorer-resizer").hidden=compact;get("inspector-resizer").hidden=compact;
    get("explorer-resizer").setAttribute("aria-valuenow", settings.explorer);
    get("inspector-resizer").setAttribute("aria-valuenow", settings.inspector);
    get("panel-resizer").setAttribute("aria-valuenow", settings.panel);
  }
  function toggle(key, open) {
    if(compact){compactOpen[key]=open===undefined?!compactOpen[key]:open;if(key!=="panel"&&compactOpen[key])compactOpen[key==="explorer"?"inspector":"explorer"]=false;}
    else if(key==="inspector"&&!['model','code'].includes(area))contextualInspector.set(area,open===undefined?!paneOpen(key):open);
    else settings[key+"Open"]=open===undefined?!settings[key+"Open"]:open;
    applySettings();if(!compact)persist();
  }
  function setArea(name){area=name;applySettings();}
  function resizeMode(matches) {compact=matches;compactOpen={explorer:false,inspector:false,panel:false};applySettings();}
  function closeDrawers(restoreFocus=false) {
    const key=compactOpen.inspector?"inspector":"explorer";compactOpen.explorer=false;compactOpen.inspector=false;applySettings();
    if(restoreFocus)get("toggle-"+key).focus();
  }
  function bottom(id) {
    toggle("panel", true);
    document.querySelectorAll("[data-bottom]").forEach(button => {const selected = button.dataset.bottom === id; button.setAttribute("aria-selected", String(selected)); button.tabIndex = selected ? 0 : -1;});
    document.querySelectorAll(".bottom-tab").forEach(panel => {panel.hidden = panel.id !== id;});
  }
  function splitter(id, key, minimum, maximum, direction) {
    const handle = get(id);
    const update = value => {settings[key] = clamp(value, minimum, maximum); settings[key + "Open"] = true; applySettings();};
    handle.addEventListener("pointerdown", event => {
      if (event.button !== 0) return;
      event.preventDefault(); const start = key === "panel" ? event.clientY : event.clientX, original = settings[key];
      handle.setPointerCapture(event.pointerId); document.body.classList.add("resizing");
      const move = e => update(original + ((key === "panel" ? e.clientY : e.clientX) - start) * direction);
      const end = e => {handle.removeEventListener("pointermove", move); handle.removeEventListener("pointerup", end); handle.removeEventListener("pointercancel", end); if (handle.hasPointerCapture(e.pointerId)) handle.releasePointerCapture(e.pointerId); document.body.classList.remove("resizing"); persist();};
      handle.addEventListener("pointermove", move); handle.addEventListener("pointerup", end); handle.addEventListener("pointercancel", end);
    });
    handle.addEventListener("keydown", event => {
      const step = ["ArrowRight", "ArrowDown"].includes(event.key) ? 16 * direction : ["ArrowLeft", "ArrowUp"].includes(event.key) ? -16 * direction : 0;
      if (step || ["Home", "End"].includes(event.key)) {event.preventDefault(); update(event.key === "Home" ? minimum : event.key === "End" ? maximum : settings[key] + step); persist();}
    });
    handle.addEventListener("dblclick", () => {update(key === "explorer" ? 230 : key === "inspector" ? 288 : 160); persist();});
  }
  function setView(next) {
    if (!canvas) return;
    view = next; views.set(canvasKey, {...next});
    canvas.setAttribute("viewBox", `${next.x} ${next.y} ${next.width} ${next.height}`);
    get("canvas-zoom").textContent = `${Math.round(next.scale * 100)}%`;
    get("canvas-zoom").title=next.scale<.85?"Overview scale. Choose 100% for readable labels.":"Readable model scale";
  }
  function viewportSize() {const r = get("model-canvas").getBoundingClientRect(); return {width:Math.max(1,r.width),height:Math.max(1,r.height)};}
  function fit() {
    if (!canvas || !baseBox) return;
    const size = viewportSize(), scale = Math.min(size.width / baseBox.width, size.height / baseBox.height);
    const width=size.width/scale,height=size.height/scale;
    setView({x:baseBox.x+(baseBox.width-width)/2,y:baseBox.y+(baseBox.height-height)/2,width,height,scale});
  }
  function zoom(factor) {
    if (!view || !canvas) return;
    const scale = clamp(view.scale * factor, .15, 3), ratio = view.scale / scale;
    const width = view.width * ratio, height = view.height * ratio;
    setView({x:view.x + (view.width-width)/2, y:view.y + (view.height-height)/2, width,height,scale});
  }
  function readable() {
    if(!canvas)return;const size=viewportSize(),x=Number(canvas.dataset.focusX??canvas.dataset.initialX??50),y=Number(canvas.dataset.focusY??canvas.dataset.initialY??75);
    setView(canvas.dataset.direction==="TB"?{x:x+95-size.width/2,y:y-45,width:size.width,height:size.height,scale:1}:{x:x-45,y:y+38-size.height/2,width:size.width,height:size.height,scale:1});
  }
  function mountCanvas(key) {
    const node = get("model-canvas").querySelector("svg"); if (!node) return;
    if (get("model").hidden) return;
    key += ":" + (node.dataset.direction||"LR");
    if (node === canvas && key === canvasKey) return;
    canvas = node; canvasKey = key;
    const nums = node.getAttribute("viewBox").split(/\s+/).map(Number); baseBox = {x:nums[0],y:nums[1],width:nums[2],height:nums[3]};
    const size = viewportSize(), previous = views.get(key);
    // Start at readable text size. Fit is an explicit overview operation for long flows.
    if(previous)setView({...previous,width:size.width/previous.scale,height:size.height/previous.scale});else readable();
    let suppressClick = false;
    node.addEventListener("pointerdown", event => {
      if (!(event.button === 1 || (event.button === 0 && panHeld)) || event.target.closest(".edit-handle")) return;
      event.preventDefault(); event.stopPropagation(); node.setPointerCapture(event.pointerId);
      const start = {x:event.clientX,y:event.clientY}, original = {...view}, rect = node.getBoundingClientRect();
      const move = e => {const dx=e.clientX-start.x,dy=e.clientY-start.y; suppressClick ||= Math.abs(dx)+Math.abs(dy)>4; setView({...original,x:original.x-dx*original.width/rect.width,y:original.y-dy*original.height/rect.height});};
      const finish = e => {node.removeEventListener("pointermove",move);node.removeEventListener("pointerup",finish);node.removeEventListener("pointercancel",finish);if(node.hasPointerCapture(e.pointerId))node.releasePointerCapture(e.pointerId);};
      node.addEventListener("pointermove",move);node.addEventListener("pointerup",finish);node.addEventListener("pointercancel",finish);
    });
    node.addEventListener("click",event=>{if(suppressClick){event.preventDefault();event.stopImmediatePropagation();suppressClick=false;}},true);
  }
  function sourceLines(data) {
    if (typeof data.text !== "string" || !Number.isInteger(data.lines?.start) || data.lines.start < 1) throw new Error("The source response has no valid line range.");
    const lines=data.text.split(/\r?\n/);if(lines.at(-1)==="")lines.pop();
    return lines.map((text,index)=>({number:data.lines.start+index,text}));
  }
  function sourceLoading(ref) {
    get("source-reference").value=ref;get("source-file").textContent=ref;
    get("source-reader").replaceChildren(make("p","Reading the captured source…","reader-message"));get("source-reader").setAttribute("aria-busy","true");get("source-metadata").replaceChildren();
  }
  function sourceError(message,code="SOURCE_UNAVAILABLE") {
    const root=get("source-reader");root.removeAttribute("aria-busy");const box=make("div",undefined,"editor-empty error-empty");box.append(make("h2",code),make("p",message),make("p","Choose another declared binding or inspect the repository connection. No source was executed."));root.replaceChildren(box);get("source-metadata").replaceChildren();
  }
  function renderSource(data) {
    if(data.status!=="connected"){sourceError(data.reason||"No source snapshot is available.",String(data.status||"unknown").toUpperCase());return;}
    const rows=sourceLines(data),root=get("source-reader");root.removeAttribute("aria-busy");root.replaceChildren();
    get("source-file").textContent=`${data.path}${data.symbol ? "  ›  "+data.symbol : ""}`;get("source-reference").value=data.reference;
    const code=make("div",undefined,"source-lines");code.setAttribute("role","region");code.setAttribute("aria-label",`Read-only source ${data.path}, lines ${data.lines.start} to ${data.lines.end}`);code.tabIndex=0;
    for(const line of rows){const row=make("div",undefined,"source-line"),number=make("span",line.number,"line-number"),content=make("code",line.text||" ");number.setAttribute("aria-hidden","true");row.append(number,content);code.append(row);}root.append(code);
    const meta=get("source-metadata");meta.replaceChildren(make("p",`${data.fragment_resolution||"unknown resolution"} · lines ${data.lines.start}–${data.lines.end}${data.truncated ? " · excerpt truncated" : ""} · ${data.scope||"Captured source only"}`));
    const details=make("details"),list=make("dl");details.append(make("summary","Snapshot identity and source range"));
    for(const [label,input] of [["File SHA-256",data.file_hash],["Snippet SHA-256",data.snippet_hash],["Source snapshot",data.source_hash],["Graph snapshot",data.graph_hash],["Symbol range",data.symbol_lines?`${data.symbol_lines.start}–${data.symbol_lines.end}`:"File scope"]])list.append(make("dt",label),make("dd",input||"Not reported"));details.append(list);meta.append(details);
  }
  function renderHistory(current, history, onPreview) {
    const root=get("case-history");root.replaceChildren();get("history-count").textContent=history?.edits?.length||0;
    if(!current){root.append(make("p","Open a change case to inspect its recorded semantic history.","muted"));return;}
    if(!history||history.status==="unavailable"){root.append(make("p",`History unavailable: ${history?.reason||"No response"}. Undo and redo are disabled.`,"muted"));return;}
    root.append(make("p",`Case revision ${history.version} · semantic cursor ${history.cursor}. Historical previews are read only; undo and redo are explicit kernel commands.`,"muted"));
    if(!history.selection){root.append(make("p","Select a meaning before semantic history begins."));return;}
    const records=[{label:`Initial meaning · ${history.selection.label} · protected`,entry:history.selection},...(history.edits||[]).map(entry=>({label:`${entry.index}. ${entry.transaction.kind.replaceAll("_"," ")} · applied`,entry})),...(history.redo||[]).map(entry=>({label:`${entry.index}. ${entry.transaction.kind.replaceAll("_"," ")} · available to redo`,entry}))];
    for(const {label,entry} of records){const row=make("div",undefined,"history-row"),button=make("button","View model","text-button");button.onclick=()=>onPreview(entry.model,label);row.append(make("span",label),button);const detail=make("details",undefined,"history-record");detail.append(make("summary",`Recorded hash ${entry.semantic_hash||"not reported"}`),make("pre",JSON.stringify(entry.transaction||entry.transactions,null,2)));row.append(detail);root.append(row);}
    const audit=make("details",undefined,"history-record");audit.append(make("summary",`Immutable command log · ${(history.events||[]).length} events`));
    for(const event of history.events||[]){const body=event.body||{};audit.append(make("p",`${event.seq}. ${event.kind} · ${body.by||"actor not reported"} · revision ${body.from_version??"?"} → ${body.to_version??"?"} · ${body.time||"time not reported"}`));}audit.append(make("p",history.audit_note||"This is case history, not Git history.","muted"));root.append(audit);
  }
  function renderEvidence(root,packet) {
    root.replaceChildren();const table=make("table",undefined,"panel-evidence-table"),head=make("thead"),header=make("tr"),body=make("tbody");
    for(const label of ["Check","Scope","Result"])header.append(make("th",label));head.append(header);
    for(const evidence of packet?.formal_evidence||[]){const row=make("tr"),scope=make("td",evidence.evidence_level?.replaceAll("_"," ")||"Declared model");scope.title=evidence.establishes||"";row.append(make("td",evidence.kind.replaceAll("_"," ")),scope,make("td",evidence.status));body.append(row);}
    if(!(packet?.formal_evidence||[]).length){const row=make("tr");row.append(make("td","Runtime and formal checks"),make("td",packet?"Current case":"No case selected"),make("td","NOT_RUN"));body.append(row);}
    const human=make("tr");human.append(make("td","Human comprehension"),make("td","Human study"),make("td","UNKNOWN"));body.append(human);table.append(head,body);root.append(table);
  }
  function renderImpact(root,data,openReference) {
    root.replaceChildren();root.append(make("h4","Known dependency ripple"));
    if(data.status!=="connected"||!data.impact){root.append(make("p",data.reason||"No impact result is available.","muted"));return;}
    const impact=data.impact;root.append(make("p",`${impact.count} linked dependants · certificate ${impact.certificate}`),make("p",data.scope||"Declared links only; unknown dependencies are not covered.","muted"));
    const list=make("div",undefined,"impact-list");
    for(const item of impact.affected||[]){const details=make("details"),heading=make("summary",`${item.type} · ${item.id}`);details.append(heading);const button=make("button","Open source reference","text-button");button.onclick=()=>openReference(item.id);details.append(button);const path=make("ol");for(const ref of item.witness||[])path.append(make("li",ref));details.append(path);list.append(details);}root.append(list);
    if(!(impact.affected||[]).length)root.append(make("p","No dependants were returned within this declared mapping."));
  }
  function init(callbacks) {
    try {const stored=JSON.parse(sessionStorage.getItem("eija-ui-layout")||"{}");for(const key of ["explorerOpen","inspectorOpen","panelOpen"])if(typeof stored[key]==="boolean")settings[key]=stored[key];for(const [key,min,max]of [["explorer",180,420],["inspector",240,440],["panel",100,420]])if(Number.isFinite(stored[key]))settings[key]=clamp(stored[key],min,max);}catch{/* Defaults remain usable. */}
    const compactQuery=window.matchMedia("(max-width: 850px)");resizeMode(compactQuery.matches);compactQuery.addEventListener("change",event=>resizeMode(event.matches));
    applySettings();splitter("explorer-resizer","explorer",180,420,1);splitter("inspector-resizer","inspector",240,440,-1);splitter("panel-resizer","panel",100,420,-1);
    get("toggle-explorer").onclick=()=>toggle("explorer");get("toggle-inspector").onclick=()=>toggle("inspector");get("close-inspector").onclick=()=>toggle("inspector",false);get("toggle-bottom").onclick=()=>toggle("panel");get("collapse-bottom").onclick=()=>toggle("panel",false);
    get("close-explorer").onclick=()=>{toggle("explorer",false);get("toggle-explorer").focus();};get("drawer-backdrop").onclick=()=>closeDrawers(true);
    get("explorer").addEventListener("click",event=>{if(compact&&event.target.closest("button:not(#close-explorer)"))closeDrawers();});
    get("start-intent").onclick=callbacks.newIntent;get("source-show-repository").onclick=()=>callbacks.openTab("source");get("open-evidence").onclick=()=>callbacks.openTab("evidence");
    document.querySelectorAll("[data-bottom]").forEach(button=>{button.onclick=()=>bottom(button.dataset.bottom);button.addEventListener("keydown",event=>{const tabs=[...document.querySelectorAll("[data-bottom]")],index=tabs.indexOf(button),next=event.key==="ArrowRight"?tabs[(index+1)%tabs.length]:event.key==="ArrowLeft"?tabs[(index+tabs.length-1)%tabs.length]:null;if(next){event.preventDefault();bottom(next.dataset.bottom);next.focus();}});});
    get("canvas-fit").onclick=fit;get("canvas-readable").onclick=readable;get("canvas-zoom-in").onclick=()=>zoom(1.2);get("canvas-zoom-out").onclick=()=>zoom(1/1.2);
    new ResizeObserver(()=>{if(!canvas||!view||get("model").hidden)return;const size=viewportSize(),width=size.width/view.scale,height=size.height/view.scale;if(Math.abs(view.width-width)+Math.abs(view.height-height)>1)setView({...view,x:view.x+(view.width-width)/2,y:view.y+(view.height-height)/2,width,height});}).observe(get("model-canvas"));
    get("model-canvas").addEventListener("wheel",event=>{event.preventDefault();if(event.ctrlKey||event.metaKey)zoom(event.deltaY<0?1.12:1/1.12);else if(view)setView({...view,x:view.x+(event.deltaX+(event.shiftKey?event.deltaY:0))/view.scale,y:view.y+(event.shiftKey?0:event.deltaY)/view.scale});},{passive:false});
    get("model-canvas").addEventListener("keydown",event=>{if(event.code==="Space"){panHeld=true;get("model-canvas").classList.add("pan-ready");if(event.target===get("model-canvas"))event.preventDefault();}if(["+","=","-","0"].includes(event.key)){event.preventDefault();if(event.key==="0")fit();else zoom(event.key==="-"?1/1.2:1.2);}});
    document.addEventListener("keyup",event=>{if(event.code==="Space"){panHeld=false;get("model-canvas").classList.remove("pan-ready");}});
    window.addEventListener("blur",()=>{panHeld=false;get("model-canvas").classList.remove("pan-ready");});
    document.addEventListener("keydown",event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="b"){event.preventDefault();toggle("explorer");}if(event.key==="Escape"){panHeld=false;get("model-canvas").classList.remove("pan-ready");if(compact&&(compactOpen.explorer||compactOpen.inspector))closeDrawers(true);}});
    document.querySelector(".editor-navigation").addEventListener("focusin",()=>{if(compact)closeDrawers();});
  }
  return {init,toggle,bottom,mountCanvas,fit,zoom,readable,sourceLines,sourceLoading,sourceError,renderSource,renderHistory,renderEvidence,renderImpact,resizeMode,setArea};
})();
if(typeof module!=="undefined")module.exports=EijaShell;
