# PlayIDE

PlayIDE is EIJA Studio's visual IDE: you see the model as a UML diagram, then build it and use the real app beside the diagram. The repository, Python package and `eija` command keep their names; PlayIDE is the product name in the interface. See [ADR-0151](adr/0151-playide-canvas-and-build-and-run.md) for the design.

```console
eija serve --pack packs/excursion --open
```

The server prints two private links. Open the PlayIDE one (it ends in `/play#…`). To look at a change case's candidate model, add `?case=<case id>` before the `#`.

## What you can do now

- **Read the model as a UML state machine.** States, the initial pseudostate and transitions labelled `action [role]`, laid out automatically. Pan, zoom, fit, and drag states to rearrange them. The arrangement is not saved yet.
- **Inspect.** Select a state or transition on the canvas or in the outline to see who may take it, its guards, the effects it must write and the effects it must never write.
- **Build & run.** One click builds the app with [`eija build`](build-an-app.md), checks it against the kernel and shows the score, for example `240/240 cases match the kernel`. Only an app that passes is started. It opens beside the diagram, where you can act as each fixture user and watch the model's rules being enforced.

## Limits

- The canvas does not edit the model yet. Change the model in the review workbench, then build again.
- One built app runs at a time, on a free loopback port. It stops when you build another model or stop the server.
- Everything in [Build an app from the model](build-an-app.md#why-you-can-trust-it-and-how-far) about how far the conformance check goes applies here too.

## Coming next

Simulated users running through the app with traffic and hotspot overlays, class diagrams for data, use case diagrams with a screen designer, component diagrams, an AI chat sidebar with plan mode (the AI only proposes), drag-and-drop UML palettes, and a health ring tied to real checks.
