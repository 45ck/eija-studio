# PlayIDE

PlayIDE is EIJA Studio's visual IDE: you see the model as a UML diagram, then build it and use the real app beside the diagram. The repository, Python package and `eija` command keep their names; PlayIDE is the product name in the interface. See [ADR-0151](adr/0151-playide-canvas-and-build-and-run.md) for the design.

```console
eija serve --pack packs/excursion --open
```

The server prints two private links. Open the PlayIDE one (it ends in `/play#…`). To look at a change case's candidate model, add `?case=<case id>` before the `#`.

## Start your own system

PlayIDE is not limited to the packs that ship with EIJA ([ADR-0185](adr/0185-start-open-and-save-your-own-system.md)). Press **Systems** in the title bar.

- **New system** starts one in a few lines. Give it a name, then choose a starting point:
  - **Blank, from a sketch.** Name the record class (for example `Ticket`) and type the state machine as the diagram labels it, one transition per line:

    ```text
    Open -> Triaged : Triage [Agent]
    Triaged -> Resolved : Resolve [Agent]
    Triaged -> Escalated : Escalate [Agent]
    Escalated -> Resolved : Fix [Engineer]
    actions: Reopen
    ```

    The first line's source is the initial state. An `actions:` or `roles:` line declares ones you will draw later; a drawn transition can only use a declared action, and each action labels one transition.
  - **A template.** One of the shipped packs (Library loan, School excursion approval, EIJA review reference journey), copied with your name and a new id.

  The kernel's pack check runs as you type and says what will be created, or what is wrong, line by line. **Create and open** saves it and opens it. A new system gets one audit effect per action and one user per role (and a revoked one, so a simulation meets a refusal). It has no laws until you add them.
- **Open** lists the systems you opened recently and the others in your systems home. The one the server started with stays one click away.
- **Save** (Ctrl+S) keeps your work in progress on this system: the plan's steps, which ones are ticked, and your screens if you edited them. "Unsaved changes" shows beside it until you save. When you open the system again, the plan comes back and the server checks every step again, like any plan. Saving never applies anything to the model in force; that still happens in the review workbench.

Systems live in `~/PlayIDE`, one folder each, with the system's own workspace (`.eija/`) inside it. Start the server with `--systems <folder>`, or set `EIJA_SYSTEMS`, to keep them somewhere else. The same can be done from the command line:

```console
eija new "Support desk" --sketch desk.txt --record Ticket
eija new "Field trips" --from excursion
```

Each prints the `eija serve` line that opens it.

## What you can do now

- **Find your way around.** PlayIDE is laid out like the IDEs you know ([ADR-0173](adr/0173-playide-workbench-shell.md)). The model outline and the inspector are on the left, the diagrams are tabs in the middle, and the chat is on the right. Run, Simulation and Running app open in a panel under the diagrams when they have something to show, and a status bar runs along the bottom. Ctrl+K searches every command and element. Ctrl+B, Ctrl+Alt+P and Ctrl+Alt+C hide or show the left side, the panel and the chat. Drag the edges to resize them; PlayIDE remembers the layout in your browser.
- **Read the model as a UML state machine.** States, the initial pseudostate and transitions labelled `action [role]`, laid out automatically. Pan, zoom, fit, and drag states to rearrange them. The arrangement is not saved yet.
- **Inspect.** Select a state or transition on the canvas or in the outline to see who may take it, its guards, the effects it must write and the effects it must never write.
- **Build & run.** One click builds the app with [`eija build`](build-an-app.md), checks it against the kernel and shows the score, for example `240/240 cases match the kernel`. Only an app that passes is started. It opens beside the diagram, where you can act as each fixture user and watch the model's rules being enforced.

- **Class diagram.** The second tab shows the pack's data model in UML class notation: classes with typed attributes, the «record» class that moves through the state machine, and associations with role names, multiplicities and aggregation or composition diamonds. Select a class to see its attributes and associations. The data model is `data.json` beside the pack's `pack.json` ([ADR-0153](adr/0153-data-models-as-uml-class-diagrams.md)). The record class's attributes become the built app's form, and the server checks every value.
- **Use cases.** The third tab draws the workflow as a UML use case diagram: one actor per role, one use case per action plus "Create <record>", inside the system boundary, with each role associated with the use cases it may perform. It is a view of the same model, not a second one. Double-click a use case to design its screen.
- **Design screens.** The **Screens** tab has one screen per use case, bound to the record class's attributes ([ADR-0154](adr/0154-use-cases-and-screens-designed-against-the-model.md)). Drag an attribute from the palette onto the screen (or press Add), drag rows to reorder them, and rename the title, labels and button. The design check runs on every edit: a create screen that leaves out a required attribute, or a screen showing an attribute the record does not have, is flagged with its code, and no app is built from it. **Build & run** builds and runs the app with your screens: the create form follows the create screen, and choosing an action in the app opens that action's screen. **Download screens.json** saves the design; put it beside the pack's `pack.json` to keep it.
- **Chat (plan mode).** The chat on the right proposes a change as numbered steps in the model's own edit vocabulary ([ADR-0156](adr/0156-chat-plan-mode-proposes-typed-steps.md)). Tick or untick each step, then **Preview on the diagram**: every tab redraws from the candidate model, with what changed highlighted, and Build & run and Simulate run on it. The policy checks the accepted steps exactly as it checks an owner's edit, so a refused step says why. Nothing is saved; **Back to the model** returns to it. A plan that matches a change the pack models can become a change case. The default proposer is an offline phrase reader, not an AI, and says so: use exact names, as in the example the chat shows for the open model.
- **Draw.** The state machine tab has a UML palette: drag State, Transition or Initial onto the diagram (dropping on a state starts there), or press it, and finish in the inspector. A selected state or transition offers renaming, moving an end, changing who may take it, and removing it; Delete removes the selection. Drawn changes join the plan as your steps, labelled You beside the AI's, and are checked and previewed the same way ([ADR-0157](adr/0157-drawn-edits-and-checks-ring.md)). Nothing is saved.
- **Ripple.** A change to the state machine changes the other diagrams too, and PlayIDE shows how ([ADR-0158](adr/0158-ripple-across-diagrams-with-checked-follow-ons.md)). Each tab gets a badge with the number of effects on it, amber for a warning and red for a problem. The plan's card lists them by diagram. Some examples:
  - a new state is a new literal of the record's state enumeration on the class diagram;
  - a new action is a new use case and gets a screen;
  - a removed action strands its screen, so the app cannot be built;
  - a state nothing leads into is unreachable.

  Click an effect to open that diagram at that element. Added and changed elements are marked on the preview, and removed ones in red on the model. For each warning or problem, the AI proposes a follow-on edit, such as removing the stranded screen or adding a transition into the new state. The server checks each one again, through the policy or the screen design check, before you can **Add** it. The default proposer is an offline rule set, not a live model.
- **See a change.** Whenever a plan or a change case differs from the model in force, a **Changes** button with a count appears on the state machine tab ([ADR-0176](adr/0176-how-a-uml-change-looks.md)). It draws both models on one layout:
  - **Changes** shows added elements in green, changed ones in amber, a moved arrow in amber with its old route dashed, and removed ones kept as faded, struck-through ghosts. Unchanged elements fade back as context.
  - **Compare** opens **Before** and **After**, which show one side each, and an onion-skin slider that fades between them. No state moves when you switch.

  Changes stays on while you flip tabs. The use case diagram shows added and removed use cases and actors, and a moved association with its old line as a ghost. The class diagram shows the record's state enumeration gaining and losing literals.

  One line above the diagram counts the change ("4 changes: 2 added, 1 moved, 1 removed"). The inspector lists each change in a sentence. `[` and `]` step through it, and a change with changed fields opens its before and after under its line. Previewing a plan also keeps every state in place now, and a removed state leaves its gap.
- **Checks.** The ring in the toolbar has five parts, each a real check on the model you are looking at:
  - every AI step looked at;
  - the screens' design check;
  - a conformance pass;
  - the diagrams agree (no ripple problem);
  - a simulation.

  A change empties the build and simulation parts until you run them again. Points come only from checking:
  - looking at an AI step (+1);
  - unticking one the policy catches (+3);
  - opening the ripple on another diagram (+1);
  - building (+3) or simulating (+2) an AI change.

  Making changes earns nothing.
- **Run bar.** Run, Pause, Step, Stop and Restart, as in Visual Studio, with the same keys: F5, F6, F10, Shift+F5 and Ctrl+Shift+F5 ([ADR-0160](adr/0160-run-bar-with-breakpoints-over-a-seeded-run.md)). Run sends seeded simulated users through the kernel one try at a time, and the state machine fills in as it goes, with the current step marked in amber (red when the kernel refused it). Select a state or transition and press F9, or **Add breakpoint** in the inspector, to stop the run when a record enters that state or someone tries that transition; it shows as a red dot. **Break when the kernel refuses** stops at every refused try. When paused, the Run panel shows who tried what and the kernel's answer, the state of every record at that step and the steps so far; Continue goes on to the next stop. Stop ends the run and stops the running app. The same seed always gives the same run, so a pause is exactly reproducible.
- **Review.** The **Review** tab reviews the change shown (a previewed plan, or a change case's candidate) against the model in force, instead of a pull request ([ADR-0175](adr/0175-review-a-change-as-a-uml-diff-you-can-run.md)). Both models are drawn on one diagram: added in green, removed dashed in red, changed in amber. Each change is a card, ranked by fixed risk rules (removing a path or changing who may act is high), including knock-on effects nobody edited, such as a state that can no longer be reached. The kernel runs every fixture actor on every action from every state on both models, and the attempts that turn out differently are the behaviour diff. For each change, **Show me** selects it on the diagram and **Predict, then run** asks what the kernel will do before showing it. **Looks right** and **Needs a change** unlock only after both. **Finish review** writes a review note bound to both models' hashes. A review never approves or applies: that stays with the owner in the review workbench. Open it from a plan's **Review it** or the preview banner. See [Review a change in PlayIDE](demos/2026-10-08-PLAYIDE-REVIEW.md).
- **Tour.** A recorded walk through all of the above: [PlayIDE tour](demos/2026-10-08-PLAYIDE-TOUR.md), and the ripple on its own: [PlayIDE ripple](demos/2026-10-08-PLAYIDE-RIPPLE.md).
- **Components.** The fifth tab is the UML component diagram of the app the model builds, read from the generated files ([ADR-0155](adr/0155-component-diagrams-read-from-the-generated-code.md)). Each line is in the code: an import (the ball lists the names imported), a route the page calls, or a file a module reads. It shows that the app's service asks the EIJA kernel for every decision. Select a component to see its files and what it uses and provides. After Build & run, the conformance score and the running server appear on it.
- **Simulate.** Simulated users, the pack's fixture actors, try 500 seeded actions, and the kernel decides every one. The diagram lights up: thicker lines carried more successful actions, dashed amber lines never succeeded, and darker states hold more records now. **Worth a look** lists the transitions that never succeeded, the states nobody reached or got stuck in, and the most-refused actions; click one to select it. **Replay** steps through the run log on the diagram. The same seed always gives the same run. See [ADR-0152](adr/0152-simulate-seeded-users-through-the-kernel.md).

- **Laws.** The **Laws** tab lists what the model must never do, whatever is drawn: the pack's laws, in plain language. Each is proved over every run the kernel allows, by every kind of actor, on the model on screen (a previewed plan included). A law is shown as holding, broken (with the shortest run that breaks it, which **Show this run** paints on the state machine), vacuous (nothing reaches what it is about), not in force, or needing review evidence. **Show on diagram** highlights what a law is about ([ADR-0166](adr/0166-laws-proved-over-every-run-for-any-pack.md)).
- **What the diagrams mean when they run.** [Executable UML on the EIJA engine](architecture/executable-uml.md) says, element by element, which views the kernel runs, which are checked designs and which are derived. `eija scxml` exports the state machine as a W3C SCXML statechart, and an independent SCXML engine agrees with the kernel on every conformance case ([ADR-0165](adr/0165-executable-uml-on-the-eija-kernel.md)).

## Limits

- Simulated users act at random within their roles. A run shows where the model lets people through and where it blocks them. It is not a measurement of real people, time or load.
- Drawn changes and plans are previewed, built and simulated, and **Save** keeps them as a draft on the system, but they are never applied (issue #89). Change the saved model in the review workbench. The screen designer's design is kept in the draft, not in the pack: download `screens.json` and commit it to make it the system's own.
- A system's actions and roles are fixed when it is created. Declare spare ones in the sketch; editing them in PlayIDE is follow-up work. A draft holds at most 12 steps.
- Screens choose which attributes a use case shows, in what order and under what label. They never change who may act or what an action does; the kernel decides that.
- One built app runs at a time, on a free loopback port. It stops when you build another model or stop the server.
- Everything in [Build an app from the model](build-an-app.md#why-you-can-trust-it-and-how-far) about how far the conformance check goes applies here too.

## Coming next

A live AI proposer (it needs the owner's permission for network use and spend), saving a plan as a change case (issue #89), and editing the data model in PlayIDE so that data changes ripple too.
