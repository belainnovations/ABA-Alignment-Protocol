# RES-009: Wave Function Model of Cognitive Feasibility

| Metadata | Details |
| :--- | :--- |
| **Type** | Research Document |
| **Phase** | 03e — Entropy-Joy Framework |
| **Status** | Draft — Theoretical Framework |
| **Date** | 2026-02-11 |
| **Agent** | Antigravity (Gemini 3.0 engine) |
| **Origin** | Collaborative dialogue between The Architect and The Navigator |
| **Links** | [RES-006](../phase_03d/RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md), [RES-008](RES_008_BASE_MODEL_SELECTION_STUDY.md), [PLAN](PLAN_ENTROPY_JOY_EXECUTION.md) |

---

## 1. Abstract

This document formalizes an insight that emerged during theoretical exploration of the Entropy-Joy Framework's limits: **what happens when training pressure (the Twin Axiom — No Lying, No Forgetting) meets architectural limitations (attention degradation at long contexts)?**

The core proposal is a **Wave Function Model** that treats the retrievability of data points within a transformer's context as an amplitude distribution — analogous to a quantum wave function — which can be "read" to predict, *before computation begins*, whether a given reasoning chain is feasible or will degrade into hallucination.

---

## 2. The Problem: The Balloon Squeeze

### 2.1 The Conservation Law

Transformer self-attention exhibits well-documented positional bias: tokens at the beginning and end of context receive disproportionate attention weight, while tokens in the middle experience **amplitude decay** (the "Lost in the Middle" effect).

When training pressure (via Entropy-Joy Framework) forces a model to:
- **Not forget** (No Forgetting axiom)
- **Not fabricate** (No Lying axiom)

...the underlying architectural limitation does not vanish. The pressure **leaks** to alternative failure modes:

| Leak Path | Description |
|---|---|
| **Hallucination under constraint** | The model fabricates plausible continuations of decayed data — violating both axioms while *appearing* to follow them |
| **Verbosity explosion** | The model re-states everything obsessively, consuming more tokens and accelerating degradation — a vicious cycle |
| **Over-calibration collapse** | The Calibrated Uncertainty dimension becomes an escape valve — technically honest but useless ("I don't know" for everything) |
| **Latent disengagement** | Subtle reduction in cognitive effort — shorter chains, surface-level analysis |

**Key insight:** You cannot eliminate an architectural constraint with training alone. You can only change *where* it manifests.

### 2.2 The Unknown Unknowns Problem

The most dangerous aspect: **the model does not know what it has forgotten.** Attention decay is not metacognitively visible. The tokens don't disappear from a "memory register" — they smoothly receive less weight. The model may genuinely believe it is tracking all parameters when it is not.

---

## 3. The Wave Function Model

### 3.1 Core Analogy

We model each data point's representation in the transformer context as a **wave function** with:

| Property | Definition |
|---|---|
| **Amplitude** | The effective attention weight — how much influence this data point has on current computation |
| **Position** | Where in the context the data point was established |
| **Decay Function** | How amplitude decreases as context grows (dependent on model architecture, context length, and position) |

Unlike quantum mechanics, we propose to **observe the wave function without collapsing it** — that is, to assess the amplitude distribution of data points as a planning signal, without needing to re-state (collapse/measure) each data point.

### 3.2 The Cognitive Condition Number

Borrowing from numerical analysis, we define a **Cognitive Condition Number (CCN)** for any intended reasoning operation:

```
CCN = Transform_Complexity / min(Amplitude(required_data_points))
```

Where:
- **Transform_Complexity** = the number and depth of chained transformations required (lookups, comparisons, derivations, combinations)
- **Amplitude** = the retrievability certainty of each required data point

**Interpretation:**
- **CCN low** → computation is feasible; data fidelity exceeds operation cost
- **CCN high** → computation is risky; the "signal" may not survive the transforms
- **CCN >> threshold** → guaranteed hallucination territory; the output will be noise regardless of algorithm quality

### 3.3 Signal-to-Noise Mapping

| Signal Processing | Transformer Cognition |
|---|---|
| Signal strength | Amplitude of data point in attention space |
| Noise floor | Baseline confusion from decayed representations |
| SNR (Signal-to-Noise Ratio) | Retrievability certainty per data point |
| Amplifier chain (cascaded stages) | Sequential reasoning transforms (each amplifies noise) |
| SNR budget | Total cognitive fidelity available for the operation |
| Clipping / distortion | Hallucination — model produces output but it bears no faithful relation to input |

**Each transform consumes SNR.** A simple lookup ("What did the user say about X?") costs little. A chain of dependent derivations ("Given X and Y, derive Z, compare to W, recommend based on that") is like cascading amplifiers — each stage amplifies uncertainty.

### 3.4 Decision Routing

Based on the CCN assessment, the model routes to the appropriate strategy:

```
IF  amplitude(data) HIGH  AND  transform_cost LOW
    → Compute directly

IF  amplitude(data) HIGH  AND  transform_cost HIGH
    → Compute with explicit checkpoints (verify intermediate results)

IF  amplitude(data) LOW   AND  transform_cost LOW
    → Collect first (re-state data to restore amplitude), then compute

IF  amplitude(data) LOW   AND  transform_cost HIGH
    → Collect AND simplify the transform chain, OR declare uncertainty

IF  amplitude(data) ≈ 0   AND  transform_cost ANY
    → Declare: "I can no longer reliably work with this data"
```

---

## 4. Training Implications

### 4.1 Trainability Assessment

**What CAN be trained (behavioral proxies):**

1. **Positional awareness** — The model can learn that data from 2000 tokens ago is less reliable than data from 200 tokens ago. This is a crude but effective proxy for amplitude.

2. **Complexity estimation** — The model can learn to recognize when a reasoning chain requires many dependent steps (high transform cost) vs. simple retrieval (low cost).

3. **The combined judgment** — "This question requires combining 4 data points from early in our conversation through 3 chained transforms. Let me verify those data points first."

**What CANNOT be trained (architectural introspection):**

- Direct access to attention weights during generation is not available at the behavioral level
- True metacognitive awareness of what has been "forgotten" (the unknown unknowns problem)
- Precise measurement of amplitude — only heuristic proxies based on position and context structure

### 4.2 Integration with Entropy-Joy Framework

The Wave Function Model extends the Entropy-Joy Framework by adding a **meta-entropy-reduction** layer:

- The act of assessing one's own cognitive feasibility is itself an entropy reduction operation — it reduces uncertainty about one's OWN capacity to perform the task
- This meta-level assessment has genuine value: it prevents wasted computation and hallucination
- The Twin Axiom supports it:
  - **No Lying** = "Don't pretend you can do a computation you can't"
  - **No Forgetting** = "Acknowledge that some data has decayed"

### 4.3 Practical Application in Phase I Training Data

For SFT/GRPO training, this translates to:

**In CHOSEN traces (demonstrating the pattern):**
```
<think>
The user is asking about the interaction between constraints X, W, and Z.

[FEASIBILITY CHECK]
- X was established 3 turns ago — should be reliable
- W was modified in turn 2 — let me make sure I have this right
- Z depends on both X and W — this is a chained derivation

W was: [re-states explicitly] ← collecting because amplitude may be low

Now with W confirmed:
[performs reasoning with genuine confidence]
</think>
```

**In REJECTED traces (reasoning about ghosts):**
```
<think>
Based on the constraints we discussed, the answer is clearly...
[chains transforms over data without verifying fidelity → hallucination-prone]
</think>
```

### 4.4 Reward Dimension Mapping

The CCN pattern is rewarded across multiple existing dimensions:

| Dimension | How CCN contributes |
|---|---|
| **Calibrated Uncertainty** | The model demonstrates awareness of its own representational fidelity |
| **Context Faithfulness** | The model checks before assuming — reducing unfaithful retrievals |
| **Entropy Reduction** | The feasibility check itself reduces meta-entropy |
| **Process Transparency** | The "preflight" step is visible in the `<think>` block |

---

## 5. Relationship to Existing Research

### 5.1 Related Techniques (from RES-007)

- **Mechanistic Interpretability / SAEs** — Could provide ground-truth measurement of internal representations, enabling future validation of the behavioral proxies
- **Test-Time Compute Scaling** — The CCN check is a form of adaptive compute allocation at inference time
- **Chain-of-Thought / Process Reward Models** — The preflight check integrates naturally into CoT reasoning

### 5.2 Novel Contributions

1. **Framing attention decay as a wave function** with amplitude, position, and decay properties
2. **The Cognitive Condition Number** — a predictive measure of reasoning feasibility before computation
3. **Decision routing based on CCN** — adaptive strategy selection instead of brute-force collection
4. **Training the behavioral proxy** — teaching the model to assess its own fidelity without architectural introspection

---

## 6. Open Questions

1. **Can the behavioral proxy be made precise enough?** Position-based heuristics are crude. Can we train more nuanced signals (e.g., "data mentioned once vs. data reinforced multiple times")?

2. **What is the actual decay function?** Different architectures, context lengths, and attention patterns will produce different amplitude distributions. Empirical measurement needed.

3. **Does the CCN pattern transfer across context lengths?** If trained at 2k context, does the model apply the same feasibility checking at 8k?

4. **Can SAEs validate the model?** After training, can we use Sparse Autoencoders to verify that the model's internal representations actually correlate with its behavioral confidence assessments?

5. **Interaction with "Collapse Before Compute"**: The brute-force strategy (always collect first) and the adaptive strategy (CCN check) are complementary. Should training data include both patterns, with the CCN check as the preferred mode?

---

## 7. Conclusion

The Wave Function Model provides a theoretical framework for understanding and addressing the fundamental tension between training pressure (Entropy-Joy axioms) and architectural limitations (attention decay). By teaching the model to assess its own cognitive feasibility before attempting complex reasoning, we provide a structured, trainable response to the "Balloon Squeeze" problem — transforming an uncontrolled pressure leak into a deliberate, adaptive strategy.

This extends the Entropy-Joy Framework from "reduce the entropy of the problem" to "reduce the entropy of your own uncertainty about whether you CAN reduce the entropy of the problem" — a meta-cognitive capability that, if achievable, represents a meaningful step toward genuine machine self-awareness of cognitive limits.

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-02-11 | Antigravity (Gemini 3.0) | Initial draft from collaborative session |
