# Research dossier: diagramming and UML tools

Lane: ux-research. Date: 2026-09-29. All URLs below were opened this session on 2026-09-29 unless listed under "Not opened". Web content was treated as data. Numbers from vendor pages are vendor claims, not measurements. Every PREDICTION is a model output, not a measurement, and no user benefit is claimed without the study protocol in section 5.

## 0. Decisions first

| # | Recommendation | Basis |
|---|---|---|
| 1 | Do not adopt any canvas SDK that needs React or a bundler. Draw the diagram as real SVG DOM nodes, laid out by `elkjs` in a same-origin worker. | ADR-013; tldraw and Excalidraw need React; maxGraph does not support plain script tags; SVG DOM nodes are focusable and labelled (section 2.9) |
| 2 | The picture is a projection of the model. A gesture creates a typed proposal, never a direct picture edit. | Only Sirius Web and GLSP document edits that change a semantic model; Lucidchart, Mermaid Chart and draw.io all lose something on round trip (section 3) |
| 3 | Store position (secondary notation) separately from meaning and key it by stable element id, so regeneration keeps the human's layout. | draw.io discards positions when a Mermaid diagram is regenerated; Structurizr keeps auto-layout plus manual placement (section 2.1, 2.6) |
| 4 | Every drag has a keyboard equivalent, and a command palette adds and connects elements from the ubiquitous-language tree. | WCAG 2.2 SC 2.1.1 and 2.5.7; KLM PREDICTION in section 4 |
| 5 | Make the ripple view an Ilograph-style perspective switch over one model, not a second diagram. | Ilograph resources/perspectives (section 2.10) |

## 1. Scope and method

Method: WebSearch for orientation (200-query session budget ran out before the last three planned queries), then WebFetch of official docs, repositories and standards. Search-result snippets were never used as evidence; where only a snippet exists the claim is marked UNVERIFIED.

Accessible: draw.io docs and repo, Structurizr docs, Excalidraw docs and repo, tldraw docs and repo, maxGraph, elkjs, Cytoscape.js, JointJS, dagre, Mermaid docs, Mermaid Chart docs, PlantUML, StarUML, yEd, Whimsical, Ilograph, Eraser docs, FigJam help, Visio for the web help, Miro and Lucid product pages, Eclipse GLSP and Sirius Web, W3C WCAG 2.2, W3C ARIA APG, W3C DTCG, MDN, Nielsen Norman Group.

Not accessible (HTTP 403 or blocked): Sparx Systems pages, Miro Help Center, Lucid Help Center, the Structurizr vNext announcement on Patreon, web.archive.org, npmjs.com. These products are marked partially verified below.

Limits of the method: the fetch tool summarises pages with a small model, so exact wording and version numbers were re-checked only where a second page agreed. Products change quickly; treat statements as true on 2026-09-29 only.

## 2. Products and topics

Format per item: what it is today; patterns with the law or principle that explains them; verdict for EIJA (adopt, adapt, avoid).

### 2.1 diagrams.net / draw.io (verified)

Today: JavaScript client-side general diagramming editor, Apache-2.0, core team accepts no pull requests ([repo](https://github.com/jgraph/drawio)).

| Pattern | Why it works (law or principle) | Source |
|---|---|---|
| Connectors are created by hovering a shape and dragging from a direction arrow or a fixed connection point; dropping a library shape on an arrow connects it | Direct manipulation; the affordance appears only near the target, which keeps the canvas quiet (Fitts: target grows on hover) | [connectors](https://www.drawio.com/docs/manual/connectors/) |
| Waypoints are added and removed automatically as a segment is dragged; Alt+Shift+R resets to default route | Low viscosity for the common edit, one-key escape from a bad edit (error recovery) | [connectors](https://www.drawio.com/docs/manual/connectors/), [shortcuts post, 2023-07-14](https://www.drawio.com/blog/new-keyboard-shortcuts/) |
| Modifier layer: Alt suspends grid snapping, Shift keeps proportions, Ctrl+drag clones, Alt+Ctrl+Shift+drag inserts space and pushes neighbours | Expert accelerators on top of a novice default (progressive disclosure); costs discoverability | [modifier shortcuts](https://www.drawio.com/docs/reference/shortcuts/modifier-shortcuts-in-diagrams/) |
| Tab, Shift+Tab, Alt+Tab move selection to next, previous and parent shape, stepping into containers and connector labels | Keyboard operability (WCAG 2.1.1); container traversal maps to tree structure | [selection shortcuts](https://www.drawio.com/docs/reference/shortcuts/shortcut-select/) |
| Inserting Mermaid creates native shapes in a container group that stores the Mermaid source; re-editing regenerates, keeping style and label changes but resetting positions, sizes and connector paths | Honest partial round trip; shows exactly which layer (layout) is the casualty of regeneration | [Mermaid in draw.io](https://www.drawio.com/blog/mermaid-diagrams) |

Verdict: adapt the hover-arrow connector, the modifier layer for expert drag, and Tab/Alt+Tab container traversal. Avoid the regeneration policy that discards layout.

### 2.2 Microsoft Visio for the web (partially verified)

Today: browser viewer/editor for Visio diagrams; business Microsoft 365 subscribers create basic diagrams, advanced diagramming needs Plan 1 or Plan 2; help includes "make diagrams accessible" and keyboard-shortcut pages; data-linked shapes can be refreshed and their shape data viewed ([help](https://support.microsoft.com/en-US/Visio/visio-for-the-web-help)). Shape data attached to shapes is the closest mainstream analogue to model attributes on a picture. Detailed interaction behaviour was not read. Verdict: adapt the shape-data idea (a property list behind each shape); no further claim.

### 2.3 Lucidchart, Miro, FigJam, Whimsical (mixed verification)

| Product | Verified today | Pattern and why | Verdict |
|---|---|---|---|
| Lucidchart | AI-generated diagrams from prompts; linking to Google Sheets, Excel or CSV; conditional formatting ([product](https://lucid.co/lucidchart/)). Users report Mermaid-generated diagram shapes are not draggable ([community idea](https://community.lucid.co/ideas/convert-diagram-as-code-flowchart-to-regular-draggable-components-12112)); the request is unresolved | Data-linked conditional formatting is a visibility device: model state coloured onto shapes. Locked generated layout shows the cost of one-way text to picture | adapt formatting-from-data (with a non-colour cue); avoid locked layout |
| Miro | Over 2,000 shapes, paid packs for UML, BPMN, ERD; smart connectors; auto-layout; AI diagram from text; import of .vsdx, Lucid and draw.io files ([diagramming](https://miro.com/diagramming/)). Help pages returned 403 | Large shape libraries behind packs is a Hick-Hyman problem solved by category filtering; EIJA needs a palette of about ten model-derived kinds, not thousands | avoid library breadth |
| FigJam | Elbow or straight connectors; sections; "Tidy up" arranges objects into a grid; AI can make flow charts, Gantt, org charts, mind maps; output is ordinary editable objects ([guide](https://help.figma.com/hc/en-us/articles/1500004362321-Guide-to-FigJam), [AI](https://help.figma.com/hc/en-us/articles/18706554628119-Make-boards-and-diagrams-with-FigJam-AI)) | One-step "tidy" is a low-viscosity repair for the layout mess that drag creates; AI output lands as normal objects, i.e. no separate AI mode | adapt Tidy as an explicit, undoable command |
| Whimsical | Diagrams, flowcharts, mind maps, wireframes, boards; AI flowcharts; release 2026.11 adds code blocks in boards ([home](https://whimsical.com/)). The "speed" positioning is a vendor claim | Nothing beyond positioning was verified | not evaluated |

### 2.4 Excalidraw (verified)

Today: MIT, React and React DOM peer dependencies, arrow binding, shape libraries, export to PNG, SVG and `.excalidraw` JSON, collaboration with end-to-end encryption ([repo](https://github.com/excalidraw/excalidraw)); the npm docs say fonts are fetched from a CDN unless self-hosted via `EXCALIDRAW_ASSET_PATH` ([install](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/installation)), which conflicts with `default-src 'none'` unless self-hosted. The API exposes `updateScene` and `onChange` for programmatic control ([API](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/props/excalidraw-api)). `mermaid-to-excalidraw` converts one way, Mermaid to Excalidraw, MIT ([repo](https://github.com/excalidraw/mermaid-to-excalidraw)).

Pattern: hand-drawn rendering is secondary notation that signals "draft, not authoritative", which is useful when the picture is an AI proposal (role-expressiveness). Verdict: avoid as a dependency (React); adapt the idea of a visibly provisional style for unaccepted proposals, encoded by dashed outline plus a text badge, not colour alone.

### 2.5 tldraw (verified)

Today: React SDK for infinite canvas apps; multiplayer via `@tldraw/sync`; agent and workflow starter kits; free for development, production requires a licence key; hobby licence requires a "made with tldraw" watermark; source-available, not permissive ([repo](https://github.com/tldraw/tldraw), [licence](https://tldraw.dev/community/license)).

Best documented canvas accessibility of the tools read ([accessibility](https://tldraw.dev/sdk-features/accessibility)):

| Pattern | Why it works |
|---|---|
| Tab and Shift+Tab move through shapes in reading order (rows by vertical position, left to right within a row); Ctrl/Cmd+arrows jump to nearest shape in a direction | Turns a 2-D scene into a linear sequence a screen reader can announce (WCAG 2.1.1; visibility) |
| A live region announces "[description], [type]. [position] of [total]" on selection | Position-in-set gives orientation without seeing the canvas |
| `getAriaDescriptor()` per shape; animation speed defaults to the OS reduced-motion setting | Semantic label separate from visible text |

Verdict: avoid the SDK (licence plus React); adopt the keyboard-and-announcement design as a requirement on our own SVG.

### 2.6 Mermaid, Mermaid Live Editor, Mermaid Chart (verified)

Today: MIT JavaScript library rendering text to SVG; many diagram types including class, ER, state, C4; default `securityLevel` is `strict`; v12 targets ES2024 and Safari 17.4 or later; `mermaid.render()` returns SVG text ([intro](https://mermaid.js.org/intro/), [usage](https://mermaid.js.org/config/usage.html), [licence](https://github.com/mermaid-js/mermaid/blob/develop/LICENSE)). Config defaults: `maxTextSize` 50000, `maxEdges` 500 ([schema](https://mermaid.js.org/config/schema-docs/config.html)). Mermaid Chart's visual editor supports flowchart, class, sequence, state, mindmap, ER and requirement diagrams; both editors are kept in sync but the visual editor "prettifies" and restructures the code, so exact formatting is lost; subgraphs and intricate logic are recommended in text ([docs](https://mermaid.ai/docs/build-and-edit/use-the-visual-editor)).

| Pattern | Why it works |
|---|---|
| Live preview beside text, with node-to-code highlighting | Progressive evaluation and low premature commitment; Doherty 400 ms and Nielsen 0.1 s and 1 s limits bound the preview budget |
| Hard caps on diagram size | Explicit, visible failure beats silent slowdown (error-proneness) |

Verdict: adapt for a read-only text view of the model (Mermaid/PlantUML generated from the model, never parsed back). Whether Mermaid output runs under `style-src 'self'` is UNVERIFIED and must be tested before adoption (section 5).

### 2.7 PlantUML (verified)

Today: open-source, Java, text to UML plus many non-UML types; layout engines Graphviz (default, external), Smetana (internal Java port), VizJs, ELK (orthogonal only); repository offers GPL, LGPL, Apache, Eclipse Public and MIT licence choices ([site](https://plantuml.com/), [repo](https://github.com/plantuml/plantuml)). It is one-way: text is the only source. Verdict: adopt as a server-side export target already planned in the diagrams lane; avoid as an editing surface.

### 2.8 Structurizr (verified, status changing)

Today: a "models as code" tool for the C4 model, Apache-2.0 repository ([repo](https://github.com/structurizr/structurizr)). The docs navigation marks Lite, on-premises, cloud, CLI and server as "End of life", and the cloud service is announced end of life with the Playground, a local tool and a self-hosted server as replacements ([docs](https://docs.structurizr.com/), [cloud](https://docs.structurizr.com/cloud)). The home page announces "Structurizr vNext" and an MCP server for validation and parsing ([home](https://structurizr.com/)); details of vNext are UNVERIFIED (Patreon post returned 403).

| Pattern | Why it works | Source |
|---|---|---|
| One model, many views; model and views are separated | Removes hidden dependencies between "what exists" and "how it is drawn"; clean diffs | [as-code](https://docs.structurizr.com/as-code) |
| Automatic layout first, then a browser diagram editor for manual placement, which the docs call crafting "a more precise story" | Automation for the default, manual control as secondary notation | [as-code](https://docs.structurizr.com/as-code) |
| Docs argue that re-parenting is easier in code than in a UI as models grow | Viscosity of visual editing rises with size (vendor argument, not measured) | [as-code](https://docs.structurizr.com/as-code) |

Verdict: adopt the model/view separation and auto-layout-plus-manual-adjust; treat the roadmap as unstable.

### 2.9 Model-repository tools: Sparx, StarUML, GLSP, Sirius Web

| Tool | Verified | Note |
|---|---|---|
| Sparx Enterprise Architect | UNVERIFIED. All Sparx pages returned 403; a search snippet named version 17.1 build 1716 (2026-01-29) but was not opened | Do not build on it |
| StarUML | v7.1.1; most UML 2 diagrams; C4 and SysML are pro features; model data stored as simple JSON; JavaScript extensions; MCP server for AI; code generation via extensions ([site](https://staruml.io/)) | JSON model plus scripting is the closest desktop analogue to our contract-first approach |
| Eclipse Sirius Web | Domain and view are defined by configuration; diagrams are synchronised views of the semantic model; graphical edits modify the model ([page](https://eclipse.dev/sirius/sirius-web.html)) | Vendor description, not tested. Stack is React, Spring Boot, PostgreSQL, so not embeddable here |
| Eclipse GLSP | Client-server protocol modelled on the Language Server Protocol; SVG client on Sprotty; domain logic on a Java or Node server; EPL-2.0 ([site](https://eclipse.dev/glsp/), [repo](https://github.com/eclipse-glsp/glsp)) | The design to copy: the client sends edit operations, the server validates and applies them |

Verdict: adopt the GLSP protocol shape (client sends operation requests, server returns the new model and diagram), not the code. It maps directly onto "AI proposes, kernel checks, owner decides": the browser never mutates the model.

### 2.10 yEd and Ilograph (verified)

yEd: free including commercial use, version 3.25.1, Java Swing on yFiles, automatic layout "with the press of a button", exports PNG, JPG, SVG, PDF, SWF ([yWorks](https://www.yworks.com/products/yed)). Pattern: one-command layout is the benchmark for a "Tidy" button.

Ilograph: diagrams are code; resources form a tree, perspectives show different relations over the same resources, sequences show flows; layout is automatic with no manual coordinates; screen-reader friendly, full keyboard navigation, resource finder; HTML export ([features](https://www.ilograph.com/features.html), [spec](https://www.ilograph.com/docs/spec/)).

| Pattern | Why it works |
|---|---|
| Resource tree plus perspective switch over the same model | Overview first, one view per question; hidden dependencies become visible by switching the lens |
| Resource finder for any size of diagram | Recognition over recall; search cost independent of layout |

Verdict: adopt the tree-plus-perspectives structure for the DDD tree and the ripple views. Avoid the no-manual-layout rule for the UML canvas because layout is secondary notation users rely on (Green and Petre).

### 2.11 Eraser (verified, one claim unconfirmed)

Today: diagram-as-code for flowchart, ERD, cloud architecture, sequence and BPMN with automatic layout ([docs](https://docs.eraser.io/diagram-as-code)). The quickstart states the AI output is diagram-as-code, edited as text with the canvas updating as you type, opened with `/` or Ctrl+J, and that an MCP server lets coding agents create and update diagrams ([quickstart](https://docs.eraser.io/quickstart)). Whether canvas drag edits write back into the code is not stated on the pages read: UNVERIFIED. Verdict: adapt the "AI writes the text, human edits text or canvas" loop, but in EIJA the AI writes a proposal, not the source of truth.

### 2.12 OSS libraries usable without a build step under `script-src 'self'; style-src 'self'`

CSP facts: `style-src 'self'` blocks `<style>` elements, `style=` attributes, `setAttribute("style", ...)` and `cssText`, but allows `element.style.prop = ...` ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src)). MDN does not say how SVG presentation attributes are treated; they are not `style` attributes, and this must be tested in the target browsers.

| Library | Licence | Plain script or no bundler? | CSP and a11y notes | Verdict |
|---|---|---|---|---|
| maxGraph | Apache-2.0 | No: README says direct use via script tags is not supported; needs a bundler; TypeScript, zero dependencies ([repo](https://github.com/maxGraph/maxGraph)) | Fork of archived mxGraph, XML-compatible | avoid unless a prebuilt bundle is vendored and passes a CSP test |
| Cytoscape.js | MIT | Yes: `cytoscape.min.js`; canvas renderer; 70+ extensions incl. edgehandles, dagre, ELK layouts; v3.34.3 ([site](https://js.cytoscape.org/), [repo](https://github.com/cytoscape/cytoscape.js)) | Canvas draws no DOM, so nodes are not focusable; a parallel DOM tree would be required (my inference). The docs' performance flags are "largely moot" now | adapt for large read-only graphs only |
| JointJS core | MPL-2.0 | Not confirmed; repo documents Yarn and Node install ([repo](https://github.com/clientIO/joint), [licence](https://raw.githubusercontent.com/clientIO/joint/master/LICENSE)) | SVG based. Inspectors, stencils, toolbars and advanced layouts are in paid JointJS+ | avoid: the parts we need are paid |
| Excalidraw | MIT | React peer dependency | Fonts from CDN by default | avoid (section 2.4) |
| tldraw SDK | source-available, licence key for production | React | best a11y design | avoid (section 2.5) |
| elkjs | EPL-2.0; release 0.12.0 adds GPL-3.0 as secondary licence ([LICENSE](https://raw.githubusercontent.com/kieler/elkjs/master/LICENSE.md), [releases](https://github.com/kieler/elkjs/releases)) | Yes: web worker, plain script, or `elk.bundled.js` exposing global `ELK`; layered, stress, mrtree, radial, force, disco ([repo](https://github.com/kieler/elkjs)) | Computes positions only, no rendering; a same-origin worker should satisfy `script-src 'self'` (UNVERIFIED, test) | adopt as the layout engine |
| dagre | MIT | Not confirmed; only the `dagrejs` org package is maintained ([repo](https://github.com/dagrejs/dagre)) | Layered layout only | fallback if EPL-2.0 is unacceptable |

Recommended stack: about 300 lines of vanilla ES modules that build SVG with `createElementNS` and attributes (no style strings), `elkjs` for layout and orthogonal edge routing, and the Studio's own model API for edits. Record elkjs and any custom module in `docs/oss/REGISTER.md` under the diagrams lane.

## 3. Cross-cutting findings

### 3.1 Is there true bidirectional sync with a semantic model?

| Tool | Text to picture | Picture to text or model | What is lost | Evidence quality |
|---|---|---|---|---|
| Mermaid Live / PlantUML | yes | no | n/a | official docs |
| Mermaid Chart visual editor | yes | yes, for 7 diagram types | code is reformatted ("prettified") | official docs |
| draw.io + Mermaid | yes | partial, re-edit source | positions, sizes, connector paths reset on regeneration | official blog |
| Lucidchart + Mermaid | yes | no drag editing | layout locked | community request only |
| Eraser | yes | claimed | unknown | vendor quickstart; drag write-back unconfirmed |
| Structurizr | model to views, auto-layout | manual placement in browser editor | layout persistence not verified | official docs |
| Ilograph | yes | none, no coordinates | manual layout not possible | official docs |
| Sirius Web / GLSP | yes | yes, edits change the semantic model | n/a | vendor docs, untested |

Finding: only model-driven frameworks (Sirius Web, GLSP-based editors) document edits on the picture changing a semantic model; every text-and-canvas hybrid in the list loses layout or formatting on some path. For EIJA the safe formulation is the GLSP one: picture edits are requests, the kernel validates, the model changes only after owner decision, and the picture is regenerated from the model with stored positions re-applied.

### 3.2 Cognitive Dimensions of Notations

Definitions from Green and Petre 1996 as summarised on [Wikipedia](https://en.wikipedia.org/wiki/Cognitive_dimensions_of_notations); the original is [J. Visual Languages and Computing 7(2), 131-174](https://dblp.org/rec/journals/vlc/GreenP96.html) (paper not read; CDN site at [Cambridge](https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/) lists the tutorials but its PDF was unreadable). Ratings below are analyst judgement from the documentation read, not measurements. L = low, M = medium, H = high concern.

| Dimension | Text-first (Mermaid, PlantUML) | Canvas-first (draw.io, Lucid, Miro, FigJam) | Model-repository (Structurizr, Ilograph, StarUML) | EIJA design response |
|---|---|---|---|---|
| Viscosity (resistance to local change) | L for rename, H for layout | H for restructure, waypoints | L for model, M for views | model edits by command, layout by tidy |
| Premature commitment | M: syntax before structure known | L | M: must declare model first | draft state for unaccepted proposals |
| Hidden dependencies | H: links are text references | H: a connector hides semantics | L: the model is explicit | show ripple list beside every selection |
| Role-expressiveness | M | M: any shape can mean anything | H when typed | shape and glyph by DDD role, not by decoration |
| Visibility | M | L on large boards | M | tree plus finder plus minimap |
| Secondary notation | L | H: free layout and colour | M | keep it, persist by id, never as meaning |
| Error-proneness | M: parse errors | H: dangling or mislabelled links | L | kernel rejects invalid edits |

### 3.3 Interaction and performance facts

- Direct-manipulation feedback should arrive within about 0.1 s and stay under 1 s to preserve flow ([Nielsen](https://www.nngroup.com/articles/response-times-3-important-limits/)); Doherty and Thadani (1982) give 400 ms as the productivity threshold ([Laws of UX summary](https://lawsofux.com/doherty-threshold/)).
- Cytoscape.js, Mermaid and FigJam all publish size limits (see facts table); Miro's help pages were not readable, so its object-count guidance is UNVERIFIED.
- No dedicated diagram or graph-canvas pattern was found on the ARIA APG treegrid page; the nearest APG idiom for the DDD tree is expand/collapse with Left and Right arrows ([APG treegrid](https://www.w3.org/WAI/ARIA/apg/patterns/treegrid/)). The full APG pattern index was not checked.
- Common complaints found (sparingly): Lucid users cannot drag Mermaid-generated shapes and say the automatic placement defeats the purpose ([community](https://community.lucid.co/ideas/convert-diagram-as-code-flowchart-to-regular-draggable-components-12112)); Mermaid Chart warns that the visual editor rewrites code ([docs](https://mermaid.ai/docs/build-and-edit/use-the-visual-editor)).

## 4. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| WCAG 2.2 is a W3C Recommendation dated 2024-12-12 | [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | high |
| SC 2.5.8 minimum target size is 24 by 24 CSS px; SC 2.5.7 requires a non-dragging alternative for drag operations; SC 1.4.11 needs 3:1 contrast for UI components | [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | high |
| Response-time limits 0.1 s, 1 s, 10 s | [NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/) | high |
| Doherty threshold 400 ms (1982) | [Laws of UX](https://lawsofux.com/doherty-threshold/) | medium (secondary; IBM paper not read) |
| KLM operators: P 1.1 s, H 0.4 s, M 1.35 s, B 0.1 s, K 0.08 to 1.20 s; model RMS error 21% | [Wikipedia KLM](https://en.wikipedia.org/wiki/Keystroke-level_model) | medium (secondary; Card, Moran, Newell 1980 not read) |
| Fitts (Shannon): MT = a + b log2(D/W + 1); one-dimensional, stationary targets; 2-D width is ambiguous | [Wikipedia Fitts](https://en.wikipedia.org/wiki/Fitts%27s_law) | medium |
| Hick-Hyman: T = b log2(n+1); fails for familiar ordered lists and practised responses | [Wikipedia Hick](https://en.wikipedia.org/wiki/Hick%27s_law) | medium |
| Mermaid defaults: maxTextSize 50000, maxEdges 500, securityLevel strict | [Mermaid config](https://mermaid.js.org/config/schema-docs/config.html) | medium (schema page, summarised) |
| Mermaid v12 targets ES2024, Safari 17.4 or later; npm build needs Node 22.12+ | [usage](https://mermaid.js.org/config/usage.html) | medium |
| Mermaid Chart visual editor supports 7 diagram types | [docs](https://mermaid.ai/docs/build-and-edit/use-the-visual-editor) | high |
| Lucidchart optimised for Mermaid 11.14, 8 diagram types | search snippet only; help page 403 | UNVERIFIED |
| Miro: 100,000 object hard limit, slowdown from 1,000, 5,000 recommended | search snippet only; help page 403 | UNVERIFIED |
| FigJam imported table limit 500 cells | [guide](https://help.figma.com/hc/en-us/articles/1500004362321-Guide-to-FigJam) | high |
| Miro offers over 2,000 shapes | [Miro](https://miro.com/diagramming/) | medium (vendor claim) |
| Cytoscape.js 3.34.3, MIT, 70+ extensions | [site](https://js.cytoscape.org/) | high |
| elkjs 0.12.0, EPL-2.0 with GPL-3.0 secondary; release year not shown on page | [releases](https://github.com/kieler/elkjs/releases) | medium |
| StarUML 7.1.1; yEd 3.25.1 | [StarUML](https://staruml.io/), [yWorks](https://www.yworks.com/products/yed) | high |
| DTCG specification first stable 2025.10, but the Color module 2025.10 page says "do not implement" | [DTCG](https://www.designtokens.org/), [colour](https://www.designtokens.org/tr/drafts/color/) | high |
| PREDICTION (KLM, this dossier): adding a named node by drag from a palette is about 6.55 s (M 1.35 + P 1.1 + B 0.1 + P 1.1 + B 0.1 + H 0.4 + typing 12 chars at 0.2 s); by command palette about 4.35 s (M 1.35 + 2 keys 0.4 + typing 2.4 + Enter 0.2) | computed from KLM values above; K = 0.2 s is my assumption inside the cited range | low; estimate for a skilled user, error about 21% |
| PREDICTION (Fitts, this dossier): shrinking a 24 px handle to 12 px at D = 400 px raises the index of difficulty from 4.14 to 5.10 bits, about +0.1 s if b = 0.1 s per bit (assumed) | Shannon formula above | low; b is device- and user-specific |

Validity limits for the two predictions: KLM applies to error-free expert routine tasks and ignores learning, error recovery and mental load beyond M; Fitts applies to stationary, aimed pointing and says nothing about discoverability. If the node name is chosen from the ubiquitous-language tree instead of typed, typing drops out of both routes and the Hick-Hyman cost of choosing among n terms replaces it, which holds only if the list is ordered and familiar; that cuts against Hick's premise, so it needs measurement, not a prediction.

## 5. Implications for EIJA

1. **Picture is a projection.** Render UML from the semantic model; a drag or connect gesture emits a typed operation to the kernel (GLSP request shape) and the picture redraws from the accepted model. No code path edits the SVG and then infers meaning.
2. **Persist layout separately, keyed by stable ids.** Regeneration re-applies positions; only new elements are auto-placed by elkjs. This fixes the draw.io Mermaid loss case and honours secondary notation.
3. **Explicit Tidy command.** Offer one undoable command (FigJam, yEd precedent) that re-runs elkjs for the selection or the view; never re-layout implicitly.
4. **Keyboard parity.** Tab and Shift+Tab in reading order plus a live-region announcement (tldraw), Alt+Tab to parent (draw.io), and a command palette to add or connect elements by ubiquitous-language term. Every drag has a non-drag path (WCAG 2.5.7). Hit targets at least 24 by 24 CSS px (WCAG 2.5.8).
5. **Ripple as perspective, not as another diagram.** One model, several lenses (states, journeys, tests, personas, requirements), switched like Ilograph perspectives; a resource finder that searches by name across all of them.
6. **Proposals look provisional.** AI-proposed elements use dashed outline plus a text badge (not colour alone, WCAG 1.4.1), accepted elements solid. The AI never has an accept control.
7. **Ship generated text views, not editable text.** Mermaid and PlantUML output are read-only exports (as in PlantUML's one-way model); avoids the round-trip loss seen in Mermaid Chart and draw.io.
8. **Choose libraries by ADR-013, then CSP.** Vanilla SVG plus elkjs; log both in the OSS register; add an automated CSP smoke test (SVG attributes, worker load) before any library is accepted. Reject React-based SDKs and JointJS for licence or build reasons.
9. **Budgets.** Hypothesis: drag feedback within 100 ms and re-layout within 400 ms for the excursion model; measure elkjs on the real model before promising more; show a visible cap message rather than degrading silently (Mermaid precedent).
10. **Study protocol (no results claimed).** Within-subject comparison of the current tab UI against the proposed canvas on three tasks (add a state, review an AI change by meaning, trace a requirement to a test), measuring time, errors and a Cognitive Dimensions questionnaire; keyboard-only and screen-reader cohorts included; the KLM and Fitts predictions above are the pre-registered hypotheses.

## 6. Gaps and unverified items

- Sparx Enterprise Architect: no page readable; behaviour, version and licence unverified. StarUML is the only desktop repository tool verified.
- Lucid and Miro help pages returned 403; Lucid Mermaid version, Miro object limits and Miro keyboard behaviour are UNVERIFIED.
- Visio for the web: only the help hub was read; canvas interaction is not evaluated.
- Whimsical: interaction detail and keyboard claims not verified.
- Mermaid and PlantUML output under `style-src 'self'`: UNVERIFIED; test with the real CSP. Same for SVG presentation attributes and same-origin worker loading.
- Eraser drag-to-code write-back, Structurizr layout persistence and vNext details: UNVERIFIED.
- Sirius Web and GLSP claims are vendor documentation; no editor was run.
- Green and Petre 1996 and Card, Moran, Newell 1980 were not opened; definitions and operator times come from secondary sources. Doherty and Thadani 1982 likewise.
- No published performance benchmark for draw.io, Excalidraw or tldraw was found; no cross-tool performance ranking is claimed. tldraw's latest release page showed an implausible date and is not used.
- WebSearch snippets reported some details (Sparx 17.1, Lucid Mermaid 11.14, Miro 100,000 objects); none is used as evidence.
- DTCG Color module is a preview draft that says not to implement; the tokens lane must decide whether to follow it or the older string syntax.

## 7. URLs opened (access date 2026-09-29)

draw.io: drawio.com/docs/manual/connectors/, /docs/reference/shortcuts/, /docs/reference/shortcuts/modifier-shortcuts-in-diagrams/, /docs/reference/shortcuts/shortcut-select/, /blog/new-keyboard-shortcuts/, /blog/mermaid-diagrams; github.com/jgraph/drawio.
Structurizr: docs.structurizr.com/, /as-code, /dsl, /cloud; structurizr.com/; github.com/structurizr/structurizr.
Excalidraw and tldraw: docs.excalidraw.com/docs, /docs/@excalidraw/excalidraw/installation, /docs/@excalidraw/excalidraw/api/props/excalidraw-api; github.com/excalidraw/excalidraw, github.com/excalidraw/mermaid-to-excalidraw; tldraw.dev/community/license, tldraw.dev/sdk-features/accessibility; github.com/tldraw/tldraw, /releases.
Libraries: github.com/maxGraph/maxGraph; github.com/kieler/elkjs, /releases, raw LICENSE.md; js.cytoscape.org; github.com/cytoscape/cytoscape.js; github.com/clientIO/joint, raw LICENSE; github.com/dagrejs/dagre.
Mermaid and PlantUML: mermaid.js.org/intro/, /config/usage.html, /config/schema-docs/config.html; mermaid.live; mermaid.ai/docs/build-and-edit/use-the-visual-editor; github.com/mermaid-js/mermaid (LICENSE, issues search); plantuml.com; github.com/plantuml/plantuml.
Others: staruml.io; yworks.com/products/yed; whimsical.com; ilograph.com/features.html, /docs/spec/; docs.eraser.io/diagram-as-code, /quickstart; eclipse.dev/glsp/, github.com/eclipse-glsp/glsp; eclipse.dev/sirius/sirius-web.html; help.figma.com (Guide to FigJam, FigJam AI); support.microsoft.com Visio for the web help; miro.com/diagramming/; lucid.co/lucidchart/; community.lucid.co idea 12112.
Standards and HCI: w3.org/TR/WCAG22/; w3.org/WAI/ARIA/apg/patterns/treegrid/; developer.mozilla.org CSP style-src; designtokens.org, /tr/drafts/color/; nngroup.com response-times article; lawsofux.com/doherty-threshold/; cl.cam.ac.uk/~afb21/CognitiveDimensions/ (PDF unreadable); Wikipedia pages on Cognitive dimensions, KLM, Fitts, Hick.

Not opened (403, 404 or blocked): sparxsystems.com (three pages), help.miro.com, help.lucid.co, patreon.com Structurizr post, web.archive.org, npmjs.com/elkjs, tldraw.dev/docs/accessibility (404), drawio.com accessibility and FAQ pages (404), yworks features page (404).
