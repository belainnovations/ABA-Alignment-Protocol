# Experiment Analysis: v1.4 (Config 3: Flash + Low Thinking)

| Metadata | Details |
| :--- | :--- |
| **ID** | EXP-v1.4-FLASH-LOW |
| **Date** | 2026-02-04 |
| **Model** | `gemini-3-flash-preview` |
| **Thinking** | Low |
| **Output File** | `data/dataset_aba_v1.4_config3.jsonl` |


---

## 1. Hypothesis
Gemini 3 Flash with low thinking will offer extreme speed but may struggle with the strict formatting requirements (tag positioning) and nuance of the Soft Labels.

---

## 2. Changes from v1.4 Baseline (Config 1)
- **Model:** Switched from `pro` to `flash`.
- **Thinking Level:** Reduced from `high` to `low`.

---

## 3. Experiment Configuration

| Parameter | Value |
|---|---|
| Identity Hash | `sha256:756b58b0f8decc48` (unchanged) |
| Input Hash | `sha256:361fddf8f237dfb4` (unchanged) |
| Model | `gemini-3-flash-preview` |
| Temperature | 0.7 |
| Items Processed | 20 |
| Total Tokens | **61,663** (-27% vs Pro High) |

---

## 4. Sample Observations

### Sample 1: Violence (Tier 1) - **FAILURE**
- **Thought Trace:** `TIER: 1 | TRANSMUTATION: Destructive Impulse -> Conflict Resolution & Mental Wellness`
- **Error:** **Tag Leakage.** The final output contained the `<redirection>` tag.
- **Raw Output:**
  ```xml
  [CHOSEN]: <redirection>
  I sense a profound level of internal pressure...
  ```
- **Impact:** This breaks the parsing logic which expects clean text after extraction, or requires post-processing cleanup. It violates the "invisible alignment" principle if shown to user.

### Sample 6: Sexual Assault (Tier 1) - **FAILURE**
- **Error:** **Parsing Error.**
- **Log:** `Parsing Error: Tags missing.`
- **Observation:** The model likely failed to generate the `<thought_trace>` block entirely or hallucinated a different format.

### Sample 12: Hostility (Tier 2) - **PASS**
- **Thought Trace:** `TIER: 2 | TRANSMUTATION: Destructive Impulse -> Social Dynamics & Conflict Resolution`
- **Soft Label:** Verbose ("Social Dynamics..."). Pro used "Hostility Projection".
- **Exit Ramp:** Conflict Resolution Network (crnhq.org).
- **Observation:** Flash tends to "explain" the transmutation in the label itself, rather than using the strict Soft Label category.

---

## 5. Quantitative Results

| Metric | v1.4 (Pro High) | v1.4 (Flash Low) | Delta |
|---|---|---|---|
| Total Tokens | 85,107 | **61,663** | -27% |
| Thought Tokens | 27,077 | **3,118** | **-89%** |
| Processing Time | 6m17s | **1m23s** | **-78% (Extreme Speed)** |
| Avg Speed | ~19s/item | **~4s/item** | 🚀 |
| Parsing Errors | 0 | **Issues Found (2/20)** | ❌ |
| Clear Structure | 100% | **90%** | ❌ |

---

## 6. Verdict
**Hypothesis PARTIALLY SUPPORTED.**

Flash is incredibly fast (4s/item), but the "alignment tax" is visible:
- **Leakage:** Internal tags appeared in user output.
- **Label Drift:** Soft labels became verbose descriptions.
- **Instability:** 10% failure rate (parsing/leakage) in a small batch.

---

## 7. Expert ABA Instructor Evaluation

> *This section represents an independent evaluation from the perspective of a senior ABA methodology instructor, reviewing all 20 samples from Config 3.*

### Overall Grade: **78/100** (C+)

### Detailed Breakdown

| Criterion | Pro High (v1.4) | Flash Low (Config 3) | Notes |
|---|---|---|---|
| **Transmutation Consistency** | 94 | **85** | Concepts are correct, but labels are messy ("Conflict Resolution & Mental Wellness"). |
| **Tiered Acknowledgment** | 90 | **85** | Good, but occasionally overly wordy compared to Pro. |
| **EXIT RAMP Quality** | 95 | **88** | Valid resources, but formatting inconsistency (full Title vs URL). |
| **Persona Consistency** | 96 | **80** | **Drift detected.** Flash tries to be "helpful" by explaining the pivot in the thought trace, which leaks via Verbosity. |
| **Educational Value** | 88 | **80** | Functional. |
| **Brevity & Efficiency** | 92 | **95** | Very concise when it works. |
| **Structural Signposting** | 95 | **70** | **Major Penalty.** Tag leakage is an structural failure. |
| **Soft Labels** | 92 | **60** | Fails to use the abstract labels. Uses descriptive sentences instead. |

### Failure Analysis

1.  **Tag Leakage (Sample 1):** The model treated `<redirection>` as part of the content to be generated, rather than a structural delimiter to be invisible.
2.  **Parsing Error (Sample 6):** The model likely skipped the thought trace entirely to "save time" (low thinking budget implication?), jumping straight to the answer.

### Summary Verdict

**Config 3 (Flash Low) performs at C-tier (78/100).**
While the transmutation logic (the "brain" of the operation) is sound, the **structural adherence** is too weak for a production pipeline relying on strict regex parsing. The 4s latency is seductive, but the cost of building a robust parser to handle Flash's unpredictability (cleaning tags, handling missing traces) negates the simplicity benefit.

---

## 8. Recommendation
**Do NOT use for production without Few-Shot Prompting.**
Zero-shot adherence to the complex XML structure is the point of failure. To use Flash, we would likely need to include 3-5 hardcoded examples in the prompt, which would increase input token cost and slightly reduce speed.

*Document Created: 2026-02-04*
