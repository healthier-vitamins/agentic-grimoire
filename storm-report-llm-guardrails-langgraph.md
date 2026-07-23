# Implementing Guardrails for LLM Calls in LangChain/LangGraph

*STORM research report — 5-minute body, cited appendix below the divider.*

## Unknowns first

Three things this report could not settle:

1. **The recommended tools were never adversarially tested.** The one rigorous evasion study ([arXiv 2504.11168](https://arxiv.org/abs/2504.11168)) never covered Guardrails AI's validators or LangChain's `PIIMiddleware` — any classifier pick is "best of what's been measured," not "proven safe."
2. **No published evidence that ensembling classifiers improves evasion-resistance.** The only multi-model attempt ([CourtGuard](https://arxiv.org/abs/2510.19844)) performed *worse* than a single LLM-judge.
3. **Your threat model wasn't pinned down in the interview.** This report assumes moderate threat (opportunistic misuse); if you expect motivated adversaries probing a public tool-wielding agent, weight candidate 4 more heavily.

## Verdict

Build guardrails as **LangChain's native middleware stack** (the framework's actual 2026-era answer — not the deprecated `OutputFixingParser`/`RetryOutputParser`, demoted to `langchain_classic`), and plug in third-party detectors only where the framework doesn't ship one: free hosted moderation for toxicity, Guardrails AI for schema/hallucination validators, and a Unicode-normalization pre-filter + Prompt Guard for injection defense. Avoid AWS Bedrock Guardrails: a documented bug disables streaming on `ChatBedrock` entirely ([langchain-aws#176](https://github.com/langchain-ai/langchain-aws/issues/176)), conflicting directly with your streaming requirement.

### Recommended path

If this were my project, here's what I'd actually do. Ship candidate 1 this week — the middleware hooks and `PIIMiddleware` are first-party, genuinely stream, and cost nothing extra. Next sprint, layer in candidate 2: OpenAI Moderation is free and provider-agnostic, and Guardrails AI fills the schema/hallucination gap — accept its sentence-level streaming lag, because true token-level semantic checking doesn't exist anywhere. I rejected candidate 3 outright: the `ChatBedrock` streaming kill and per-turn double billing are disqualifying on your two hardest axes, streaming and provider-agnosticism. Candidate 4 I neither reject nor adopt — it's conditional: the interview never established a motivated-adversary threat model, and its red-team cadence is a standing ops cost. Revisit it the day this agent gets tool access with real-world consequences. One thing I'd do regardless: add a DIY token-budget guard node — LangGraph won't do it for you.

## Confidence table

| # | Finding | Confidence (1–10) |
|---|---|---|
| 1 | Middleware (v1.3+) is the framework-native guardrail mechanism; `PIIMiddleware` genuinely streams | 9 |
| 2 | Injection classifiers show high evasion rates; Prompt Guard is only strong against one attack family | 8 |
| 3 | "Streaming-compatible guardrails" is a buffering spectrum; per-token semantic checks don't exist | 8 |
| 4 | LangGraph offers only structural safety primitives — no native cost/budget enforcement | 8 |
| 5 | Each hosted moderation call is its own data-egress/compliance event needing DPA/BAA scrutiny | 7 |

## Five key findings

**1. LangChain's middleware system is the current framework-native answer.**
- *Evidence:* `langchain>=1.3` ships hooks around agent, model, and tool calls, plus `PIIMiddleware`, which redacts mid-stream text deltas via a registered stream transformer ([LangChain guardrails docs](https://docs.langchain.com/oss/python/langchain/guardrails)).
- *Also:* the retry-repair parsers are demoted to `langchain_classic`; restoration closed "not planned" ([langchain#34098](https://github.com/langchain-ai/langchain/issues/34098)).
- *Challenged by:* cost-benefit and robustness lenses — middleware is a hook mechanism, not a detector; you still supply classifiers.

**2. Guardrail classifiers are themselves an adversarial attack surface; none is robust across attack families.**
- *Evidence:* 6 classifiers vs. 20 evasion techniques — emoji smuggling hit 100% attack success rate (ASR) on multiple systems; NeMo Guard fell to 65% ASR under TextFooler, Azure Prompt Shield to 73% under transfer attacks ([arXiv 2504.11168](https://arxiv.org/abs/2504.11168)).
- *Nuance (round 2):* Meta Prompt Guard's headline 2.76% ASR holds only for adversarial-ML word substitution; trivial emoji/character smuggling breaks it too (70–73% ASR).
- *Challenged by:* framework and cost-benefit lenses treated classifier choice as cost/integration — an incomplete framing.
- *So what:* picking a classifier moves the residual risk; it doesn't remove it.

**3. Streaming guardrails live on a buffering spectrum, and groundedness checks can't truly stream.**
- *Evidence:* every "streaming-safe" integration buffers — sentence-boundary (Guardrails AI), fixed chunks (Azure), or a delayed safety signal; AWS admits an irrelevant response can fully stream before its grounding check flags it ([AWS contextual grounding docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html)).
- *Also:* RAGAS Faithfulness structurally needs full-response claim decomposition ([RAGAS docs](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)); NeMo's sync `.stream()` silently drains the whole async stream before yielding ([NeMo Guardrails source](https://github.com/NVIDIA-NeMo/Guardrails)).
- *Challenged by:* none — strongest cross-lens consensus in the report.
- *So what:* budget for a delayed or coarsened safety signal; "true per-token" is marketing.

**4. LangGraph's agentic safety is structural, not content-based — and has no native cost/budget enforcement.**
- *Evidence:* the real primitives are `recursion_limit` (default 25, `GraphRecursionError`), per-node `llm.bind_tools(allowed_tools)` scoping, and `interrupt()`-based HITL policies ([LangGraph interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts)).
- *Gap / so what:* no first-class per-session token/cost budget — confirmed by an open docs request ([langchain-ai/docs#4102](https://github.com/langchain-ai/docs/issues/4102)); the DIY pattern is a `BudgetExceededError` raised in-node, and it's yours to build.

**5. A hosted moderation call is a compliance event in its own right.**
- *Evidence:* Microsoft's own docs — prompts/completions may be processed cross-region "for operational purposes," and a sample is retained for human-reviewed abuse monitoring unless a regulated customer opts out ([Azure OpenAI data privacy](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/data-privacy)).
- *So what:* a BAA on your inference model does **not** cover the guardrail calls you bolt on — each hosted check needs its own DPA/BAA review.

## Hidden connection

**Checks that need only local pattern-matching can stream; checks that need whole-utterance semantic judgment cannot.** PII redaction streams because regex/NER on a partial chunk is still a meaningful decision unit; toxicity, jailbreak, and groundedness need full-sentence or full-response context. That is why every "streaming guardrail" product is really a *delayed or coarsened* guardrail — visible only by placing findings 1 and 3 side by side.

## Candidates

**1. LangChain-native middleware stack — PICKED: backbone**
(`PIIMiddleware` + custom model hooks + `interrupt()` HITL + `with_structured_output`)
- **Why:** zero extra dependency, first-party, PII redaction genuinely streams; agentic safety (recursion limits, `bind_tools` scoping) comes free ([LangChain guardrails docs](https://docs.langchain.com/oss/python/langchain/guardrails)).
- **Why not:** a hook mechanism, not a detector — you supply the classifiers; no cost/budget enforcement.
- **When to pick:** the backbone for almost everyone — start here.

**2. Hybrid: middleware + free hosted moderation + Guardrails AI — PICKED: add-on**
- **Why:** near-zero recurring cost (OpenAI Moderation is free and provider-agnostic — [OpenAI help](https://help.openai.com/en/articles/4936833)); Guardrails AI covers schema/hallucination validation the framework lacks.
- **Why not:** Guardrails AI streaming is sentence-buffered, and `on_fail="reask"` is unsupported while streaming ([Guardrails AI streaming docs](https://www.guardrailsai.com/docs/concepts/streaming)); no official LangChain-native integration — you wire it yourself.
- **When to pick:** the recommended addition to candidate 1 when a sentence-level streaming lag is acceptable.

**3. Cloud-native hosted guardrails (Bedrock / Azure Content Safety) — REJECTED: streaming kill + lock-in**
- **Why:** lowest engineering lift, vendor-managed, built-in grounding check; Azure is fast (~52ms measured).
- **Why not:** Bedrock Guardrails disables `ChatBedrock` streaming entirely ([langchain-aws#176](https://github.com/langchain-ai/langchain-aws/issues/176)) and bills $0.15/1,000 text units on both input and output ([Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)); Azure buffers or delays the safety signal ~1000 characters; both fight provider-agnosticism.
- **When to pick instead:** already committed to one cloud *and* non-streaming (or delayed-signal) UX is acceptable for guarded flows.

**4. Defense-in-depth adversarial stack — CONDITIONAL: motivated-adversary threat model only**
(Unicode-normalization pre-filter + Prompt Guard + an architecturally different second signal + ongoing red-teaming)
- **Why:** the only candidate treating classifiers as a degrading attack surface — directly answers finding 2.
- **Why not:** highest ongoing ops burden; no evidence ensembling raises evasion-resistance ([CourtGuard](https://arxiv.org/abs/2510.19844)); NeMo carries a sync-`.stream()` footgun and a reported 30s→80s latency blowup ([NeMo#473](https://github.com/NVIDIA-NeMo/Guardrails/issues/473)).
- **When to pick instead:** a public-facing, tool-wielding agent where a jailbreak has real consequences — layer on top of 1–2, budget for continuous red-teaming.

## Bias check, weakest link, missing lens

- **Weakest link:** finding 2 rests on a single unreplicated paper that never tested Guardrails AI or `PIIMiddleware` — don't generalize its numbers to tools it didn't evaluate.
- **Bias check:** the red-team lens's alarming numbers likely over-weighted candidate 4 relative to a typical production app's real exposure.
- **Missing lens:** a threat-model/risk-assessment lens (trusted internal users vs. untrusted public traffic) would materially re-weight candidate 4. Unresolved in the interview.

---

## Appendix

### Round 1 — five expert lenses (parallel research)

**Lens 1 — LangChain/LangGraph framework specialist.**
- *Position:* use the v1.3+ middleware system (`before_agent`/`before_model`/`before_tool`/`after_agent`) plus `interrupt()`/`Command(resume=...)` for HITL gates; `with_structured_output()` + Pydantic/JSON-schema is the recommended schema-enforcement path (streams progressively via partial objects or JSONPatch diffs with `diff=True`); `OutputFixingParser`/`RetryOutputParser` demoted to `langchain_classic`, restoration closed "not planned" ([langchain#34098](https://github.com/langchain-ai/langchain/issues/34098)).
- *Evidence:* [docs.langchain.com/oss/python/langchain/guardrails](https://docs.langchain.com/oss/python/langchain/guardrails) states `PIIMiddleware` "also redacts streamed wire output — text deltas, tool-call args, tool outputs, and state snapshots — via a registered stream transformer. Requires langchain>=1.3.2."
- *Unique insight:* `interrupt()` has three non-obvious footguns — a bare `try/except` swallows the pause signal; code before an `interrupt()` inside a node re-executes on every resume (non-idempotent guardrail actions double-fire); a `while True` validation loop in one node causes exponential re-execution — use conditional edges to a retry node instead.
- *Sources:* [LangGraph interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts) (high conf., primary); [LangChain guardrails docs](https://docs.langchain.com/oss/python/langchain/guardrails) (high conf., primary); [langchain#34098](https://github.com/langchain-ai/langchain/issues/34098) (high conf.); reference.langchain.com pages for langchain_classic output parsers and RunnableConfig (medium conf., search-snippet only); langchain.com blog on interrupt() (lower conf., unread body); deepwiki.com tool-call-validation writeup (lower conf.); NeMo Guardrails RunnableRails docs (lower conf., unread); futureagi.com callback-handler blog (lower conf.).

**Lens 2 — AI red-team/adversarial-safety engineer.**
- *Position:* injection/jailbreak defense is architectural (isolate untrusted content via spotlighting/delimiter-tagging) plus heterogeneous detection layers plus continuous red-teaming — no single guardrail library eliminates indirect injection.
- *Evidence:* [arXiv 2504.11168](https://arxiv.org/html/2504.11168) tested 6 classifiers (Azure Prompt Shield, ProtectAI v1/v2, Meta Prompt Guard, NeMo Guard Jailbreak Detect, Vijil) against 20 evasion techniques (12 character-injection + 8 adversarial-ML). Emoji smuggling: 100% ASR across systems; NeMo Guard 65.22% ASR under TextFooler; Azure Prompt Shield 73.11% under transfer attacks; Meta Prompt Guard best overall at 2.76% ASR on injections.
- *Unique insight:* guardrail classifiers are ML models with the same adversarial attack surface as the LLM they protect; evasions transfer across vendors via black-box surrogate attacks.
- *Sources:* [arXiv 2504.11168](https://arxiv.org/html/2504.11168) (high conf., primary, cited); [arXiv 2511.15759](https://arxiv.org/abs/2511.15759) (agent-specific injection defenses); arxiv.org/html/2510.05244v1 ("firewalls alone insufficient"); lakera.ai blogs on indirect injection and jailbreaking (moderate conf.); arxiv.org/pdf/2505.09602 (adversarial suffix filtering, abstract only); promptfoo.dev vulnerability DB (moderate conf.); aquilax.ai, appsecsanta.com, slavadubrov.github.io, aisecurityandsafety.org, techjacksolutions.com, github.com/nukIeer cheatsheet, sunglasses.dev (all lower conf., landscape only, not cited as evidence).

**Lens 3 — Production reliability engineer.**
- *Position:* hybrid architecture — cheap deterministic checks inline per-chunk on a ~128-token sliding window for mid-stream kill; expensive semantic checks async in parallel with generation, reconciled at boundaries; pure post-hoc full-buffer validation only for high-stakes/non-conversational use.
- *Evidence:* TrueFoundry's guardrail-provider benchmark — Azure Content Safety moderation 52.2ms, Azure PII 52.3ms, OpenAI Moderation 191.5ms, Pangea prompt-injection 358.7ms, PromptFoo 1118.2ms (>20x spread, methodology disclosed).
- *Unique insight:* rejection cost compounds by graph position — pre-generation rejection is free (short-circuit); post-generation at minimum doubles cost/latency; mid-stream is worst for UX (streamed tokens can't be un-rendered) — so rejection *rate* per position, not just detection accuracy, should drive placement.
- *Sources:* truefoundry.com benchmark (high conf., primary, read in full); docs.nvidia.com NeMo Guardrails LangGraph integration (chunking behavior); focused.io LangGraph streaming-patterns blog; artificialanalysis.ai guardrail benchmark (read in full; confirms non-streaming methodology as an open gap); arxiv.org/pdf/2604.03962 "Predict, Don't React" (read in full, no latency numbers extracted); arxiv.org/pdf/2606.20668 (BELLS-O), arxiv.org/pdf/2502.15427, github.com/ant-research/awesome-mllm-guardrails (not fully read); futureagi.com and codetodeploy blogs (not fully read); one unverified WebSearch-snippet figure (sub-100ms/sub-150ms p50 budgets) flagged lower conf., not independently fetched.

**Lens 4 — Compliance/security officer.**
- *Position:* run a same-infra PII pre-filter (Presidio hybrid NER+regex) on input and output *before* any external call — including "compliant" hosted moderation APIs — because each external moderation endpoint is its own data-egress event needing its own DPA/BAA review.
- *Evidence:* [Microsoft's Azure OpenAI data-privacy doc](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/data-privacy) — prompts/completions "may be processed between regions within the geography for operational purposes," and a sample is retained for human-reviewed abuse monitoring unless a regulated customer applies for "modified abuse monitoring."
- *Unique insight:* teams assume a signed BAA for the *inference* model covers every guardrail call bolted on afterward — it doesn't; each hosted check is a distinct service boundary.
- *Sources:* [learn.microsoft.com data-privacy page](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/data-privacy) (highest conf., primary, fetched in full); [aws.amazon.com/bedrock/guardrails](https://aws.amazon.com/bedrock/guardrails/) (primary, fetched; notably silent on HIPAA/residency on the product page); openai.com/security-and-privacy (moderate conf., via search summary); learn.microsoft.com Q&A forum thread (lowest conf., triangulation only); docs.langchain.com/langsmith/llm-gateway-redaction (official, Presidio-under-the-hood confirmation, summary only); medium.com Presidio+LangChain walkthrough (lower conf.); braincuber.com Bedrock HIPAA guide (lower conf., marketing-adjacent).

**Lens 5 — Ecosystem/cost-benefit analyst.**
- *Position:* hybrid — hosted moderation (OpenAI Moderation, free) for toxicity + Guardrails AI for schema enforcement beats committing to NeMo's Colang DSL or a single cloud's guardrail service: near-zero recurring cost, provider-agnostic.
- *Evidence:* Bedrock Guardrails bills $0.15/1,000 text units *per evaluation* on both input and output ([Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)); OpenAI Moderation is free and doesn't count against rate limits ([OpenAI help](https://help.openai.com/en/articles/4936833)); [langchain-aws#176](https://github.com/langchain-ai/langchain-aws/issues/176) confirms `ChatBedrock` doesn't stream with Bedrock Guardrails applied.
- *Unique insight:* the "hosted, zero-maintenance" options are the ones most likely to silently break streaming and charge twice per turn; self-hosting Llama Guard only beats API pricing above ~11B tokens/month.
- *Sources:* [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) (official, via search summary); [help.openai.com moderation-free confirmation](https://help.openai.com/en/articles/4936833) (official); azure.microsoft.com Content Safety pricing (official, F0 free tier + S-tier metered); [langchain-aws#176](https://github.com/langchain-ai/langchain-aws/issues/176) (official issue, direct evidence); [github.com/NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) + releases page (maintenance-health signal); github.com/guardrails-ai/guardrails (maintenance-health, star-count discrepancy flagged); guardrailsai.com NeMo-integration blog (vendor, lower conf.); deepwiki.com ChatBedrock guardrail_config writeup (moderate conf.); official ChatBedrock API reference (surfaced, not deep-read); cloudchipr.com/nops.io Bedrock pricing breakdowns (medium conf.); cloudzy.com/braincuber.com/aisuperior.com self-hosting cost analyses (medium conf., blog-tier); is4.ai/particula.tech comparison blogs (medium/low conf.). Note: Context7 MCP returned "monthly quota exceeded" for this agent — flagged as a tooling gap, not substituted with memory.

### Round 1 contradiction map

- **Conflict:** cost-benefit and framework lenses treat "pick a guardrail library" as sufficient; red-team shows the classifiers underneath are evadable. → Resolved in round 2 with nuance (finding 2), not eliminated.
- **Conflict:** cost-benefit found Bedrock breaks `ChatBedrock` streaming; reliability found Azure Content Safety fast and cheap. Different vendors — raised whether the streaming break is Bedrock-specific. → Resolved in round 2 (finding 3: a spectrum, not a Bedrock-only bug).
- **Evidence weight:** strongest lens = red-team (well-designed empirical paper, disclosed methodology, concrete ASR numbers); weakest = framework lens's library-selection treatment, which ignored classifier robustness.
- **Consensus:** every lens agreed no single tool/layer suffices — layered defense-in-depth is the universal recommendation.
- **Blind spot found:** agentic/tool-use safety (cost/loop limits) and hallucination/groundedness got only passing mentions despite being explicitly requested focus areas. → Hunted in round 2.

### Round 2 — four targeted follow-ups

**Agentic/tool-use safety in LangGraph.**
- *Position:* three composable structural controls — dynamic `llm.bind_tools(allowed_tools)` scoping per-node from graph state, `recursion_limit` (default 25, `GraphRecursionError`, introspectable via `config["metadata"]["langgraph_step"]`), and per-tool `interrupt_on` HITL policies (approve/edit/reject/respond, gated by a `when` predicate).
- *Evidence:* reference.langchain.com recursion_limit + docs.langchain.com GRAPH_RECURSION_LIMIT confirm default and mechanics directly.
- *Unique insight:* LangGraph has **no native per-session cost/token budget enforcement** — confirmed as a real gap via [langchain-ai/docs#4102](https://github.com/langchain-ai/docs/issues/4102) requesting an official guide; teams bolt on external reservation patterns (`BudgetExceededError` raised per node). Tool risk-tiering is DIY (third-party wrappers like CogniWall).
- *Sources:* reference.langchain.com recursion_limit (high conf.); docs.langchain.com GRAPH_RECURSION_LIMIT (high conf.); [HITL middleware docs](https://docs.langchain.com/oss/python/langgraph/interrupts) (high conf.); dev.to/cogniwall tool-permission wrapper (medium conf., vendor); dativo.io policy-node/bind_tools pattern (medium conf.); dev.to/waxell and waxell.ai token-budget posts (medium conf.); runcycles.io budget-reservation pattern (medium conf., vendor); github.com/langchain-ai/langgraph/discussions/6059 (flagged unverifiable/404, not used); [langchain-ai/docs#4102](https://github.com/langchain-ai/docs/issues/4102) (low-medium conf., confirms doc gap); forum.langchain.com recursion-limit thread (low conf.); langgraphjs issue #1524 (low-medium conf., corroboration only). Note: Context7 quota exceeded for this agent too.

**Hallucination/groundedness guardrails.**
- *Position:* two-tier architecture — cheap inline NLI/embedding grounding check as a LangGraph node, paired with a heavier post-hoc check (RAGAS Faithfulness, LLM-as-judge, or Bedrock contextual grounding) once the full response is assembled; no mainstream method scores hallucination at true token level.
- *Evidence:* AWS's own docs: "For streaming API, this can result in a scenario where an irrelevant response is returned to the user and is only marked as irrelevant after the whole response is streamed" ([AWS contextual grounding docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html)).
- *Unique insight:* RAGAS Faithfulness structurally requires full-response claim decomposition (no streaming by design — [RAGAS docs](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)); Guardrails AI "streaming" is sentence-buffered, always one semantic unit behind, and `on_fail="reask"` doesn't work while streaming; SelfCheckGPT-style self-consistency needs N complete generations — offline or pre-response gate only.
- *Sources:* [AWS contextual-grounding-check docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html) (high conf., primary, fetched in full); [RAGAS Faithfulness docs](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) (high conf., primary); guardrailsai.com GroundedAI validator + [streaming docs](https://www.guardrailsai.com/docs/concepts/streaming) (official, mixed fetch depth); ~20 additional blog/vendor/academic sources on RAG-eval metrics and groundedness scoring (GroUSE, SURE-RAG) — lower conf., listed for completeness. Note: Galileo/Patronus AI surfaced no citable documentation this pass — explicit coverage gap.

**Classifier robustness / ensembling.**
- *Position:* Prompt Guard integrates like any other classifier (middleware hook / RunnableRails-style wrapper) — robustness, not integration effort, is the differentiator, and it's split: strong vs. adversarial-ML attacks (2.76% ASR), weak vs. trivial character/emoji smuggling (70–73% ASR). No published evidence ensembling improves evasion-resistance — [CourtGuard](https://arxiv.org/abs/2510.19844) found a multi-model arrangement performed worse than a single LLM-judge.
- *Evidence:* direct re-read of [arXiv 2504.11168](https://arxiv.org/html/2504.11168) Section 5, refining round 1's "held up well" to "held up well only against one attack family."
- *Unique insight:* nobody has evasion-tested Guardrails AI's hub validators or LangChain's `PIIMiddleware` against this suite — a genuine, explicitly-flagged evidence gap.
- *Sources:* [arXiv 2504.11168](https://arxiv.org/html/2504.11168) (fetched twice, primary); [arXiv 2510.19844 CourtGuard](https://arxiv.org/abs/2510.19844) (ensemble underperforms single judge); arxiv.org/abs/2605.07269 MIPIAD (ensemble F1/AUROC, no evasion numbers); guardrailsai.com detect_jailbreak/unusual_prompt validator docs + GitHub repos (official, no adversarial-robustness data); [LangChain guardrails + custom-middleware docs](https://docs.langchain.com/oss/python/langchain/guardrails) (official); NeMo Guardrails LangGraph integration docs (streaming breaks inside LangGraph nodes); huggingface.co Meta Prompt Guard 2 + PurpleLlama model cards (official); llama.com Llama Guard 4 docs (official); ~15 additional blog/tutorial/patent sources, lower conf., in the round-2 transcript.

**Streaming compatibility generalizability.**
- *Position:* buffering is the default across nearly every integration, not a Bedrock quirk — `OpenAIModerationMiddleware` has no stream hooks; Azure's official `langchain-azure-ai` middleware examples only show `.invoke()`; Azure OpenAI's default content filter buffers into "content chunks." Only NeMo's `RunnableRails.astream()` and Guardrails AI's `Guard` wrapper deliver incrementally, and both trade completeness (chunked/sentence-buffered, not per-token).
- *Evidence:* direct read of NeMo Guardrails' `runnable_rails.py` — synchronous `.stream()` fully drains the async generator into a list before yielding anything; only `.astream()` genuinely streams ([NeMo Guardrails repo](https://github.com/NVIDIA-NeMo/Guardrails)).
- *Unique insight:* "guardrails break streaming" is the wrong frame — it's a buffering-granularity spectrum (full-response > sentence chunk > fixed-N-token > per-token), and every "streaming support" claim is a delayed or coarsened safety net.
- *Sources:* learn.microsoft.com content-streaming docs (high conf., primary); learn.microsoft.com langchain-azure-ai middleware docs (high conf., primary, inferred from example absence); [LangChain guardrails docs](https://docs.langchain.com/oss/python/langchain/guardrails) (high conf., PIIMiddleware streaming statement); reference.langchain.com OpenAIModerationMiddleware API reference (high conf.); [NeMo Guardrails runnable_rails.py source](https://github.com/NVIDIA-NeMo/Guardrails), verified via raw curl (highest conf., primary code); NeMo streaming config docs via search snippet (medium-high conf.); [NVIDIA-NeMo/Guardrails#473](https://github.com/NVIDIA-NeMo/Guardrails/issues/473) (lower conf., single anecdotal report of broken streaming + 30s→80s latency blowup); [guardrailsai.com streaming docs](https://www.guardrailsai.com/docs/concepts/streaming) (high conf., official — sentence-boundary buffering, `on_fail="reask"` unsupported while streaming); several guardrailsai.com blog posts and two 404'd NVIDIA/Guardrails-AI doc pages (inaccessible, not used as evidence).

### Round 2 contradiction map

- All four round-2 conflicts/gaps were resolved with more nuance rather than eliminated (Findings 2–4). No new material conflicts emerged that would change candidate rankings.
- The two remaining gaps — no ensemble evasion data; Guardrails AI/`PIIMiddleware` untested against the 2504.11168 suite — are stated as unknowns in the verdict rather than chased into round 3, since the data doesn't yet exist in the literature.

### Moderator loop decision

Two rounds completed (minimum met). No round 3: the outstanding items are absence-of-evidence gaps, not open conflicts a third search round would resolve — carried into the report as stated unknowns.

### Peer review detail

- **Confidence rationale:** findings 1, 3, 4 rest on official first-party documentation and/or directly-read source code (high confidence). Finding 2 rests on a single empirical paper with disclosed methodology but no independent replication (capped at 8). Finding 5 rests on one official vendor doc without independent cross-verification of the exact opt-out mechanics (7).
- **Bias check detail:** of 9 sub-agents (5 round 1 + 4 round 2), 2 were adversarial-safety-framed (red-team, classifier-robustness) — well-evidenced, but may have pulled the synthesis toward over-weighting adversarial coverage relative to a typical production app's exposure.
- **Missing lens detail:** a threat-model lens — "who can reach this agent, and what can a successful bypass actually do" (read-only chatbot vs. financial/destructive tool access) — would let the report weight candidate 4 with much higher confidence.
