# ADR-0205: The class diagram says what is drawn and what is built

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE software architecture views (issue #145; follows ADR-0153 and ADR-0202)

## Context and problem statement

The built app stores records of the record class only (ADR-0150, ADR-0153). Its attributes are the app's form, checked on the server. The other classes and every association are drawn on the class diagram but never built: the app never stores a `Member`, never looks one up and never checks a multiplicity. Nothing said so. In `library-loan` the diagram shows `Loan 0..* — borrower 1 Member`, while the form takes `memberCard` as free text. A reader who knows UML reads the association as enforced. "UML you can trust" fails quietly when the diagram claims more than the app does.

## Decision drivers

* The diagram must not claim more than the app does, in UML's own notation and without a new stereotype.
* The server says what is built, as it does for every other check. The page only draws the report.
* No kernel change. Building the associations needs records of several classes (#65), which waits on #80.

## Considered options

* **Report what is built, and mark the rest on the diagram (chosen).** `application.class_build.class_build(data)` lists the built class, the classes drawn only, each association as drawn, not built, and the record attributes that stand in for an association.
* **Draw the unbuilt parts dashed.** Rejected: a dashed line is a dependency in UML, and a dashed class means nothing standard.
* **Build to-one associations as reference fields now.** This is the real fix (step 2 of #145). It needs the multi-entity runtime (#65), a kernel change that waits on #80.

## Decision outcome

Chosen option.

* `class_build` is pure and reads the data model only. A record attribute whose leading camelCase word names a class or role the record is associated with (`memberCard` beside `borrower: Member`) is `ATTRIBUTE_STANDS_IN_FOR_ASSOCIATION`, severity *consider*. The app checks the text, not that such a member exists.
* `GET /api/play/data` returns the report as `build`. A previewed plan with data-model steps carries its own report as `class_build`.
* On the class diagram, a class that is drawn only is grey, and an attribute that stands in for an association is amber. The hint under the diagram says that only the «record» class is built. The inspector says why and names the limit (#65).
* The ripple (ADR-0158) lists a stand-in attribute that a change introduces under *Class diagram*, as a "To consider".

### Consequences

* Good: the diagram no longer claims more than the app does, and the reader is told where.
* Good: a chat round that adds `copyBarcode` to `Loan` is told that it stands in for the association to `Copy`.
* Bad: the stand-in check is a naming heuristic. An attribute named otherwise is not found, and an attribute that merely shares a word is a false "to consider". It is advice, never a problem, and it never blocks a build.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| None new | A few lines over EIJA's own data model (ADR-0153); no tool reports which parts of a class diagram a generated app builds | Replaced by building associations with the multi-entity runtime (#65) |
