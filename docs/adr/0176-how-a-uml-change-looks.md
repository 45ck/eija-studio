# ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses

* Status: accepted for the state machine
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner asked how a change can be reviewed as a UML change instead of a pull request, and "how you even view a UML change (ghost UI/UX?)". PlayIDE could already preview a plan (ADR-0156) and mark the ripple on each diagram (ADR-0158), but it showed a change by flipping between two separate drawings:

* **Preview** drew the candidate, with added and changed elements marked. What the plan removed was not there at all.
* **Back to the model** drew the model in force, with what the plan removed marked in red.

Each side was laid out on its own, so a state could jump when you flipped, and you never saw the removed parts and the new parts together. A deleted path, which is often the riskiest part of a change, was easy to miss.

## Decision drivers

* Nothing a change removes may silently disappear from the picture.
* A state keeps its place whichever side you look at, so the eye can compare.
* Keep it UML: the same state machine notation, with the change drawn on it rather than in a separate list.
* One source of truth. The diff is computed on the server from the two models, using the one definition of "changed" that the ripple and the Mermaid diff already share (`domain.impact.changed_fields`).
* Read-only. A picture of a change saves, approves and applies nothing.

## What existing tools do

| Tool | How it shows a model or diagram change | What PlayIDE takes from it |
|---|---|---|
| [LemonTree](https://help.lieberlieber.com/LemonTree/Diagram-Viewer.html) (LieberLieber, proprietary) | Two diagrams side by side, each against a common base. New elements get a green border and changed ones an orange border. Deleted elements are not rendered. | The colours. Not the side-by-side, and not hiding deletions. |
| [EMF Compare](https://news.obeosoft.com/post/diagram-comparison-with-emf-compare-2) with Papyrus (EPL-2.0) | Model tree diff with old and new diagrams side by side, and decorators on changed figures. Its authors called how to show a deleted element an open question. | The structured, per-element change list. JVM and Eclipse RCP, so reference only. |
| draw.io (Apache-2.0) | No built-in compare. A common workaround [renders both revisions to PNG and diffs the pixels](https://www.innoq.com/ch/blog/draw-the-diff/). | Nothing: a pixel diff does not know which state moved or why. |
| [GitHub image diff](https://github.blog/news-insights/the-library/behold-image-view-modes/) | 2-up, swipe and onion skin, where an opacity slider fades one version into the other. | The onion skin, as a slider between Before and After. |
| Code review (GitHub, Gerrit, VS Code) | Unified view of both sides, next and previous hunk, context lines shown fainter. | The merged view, `[` and `]` to step through changes, and unchanged elements faded as context. |

PlayIDE has what these tools lack: the two models, not two pictures. It can lay out both together and say exactly what each element's status is.

## Considered options

* **One union diagram with ghosts and lenses** (chosen).
* **Side by side**, as LemonTree and EMF Compare do. It halves the space for each diagram and makes the eye match positions across two panes.
* **Pixel diff or onion skin of two separate renders.** Layouts differ, so everything appears to change.
* **Keep flipping between Preview and Back to the model.** It hides one side at a time, which is the problem.

## Decision outcome

Chosen option.

* **Server.** `application/ghost_diff.py` (`ghost_diff(before, after)`, format `eija.ghost-diff.v1`) is a pure function of two `Workflow`s. It returns every state and transition of both models, each with a status:
  * `same`, `added` or `removed`, by membership;
  * `changed`, with each changed field's before and after;
  * `moved`, for an action that now joins other states. The new route is drawn, and the old one stays as a `was` ghost, so a moved arrow reads as one change rather than an unrelated delete and add.

  It also returns a numbered list of changes in a fixed order, each with a sentence and the cell it is about. A moved initial state is one change. Reordering either model changes nothing. `POST /api/play/diff` diffs the change shown (a change case's candidate and any accepted plan steps) against the model in force (the active baseline or the case's baseline). It is read-only.
* **The Changes view.** On the state machine tab, a **Changes** button with a count appears whenever there is a change. It swaps the editable canvas for the change drawn on one layout of both models:
  * **Changes:** added elements in green with `+`, changed in amber with `~`, moved in amber with `↷` and the old route as a dashed `was` ghost, and removed elements kept as faded, dashed, struck-through ghosts with `−`. Unchanged elements fade back as context (**Fade unchanged**).
  * **Before:** the model in force, with nothing the change adds.
  * **After:** the change, with nothing it removes.
  * **Onion skin:** a slider between Before and After.

  No state moves between lenses. The change list under the diagram says each change in a sentence. `[` and `]` (or the arrows) step through it, and the inspector shows the change with a before and after table for each changed field. `B`, `C` and `A` pick a lens while focus is in the view. Another tab, or pressing **Changes** again, returns to the editable diagram.
* **Stable preview.** While a plan can be previewed, the state machine tab lays out the model in force and the candidate together, in a fixed order. Preview and Back to the model no longer move any state, and a removed state leaves its gap.
* **One renderer for every view of a change.** The renderer is `window.PlayDiff.mount(box, ghost, options)`. It returns lenses, the onion skin, `show(change)` and `fit()`. The Review tab (ADR-0175) now draws its canvas with it: `POST /api/play/review` also returns the union, the canvas lays it out top to bottom, and the review's knock-on states are tinted amber. There is one way a change is drawn, not two.

### Consequences

* Good: a deleted path stays visible as a ghost in the merged view, so a reviewer sees what goes away as well as what arrives.
* Good: flipping lenses and previewing a plan move nothing, so a change can be seen as motion between two otherwise identical pictures.
* Good: the view needs no new rules on the page. It styles what the server returns.
* Bad: the component diagram keeps the ripple marks of ADR-0158 (regenerated components in amber). Its components are read from the built files, and a state-machine change regenerates them rather than adding or removing them.
* Bad: a layout of both models is a compromise for each. A large change can place the model in force slightly differently from its own layout.
* Revisit when: the class or use case diagrams become editable (then they need ghosts too), or a reviewer study shows which lens people actually use.

### Update: calm by default

The owner found the drawing right but the view around it too busy: two toolbars of lenses, a slider and a checkbox, a legend, a list strip and an inspector all at once. The view now opens in one default, the Changes lens with unchanged parts faded. Above the diagram sit one summary line (the counts in their colours, which also serves as the legend), `‹ Change n of N ›`, and **Compare**. Compare reveals the lenses, the onion skin and Fade unchanged. The change list moves into the inspector, so there is one place to read the change, and the before and after table opens under a change only when it has changed fields or a route. The drawing, the keys and the server are unchanged.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| maxGraph 0.25.0 and Dagre (existing, Apache-2.0 and MIT) | Adopted: maxGraph draws and styles the cells (opacity, dashes, strikethrough), Dagre lays out the union | — |
| EMF Compare with Papyrus (EPL-2.0) | Needs an Ecore metamodel of the diagram and the Eclipse runtime; a second source of truth | Pattern only: a per-element change list |
| LemonTree (proprietary) | Closed source, Enterprise Architect only | Pattern only: green and orange status colours |
| GitHub image view modes, webdiff (MIT) | Compare pixels, not elements | Pattern only: onion skin |
| N2G (MIT) draw.io graph compare | Python library that marks changes on draw.io XML from graph data; no lenses and no UML state machine notation | Adopt for a draw.io export of the diff |

### Update: the same change on the class and use case diagrams

**Changes** is now a mode across the diagram tabs rather than a view of the state machine only. While it is on, the class and use case diagrams draw the same change as the state machine, in the same colours and marks. Flipping tabs keeps it on, and pressing **Changes** again turns it off on every diagram.

* **Use cases.** `ghost_diff` also returns `use_cases`, the use case diagram of both models (ADR-0153). It has a use case per action, an actor per role, and who takes which, each with a status. A removed use case or actor stays as a dashed, struck-through ghost. A role change keeps the use case (amber) and moves its association, with the old line as a ghost. A moved arrow is the same use case. A test checks that it names the same new and gone use cases and actors as the ripple.
* **Classes.** The record's state enumeration lists the states of both models. Added literals are green, removed ones struck through, and the rest faded.
* The change list stays in the inspector on each diagram. Picking a change selects its use case, or the enumeration that holds its literal.
