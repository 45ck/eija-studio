"use strict";
// Present the repository adapter's observed snapshot. No source evaluation or semantic inference.
const EijaSource = (() => {
  const make = (tag, text, cls) => {const n = document.createElement(tag); if (text !== undefined) n.textContent = String(text); if (cls) n.className = cls; return n;};
  const value = input => input === undefined || input === null ? "Not reported" : typeof input === "object" ? JSON.stringify(input) : String(input);
  function state(connection) {
    if (!connection) return {status:"unconfigured", title:"Repository not configured", connected:false, reason:"Start EIJA with --repo PATH to inspect a local checkout. The Model tab still shows the declared domain pack."};
    if (connection.status === "connected") return {status:"connected", title:"Repository snapshot available", connected:true, reason:"Read-only source capture. The displayed facts describe the last fetched snapshot, not continuous monitoring."};
    return {status:connection.status || "unknown", title:`Repository ${connection.status || "status unknown"}`, connected:false, reason:connection.reason || "Repository source extraction did not produce an available snapshot."};
  }
  function rowTable(headers, rows, caption) {
    const wrap = make("div", undefined, "source-table-wrap"), table = make("table"), head = make("thead"), headings = make("tr"), body = make("tbody");
    wrap.tabIndex = 0; wrap.setAttribute("role", "region"); wrap.setAttribute("aria-label", caption || `Source table: ${headers.join(", ")}`);
    if (caption) table.append(make("caption", caption));
    for (const header of headers) {const th = make("th", header); th.scope = "col"; headings.append(th);}
    head.append(headings);
    for (const cells of rows) {const tr = make("tr"); for (const cell of cells) tr.append(make("td", value(cell))); body.append(tr);}
    table.append(head, body); wrap.append(table); return wrap;
  }
  function section(parent, title, text) {
    const block = make("section", undefined, "source-section"); block.append(make("h3", title)); if (text) block.append(make("p", text, "muted")); parent.append(block); return block;
  }
  function details(parent, title, build) {
    const item = make("details", undefined, "source-details"); item.append(make("summary", title)); let built = false;
    item.addEventListener("toggle", () => {if (item.open && !built) {built = true; build(item);}}); parent.append(item); return item;
  }
  function bulletList(parent, items) {
    const list = make("ul"); for (const item of items || []) list.append(make("li", value(item))); parent.append(list);
  }
  function statusChip(parent, label, status) {
    const chip = make("span", `${label}: ${value(status)}`, "source-badge"); chip.dataset.status = String(status || "UNKNOWN").toLowerCase(); parent.append(chip);
  }
  function syntaxRows(observed, kind) {
    return (observed?.symbols || []).flatMap(symbol => (symbol.facts || []).filter(fact => fact.kind === kind).map(fact => [symbol.ref, fact.line, fact.value]));
  }
  function renderGit(parent, connection) {
    const git = connection.git;
    const block = section(parent, "Checkout and worktrees", "Metadata was captured without running project code. Untracked files are not inspected.");
    if (!git) {block.append(make("p", "Git metadata was not reported.")); return;}
    block.append(rowTable(["Field", "Observed value"], [
      ["Checkout", connection.root], ["HEAD", git.head], ["Branch", git.branch === null ? "Detached or unborn branch" : git.branch],
      ["Tracked working tree", git.dirty === true ? "Dirty" : git.dirty === false ? "Clean" : "Unknown"],
      ["Untracked files", git.untracked], ["Worktree reporting limit", git.worktree_limit]
    ]));
    const trees = git.worktrees || [];
    if (trees.length) block.append(rowTable(["Path", "Branch", "HEAD", "Flags"], trees.map(tree => [tree.path, tree.branch || (tree.detached ? "Detached" : "Not reported"), tree.head,
      ["detached", "bare", "locked", "prunable"].filter(flag => tree[flag]).join(", ") || "None reported"]), `${trees.length} reported worktrees`));
    else block.append(make("p", "No worktree records were returned."));
  }
  function renderCoverage(parent, connection) {
    const coverage = connection.coverage || {}, excluded = Object.entries(coverage.excluded || {});
    const block = section(parent, "Capture coverage", coverage.scope || "Coverage scope was not reported.");
    const badges = make("div", undefined, "source-badges");
    statusChip(badges, "Tracked files", coverage.tracked_files); statusChip(badges, "Captured files", coverage.captured_files);
    statusChip(badges, "Excluded files", coverage.excluded ? excluded.reduce((sum, [, count]) => sum + Number(count || 0), 0) : undefined);
    statusChip(badges, "Semantic coverage", coverage.semantic_complete === true ? "Reported complete" : coverage.semantic_complete === false ? "Partial" : "Unknown"); block.append(badges);
    if (excluded.length) block.append(rowTable(["Exclusion reason", "File count"], excluded));
    bulletList(block, coverage.limitations);
    const gaps = connection.gaps || [];
    details(block, `Extraction gaps (${gaps.length})`, item => {
      if (gaps.length) item.append(rowTable(["Path", "Reason"], gaps.map(gap => [gap.path || "Capture", gap.reason])));
      else item.append(make("p", "No extraction gaps were reported. This does not establish complete semantic coverage."));
    });
  }
  function renderBindings(parent, connection) {
    const bindings = connection.bindings || [], resolved = bindings.filter(binding => binding.resolved === true).length;
    const block = section(parent, "Declared source bindings", `${resolved} resolved · ${bindings.length - resolved} unresolved. A resolved binding identifies captured bytes or syntax; it does not establish that a domain rule is implemented correctly.`);
    if (!bindings.length) {block.append(make("p", "No source bindings were returned.")); return;}
    block.append(rowTable(["Term", "Source reference", "Resolution"], bindings.map(binding => [binding.term, binding.target, binding.resolved === true ? "Resolved" : "Unresolved"])));
    details(block, "Binding fingerprints", item => item.append(rowTable(["Term", "Reference", "Digest"], bindings.map(binding => [binding.term, binding.target, binding.digest]))));
  }
  function renderLint(parent, connection) {
    const lint = connection.lint || {verdict:"NOT_RUN"}, findings = lint.findings || [];
    const block = section(parent, "Source-link checks", "These are the adapter's actual Weave findings. Source-link lint is separate from runtime tests, model conformance and human review.");
    const badges = make("div", undefined, "source-badges"); statusChip(badges, "Lint verdict", lint.verdict); statusChip(badges, "Findings", findings.length); block.append(badges);
    if (findings.length) {
      block.append(rowTable(["Rule", "Diagnostic", "Location", "Recorded arguments"], findings.map((finding, index) => [
        finding.rule || finding.code || finding.rule_id || `Finding ${index + 1}`,
        typeof finding === "string" ? finding : finding.message_id || finding.message || "No message supplied",
        finding.uri ? `${finding.uri}${finding.start_line ? ":" + finding.start_line : ""}` : "No source location supplied",
        Object.entries(finding.args || {}).map(([key, input]) => `${key}: ${value(input)}`).join("; ") || "None supplied"
      ])));
      details(block, "Exact finding records and witnesses", item => item.append(make("pre", JSON.stringify(findings, null, 2))));
    }
    else block.append(make("p", lint.verdict === "NOT_RUN" ? "Source-link checks did not run." : "No source-link findings were returned; use the reported verdict and coverage limits."));
    const notRun = lint.not_run || [];
    if (notRun.length) {block.append(make("h4", "Checks not run")); block.append(rowTable(["Rule", "Reason"], notRun.map(item => typeof item === "string" ? ["Not reported", item] : [item.rule, item.reason])));}
    const verdicts = Object.entries(lint.verdicts || {});
    if (verdicts.length) details(block, "Per-rule verdicts", item => item.append(rowTable(["Rule", "Verdict"], verdicts)));
  }
  function renderObserved(parent, observed) {
    const block = section(parent, "Observed implementation facts", "The declared domain journey and the observed implementation are separate. These Python syntax facts do not establish reachability, successful execution or equivalence.");
    if (!observed) {block.append(make("p", "No implementation-fact extractor result is available for this snapshot. Generic source bindings remain available above.")); return;}
    const badges = make("div", undefined, "source-badges");
    statusChip(badges, "Extraction", observed.extraction?.status); statusChip(badges, "Method", observed.extraction?.method);
    statusChip(badges, "Conformance", observed.conformance?.status || "NOT_RUN"); block.append(badges);
    block.append(make("p", observed.conformance?.reason || "Source occurrences do not prove implementation equivalence.", "source-limitation"));
    bulletList(block, observed.extraction?.limitations);
    const declared = observed.declared_model || {};
    block.append(rowTable(["Declared model", "Status", "Scope"], [[declared.pack_id, declared.status, declared.scope]]));
    for (const [kind, title, explanation] of [
      ["stage_write_syntax", "Stage write occurrences", "Literal or expression syntax assigned to stage. A listed occurrence is not a proved state transition."],
      ["principal_require_call", "Capability check calls", "Calls to principal.require found in the source. Their presence alone does not prove that every path enforces authority."],
      ["unmodeled_predicate", "Predicates outside the declared workflow", "Observed if, conditional, while and assertion expressions. No path condition, call graph or data-flow proof is inferred."],
      ["stage_type_declaration", "Stage type declarations", "The annotation as written in the captured source."]
    ]) {
      const rows = syntaxRows(observed, kind);
      details(block, `${title} (${rows.length})`, item => {item.append(make("p", explanation, "muted"));
        if (rows.length) item.append(rowTable(["Exact source reference", "Line", "Observed syntax"], rows)); else item.append(make("p", "No occurrences of this kind were reported in the captured symbols."));
      });
    }
    const declarations = (observed.symbols || []).filter(symbol => Object.hasOwn(symbol, "literal_names"));
    details(block, `Declared tool and owner-operation names (${declarations.length})`, item => {
      item.append(make("p", "Names extracted from literal declarations; this is not a runtime capability or authorization test.", "muted"));
      item.append(rowTable(["Source reference", "Status", "Names"], declarations.map(symbol => [symbol.ref, symbol.status, symbol.literal_names?.join(", ") || symbol.reason || "Not resolved"])));
    });
    const gaps = observed.gaps || [];
    if (gaps.length) {block.append(make("h4", `Unresolved observations (${gaps.length})`)); block.append(rowTable(["Source", "Status", "Reason"], gaps.map(gap => [gap.ref || gap.path, gap.status, gap.reason])));}
    details(block, "Observed symbol and source identities", item => {
      item.append(rowTable(["Source file", "Status", "SHA-256 / reason"], (observed.sources || []).map(source => [source.path, source.status, source.sha256 || source.reason])));
      item.append(rowTable(["Symbol reference", "Lines", "Status", "AST digest / reason"], (observed.symbols || []).map(symbol => [symbol.ref, symbol.line ? `${symbol.line}–${symbol.end_line || symbol.line}` : "Unknown", symbol.status, symbol.ast_sha256 || symbol.reason])));
    });
  }
  function renderHashes(parent, connection) {
    const block = section(parent, "Snapshot identities", "Hashes identify the captured inputs. They do not prove correctness, confer approval or show that the working tree is still unchanged.");
    block.append(rowTable(["Subject", "Digest"], [["Captured source", connection.source_hash], ["Linked graph", connection.graph_hash], ["Domain pack", connection.pack?.digest], ["Observed facts", connection.observed_facts?.source_digest]]));
    const hashes = Object.entries(connection.file_hashes || {});
    details(block, `Captured file fingerprints (${hashes.length})`, item => item.append(rowTable(["Repository path", "SHA-256"], hashes)));
  }
  function render(root, connection) {
    root.replaceChildren();
    const info = state(connection), heading = make("div", undefined, "source-heading");
    heading.append(make("h2", info.title), make("p", info.reason)); root.append(heading);
    const badges = make("div", undefined, "source-badges"); statusChip(badges, "Connection", info.status); statusChip(badges, "Tests via source indexing", "NOT_RUN"); root.append(badges);
    root.append(make("p", "Source indexing does not run project tests. Model/runtime evidence is shown separately in Evidence & decision.", "source-limitation"));
    if (!info.connected) {
      if (connection?.root) root.append(make("p", "Configured root: " + connection.root));
      renderLint(root, connection || {lint:{verdict:"NOT_RUN", findings:[], not_run:[]}}); return;
    }
    renderGit(root, connection); renderCoverage(root, connection); renderBindings(root, connection);
    renderLint(root, connection); renderObserved(root, connection.observed_facts); renderHashes(root, connection);
  }
  return {render, state, syntaxRows};
})();
if (typeof module !== "undefined") module.exports = EijaSource;
