# Model AI agents, timers and external systems

Most systems you design now have actors that are not people: an AI agent that triages and proposes, a scheduled job that escalates, a payment provider that calls back. In UML they are all actors. In PlayIDE each is a role with a **kind**, and laws about kinds keep a person where the decision has to stay with a person ([ADR-0210](adr/0210-actors-that-are-not-people.md)).

The worked example is the **Refund desk** pack (`packs/refund-desk`):

```console
eija serve --pack packs/refund-desk      # then open /play from the launch link
eija laws --pack packs/refund-desk       # every law proved over every run
eija scenarios --pack packs/refund-desk  # its seven test cases
```

## The four kinds

| Kind | UML notation in PlayIDE | Typical role | How it acts in the kernel |
|---|---|---|---|
| `human` (default) | stick figure | Customer, Supervisor | Authorised by role; `actor_assigned` can mean "on shift" |
| `agent` | actor box «agent» | SupportAgent | Authorised by role, exactly like a person. Pausing it is making its actor inactive: every step is then `ACTOR_REVOKED` |
| `timer` | actor box «timer» | SlaTimer | A scheduled job that takes its step when it runs |
| `system` | actor box «system» | PaymentGateway | An external system's callback (settled, failed) |

Declare the kind on the role in `pack.json`. A role without `kind` is a person.

```json
"roles": [
  {"id": "Supervisor", "description": "A person on the support desk."},
  {"id": "SupportAgent", "kind": "agent", "description": "An AI agent: triages and proposes; never decides."},
  {"id": "SlaTimer", "kind": "timer", "description": "Escalates a proposal nobody decided in time."},
  {"id": "PaymentGateway", "kind": "system", "description": "Calls back when a payout settles or fails."}
]
```

## Patterns

**The agent proposes, a person decides.** Give the agent the steps that prepare a decision (`AssessRequest`, `ProposeRefund`) and a person the step that makes it (`ApproveRefund`). Then state who decides as a law about kinds, not about one role:

```json
{"id": "only-people-approve", "kind": "only_kind_holds", "code": "HUMAN_DECISION:ApproveRefund",
 "role_kinds": ["human"], "action": "ApproveRefund",
 "description": "Only a person approves a refund."}
```

`role_never_holds SupportAgent` would say less: it is silent the day a second agent role appears, and silent for a role nobody declared. A kind law binds to every role of its kinds when the pack loads, and a role without a declared kind never counts.

**Guard the state, not just the action.** `only_kind_enters` covers every way into a state, including ones added later (here `ResolveEscalation` and `RetryPayout` also enter Approved):

```json
{"id": "approved-by-people", "kind": "only_kind_enters", "code": "HUMAN_DECISION:Approved",
 "role_kinds": ["human"], "state": "Approved"}
```

**A person in the loop on every path.** `path_requires_kind` says no run reaches a state by agents and machines alone. It is a sequence law, like `path_requires`, judged on the table on every edit and on every run by the law proof:

```json
{"id": "person-in-the-loop", "kind": "path_requires_kind", "code": "HUMAN_IN_THE_LOOP:Paid",
 "role_kinds": ["human"], "state": "Paid"}
```

**Escalation by a timer.** A transition held by the timer role moves a stale proposal to `WithSupervisor`, and a person resolves it. Draw it like any transition; the use case diagram shows the «timer» actor on the system boundary.

**An external system calls in.** Give the provider's callbacks their own role of kind `system` and protect them: "only the payment system confirms a payout" (`only_kind_holds` with `role_kinds: ["system"]`) means nobody marks a refund paid by hand.

**A kill switch for the agent.** An inactive actor is refused at once (`ACTOR_REVOKED`). The fixture `support-bot-paused` shows it in the Tests tab and in Simulate.

## See it work

1. **Use cases** tab: the Supervisor and Customer are stick figures; SupportAgent, SlaTimer and PaymentGateway are «agent», «timer» and «system» boxes.
2. **Chat**: `allow SupportAgent to ApproveRefund`. The plan is refused and names `only-people-approve`, `approved-by-people` and `person-in-the-loop`. Ask `Let the support agent approve refunds itself` and the offline proposer offers the hand-off instead (the agent escalates to a supervisor), which the policy allows.
3. **Sequences**: select *The AI agent cannot approve the refund it proposed*. The «agent» lifeline calls `ApproveRefund()` inside a `neg` fragment and the record answers `refused: ROLE_DENIED`.
4. **Simulate**: under the totals, one line each for People, AI agents, Timers and External systems: what they tried, what went through and the kernel's refusals (the paused agent's `ACTOR_REVOKED`, an agent's slip at `ApproveRefund` as `ROLE_DENIED`).
5. **Laws** tab: every law holds over every run, with the kind laws named in plain language.
6. **Tests** tab: `The AI agent cannot approve the refund it proposed` passes because the kernel refuses the step.

## A second example: AI ops deploys

`packs/ai-ops` is the same pattern in another domain. An AI ops agent opens a change and asks for a build. The CI server («system») reports green or red, the engineer on call signs the deploy off (when on the rota), the deploy window («timer») starts the rollout, and the health monitor («system») confirms it or rolls it back on its own.

- `only-on-call-signs-off` and `scheduled-by-people` keep the decision to ship with a person; `person-before-production` says no run reaches production without one.
- `ci-reports-green` (`only_kind_holds` with `role_kinds: ["system"]`) means the agent cannot mark its own build as passing.
- Rolling back needs no person: machines may always move toward safety. Kind laws are directional; write them only where a decision has to stay with a person.

In the **Sequences** tab, «agent», «timer» and «system» lifelines are drawn as actor boxes with their keyword, and the step the kernel refuses (the agent signing off) is a `neg` fragment with the kernel's reply.

## Not modelled yet

- **Amounts.** "The agent may approve refunds under 50" needs value guards in the kernel (issue #93). Today a law keeps the whole decision with a person.
- **Elapsed time.** A timer is an actor that acts when run, not `after(48h)`; time triggers are issue #93.
- **Agents talking to agents, or to other records.** Messages and cross-object actions are issue #93; one record moves through one state machine.
- **Declaring a kind from a sketch, the chat or a UML import.** A system started in PlayIDE gets people as roles; set `kind` in its `pack.json`.
