# Dagre layout adapter

EIJA uses the official **@dagrejs/dagre 1.1.8** browser bundle for state placement,
edge routing and edge-label placement. The custom three-column placement and
quadratic routing have been removed. This implements the OSS layout choice in
[WBS 2.2](WBS.md); it does not introduce a second semantic model.

## Ownership of meaning and geometry

`canvas.js` constructs a fresh Graphlib graph from the current server model on
each render. That graph contains only opaque node/edge identifiers, dimensions
and label dimensions. The library supplies positions and routed points. It never
receives a reference to a Workflow, transaction, role, law, receipt or API client.
Domain labels remain text in EIJA's SVG renderer. Opaque graph identifiers also
prevent unusual domain labels from colliding with Graphlib's object keys.

The server's saved layout positions retain their existing coordinate convention.
The adapter translates the library's routed points between the two endpoint
offsets when saved positions exist. A saved placement can produce crossings or
overlap; this adapter does not infer a new layout or change the owner's saved
positions. Automatic geometry is not persisted. Dragging a transition endpoint
still uses the server's affordance transaction, dry-run result and versioned edit.

If the library is unavailable, the canvas states that layout is unavailable and
the existing transition editor remains usable. There is no custom fallback layout
engine and no automatic semantic repair.

## Pin, provenance and licence

The [vendor record](../../src/eija_studio/resources/web/vendor/dagre.VENDOR.json)
contains the official npm tarball URL, registry SHA-512 integrity, vendored-file
SHA-256 hashes and dependency licence attribution. The bundle is **97,200 bytes**,
copied unmodified from `package/dist/dagre.min.js`. It includes Graphlib 2.2.4.
Both packages are MIT licensed; both upstream licence files ship with the bundle.
No npm install, build step, CDN request or project execution is needed at runtime.

Official sources checked on 2026-10-02:

- [Dagre repository](https://github.com/dagrejs/dagre)
- [Pinned Dagre package metadata](https://registry.npmjs.org/@dagrejs/dagre/1.1.8)
- [Bundled Graphlib package metadata](https://registry.npmjs.org/@dagrejs/graphlib/2.2.4)

The current npm release **3.1.1** was also downloaded and evaluated. Its smaller
48,956-byte browser bundle failed the self-loop endpoint check used here. For a
two-node left-to-right graph with 190 by 76 nodes, a loop on the second node
returned endpoints `(340, 239)` and `(435, 201)` while that node occupied
`x=340..530, y=75..151`. Neither endpoint touched its node. Version 1.1.8 returned
endpoints on `y=151`, the node boundary, for the same fixture. This local regression
is the reason for the older pin; it is not a general quality claim about either
release. The regression test must pass before a future upgrade.

## Reproduction and evidence limits

Run `node --test tests/web/workbench.test.cjs`, or the existing pytest wrapper
`tests/test_workbench_surface.py`. The tests use the actual vendored browser bundle
and cover deterministic geometry, reordered inputs, cycles, parallel edges,
self-loops, saved placement, arbitrary domain labels and immutable semantic input.
They also retain the original accepted/refused/stale typed-edit checks.

The bundle's hashes are checked. A Node VM runs the bundle and a layout with string
and WebAssembly code generation disabled and network/DOM access traps installed.
The vendored bundle has no `eval(`, `Function(`, fetch, XMLHttpRequest or DOM calls
in the inspected runtime. This is useful compatibility evidence, **not a browser
CSP or accessibility result**. Browser validation remains a separate check under
the Studio's unchanged `script-src 'self'` policy. The HTTP adapter must allow
only the additional `/assets/vendor/dagre.min.js` asset; no CSP relaxation is
required by this integration.

Source fixture review remains outstanding when implementation bytes differ from
the owner-stamped fixture. This dependency integration neither re-stamps that
fixture nor authorizes application of a change case.
