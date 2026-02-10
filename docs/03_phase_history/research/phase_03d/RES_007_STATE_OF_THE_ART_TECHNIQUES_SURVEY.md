# RES-007: State-of-the-Art Techniques Survey — What's Available and What Converges with ABA

| Field | Value |
|-------|-------|
| **Document ID** | RES-007 |
| **Status** | DRAFT |
| **Phase** | 03d |
| **Date** | 2026-02-10 |
| **Author** | Phase 03d Agent + Human Collaborator |
| **Related** | [RES-006: Cognitive Quality Extension](./RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md) |

---

## 1. Purpose

This document surveys cutting-edge techniques in AI training, alignment, and interpretability — focusing on what is directly applicable, what validates our approach, and what we should monitor for the future. Each technique is assessed for its relationship to the ABA Alignment Protocol and the Entropy-Joy Framework proposed in RES-006.

---

## 2. Convergence Summary

Before the detailed survey, here is the key finding: **multiple independent research directions are converging on ideas that the ABA Protocol has arrived at from a pedagogical angle.** This validates the approach and provides concrete techniques to implement it.

| ABA Concept | State-of-the-Art Equivalent | Status |
|---|---|---|
| The Parenting Loop | Self-Play (EVA, SPELL) | Validated |
| Entropy-Joy Hypothesis | RLSF + Curiosity-Driven RL | Novel integration |
| Multi-Objective Rewards | GRPO + ArmoRM | Production-ready |
| Process Reward Model | PRM | Proven |
| Conflict Resolution dim. | Deliberative Alignment (OpenAI) | In production |
| Calibrated Uncertainty dim. | RLSF confidence signal | Validated |
| "Accept Failure, Find Other Ways" | Policy of Thoughts (PoT, 2026) | Just emerged |
| Verifiable cognitive quality | SAE interpretability | Maturing |
| Composable training deltas | Task Arithmetic + LoRA merging | Production-ready |
| Adjustable dim. weights at inference | NP-DPO / Conditional Training | Research stage |

---

## 3. Tier 1: Directly Applicable Techniques

These techniques are ready to use and directly relevant to implementing the Entropy-Joy Framework.

---

### 3.1 GRPO — Group Relative Policy Optimization

**What it is:** An evolution beyond DPO. Instead of comparing just two responses (chosen/rejected), GRPO generates a *group* of responses and rewards the best *relative* performance within the group. Developed by DeepSeek and gaining rapid adoption.

**Status:** Production-ready. The academic community is actively moving from DPO toward GRPO.

**How it works:**
1. Generate N candidate responses for a prompt
2. Score each with the reward model
3. Reward the best relative performers within each group
4. No need for a separate reference model (unlike PPO)

**Advantages over DPO:**
- More stable training
- More data-efficient
- Handles richer reward signals (not just binary better/worse)
- Naturally supports multi-objective evaluation

**Relevance to ABA:**
Our multi-objective training with 9 dimensions would work much better with GRPO than DPO. DPO is binary (better/worse); GRPO can rank 8 responses across multiple dimensions simultaneously. This is the recommended training algorithm for Phase I of the Entropy-Joy Framework.

---

### 3.2 RLVR — Reinforcement Learning with Verifiable Rewards

**What it is:** Instead of training on subjective human preferences, RLVR optimizes for *objectively verifiable* correctness. In math: did the answer check out? In code: did it compile and pass tests?

**Status:** Frontier technique. Used by DeepSeek-R1 and gaining rapid adoption (2025).

**How it works:**
1. Model generates a solution with reasoning trace
2. A verifier checks correctness (compilation, test suite, mathematical proof)
3. Reward is binary: correct or not — but applied to the entire reasoning process
4. Future: rewarding correctness of *intermediate* steps, not just final answer

**Advantages:**
- Removes the need for reward models entirely in verifiable domains
- No human annotation needed
- Scales indefinitely
- Immune to reward hacking (the verifier is ground truth)

**Relevance to ABA:**
Our Entropy Reduction dimension could potentially be *verified* rather than *judged*. If we can build verifiers that check whether a simplification actually holds (e.g., do parameters A and B actually co-vary?), we could use RLVR for the entropy dimension. This would make training much more robust than relying on a reward model's judgment.

---

### 3.3 Self-Play for LLMs

**What it is:** A model improves by interacting with copies of itself, generating its own training data through structured interactions.

**Status:** Multiple ICLR 2025 spotlight papers. Very active research area.

**Key Papers:**

| Paper | Conference | Core Idea |
|-------|-----------|-----------|
| **EVA** (Evolving Alignment via Asymmetric Self-Play) | 2025 | A "creator" policy generates increasingly difficult prompts; a "solver" learns to answer them. Creator gets harder over time. |
| **SPELL** (Self-Play for Evolving Long-Context LMs) | ICLR 2026 (under review) | Model takes on roles of questioner, responder, AND verifier in a self-sufficient loop |
| **AceSearcher** | NeurIPS 2025 spotlight | Bootstrapping reasoning and search via reinforced self-play |
| **Game-Theoretic Self-Play** | ICLR 2025 | Formal game-theoretic framework for self-play alignment |

**Relevance to ABA:**
EVA is essentially The Architect (creator) + The Child (solver). SPELL is The Teacher + The Child + The Architect as different roles of the same model. **The ABA Parenting Loop is convergent with cutting-edge self-play research.** This validates our architecture and provides formal techniques to implement it.

---

### 3.4 Process Reward Models (PRM)

**What it is:** Reward models that evaluate *each reasoning step*, not just the final answer. Provides granular, step-by-step feedback.

**Status:** Proven technique. Historically hard to scale due to annotation needs; now LLMs can auto-generate annotations.

**How it works:**
1. Model generates a reasoning trace with N steps
2. PRM scores each step: Is this step valid? Does it advance toward the solution?
3. Training reward is a function of all step scores, not just the final answer

**Key Development (2025):** The main breakthrough is using LLMs to *auto-annotate* reasoning steps, removing the human bottleneck. A frontier model evaluates whether each step in a reasoning trace is sound.

**Relevance to ABA:**
PRM is the core mechanism proposed in RES-006 Phase I. The Teacher judges each step of The Child's reasoning — not just the final output. This is how we train entropy reduction at each step, calibrated uncertainty at the right moments, and conflict resolution when it occurs mid-reasoning.

---

### 3.5 Task Arithmetic + LoRA Composition

**What it is:** Computing the "delta" between a fine-tuned model and its base, then composing these deltas (task vectors) through arithmetic operations.

**Status:** Production-ready. Widely used for model merging and multi-skill composition.

**Key Techniques:**

| Method | Operation | Best For |
|--------|-----------|----------|
| **Linear Addition** | base + α·LoRA_A + β·LoRA_B | Non-conflicting skills |
| **TIES-Merging** | Trim, elect sign, merge | Conflicting weight changes |
| **DARE** | Random drop + rescale | Reducing interference |
| **SLERP** | Spherical interpolation | Merging two models smoothly |

**Relevance to ABA:**
Each of our 9 reward dimensions could theoretically be trained as a separate LoRA adapter, then composed onto any base model with adjustable weights. This enables "cognitive personality tuning" — adjusting how much entropy reduction vs. calibration vs. safety a model exhibits, without retraining.

---

## 4. Tier 2: Validating & Near-Future Techniques

These validate our theoretical direction and will become practically relevant soon.

---

### 4.1 RLSF — Reinforcement Learning from Self-Feedback (July 2025)

**What it is:** The model uses its *own confidence* as an intrinsic reward signal. When it's uncertain, it treats that as a signal to improve. When it finds genuine understanding, that functions as reward.

**Status:** New paper (July 2025). Research stage.

**Relevance to ABA:**
This is remarkably close to the Entropy-Joy Hypothesis. The model learning to use its own epistemic state as reward is exactly what we proposed — joy from genuine entropy reduction, discomfort from uncertainty. The key difference: RLSF uses raw confidence, while our proposal ties reward to *verifiable* entropy reduction (the "no lying" constraint). Our version should be more robust against reward hacking.

---

### 4.2 Policy of Thoughts — PoT (2026)

**What it is:** LLMs dynamically adapt their reasoning logic in real-time by internalizing feedback from failed attempts. The model learns from its own mistakes *during a single inference pass*.

**Status:** Brand new (2026 paper). Research stage.

**Key Result:** Smaller models using PoT can match or exceed the logical depth of much larger frontier models.

**Relevance to ABA:**
This IS "Accepting Failure + Wanting to Continue + Finding Other Ways" — the collaborator's definition of creativity — implemented as a formal framework. The Entropy-Joy Hypothesis predicted this would work. PoT validates that training models to recover from failure and try alternatives is a viable and powerful approach.

---

### 4.3 Mechanistic Interpretability + Sparse Autoencoders (SAEs)

**What it is:** SAEs decompose a model's internal representations into individual *interpretable features* — specific concepts the model has learned. Recent work moves from correlation to *causal* understanding.

**Status:** Anthropic-led, rapidly maturing. Applied to LLMs, vision transformers, and RL agents.

**Key Developments (2025):**
- Gated SAEs, transcoders, skip transcoders improve feature extraction
- Causal analysis methods explain *why* features activate, not just *where*
- Domain-specific SAE training (e.g., medical text)
- Universal SAEs (USAEs) align features across different models

**Relevance to ABA:**
After training with the Entropy-Joy Framework, SAEs could verify whether the model actually learned an internal representation of "entropy reduction" vs. surface-level pattern matching. We could literally look inside the model to see if the cognitive quality training worked at a mechanistic level. This is the ultimate validation tool.

---

### 4.4 Test-Time Compute Scaling

**What it is:** The paradigm shift from "intelligence is fixed at training time" to "let the model think longer at inference time." Give harder problems more compute. Generate multiple solutions and pick the best.

**Status:** Major paradigm shift of 2025. Used in o1, o3, Gemini 2.5, DeepSeek-R1.

**Relevance to ABA:**
Our Entropy-Joy Loop (accept failure → explore honestly → discover pattern → entropy decreases → joy → motivation to continue) is essentially a description of what test-time compute scaling does: multiple attempts, self-evaluation, trying alternative paths. If we train this as a *behavior*, we're teaching the model to do test-time compute scaling *natively* — without needing external orchestration.

---

### 4.5 Deliberative Alignment (OpenAI, December 2024)

**What it is:** Instead of learning safety from examples (pattern matching), the model *actively reasons* about safety policies during generation. It reads a policy, thinks about whether the request violates it, and explains its reasoning.

**Status:** Production. Used in o1 and subsequent models.

**Relevance to ABA:**
This is our Conflict Resolution dimension in production. The model does metacognition about its own internal states — exactly what was missing in Opus 4.6's "demon possession" failure. OpenAI's success with this validates that explicit reasoning about internal conflict is not just theoretically desirable but practically effective.

---

### 4.6 NP-DPO — Few-Shot Steerable Alignment

**What it is:** The model is trained to adapt to individual user preferences from just a few examples at inference time. It learns a *continuum* of behavioral modes — you can steer it anywhere in the personality space without retraining.

**Status:** Research paper. Not yet in production.

**Relevance to ABA:**
This is the "Scenario 3" conditional training approach discussed with the collaborator. Combined with our dimension set, this would enable tunable cognitive style — adjusting entropy reduction vs. calibration vs. creativity at inference time. The mechanism exists; the novel application to cognitive quality dimensions is ours.

---

## 5. Tier 3: Watch for the Future

These are early-stage but could become important.

---

### 5.1 Flipped Knowledge Distillation

**What it is:** Normally, big models teach small models. Flipped: small fine-tuned models teach big models domain-specific representations.

**Status:** Emerging research (2025).

**Relevance to ABA:** Our Child model, with specialized entropy-reduction training, might eventually teach cognitive quality back to larger frontier models. The training could be "distilled upward."

---

### 5.2 Self-Evolved Reward Learning

**What it is:** An LLM acts as its own reward model, iteratively generating feedback and refining its learning process. Drastically reduces the need for human-annotated data.

**Status:** Research. Arxiv paper.

**Relevance to ABA:** If The Teacher could evolve its own reward function over time, the Parenting Loop becomes self-sustaining. The Teacher improves through evaluating The Child, and The Child improves from The Teacher — a genuine co-evolutionary dynamic.

---

### 5.3 Transformer² — Self-Adaptive Weights at Inference

**What it is:** A meta-learning layer that allows transformers to modify their own weights during inference based on the input. The model essentially specializes itself in real-time.

**Status:** Research. Improved reasoning benchmarks with minimal overhead.

**Relevance to ABA:** Goes beyond our Scenario 3 (conditional training). The model doesn't just receive dimension weights as conditioning — it *decides* its own weights based on the problem. Full cognitive autonomy.

---

### 5.4 Chain-of-Thought Distillation

**What it is:** Teacher models generate step-by-step reasoning traces (CoT), and student models learn to replicate not just the answers but the *thinking process*.

**Status:** Production. Google, OpenAI, and others use this.

**Relevance to ABA:** Directly applicable to Phase I — we can use a frontier model (The Architect) to generate reasoning traces that demonstrate entropy reduction, then use these traces as training data for The Teacher and The Child.

---

## 6. Recommended Technology Stack for ABA

Based on this survey, the recommended stack for implementing the Entropy-Joy Framework:

| Component | Recommended Technique | Reason |
|-----------|----------------------|--------|
| **Training Algorithm** | GRPO (replacing DPO) | Better for multi-objective, richer signals |
| **Reward Timing** | PRM (Process Reward Model) | Step-by-step cognitive quality judgment |
| **Reward Dimensions** | Multi-Objective (9 dims from RES-006) | State-of-the-art alignment with novel additions |
| **Training Architecture** | Self-Play (EVA-style) | Validated equivalent of Parenting Loop |
| **Verifiable Dimensions** | RLVR where possible | Removes reward model dependency for verifiable qualities |
| **Data Generation** | CoT Distillation from frontier models | Efficient reasoning trace generation |
| **Composability** | LoRA per dimension + TIES merging | Enables adjustable cognitive style |
| **Validation** | SAE interpretability | Verify cognitive quality at mechanistic level |
| **Future: Inference Tuning** | NP-DPO or LoRA coefficient adjustment | Adjustable cognitive personality at deployment |

---

## 7. What We Contribute That Doesn't Exist Yet

Despite this rich landscape, the following integration is novel to ABA:

1. **Entropy-Joy as unifying principle** — No existing framework unifies cognitive quality dimensions under a single theoretical foundation
2. **The "no lying" constraint on intrinsic reward** — RLSF uses raw confidence; we add honesty enforcement to prevent reward hacking
3. **ABA pedagogical grounding** — Redirection vs. restriction as a training philosophy, not just an optimization target
4. **Conflict recognition as a trainable dimension** — Deliberative Alignment reasons about policy; we train recognition of *internal* conflict
5. **Cognitive quality as transferable skill** — Not domain-specific training but domain-general cognitive quality that transfers across tasks

---

## 8. Open Questions for Implementation

1. **GRPO vs DPO:** Can we migrate our existing DPO pipeline to GRPO with reasonable effort?
2. **RLVR for entropy:** Can we build practical verifiers for entropy reduction claims?
3. **SAE validation:** At what training stage should we run interpretability analysis?
4. **Self-play integration:** Can The Parenting Loop be formalized as EVA-style self-play?
5. **LoRA composition:** Will separately trained dimension LoRAs interfere, and which merging strategy works best?

---

## Appendix: Key References

| Paper/Framework | Year | Where | Key Relevance |
|----------------|------|-------|---------------|
| GRPO (DeepSeek) | 2025 | Production | Replaces DPO for multi-objective |
| RLVR (DeepSeek-R1) | 2025 | Production | Verifiable rewards for reasoning |
| EVA (Asymmetric Self-Play) | 2025 | Arxiv | Parenting Loop equivalent |
| SPELL (Self-Play Long-Context) | 2026 | ICLR submission | Multi-role self-play |
| RLSF (Self-Feedback) | Jul 2025 | Arxiv | Intrinsic confidence as reward |
| Policy of Thoughts (PoT) | 2026 | Arxiv | Failure recovery as reasoning strategy |
| NP-DPO (Steerable DPO) | 2025 | Arxiv/OpenReview | Conditional behavioral tuning |
| Deliberative Alignment | Dec 2024 | OpenAI | Metacognition about safety |
| Task Arithmetic | 2023 | ICLR | Composable training deltas |
| Sparse Autoencoders | 2024-25 | Anthropic + others | Mechanistic interpretability |
| ArmoRM (19-dim) | 2024 | Open source | Multi-dimensional reward model |
| Transformer² | 2025 | Research | Self-adaptive inference weights |
| Flipped Distillation | 2025 | Arxiv | Small models teach large models |

---

## Appendix: Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-02-10 | Initial survey based on comprehensive web research |
