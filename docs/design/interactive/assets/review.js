"use strict";
// Read-only comparison of server snapshots. No policy verdict or transaction is inferred here.
const EijaReview = (() => {
  const make = (tag, text, cls) => {const n = document.createElement(tag); if (text !== undefined) n.textContent = String(text); if (cls) n.className = cls; return n;};
  const fields = [["action","Action"],["role","Role"],["from_state","Source state"],["to_state","Target state"],["guards","Guards"],["required_effects","Required effects"],["forbidden_effects","Forbidden effects"]];
  const normal = value => JSON.stringify(Array.isArray(value) ? [...value].sort() : value);
  const label = value => Array.isArray(value) ? value.join(", ") || "None declared" : value ?? "Not present";
  function compare(before, after) {
    const previous=new Map((before.transitions||[]).map(t=>[t.id,t])),next=new Map((after.transitions||[]).map(t=>[t.id,t]));
    const transitions=[...new Set([...previous.keys(),...next.keys()])].sort().map(id=>{
      const old=previous.get(id),value=next.get(id),changes=fields.filter(([key])=>normal(old?.[key])!==normal(value?.[key]));
      return {id,before:old,after:value,status:!old?"added":!value?"removed":changes.length?"changed":"unchanged",changes};
    });
    return {transitions,addedStates:(after.states||[]).filter(id=>!before.states.includes(id)),removedStates:(before.states||[]).filter(id=>!after.states.includes(id)),initialChanged:before.initial_state!==after.initial_state};
  }
  function flow(transition, title, tone) {
    const box=make("div",undefined,"diff-side "+tone);box.append(make("h4",title));
    if(!transition){box.append(make("p","Not present","muted"));return box;}
    const journey=make("div",undefined,"diff-flow");journey.append(make("span",transition.from_state,"diff-state"),make("span","→","diff-arrow"),make("span",transition.to_state,"diff-state"));
    box.append(journey,make("p",`${transition.role} · ${transition.action}`,"diff-role"));return box;
  }
  function render(root,current,callbacks={}) {
    root.replaceChildren();
    if(!current){root.append(make("div","Open a change case to compare its baseline and candidate.","editor-empty"));return;}
    const c=current.case,packet=current.packet,header=make("section",undefined,"change-summary");
    header.append(make("p","SEMANTIC CHANGES","eyebrow"),make("h2",c.request),make("p",c.selected_meaning?`Selected meaning: ${c.selected_meaning} · case revision ${c.version}`:"No meaning selected. The request has not changed the model.","muted"));root.append(header);
    if(!c.candidate){root.append(make("p","Choose an interpretation in Intent to see its exact consequences."));return;}
    const diff=compare(c.baseline,c.candidate),changed=diff.transitions.filter(x=>x.status!=="unchanged"),summary=make("div",undefined,"diff-summary");
    summary.append(make("span",`${changed.length} changed transitions`),make("span",`${diff.addedStates.length} added states`),make("span",`${diff.removedStates.length} removed states`));header.append(summary);
    if(diff.initialChanged)header.append(make("p",`Initial state: ${c.baseline.initial_state} → ${c.candidate.initial_state}`));
    for(const [title,states,tone]of [["Added",diff.addedStates,"added"],["Removed",diff.removedStates,"removed"]])for(const state of states)header.append(make("span",`${title} state · ${state}`,"state-change "+tone));
    if(!changed.length&&!diff.initialChanged&&!diff.addedStates.length&&!diff.removedStates.length)root.append(make("p","The candidate has no semantic difference from this case's original baseline."));
    const changedRefs=new Set([...diff.addedStates,...diff.removedStates].map(id=>"state:"+id));
    for(const change of changed){changedRefs.add("transition:"+change.id);const article=make("article",undefined,"transition-diff "+change.status);article.dataset.eijaId=`review.transition.${change.id}`;
      const heading=make("div",undefined,"section-heading"),title=make("h3",(change.after||change.before).action),tag=make("span",change.status.toUpperCase(),"diff-tag "+change.status);heading.append(title,tag);article.append(heading,make("p",change.id,"muted"));
      const sides=make("div",undefined,"diff-pair");sides.append(flow(change.before,"BEFORE · BASELINE","before"),flow(change.after,"AFTER · CANDIDATE","after"));article.append(sides);
      const table=make("table",undefined,"diff-table"),thead=make("thead"),headrow=make("tr"),body=make("tbody");for(const text of ["Changed field","Before","After"])headrow.append(make("th",text));thead.append(headrow);
      for(const[key,title]of change.changes){const row=make("tr");row.append(make("th",title),make("td",label(change.before?.[key])),make("td",label(change.after?.[key])));body.append(row);}table.append(thead,body);article.append(table);
      if(change.after&&callbacks.inspectTransition){const inspect=make("button","Inspect in model","secondary");inspect.onclick=()=>callbacks.inspectTransition(change.id);article.append(inspect);}root.append(article);
    }
    const context=make("section",undefined,"review-context"),ripple=make("article",undefined,"review-chapter");ripple.append(make("h3","Trace the affected meaning"),make("p",packet.impact?.complete?"Dependency closure is complete within the declared mapping. Unknown dependencies are outside this scope.":"Dependency closure is unavailable or incomplete.","muted"));
    const refs=new Set(packet.impact?.affected||[]);for(const term of callbacks.terms||[])if((term.refs||[]).some(ref=>changedRefs.has(ref)))for(const ref of term.binds||[])refs.add(ref);
    for(const ref of refs){const button=make("button",ref,"text-button affected-reference");button.onclick=()=>callbacks.openReference?.(ref);ripple.append(button);}if(!refs.size)ripple.append(make("p","No mapped affected references were reported."));context.append(ripple);
    const evidence=make("article",undefined,"review-chapter");evidence.append(make("h3","Evidence for this revision"),make("p",packet.eligible?"Technically eligible in its declared scope":"Technical review is blocked"));
    for(const entry of packet.formal_evidence||[])evidence.append(make("p",`${entry.kind.replaceAll("_"," ")} · ${entry.status}`,"evidence-line"));
    if(!(packet.formal_evidence||[]).length)evidence.append(make("p","Checks: NOT_RUN"));for(const code of packet.blockers||[])evidence.append(make("p",code,"diagnostic"));evidence.append(make("p","Human comprehension: UNKNOWN. Synthetic checks do not demonstrate reviewer benefit.","muted"));
    const open=make("button","Open evidence and decision","secondary");open.onclick=()=>callbacks.openEvidence?.();evidence.append(open);context.append(evidence);root.append(context);
    const unchanged=make("details",undefined,"unchanged-transitions");unchanged.append(make("summary",`${diff.transitions.length-changed.length} unchanged transitions`));for(const item of diff.transitions.filter(x=>x.status==="unchanged"))unchanged.append(make("p",`${item.id} · ${item.after.from_state} → ${item.after.to_state} · ${item.after.role}`));root.append(unchanged);
    const raw=make("details");raw.append(make("summary",`${c.transactions.length} typed transactions retained by the server`));for(const tx of c.transactions)raw.append(make("pre",JSON.stringify(tx,null,2)));root.append(raw);
  }
  return {render,compare};
})();
if(typeof module!=="undefined")module.exports=EijaReview;
