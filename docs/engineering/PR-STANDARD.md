# Pull request standard

A pull request is a design document that happens to carry a diff. A reader who has not seen the branch should
understand what changed, why, how we know it works, and what it costs, in about two minutes. This applies equally
to pull requests written by people and by agents.

## Required sections

Use [the template](../../.github/pull_request_template.md). Every section is required; write "None" rather than
deleting one.

1. **Summary.** Two or three sentences in plain language, for a reader who has not seen the branch: what the user
   or developer can now do, and why it matters for the POC (docs/engineering/POC-DEFINITION.md) or the demo.
2. **See it.** At least one GIF (see [Media](#media)). A still screenshot or a rendered diagram can supplement a
   GIF but does not replace it.
3. **What changed and why.** The design decision, the alternatives rejected, and links to the ADRs added or
   superseded. Describe the change in terms of the domain (the model, the language, the evidence) before the files.
4. **Evidence.** Gate results copied verbatim from `nox` (`session: result`), new tests and what they prove,
   and a statement that each negative control fails as it should. Separate MEASUREMENT from PREDICTION. Anything
   that did not run because a prerequisite was missing (Docker, Chrome, a CLI login, the network) is NOT_RUN,
   with the reason. It is never reported as a pass.
5. **Review record.** A table of the independent review findings (finding | severity | resolution), including
   deferred items with a reason and the complexity debt that was added.
6. **Risk and rollback.** What could break, who would notice, and how to revert it.
7. **Owner actions.** Anything only the owner can do (restamping the release fixture, keys, consents, publishing).
   Write "None" if there are none.

## Media

- **Visible change** (Studio, diagrams, demos): a GIF of the real product doing the new thing, recorded by
  `python -m demos pr-gif browser`. Show the real cursor path and the result; do not stage a mock.
- **Non-visual change** (kernel, gates, verification, tooling): a GIF of a terminal session that shows the new
  behaviour, including a negative control failing, recorded by `python -m demos pr-gif terminal`. A GIF of a test
  run alone is not enough. Show the behaviour the tests protect.
- Keep each GIF under 5 MB, 1280 px wide at most and 20 s long at most. Loop once through the whole story; it
  should not cut off mid-action.
- Media are published to the orphan `pr-media` branch under `pr/<number>/` and embedded by their raw URL, so
  `main` never carries binary history. A GIF that becomes product documentation is copied into `docs/assets/`
  by the pull request that documents it.

## Writing

- Lead with the outcome, not the activity: "The review packet now shows the Z3 proof and blocks on a failed
  one" rather than "Added evidence kinds".
- Keep it short and concrete: numbers, names and links. Leave out adjectives, filler and marketing.
- Say plainly what is not done, what is uncertain, and what was not tested. An honest limit is worth more than
  a confident claim.
- Keep the title in conventional-commit form (`feat(evidence): …`), and keep it under 72 characters.

## Merge protocol

An independent adversarial review is done and every blocker and major finding is fixed. Main has been merged in,
and every gate passes on the merge result. The description meets this standard, including the GIF. Only then is
the pull request merged with a merge commit.
