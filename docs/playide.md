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

- **Class diagram.** The second tab shows the pack's data model in UML class notation: classes with typed attributes, the «record» class that moves through the state machine, and associations with role names, multiplicities and aggregation or composition diamonds. Select a class to see its attributes and associations. The data model is `data.json` beside the pack's `pack.json` ([ADR-0153](adr/0153-data-models-as-uml-class-diagrams.md)). The record class's attributes become the built app's form, and the server checks every value.
- **Simulate.** Simulated users, the pack's fixture actors, try 500 seeded actions, and the kernel decides every one. The diagram lights up: thicker lines carried more successful actions, dashed amber lines never succeeded, and darker states hold more records now. **Worth a look** lists the transitions that never succeeded, the states nobody reached or got stuck in, and the most-refused actions; click one to select it. **Replay** steps through the run log on the diagram. The same seed always gives the same run. See [ADR-0152](adr/0152-simulate-seeded-users-through-the-kernel.md).

## Limits

- Simulated users act at random within their roles. A run shows where the model lets people through and where it blocks them. It is not a measurement of real people, time or load.
- The canvas does not edit the model yet. Change the model in the review workbench, then build again.
- One built app runs at a time, on a free loopback port. It stops when you build another model or stop the server.
- Everything in [Build an app from the model](build-an-app.md#why-you-can-trust-it-and-how-far) about how far the conformance check goes applies here too.

## Coming next

Use case diagrams with a screen designer, component diagrams, an AI chat sidebar with plan mode (the AI only proposes), drag-and-drop UML palettes, and a health ring tied to real checks.
