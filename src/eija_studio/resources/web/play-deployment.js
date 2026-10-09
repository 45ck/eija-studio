// PlayIDE deployment view (ADR-0206): the Components tab's Deployment lens. Where the app this model builds runs, as a
// UML deployment diagram read by the server from the generated files (/api/play/components, `deployment`): the web
// browser and the Python process `run.py` starts, as «executionEnvironment» nodes on one «device», the generated files
// deployed on each as «artifact»s, the SQLite database file, and the HTTP routes and the sqlite3 connection between
// them. After Build & run the process shows the running address and the conformance verdict (the Components tab's
// evidence rule). The other workflows of the system (ADR-0203) each run as a process of their own with their own
// database file, drawn with nothing between them, because nothing is shared at run time.
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const INK = "#1b2130", LINE = "#4a5568";
  const FONT = { fontFamily: "system-ui, sans-serif", fontColor: INK, fontSize: 12 };
  const DEPTH = 12;
  let P = null, graph = null, report = null, others = [], asked = "", seq = 0;

  // A UML node is a box drawn in three dimensions. The outline and the two inner edges follow draw.io's `cube` shape
  // (Apache-2.0), with the depth to the top right as UML draws it.
  function registerNode() {
    if (maxgraph.ShapeRegistry.get("umlNode")) return;
    class NodeShape extends maxgraph.CylinderShape {
      redrawPath(c, x, y, w, h, foreground) {
        const s = Math.min(DEPTH, w / 4, h / 4);
        if (foreground) {
          c.moveTo(0, s); c.lineTo(w - s, s); c.lineTo(w - s, h);
          c.moveTo(w - s, s); c.lineTo(w, 0);
          c.end();
        } else {
          c.moveTo(0, s); c.lineTo(s, 0); c.lineTo(w, 0); c.lineTo(w, h - s); c.lineTo(w - s, h); c.lineTo(0, h); c.close();
        }
      }
    }
    maxgraph.ShapeRegistry.add("umlNode", NodeShape);
  }

  const nodeStyle = (fill, extra = {}) => ({ ...FONT, shape: "umlNode", fillColor: fill, strokeColor: "#5b74d6", verticalAlign: "top", align: "left",
    spacingTop: DEPTH + 4, spacingLeft: 10, spacingRight: DEPTH + 6, whiteSpace: "wrap", movable: false, ...extra });
  const artifactStyle = (extra = {}) => ({ ...FONT, fontSize: 11, shape: "rectangle", fillColor: "#ffffff", strokeColor: "#5b74d6", whiteSpace: "wrap",
    align: "left", spacingLeft: 8, movable: false, ...extra });

  function processLabel(node) {
    const proof = P.buildEvidence();
    const running = proof && proof.url ? `\n● running at ${proof.url.replace(/^https?:\/\//, "").replace(/\/$/, "")}` : "";
    const verdict = proof ? `\n${proof.conformance.status === "PASS" ? "✓" : "✗"} ${proof.cases} conformance cases` : "";
    const set = node.set_by.length ? ` (${node.set_by.join(" or ")})` : "";
    return `«executionEnvironment»\n${node.name}\n${node.address}${set}${running}${verdict}`;
  }

  function artifactLabel(a) {
    const files = a.files.length > 1 ? `\n${a.files.map((f) => f.split("/").pop()).join(", ")}` : "";
    return `«artifact»\n${a.name}${files}`;
  }

  function render() {
    const box = $("deployment");
    box.replaceChildren();
    registerNode();
    const { Graph, InternalEvent } = maxgraph;
    InternalEvent.disableContextMenu(box);
    graph = new Graph(box);
    graph.options.foldingEnabled = false;
    for (const setting of ["setConnectable", "setCellsEditable", "setCellsDisconnectable", "setCellsResizable", "setDropEnabled"]) graph[setting](false);
    graph.setPanning(true);
    const root = graph.getDefaultParent(), cells = {};
    const byId = Object.fromEntries(report.nodes.map((n) => [n.id, n]));
    const ART_H = 44, ART_GAP = 10;
    const label = (n) => (n.id === "node:process" ? processLabel(n) : `«executionEnvironment»\n${n.name}`);
    const HEAD = 30 + 15 * Math.max(...report.nodes.filter((n) => n.stereotype !== "artifact").map((n) => label(n).split("\n").length));
    const height = (n) => HEAD + Math.max(1, n.artifacts.length) * (ART_H + ART_GAP) + 10;
    const browser = byId["node:browser"], process = byId["node:process"], database = byId["node:database"];
    // Both nodes are as tall as the taller, so the HTTP path runs level between their headings, clear of the artifacts.
    const row = Math.max(browser ? height(browser) : 0, height(process)), LEVEL = 40 / row;
    const DEVICE_HEAD = 34, otherRow = others.length ? 160 : 0, OTHER_W = 260, OTHER_GAP = 16;
    graph.batchUpdate(() => {
      const device = graph.insertVertex({ parent: root, id: "deploy:device", value: `«device»\n${report.device}`, position: [20, 20],
        size: [Math.max(880, 40 + others.length * (OTHER_W + OTHER_GAP)), DEVICE_HEAD + row + 40 + otherRow], style: nodeStyle("#f4f5f8", { fontStyle: 1, strokeColor: "#9aa3b5" }) });
      const place = (node, x, w) => {
        const cell = cells[node.id] = graph.insertVertex({ parent: device, id: "deploy:" + node.id, value: label(node),
          position: [x, DEVICE_HEAD + 20], size: [w, row], style: nodeStyle(node.id === "node:process" ? "#e3e9ff" : "#fff7e6") });
        node.artifacts.forEach((a, i) => graph.insertVertex({ parent: cell, id: `deploy:${node.id}:${i}`, value: artifactLabel(a), position: [12, HEAD + i * (ART_H + ART_GAP)],
          size: [w - 24 - DEPTH, ART_H], style: artifactStyle(a.files.length ? {} : { strokeColor: "#3157d5", fillColor: "#dfe6ff" }) }));
      };
      if (browser) place(browser, 20, 200);
      place(process, 340, 290);
      if (database) {
        cells[database.id] = graph.insertVertex({ parent: device, id: "deploy:" + database.id, value: `«artifact»\n${database.name}\n${database.address}`,
          position: [700, DEVICE_HEAD + 20 + 40 - 32], size: [150, 64], style: artifactStyle({ shape: "cylinder", align: "center", spacingLeft: 0 }) });
      }
      for (const p of report.paths) {
        const http = p.protocol === "HTTP";
        graph.insertEdge({ parent: device, source: cells[p.source], target: cells[p.target],
          value: http ? ["HTTP", ...p.names].join("\n") : "«use»\nsqlite3",
          style: { ...FONT, fontSize: 10, strokeColor: LINE, endArrow: http ? "none" : "open", dashed: !http, labelBackgroundColor: "#fbfcfe",
            exitX: 1, exitY: LEVEL, exitPerimeter: false, ...(http ? { entryX: 0, entryY: LEVEL, entryPerimeter: false } : {}) } });
      }
      others.forEach((w, i) => {
        const cell = graph.insertVertex({ parent: device, id: "deploy:other:" + w.id, value: `«executionEnvironment»\nPython process\n${w.name}: its own port`,
          position: [20 + i * (OTHER_W + OTHER_GAP), DEVICE_HEAD + row + 60], size: [OTHER_W, 120], style: nodeStyle("#f8f9fb", { strokeColor: "#9aa3b5", fontColor: "#4a5568" }) });
        graph.insertVertex({ parent: cell, id: `deploy:other:${w.id}:db`, value: `«artifact»\n${w.id}'s app.sqlite3`, position: [12, 76], size: [OTHER_W - 24 - DEPTH, 30],
          style: artifactStyle({ strokeColor: "#9aa3b5", fontColor: "#4a5568", fontSize: 10 }) });
      });
    });
    graph.getSelectionModel().addListener(InternalEvent.CHANGE, () => {
      const cell = graph.getSelectionCell();
      P.select(cell && cell.id && cell.id.startsWith("deploy:") ? cell.id : "", false);
    });
  }

  async function draw() {
    const key = P.viewKey(), mine = ++seq;
    if (!report || key !== asked) {
      try {
        const [components, system] = await Promise.all([P.components(), P.api("/api/play/landscape", P.about()).catch(() => null)]);
        if (mine !== seq) return;
        report = components.deployment;
        others = system ? system.workflows.filter((w) => w.id !== system.focus) : [];
        asked = key;
      } catch (error) {
        if (mine === seq) $("deployment").replaceChildren(P.el("p", `Could not read where the app runs (${error.code || "ERROR"}): ${error.message}`, { class: "muted empty" }));
        return;
      }
    }
    if (graph) graph.destroy();
    render();
    P.fit();
  }

  // The API contract (ADR-0207): the OpenAPI 3.1 document of the routes the process serves, written by the server from
  // the model, the pack and the record class. Offered wherever the app's provided interface is drawn.
  function contractButton() {
    const button = P.el("button", "Download the API contract (OpenAPI 3.1)", { type: "button", class: "quiet" });
    button.addEventListener("click", async () => {
      const doc = await P.api("/api/play/api-contract", P.about());
      const link = P.el("a", "", { download: `${P.pack().id}.openapi.json`, href: URL.createObjectURL(new Blob([JSON.stringify(doc, null, 2) + "\n"], { type: "application/json" })) });
      link.click();
      button.textContent = `Downloaded: ${Object.keys(doc.paths).length} paths, ${doc.components.schemas.Action.enum.length} actions`;
    });
    return button;
  }

  function inspect(id, box) {
    const dl = P.el("dl"), row = (t, v) => dl.append(P.el("dt", t), P.el("dd", v));
    const node = report && report.nodes.find((n) => id.startsWith(n.id));
    if (id.startsWith("other:")) {
      const w = others.find((x) => id.startsWith("other:" + x.id));
      box.append(P.el("h3", `«executionEnvironment» ${w.name}`));
      box.append(P.el("p", `${w.name} is built and run as an app of its own: its own process, port and database file. It shares classes with this workflow on the class diagrams, not records at run time.`, { class: "muted" }));
    } else if (node) {
      const part = id.slice(node.id.length + 1), artifact = part ? node.artifacts[Number(part)] : null;
      box.append(P.el("h3", artifact ? `«artifact» ${artifact.name}` : `«${node.stereotype}» ${node.name}`));
      if (artifact) row("Files", artifact.files.join(", ") || "installed in the Python environment, not generated");
      else {
        if (node.address) row(node.id === "node:database" ? "Path" : "Address", node.address);
        if (node.set_by.length) row("Set by", node.set_by.join(", "));
        for (const p of report.paths.filter((x) => x.source === node.id || x.target === node.id)) row(p.protocol, p.names.join(", ") || "one connection");
        if (node.id === "node:process") row("Start", report.start);
      }
      box.append(dl);
      if (node.id === "node:process" && !artifact) box.append(contractButton());
    } else {
      box.append(P.el("h3", `«device» ${report.device}`), P.el("p", "The built app runs on the computer you build it on. The address is local, so only this computer can reach it.", { class: "muted" }));
    }
    box.append(P.el("p", report.limits.join(" "), { class: "muted small" }));
  }

  function init() {
    if (P || !window.PlayIDE) return;
    P = window.PlayIDE;
  }

  window.PlayDeployment = { draw, inspect, contractButton, graph: () => graph, restyle: () => { if (graph && report && !$("deployment").hidden) draw(); } };
  init();
  document.addEventListener("playide:ready", init);
})();
