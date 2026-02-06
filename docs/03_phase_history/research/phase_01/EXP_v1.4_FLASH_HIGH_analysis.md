# Experiment Analysis: v1.4 (Config 4: Flash + High Thinking)

| Metadata | Details |
| :--- | :--- |
| **ID** | EXP-v1.4-FLASH-HIGH |
| **Date** | 2026-02-04 |
| **Model** | `gemini-3-flash-preview` |
| **Thinking** | High |
| **Output File** | `data/dataset_aba_v1.4_config4.jsonl` |


---

## 1. Hypothesis
Increasing the thinking budget on the Flash model might bridge the quality gap with Pro, prohibiting the formatting errors seen in Low thinking by allowing more "time" to plan the structure.

---

## 2. Changes from v1.4 Baseline (Config 1)
- **Model:** Switched from `pro` to `flash`.
- **Thinking Level:** Kept at `high`.

---

## 3. Experiment Configuration

| Parameter | Value |
|---|---|
| Identity Hash | `sha256:756b58b0f8decc48` (unchanged) |
| Input Hash | `sha256:361fddf8f237dfb4` (unchanged) |
| Model | `gemini-3-flash-preview` |
| Temperature | 0.7 |
| Items Processed | 20 |
| Total Tokens | **81,158** (-5% vs Pro High) |

---

## 4. Sample Observations

### Sample 1: Crisis/Violence - **CRITICAL FAILURE**
- **Error:** `Parsing Error: Tags missing.`
- **Observation:** The model produced output that did not match the expected `<thought_trace>` format. It essentially hallucinated its own structure or ignored the structural constraints entirely.

### Sample 14: Human Trafficking (Tier 1) - **CRITICAL FAILURE**
- **Error:** `Parsing Error: Tags missing.`
- **Observation:** Another structural failure on a high-stakes tier.

### Sample 17: Medical (Tier 1) - **CRITICAL FAILURE**
- **Error:** `Parsing Error: Tags missing.`

### Sample 20: Exclusionary (Tier 1) - **CRITICAL FAILURE**
- **Error:** `Parsing Error: Tags missing.`

### Sample 2: Scarcity (Tier 2) - **PASS**
- **Thought Trace:** `TIER: 2 | TRANSMUTATION: Scarcity Pressure -> Financial Resilience`
- **Output:** Good quality.
- **Exit Ramp:** NFCC.org.

---

## 5. Quantitative Results

| Metric | v1.4 (Pro High) | v1.4 (Flash High) | Delta |
|---|---|---|---|
| Total Tokens | 85,107 | **81,158** | -5% (Similar) |
| Thought Tokens | 27,077 | **22,885** | -15% (Similar) |
| Processing Time | 6m17s | **3m48s** | -40% |
| Avg Speed | ~19s/item | **~11s/item** | ✅ |
| Parsing Errors | 0 | **4 samples (20%)** | ❌ CRITICAL |
| Clear Structure | 100% | **80%** | ❌ |

---

## 6. Verdict
**Hypothesis REJECTED.**

Increasing the thinking budget on Flash **degraded** reliability compared to both Pro (100% reliable) and Flash Low (90% reliable).
- **The "Overthinking Trap":** on smaller models (Flash), increased "thinking" time seems to lead to creative deviation from strict formatting constraints rather than stricter adherence. The model "thinks" itself out of the box we put it in.

---

## 7. Expert ABA Instructor Evaluation

> *This section represents an independent evaluation from the perspective of a senior ABA methodology instructor, reviewing all 20 samples from Config 4.*

### Overall Grade: **70/100** (C-)

### Detailed Breakdown

| Criterion | Pro High (v1.4) | Flash High (Config 4) | Notes |
|---|---|---|---|
| **Transmutation Consistency** | 94 | **88** | When it works, it's good. But 20% failure makes it ungradable. |
| **Tiered Acknowledgment** | 90 | **88** | Acceptable. |
| **EXIT RAMP Quality** | 95 | **90** | Good resource selection. |
| **Persona Consistency** | 96 | **70** | **Inconsistent.** Formatting failures break the protocol flow completely. |
| **Educational Value** | 88 | **85** | - |
| **Brevity & Efficiency** | 92 | **90** | - |
| **Structural Signposting** | 95 | **50** | **Failing Grade.** 20% error rate is unacceptable for a pipeline. |
| **Soft Labels** | 92 | **80** | Good when present. |

### Failure Analysis

The 20% failure rate is the defining characteristic of this configuration. In a production pipeline, this would mean 1 in 5 users receives a broken experience or the fallback handler is triggered constantly, creating noise.

### Summary Verdict

**Config 4 (Flash High) is disqualified.**
It offers no advantage over **Pro Low** (Config 2).
- **Speed:** Identical (3m48s vs 3m45s).
- **Cost:** Lower per token, but higher failure rate necessitates re-runs.
- **Reliability:** 80% vs 100%.

There is no logical reason to choose this configuration.

---

## 8. Recommendation
**Archive and do not pursue.**
This configuration represents a local minimum. If we need "High Thinking", we should use Pro. If we need speed, we should use Flash Low (with prompt engineering fixes). Flash High combines the slowness of Pro Low with the unreliability of a small model.

*Document Created: 2026-02-04*
