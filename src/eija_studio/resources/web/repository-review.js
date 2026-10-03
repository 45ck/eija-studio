"use strict";
// Presentation of immutable Git observations. No fetch, diff generation or source execution.
const EijaRepositoryReview = (() => {
  const views = ["diff", "before", "after", "syntax", "impact"];
  const labels = {diff:"Git diff", before:"Before source", after:"After source", syntax:"Syntax", impact:"Known impact"};
  const fileStatuses = {added:"+ Added", deleted:"− Deleted", modified:"◇ Modified"};
  const symbolStatuses = {added:"+ Added", removed:"− Removed", changed:"◇ Changed", unchanged:"= Unchanged", ambiguous:"? Ambiguous"};
  const objectId = value => typeof value === "string" && /^(?:[0-9a-f]{40}|[0-9a-f]{64})$/.test(value);
  let serial=0;const mountIds=new WeakMap();
  const text = value => value === undefined || value === null ? "Not reported" : typeof value === "object" ? JSON.stringify(value) : String(value);
  const short = value => typeof value === "string" ? value.slice(0, 12) : "Not reported";
  const copy = value => value && JSON.parse(JSON.stringify(value));
  function make(tag, value, cls) {const node=document.createElement(tag);if(value!==undefined)node.textContent=text(value);if(cls)node.className=cls;return node;}
  function button(label, run, action) {const node=make("button",label);node.type="button";node.onclick=run;if(action)node.dataset.repositoryAction=action;return node;}
  function disclosure(parent, title, content) {const node=make("details");node.append(make("summary",title));content(node);parent.append(node);return node;}
  function record(parent, entries) {const list=make("dl",undefined,"repository-identities");for(const [label,value]of entries)list.append(make("dt",label),make("dd",text(value)));parent.append(list);return list;}
  function message(parent, title, detail, status="status") {const box=make("section",undefined,"repository-message");box.setAttribute("role",status);box.append(make("h3",title),make("p",detail));parent.append(box);return box;}
  function identity(side) {return side&&objectId(side.commit)&&objectId(side.tree)&&typeof side.changed_source_hash==="string"&&side.changed_source_hash.length>0;}
  function sameSide(a,b) {return ["commit","tree","changed_source_hash"].every(key=>a?.[key]===b?.[key]&&typeof a?.[key]==="string");}
  function sameBlob(record,selected,reference) {
    if(record===null)return selected===null;
    if(!record||!selected||record.blob!==selected.blob)return false;
    if(selected.status==="captured")return record.status==="captured"&&["file_sha256","mode","byte_length"].every(key=>record[key]===selected[key]);
    if(selected.status==="unavailable")return record.status==="unavailable";
    return reference!=null&&selected.reference===reference&&record.status==="captured"&&["not_present","ambiguous"].includes(selected.status);
  }
  function sameSymbol(row,selected,side,reference) {
    if(!selected||selected.status==="unavailable")return true;
    if(reference==null)return !selected.symbol;
    const facts=(row.extraction?.[side]?.symbols||[]).filter(fact=>fact.reference===reference);
    if(selected.status==="not_present")return facts.length===0;
    if(selected.status==="ambiguous")return facts.length>1;
    const fact=row.symbols.find(item=>item.reference===reference)?.[side];
    return facts.length===1&&fact&&["reference","kind","syntax_digest","start_line","end_line"].every(key=>selected.symbol?.[key]===fact[key]&&facts[0][key]===fact[key]);
  }
  function selectionFor(comparison,path,reference=null) {return {comparison_id:comparison.comparison_id,base_commit:comparison.base.commit,head_commit:comparison.head.commit,path,reference};}
  function selectionMatches(comparison,selection) {return selection?.comparison_id===comparison.comparison_id&&selection.base_commit===comparison.base.commit&&selection.head_commit===comparison.head.commit;}
  function inspect(comparison,file,selection) {
    if(!comparison)return {status:"empty"};
    if(!["available","partial"].includes(comparison.status))return {status:comparison.status||"unavailable",reason:comparison.reason};
    if(comparison.schema!=="eija.repository.change.v1"||comparison.read_only!==true||!identity(comparison.base)||!identity(comparison.head)||!comparison.comparison_id||!Array.isArray(comparison.files))return {status:"invalid",reason:"The comparison response has no complete immutable read-only subject."};
    if(!selection)return {status:"select_file",comparison};
    if(!selectionMatches(comparison,selection))return {status:"mismatch",comparison,reason:"The selection belongs to another comparison or commit pair."};
    const row=comparison.files.find(value=>value.path===selection.path);
    if(!row||selection.reference!=null&&!(row.symbols||[]).some(symbol=>symbol.reference===selection.reference))return {status:"mismatch",comparison,reason:"The selected file or syntax reference is not in this comparison inventory."};
    if(!file)return {status:"select_file",comparison,row,selection};
    if(!["available","partial"].includes(file.status))return {status:"file_unavailable",comparison,row,selection,reason:file.reason||"This historical file response is unavailable."};
    const matches=file.schema==="eija.repository.change-file.v1"&&file.read_only===true&&file.comparison_id===comparison.comparison_id&&sameSide(file.base,comparison.base)&&sameSide(file.head,comparison.head)&&file.path===selection.path&&(file.selected_reference??null)===(selection.reference??null)&&["before","after"].every(side=>sameBlob(row[side],file[side],selection.reference)&&sameSymbol(row,file[side],side,selection.reference));
    if(!matches)return {status:"mismatch",comparison,row,selection,reason:"The file response does not match the selected comparison, commits, trees, captured digests, path and reference. Reload this comparison."};
    return {status:"ready",comparison,row,selection,file};
  }
  function coverage(comparison) {
    const data=comparison.coverage||{},reasons=Object.entries(data.excluded_by_reason||{}),validCount=value=>Number.isInteger(value)&&value>=0;
    const excluded=reasons.reduce((sum,[,count])=>sum+(validCount(count)?count:0),0),displayed=comparison.files.length;
    return {total:data.changed_paths_total,displayed,reported:data.displayed_paths,excluded,reasons,
      reconciles:data.inventory_reconciles===true&&validCount(data.changed_paths_total)&&data.displayed_paths===displayed&&reasons.every(([,count])=>validCount(count))&&data.changed_paths_total===displayed+excluded};
  }
  function diffRows(value) {
    return (value.match(/[^\n]*\n|[^\n]+$/g)||[]).map(line=>({text:line,kind:/^(?:diff |index |--- |\+\+\+ |@@|\\)/.test(line)?"header":line[0]==="+"?"added":line[0]==="-"?"removed":"context"}));
  }
  function scope(parent) {parent.append(make("p","Behavior · NOT_RUN · changed-source scope only; known impact is incomplete.","repository-scope"));}
  function renderHeader(s) {
    const c=s.info.comparison,header=make("header",undefined,"repository-review-header");
    header.append(make("h2","Repository changes"),make("span",`${c.status.toUpperCase()} · read-only`,"repository-status"));
    const pair=make("div",undefined,"repository-revision-pair");
    for(const [side,title]of [["base","Before"],["head","After"]]){const caption=make("p");caption.dataset.repositoryRevision=side;caption.setAttribute("aria-label",`${title} immutable commit ${c[side].commit}`);caption.append(make("strong",title),make("code",short(c[side].commit)));pair.append(caption);}
    header.append(pair);s.shell.append(header);scope(s.shell);s.metadata=make("div",undefined,"repository-metadata");s.shell.append(s.metadata);
    const identityDetails=disclosure(s.metadata,"Immutable comparison identity and capture policy",node=>{
      record(node,[["Comparison ID",c.comparison_id],["Pack",c.pack?.id],["Pack digest",c.pack?.digest],["Git",c.tools?.git_version],["Python",c.tools?.python_version]]);
      for(const [side,title]of [["base","Before"],["head","After"]])record(node,[[`${title} commit`,c[side].commit],[`${title} tree`,c[side].tree],[`${title} changed-files-only digest`,c[side].changed_source_hash]]);
      node.append(make("p","These changed-files-only digests are not the whole live repository source hash. The working tree is not compared or executed. Syntactic changes and partial known impact do not establish behavioral correctness; model receipts do not cover this code comparison."));
      record(node,Object.entries(c.capture_policy||{}));record(node,Object.entries(c.scope||{}));
    });identityDetails.className="repository-identity-disclosure";
  }
  function renderCoverage(s) {
    const c=s.info.comparison,counts=coverage(c),bar=make("div",undefined,"repository-coverage");
    bar.append(make("p",`${text(counts.total)} changed paths · ${counts.displayed} displayed · ${counts.excluded} excluded`));
    if(!counts.reconciles)message(bar,"Inventory does not reconcile","Reported totals or displayed records are inconsistent. Completeness is unknown.","alert");
    if(counts.excluded||c.gaps?.length||!counts.reconciles)disclosure(bar,`Capture exclusions and gaps (${counts.excluded} excluded; ${c.gaps?.length||0} gaps)`,node=>{
      record(node,counts.reasons);for(const gap of c.gaps||[])node.append(make("p",`${gap.path?gap.path+" · ":""}${gap.reason||"Gap"} · ${gap.message||"No detail returned"}`));
    });
    s.metadata.append(bar);
  }
  function renderNavigator(s) {
    const nav=make("nav",undefined,"repository-file-navigator");nav.setAttribute("aria-label","Changed repository files");nav.tabIndex=0;
    nav.append(make("h3",`Changed files (${s.info.comparison.files.length})`));
    const buttons=[];
    for(const row of s.info.comparison.files){const ref=selectionFor(s.info.comparison,row.path),node=button("",()=>s.options.onSelectFile?.(copy(ref))),parts=row.path.split("/"),name=parts.pop(),status=fileStatuses[row.status]||row.status;
      node.append(make("span",name,"repository-filename"),make("small",parts.join("/")||"Repository root","repository-parent-path"));node.title=`${status} · ${row.path}`;node.setAttribute("aria-label",node.title);node.dataset.fileStatus=row.status;
      node.id=`${s.prefix}-file-${encodeURIComponent(row.path)}`;node.dataset.repositoryPath=row.path;node.setAttribute("aria-pressed",String(row.path===s.info.row?.path));node.disabled=!s.options.onSelectFile;buttons.push(node);nav.append(node);}
    nav.addEventListener("keydown",event=>{if(!["ArrowDown","ArrowUp","Home","End"].includes(event.key))return;const index=buttons.indexOf(event.target);if(index<0)return;event.preventDefault();const next=event.key==="Home"?0:event.key==="End"?buttons.length-1:(index+(event.key==="ArrowDown"?1:-1)+buttons.length)%buttons.length;buttons[next].focus();});
    if(s.options.navigatorRoot){nav.classList.add("external");s.options.navigatorRoot.append(nav);}else s.body.append(nav);
    s.navigator=nav;
  }
  function referenceLabel(reference) {
    const index=reference.indexOf("#"),fragment=index<0?reference:reference.slice(index+1);let label=fragment;
    try{label=decodeURIComponent(fragment);}catch{/* Malformed display escapes retain their literal identity. */}
    return label.replace(/^js\/[^/]+\//,"")||reference;
  }
  function orderedReferences(symbols,filter) {const changed=symbols.filter(item=>item.status!=="unchanged");return filter==="all"?[...changed,...symbols.filter(item=>item.status==="unchanged")]:changed;}
  function chooseReference(s,reference) {
    s.symbolDisclosure.open=false;s.symbolSummary.focus();
    const selected=selectionFor(s.info.comparison,s.info.row.path,reference);
    if(reference===null)s.options.onSelectFile?.(selected);else s.options.onSelectSymbol?.(selected);
  }
  function renderReferenceChoices(s) {
    const symbols=s.info.row.symbols||[];s.symbolChoices.replaceChildren();
    for(const symbol of orderedReferences(symbols,s.symbolsFilter)){
      const label=referenceLabel(symbol.reference),collision=symbols.some(other=>other.reference!==symbol.reference&&other.kind===symbol.kind&&referenceLabel(other.reference)===label);
      const node=button("",()=>chooseReference(s,symbol.reference));node.append(make("span",`${symbolStatuses[symbol.status]||symbol.status} · ${collision?symbol.reference:label}`),make("small",symbol.kind,"repository-symbol-kind"));
      node.title=symbol.reference;node.setAttribute("aria-label",`${symbolStatuses[symbol.status]||symbol.status} · ${symbol.kind} · ${symbol.reference}`);node.id=`${s.prefix}-symbol-${encodeURIComponent(symbol.reference)}`;node.dataset.repositoryReference=symbol.reference;node.disabled=!s.options.onSelectSymbol;node.setAttribute("aria-pressed",String(symbol.reference===s.info.selection?.reference));s.symbolChoices.append(node);
    }
    if(!s.symbolChoices.children.length)s.symbolChoices.append(make("p","No changed or unresolved references reported. Choose All references to inspect the extracted inventory.","repository-muted"));
  }
  function renderReferenceChooser(s,header) {
    const row=s.info.row,symbols=row.symbols||[],changed=symbols.filter(item=>item.status!=="unchanged").length;
    s.symbolDisclosure=disclosure(header,`${symbols.length} extracted syntax references`,node=>{
      const controls=make("div",undefined,"repository-symbol-controls"),label=make("label","Show references"),select=make("select");select.id=`${s.prefix}-symbols-filter`;select.dataset.repositorySymbolFilter="";label.htmlFor=select.id;
      for(const [value,caption]of [["changed",`Changed / unresolved (${changed})`],["all",`All references (${symbols.length})`]]){const option=make("option",caption);option.value=value;select.append(option);}select.value=s.symbolsFilter;select.onchange=()=>{s.symbolsFilter=select.value;renderReferenceChoices(s);};
      const whole=button("Whole file",()=>chooseReference(s,null));whole.id=`${s.prefix}-whole-file`;whole.disabled=!s.options.onSelectFile;whole.setAttribute("aria-pressed",String(!s.info.selection?.reference));controls.append(label,select,whole);
      s.symbolChoices=make("div",undefined,"repository-symbols");s.symbolChoices.setAttribute("role","group");s.symbolChoices.setAttribute("aria-label","Extracted syntax references in selected file");node.append(controls,s.symbolChoices);
    });s.symbolDisclosure.className="repository-reference-chooser";s.symbolSummary=s.symbolDisclosure.children[0];s.symbolSummary.id=`${s.prefix}-symbols-summary`;s.symbolDisclosure.open=!!s.options.symbolsOpen;renderReferenceChoices(s);
  }
  function renderFileHeader(s) {
    const row=s.info.row,header=make("header",undefined,"repository-file-header"),title=make("div",undefined,"repository-file-title"),context=make("div",undefined,"repository-file-context");title.append(make("h3",row.path),make("span",fileStatuses[row.status]||row.status));header.append(title,context);
    if(s.info.selection?.reference){const ref=s.info.selection.reference,symbol=row.symbols.find(item=>item.reference===ref),selected=disclosure(context,`Selected · ${referenceLabel(ref)} · ${symbolStatuses[symbol?.status]||symbol?.status||"Status not reported"}`,node=>node.append(make("code",ref)));selected.className="repository-selected-reference";selected.dataset.repositorySelectedReference=ref;selected.title=ref;selected.children[0].setAttribute("aria-label",`Selected reference identity · ${ref}`);}
    if((row.symbols||[]).length)renderReferenceChooser(s,context);
    else context.append(make("p","No extracted syntax references reported. The file diff remains available when captured.","repository-muted"));
    const extraction=row.extraction||{};context.append(make("p",`Syntax before: ${extraction.before?.status||"Not reported"} · after: ${extraction.after?.status||"Not reported"}. Extracted facts only.`,"repository-extraction"));s.content.append(header);
  }
  function renderTabs(s) {
    const tabs=make("div",undefined,"repository-view-tabs");tabs.setAttribute("role","tablist");tabs.setAttribute("aria-label","Historical file views");s.tabs=[];
    for(const value of views){const node=button(labels[value],()=>showView(s,value));node.id=`${s.prefix}-${value}`;node.dataset.repositoryView=value;node.setAttribute("role","tab");node.setAttribute("aria-controls",`${s.prefix}-panel`);s.tabs.push(node);tabs.append(node);}
    tabs.addEventListener("keydown",event=>{const index=s.tabs.indexOf(event.target);if(index<0)return;const next=event.key==="ArrowRight"?(index+1)%views.length:event.key==="ArrowLeft"?(index+views.length-1)%views.length:event.key==="Home"?0:event.key==="End"?views.length-1:-1;if(next<0)return;event.preventDefault();showView(s,views[next]);s.tabs[next].focus();});
    s.panel=make("section",undefined,"repository-file-view");s.panel.id=`${s.prefix}-panel`;s.panel.tabIndex=0;s.panel.setAttribute("role","tabpanel");s.content.append(tabs,s.panel);showView(s,s.view,false);
  }
  function showView(s,value,notify=true) {
    if(s.stopped||!views.includes(value))return;s.view=value;
    for(const node of s.tabs){const selected=node.dataset.repositoryView===value;node.setAttribute("aria-selected",String(selected));node.tabIndex=selected?0:-1;}
    s.panel.replaceChildren();s.panel.dataset.repositoryVisibleView=value;s.panel.setAttribute("aria-labelledby",`${s.prefix}-${value}`);
    if(value==="diff")renderDiff(s);else if(value==="syntax")renderSyntax(s);else if(value==="impact")renderImpact(s);else renderSide(s,value);
    if(notify)s.options.onViewChange?.(value,copy(s.info.selection));
  }
  function renderDiff(s) {
    const diff=s.info.file.unified_diff||{};s.panel.append(make("p","Git-generated unified diff · file-wide, including when a syntax reference is selected.","repository-muted"));
    if(diff.status!=="AVAILABLE"){message(s.panel,`Diff · ${diff.status||"NOT_RUN"}`,diff.reason||"Git diff was not returned.");return;}
    if(diff.truncated)s.panel.append(make("p","Partial diff: the server reports truncation.","repository-warning"));
    if(typeof diff.text!=="string"){message(s.panel,"Diff unavailable","The response has no textual diff.","alert");return;}
    if(!diff.text){message(s.panel,"No textual hunks","Git returned no textual hunks for this changed path. Consult the file metadata for non-textual changes.");return;}
    const pre=make("pre",undefined,"repository-unified-diff");pre.tabIndex=0;pre.setAttribute("role","region");pre.setAttribute("aria-label",`Git unified diff for ${s.info.row.path}`);pre.dataset.repositoryDiff="git";
    if(diff.text.split("\n",4097).length>4096)pre.textContent=diff.text;else for(const row of diffRows(diff.text)){const line=make("span",row.text,`repository-diff-line ${row.kind}`);line.dataset.diffKind=row.kind;pre.append(line);}s.panel.append(pre);
  }
  function validSource(side) {return side?.status==="captured"&&typeof side.text==="string"&&Number.isInteger(side.range?.start)&&side.range.start>0&&Number.isInteger(side.range?.end)&&side.range.end>=side.range.start&&side.range.end-side.range.start<200&&typeof side.file_sha256==="string"&&typeof side.snippet_sha256==="string"&&objectId(side.blob);}
  function historicalSide(file,side,selection) {const data=file[side],subject=side==="before"?file.base:file.head;return {...copy(data),selection:copy(selection),side,commit:subject.commit,tree:subject.tree,changed_source_hash:subject.changed_source_hash,read_only:true};}
  function renderSide(s,side) {
    const data=s.info.file[side],title=side==="before"?"Before":"After",commit=s.info.comparison[side==="before"?"base":"head"].commit;
    const caption=make("div",undefined,"repository-source-caption");s.panel.dataset.repositorySide=side;caption.append(make("h4",`${title} · immutable commit ${short(commit)}`));s.panel.append(caption);
    if(!data){message(s.panel,"Not present",`This file is not present in the ${title.toLowerCase()} commit.`);return;}
    if(data.status!=="captured"){message(s.panel,data.status==="not_present"?"No extracted match":data.status==="ambiguous"?"Ambiguous syntax reference":"Source unavailable",data.status==="not_present"?`No matching reference was extracted on this side (${s.info.row.extraction?.[side]?.status||"status not reported"}). This is not proof of absence outside the extractor's scope.`:data.status==="ambiguous"?"Multiple extracted definitions have this reference. No definition was chosen.":"This side was not captured as permitted text.");return;}
    if(!validSource(data)){message(s.panel,"Source response invalid","Exact text, range and historical identities are required; no live-source fallback is available.","alert");return;}
    caption.append(make("p",`Lines ${data.range.start}–${data.range.end}${data.truncated?" · excerpt truncated":""} · read-only historical source`,data.truncated?"repository-warning":"repository-muted"));
    if(s.options.onOpenSide)s.panel.append(button(`Open ${title.toLowerCase()} in source reader`,()=>s.options.onOpenSide(historicalSide(s.info.file,side,s.info.selection)),`open-${side}`));
    const sourceRegion=make("div",undefined,"repository-code");sourceRegion.tabIndex=0;sourceRegion.setAttribute("role","region");sourceRegion.setAttribute("aria-label",`${title} historical source, ${s.info.row.path}, lines ${data.range.start} to ${data.range.end}`);
    const gutter=make("pre",Array.from({length:data.range.end-data.range.start+1},(_,i)=>data.range.start+i).join("\n"),"repository-line-numbers");gutter.setAttribute("aria-hidden","true");
    const code=make("pre",data.text,"repository-code-text");code.dataset.repositorySource=side;sourceRegion.append(gutter,code);s.panel.append(sourceRegion);
    disclosure(s.panel,`${title} blob and excerpt identities`,node=>record(node,[["Commit",commit],["Git blob",data.blob],["File SHA-256",data.file_sha256],["Snippet SHA-256",data.snippet_sha256],["Symbol",data.symbol?.reference],["Symbol lines",data.symbol?`${data.symbol.start_line}–${data.symbol.end_line}`:"File scope"]]));
  }
  function renderSyntax(s) {
    s.panel.append(make("h3","Syntactic observations"),make("p","Added, removed or changed syntax does not establish a behavioral change, equivalence or reachability. Partial extraction can make definitions appear added or removed; no rename identity is inferred."));
    for(const [side,title]of [["before","Before"],["after","After"]]){
      const facts=s.info.row.extraction?.[side]||{},section=make("section",undefined,"repository-syntax-side");section.append(make("h4",`${title} extraction · ${facts.status||"Not reported"}`));
      record(section,[["Method",facts.method],["Parser",facts.parser_version],["Grammar",facts.grammar_version]]);for(const gap of facts.gaps||[])section.append(make("p",`${gap.reason||"Gap"} · ${gap.message||"No detail returned"}`,"repository-warning"));s.panel.append(section);
    }
    const symbols=(s.info.row.symbols||[]).filter(item=>!s.info.selection.reference||item.reference===s.info.selection.reference);
    for(const symbol of symbols)disclosure(s.panel,`${symbolStatuses[symbol.status]||symbol.status} · ${symbol.reference}`,node=>{
      record(node,[["Kind",symbol.kind],["Status",symbol.status]]);for(const [side,title]of [["before","Before"],["after","After"]])record(node,[[`${title} syntax digest`,symbol[side]?.syntax_digest],[`${title} lines`,symbol[side]?`${symbol[side].start_line}–${symbol[side].end_line}`:`No unique extracted match · ${s.info.row.extraction?.[side]?.status||"extraction not reported"}`]]);
    });
    if(!symbols.length)s.panel.append(make("p","No extracted syntax records for this selection. File-level differences do not supply missing syntax analysis."));
  }
  function renderImpact(s) {
    s.panel.append(make("h3","Partial known impact"),make("p","Changed-file syntax and the configured pack only. Unmodified files and runtime dependencies are omitted. This is not a complete impact set."));
    for(const [side,title]of [["before","Before"],["after","After"]]){
      const data=s.info.file.known_impact?.[side]||{},section=make("section",undefined,"repository-impact-side");section.append(make("h4",`${title} · ${data.status||"NOT_RUN"}`),make("p",data.reason||data.scope||"No known-impact result returned."));
      record(section,[["Uncaptured inventory count",data.uncaptured_inventory_count],["Captured changed-source digest",data.captured_source_hash],["Graph hash",data.graph_hash],["Reported target",data.impact?.target],["Reported affected count",data.impact?.count]]);
      if(data.complete===true)section.append(make("p","Unexpected completeness flag: this interface admits only partial changed-file scope.","repository-warning"));
      for(const item of data.impact?.affected||[])disclosure(section,`${item.type||"Reference"} · ${item.id}`,node=>{node.append(make("p",`Rank: ${text(item.rank)}`));const chain=make("ol");for(const ref of item.witness||[])chain.append(make("li",ref));node.append(chain);});
      for(const gap of data.gaps||[])section.append(make("p",text(gap),"repository-warning"));s.panel.append(section);
    }
  }
  function render(root,options={}) {
    root.replaceChildren();const info=inspect(options.comparison,options.file,options.selection),shell=make("section",undefined,"repository-review");root.append(shell);
    if(!mountIds.has(root))mountIds.set(root,`repository-review-${++serial}`);
    const s={info,options,shell,view:views.includes(options.view)?options.view:"diff",symbolsFilter:options.symbolsFilter==="all"?"all":"changed",stopped:false,prefix:mountIds.get(root)};
    const controller={destroy(){s.stopped=true;s.navigator?.remove();},getState(){return {selection:copy(info.selection)||null,view:s.view,symbolsOpen:!!s.symbolDisclosure?.open,symbolsFilter:s.symbolsFilter};},openSide(side){if(s.stopped||info.status!=="ready"||!["before","after"].includes(side))return false;showView(s,side);return true;}};
    shell.dataset.repositoryStatus=info.status;shell.setAttribute("aria-label","Immutable repository change review");
    if(options.loading){shell.setAttribute("aria-busy","true");message(shell,info.comparison?"Retained comparison while loading":"Loading repository comparison",info.comparison?"The displayed immutable pair is retained until the new request succeeds. It is not the pending result.":"Waiting for a pinned local commit pair.");}
    if(options.error){const error=message(shell,`${options.error.code||"REQUEST_FAILED"}`,options.error.message||"The request failed. The last returned comparison may be retained.","alert");if(options.error.details)disclosure(error,"Exact error details",node=>record(node,Object.entries(options.error.details)));}
    if(!info.comparison){if(!options.loading)message(shell,info.status==="unconfigured"?"Repository comparison is not configured":info.status==="empty"?"Choose two immutable revisions":"Repository comparison unavailable",info.reason||"No immutable commit comparison has been returned.");scope(shell);return controller;}
    shell.dataset.comparisonId=info.comparison.comparison_id;shell.dataset.baseCommit=info.comparison.base.commit;shell.dataset.headCommit=info.comparison.head.commit;
    renderHeader(s);renderCoverage(s);s.body=make("div",undefined,"repository-review-body");if(options.navigatorRoot)s.body.classList.add("external-navigator");shell.append(s.body);renderNavigator(s);
    s.content=make("section",undefined,"repository-selected-file");s.body.append(s.content);
    if(info.row)renderFileHeader(s);
    if(info.status==="ready")renderTabs(s);
    else if(info.status==="mismatch")message(s.content,"Historical response does not match selection",info.reason,"alert");
    else if(info.status==="file_unavailable")message(s.content,"Historical file unavailable",info.reason);
    else if(!info.comparison.files.length){const counts=coverage(info.comparison);message(s.content,counts.reconciles&&counts.total===0?"No changed paths between these commits":"No changed files available within capture scope",counts.total===0?"An empty byte comparison does not establish behavioral equivalence.":"Inspect the excluded counts and capture gaps; this is not a claim of no changes.");}
    else message(s.content,options.loading==="file"?"Loading selected historical file":"Select a changed file","Choose a file or extracted reference to inspect its exact Git diff and immutable before/after source.");
    return controller;
  }
  return {render,inspect,selectionFor,coverage,diffRows,validSource,referenceLabel,orderedReferences};
})();
if(typeof module!=="undefined")module.exports=EijaRepositoryReview;
