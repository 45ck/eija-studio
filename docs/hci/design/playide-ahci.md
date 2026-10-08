# PlayIDE: UML, HCI and agentic HCI

How working with UML in PlayIDE should feel for a person, how the person and the AI share the work, and which parts of that the product already does. Decision records: [ADR-0170](../../adr/0170-playide-assist-ask-complete-palette-review.md) (the assist layer), [ADR-0171](../../adr/0171-permissions-matrix-and-reachability-questions.md) (who can do what) and [ADR-0172](../../adr/0172-review-view-for-reading-the-model.md) (the review view). Earlier aspect decisions this builds on: [HCI-ADR-0064](../../adr/0064-hci-ai-interaction.md) (proposal cards and the delegation fence), [ADR-0156](../../adr/0156-chat-plan-mode-proposes-typed-steps.md) (plan mode) and [ADR-0157](../../adr/0157-drawn-edits-and-checks-ring.md) (drawing and the checks ring).

**Status of the claims here.** This is a design argument from published research and from the product as built. Nobody has been measured using PlayIDE. Where a principle cites a study, the study is about AI-assisted decisions in general, not about this product. A usability study is still owed (see the last section).

## 1. Who it is for and what they are doing

The users are software engineers who already read and write UML: state machines, class diagrams, use cases, components and sequences. They do not need notation taught. What they lack in today's tools is a model they can **trust**: one that runs, that the code is checked against, and that an AI can change without the engineer losing track of what changed.

So the job is: *when I, or an AI working for me, change how the system behaves, I want to see the change on the diagrams I already think in, try it, and know it is still correct, without reading a pull request diff line by line.*

## 2. One model, many views, all executable

Every PlayIDE tab is a view of **one** model (ADR-0093: one source per fact). None of them is a picture drawn beside the code.

| UML view | What it is in the built app | Where it comes from |
|---|---|---|
| State machine | The rules: which action, by which role, moves a record from which state to which | The workflow model; the kernel executes it |
| Class diagram | The data: the record's attributes become the app's form and validation | The pack's data model |
| Use cases | Who may do what: each role's actions, and the screens they get | Derived from the workflow's transitions |
| Screens | The UI: one screen per use case, checked against the record class | The screen designer, bound to use cases |
| Components | The code structure of the generated app | Read from the generated files, not drawn |
| Permissions | Who may take which action from which state, and who the kernel actually lets through | Projected from the transitions; every cell tried in the kernel |
| Sequence (Simulate) | What seeded users actually did, step by step | Traces from the kernel during Simulate |

This is what "executable UML" means here: the state machine is not a specification someone later implements. The kernel runs it, `eija build` generates an app from it, and every build is checked case by case against the kernel before it starts (ADR-0150, ADR-0151). Executable UML and MDA stalled on expressiveness. PlayIDE's answer is to support a bounded set of semantics explicitly and to refuse what it cannot run, rather than to draw what it cannot run.

## 3. The interaction loop: design, check, run

Norman's two gulfs (classic HCI, not re-verified this session) frame the loop:

* **Gulf of execution**: how hard it is to make the system do what you mean. PlayIDE narrows it with direct manipulation on UML notation (drag a State, drop a Transition on the state it leaves) and with a chat that turns a request into typed steps.
* **Gulf of evaluation**: how hard it is to tell what happened. Here a diagram alone is not enough, because a diagram can look right and be wrong. PlayIDE closes this gulf with *executed* evidence: the policy's verdict on every step, conformance cases from Build & run, and refusals from Simulate, all shown on the same diagram.

The loop a person runs is short and repeated: **change** (draw or ask) → **see** (preview on every view) → **check** (policy verdict, show each AI step) → **run** (Build & run, Simulate) → **keep or go back**. Nothing in that loop saves anything. Making a change real goes through a change case and the owner's review.

## 4. Agentic HCI: who does what

When an AI is in the loop, the interface has to make the division of labour obvious and keep it fixed.

| Who | May | May not |
|---|---|---|
| AI | Propose a plan of typed steps, each with a reason | Choose meaning, save, approve, apply, change protected policy |
| You | Draw, ask, accept or reject each step, preview, build, simulate | Bypass the policy (the server re-checks every step) |
| Kernel and policy | Decide whether a step is legal and what the model means | Be overruled by the page or the AI |
| Owner | Approve and apply a change case in the review workbench | (the only route to a real change) |

The principles below follow from that table and from the research.

**A1. The AI proposes; it never acts.** Its output is a list of typed transactions in the same vocabulary a person's drawing produces, re-parsed and re-checked on the server (ADR-0156). This is the delegation fence of HCI-ADR-0064, and the MCP specification's "human in the loop with the ability to deny" (cited there).

**A2. Show the fence all the time, not in a tooltip.** The chat says in one line who proposes, who checks and who approves. People calibrate trust to what they understand a system can do (Lee and See 2004, cited in HCI-ADR-0064); a fence they cannot see does not inform that.

**A3. Ground the request in what the person is looking at.** In conversation, people build common ground before they act on what was said (Clark and Brennan's grounding, classic, not re-verified). An AI asked "rename it" from a blank box has none. PlayIDE asks *about the selection*: selecting a state or transition offers the requests that make sense for it, with its exact name already filled in. This is also the missing "ask AI at a selected element" task (T13) that HCI-ADR-0064 records the earlier UI could not do.

**A4. Make the system's abilities visible.** The offline proposer reads a bounded grammar with exact names. Hiding that and letting people guess violates Amershi et al.'s first two guidelines (make clear what the system can do, and how well; cited in HCI-ADR-0064). PlayIDE shows the phrases it reads as buttons, leaves blanks (‹state›, ‹role›) to fill, and completes exact model names while typing. A request with an unfilled blank is stopped before it is sent, with the blank named.

**A5. Make checking cheaper than accepting.** Explanations raised acceptance of AI recommendations whether or not they were right (Bansal et al. 2021), and automation bias is not fixed by training or instructions (Parasuraman and Manzey 2010); both are cited in HCI-ADR-0064. The remedy is not more text but less effort to verify: each AI step has **Show me** on the diagram, the policy's verdict on every step, and a keyboard path through the plan (J/K to move, S to show, Space to accept or reject, P to preview). Rejecting is as cheap as accepting.

**A6. Reward checking, never output.** Points come from looking at AI steps, catching a step the policy refuses, and building or simulating the AI's change; never from making steps (ADR-0157). Cognitive forcing functions cut overreliance but were rated least favourably (Buçinca et al. 2021, cited in HCI-ADR-0064), so PlayIDE rewards the check rather than forcing it.

**A7. Cheap to be wrong, easy to stop.** Nothing persists from a plan. **Back to the model** undoes a preview at once; a newer plan retires the old one. Horvitz's mixed-initiative principles ask for efficient termination and for minimising the cost of poor guesses (cited in HCI-ADR-0064).

**A8. One place for every command.** Engineers move between keyboard and mouse. A command palette (Ctrl+K, ⌘K on a Mac) reaches every command and every model element by typing, including "Ask the AI about Overdue". It only presses the page's own buttons, so it can do nothing a click could not.

**A9. Keyboard shortcuts must not ambush.** Single-key shortcuts act only while focus is inside the plan being reviewed (WCAG 2.1.4, focus-only). Space is the checkbox's own toggle, so nothing ticks a step on the person's behalf.

**A10. Let people ask the model questions, not only look at it.** A diagram shows structure; an engineer reviewing a change wants to know what it allows. The questions reviewers and auditors ask first are about access: who can do what, and can anything happen without the right person. PlayIDE answers "can a record reach Overdue without a Clerk?" with a proof over the model (No), a path the kernel committed step by step (Yes), or Not shown when the fixture actors could not take the path. A previewed AI plan gets the same question asked again, beside the permissions it adds and removes. This is the review-by-meaning idea of HCI-ADR-0063 applied to access rules, where AI-written apps most often go wrong.

## 5. What PlayIDE does today

| Principle | In the product | Where |
|---|---|---|
| A1 | Plan mode: typed steps, server re-check, preview on every view | ADR-0156 |
| A2 | "AI proposes steps · You check, preview and try them · Owner approves and applies in the review workbench" under the chat heading | ADR-0170 |
| A3 | "About Overdue: Add a state after, Rename, Add a transition from here, Start records here, Remove" when Overdue is selected; "Ask the AI about …" in the palette | ADR-0170 |
| A4 | Phrase buttons with ‹blanks›; Tab moves to the next blank; exact-name completion (states, actions, roles, and states the request itself adds); a request with a blank is held | ADR-0170 |
| A5 | Show me, per-step verdicts, review keys J/K, S, Space, P | ADR-0157, ADR-0170 |
| A6 | Checks ring and points for checking only | ADR-0157 |
| A7 | Nothing saved; Back to the model; retired plans | ADR-0156 |
| A8 | Command palette, Ctrl+K / ⌘K, native `<dialog>` | ADR-0170 |
| A9 | Focus-only review keys | ADR-0170 |
| A10 | Permissions tab: role by state matrix tried in the kernel, reachability questions, a plan's permission changes flagged | ADR-0171 |

## 6. Not done yet, and what would change it

* **No human has used this yet.** The principles are argued, not measured. The next step is a small task-based study with UML-literate engineers: plant a confidently wrong AI step in a plan and measure how often it is caught, with and without the review keys and Show me. The Wharton result cited in the positioning research (rewards plus instant feedback doubled how often people caught a wrong AI) is the hypothesis to test, not a result about PlayIDE.
* **The proposer is a fixture.** A live model behind the same `PlanProposer` port needs the owner's permission for network and spend. When it arrives, A3 and A4 matter more, not less: the selection becomes the context sent with the request.
* **The ripple across diagrams** (a change on one view and the follow-on changes it needs on the others) is being built in a separate thread; it belongs in the same plan card, as AI-proposed follow-on steps the person checks like any other.
* **Run controls** landed as the run bar (ADR-0160); the palette lists Run, Pause, Step, Stop and Restart whenever their buttons are usable. **Model-level review** (reviewing a change case in PlayIDE instead of a pull request) is a separate thread; the palette will reach its controls the same way, by pressing the page's buttons.
* **Code outside the model.** When PlayIDE connects a repository, some code is generated from the model and checked against the kernel, and some is not. The second kind should be marked "outside the model's guarantees" wherever it appears (the component diagram, a review), so nobody reads a green check as covering it. Today every component PlayIDE draws is generated, so there is nothing to mark yet; this belongs with source-connected review (ADR-0147) when a checkout is shown beside the model.
* **Diff-first review.** Reviewing an AI change as a diagram diff with a question like A10's beside it, rather than starting from drawing, is the subject of the "Review changes in PlayIDE, not PRs" thread. The reachability route (`/api/play/reach`) is there for it to reuse.
* **Audience.** The owner kept the audience as people who know UML (8 October 2026): PlayIDE does not teach UML or translate it into captions. But UML is also how non-technical stakeholders sometimes review a design, so `/play?view=review` shows the same diagrams, Permissions, Simulate and the running app with every editing tool out of view (ADR-0172). It is a view, not a permission: nothing in PlayIDE persists a change, and approval stays with the owner in the review workbench.
* **The sidebar was dense.** Checks, chat, inspector, simulation and the running app shared one column, and the owner found it "too much going on". ADR-0173 gave each a fixed place in a workbench shell modelled on Visual Studio, VS Code, Cursor and draw.io; see section 7.

## 7. The workbench shell (ADR-0173)

Each region has one job and stays where it is, in the place an engineer from an IDE looks first.

| Region | What it holds | Shown | After |
|---|---|---|---|
| Title bar | PlayIDE and the model, the command center (Ctrl+K), toggles for the side bar, the panel and the chat | Always | VS Code's command center; Cursor's title bar |
| Toolbar | Run bar, Simulate, Build & run; the checks ring opens its list as a popover | Always | Visual Studio's standard and debug toolbars |
| Left | Model outline above the inspector | By default; Ctrl+B | Visual Studio's Solution Explorer above Properties |
| Centre | Diagram tabs (state machine, class, use cases, screens, components), then Laws, Permissions and Review; ripple badges on the tabs; the UML palette as a column beside the state machine | Always | VS Code editor tabs; draw.io's shape library |
| Panel | Run, Simulation, Running app, one at a time, resizable | When one of them has something; Ctrl+Alt+P | VS Code's panel; Visual Studio's output windows |
| Right | Chat in plan mode, full height, with the authority strip and the suggestions | By default (not in the review view); Ctrl+Alt+C | Cursor's agent panel; the Codex app's conversation |
| Status bar | Model, "Previewing a plan", selection, toast, Simulate score, Ctrl K | Always | VS Code and Visual Studio status bars |

What changed for the agentic side: the chat no longer moves or shrinks when a run starts. The fence (A2) and a plan under review stay in view while the plan's effect plays out in the panel below the diagram, so checking a step and watching it run happen side by side (A5). The checks ring stays one click away, and its list no longer pushes the chat down (A6). The layout toggles are in the command palette too (A8).

## 8. Adding and editing on the diagram (ADR-0174)

Dragging was the only pointer way to add an element, and the form it opened sat in the inspector, away from the diagram. Now a palette item is picked and placed with a click, a double-click adds or edits in place, and a small editor opens where you click. Enter adds the step to the plan; Escape drops it. There is no modal, so the plan, its verdict and the chat stay in view while you edit (A5). Every gesture still makes one typed step that the server checks, whether you or the AI made it (A1). The review view ignores all of them.
