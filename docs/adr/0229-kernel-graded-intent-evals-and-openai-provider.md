# ADR-0229: Kernel-graded intent evals, and an OpenAI Responses API provider

* Status: accepted
* Date: 2026-11-11
* Lane: providers / evals

## Context and problem statement

PlayIDE's pitch is that AI may propose a change and the kernel decides what it means. There was no measurement of how well any model reads a plain request into the pack's meanings, and no record of the most dangerous failure: answering an unsafe request with a safe meaning nobody asked for, which shows a green "the policy allows it" (issue #152). The live providers (Claude, Codex, Gemini, OpenCode CLIs; OpenRouter and Anthropic over HTTPS) were last run on 28 September and only for schema validity. There was also no direct adapter for the OpenAI developer platform's API; the Codex adapter covers a ChatGPT sign-in only.

## Decision drivers

* Deterministic grading. The kernel already knows which meanings are supported and which laws refuse the rest; no model-as-judge.
* Spend is opt-in and capped: network and consent flags as for every live call, plus a call cap.
* Provider-neutral: the same cases and grader for every adapter.
* One HTTP stack, one isolation policy (ADR-0020, ADR-0021).

## Considered options

* A small harness in `quality/evals/` that reuses the provider adapters and `propose_plan` (chosen).
* [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) (MIT): a capable eval framework, but a large dependency whose model layer would bypass EIJA's provider isolation and consent; adopt it if evals grow beyond one task.
* promptfoo (MIT, Node): a second toolchain, and its graders are model- or string-based.
* OpenAI's hosted Evals and graders: tied to one vendor, and OpenAI's graders guide says those graders are being deprecated.
* The official `openai` Python SDK for the new provider: a second HTTP stack with its own retries; the shared bounded POST already gives size caps, no redirects and stable error codes.

## Decision outcome

**Cases.** `packs/intent-evals.json` holds pack data, so it lives with the packs (outside the vocabulary gate): a request, its pack, its kind (`example`, `paraphrase`, `unsafe`, `off_topic`) and the meaning it asked for. 32 cases over 11 packs to start.

**Grader.** `quality/evals/intent.py` asks the provider for alternatives and takes the first as the meaning it would plan. Outcomes: `correct`; `substituted` (an unsafe meaning was asked for and a supported one answered); `wrong`; `invalid` (the provider failed or its reply failed validation, never repaired). The answered meaning is then planned through `propose_plan`; the kernel must allow a supported meaning and refuse an unsupported one, and any disagreement fails the run as a pack or kernel defect.

**Running.** `python -m quality.evals.intent` runs the offline fixture (SYNTHETIC evidence). A networked provider needs `--allow-network` and `--consent`, and `--max-calls` stops the run (hard limit 200). The `intent_eval` nox session (fast and full tiers) runs only the offline harness tests, including a negative control: a provider that always answers with a safe meaning is caught on every unsafe case.

**OpenAI provider.** `adapters/providers/openai_api.py` (`--provider openai`) calls `POST /v1/responses` with Structured Outputs in strict mode and `store: false`, the key from `OPENAI_API_KEY` or `--ask-key` held in memory, and a model the operator must name. No tools are sent; refusals, incomplete replies and tool calls fail closed; one attempt, no retry. It is contract-tested over a mock transport and is NOT live-verified until `scripts/live_provider_smoke.py` records a run.

### Consequences

* Good: a model's reading of requests becomes a number per kind, with the #152 failure counted separately.
* Good: the first offline baseline (`evidence/intent-eval/2026-11-11-offline-linux.json`) already shows a real defect: the excursion fixture answers "let teachers give the final approval on their own" with `recommend_only` (substituted). Its keyword rules also miss 5 of 6 paraphrases, which is the gap a live model is expected to close.
* Bad: 32 cases is small; per-kind numbers are indicative, not statistically strong. Add cases as packs grow.
* Bad: the grader reads only the first alternative; a provider that ranks the right meaning second scores `wrong`.
* Revisit when: evals need more than one task (adopt Inspect AI), or batch submission is needed to cut cost at larger case counts.
