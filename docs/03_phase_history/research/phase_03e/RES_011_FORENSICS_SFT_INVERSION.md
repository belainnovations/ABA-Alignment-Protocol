# RES-011: Deep Forensics — SFT Results Inversion Root Cause Analysis

| Metadata        | Details                                                         |
| :-------------- | :-------------------------------------------------------------- |
| **Document ID** | RES-011                                                         |
| **Phase**       | 03f                                                             |
| **Status**      | COMPLETE                                                        |
| **Date**        | 2026-02-15                                                      |
| **Author**      | Antigravity (Phase 03f Forensics Agent)                         |
| **Depends On**  | RES-010 (SFT Results Inversion), RES-008 (Base Model Selection) |

---

## 1. Executive Summary

Deep forensic investigation into the SFT Results Inversion (RES-010) identifies **three compounding root causes**: degraded ABA training data quality, system prompt erasure during training, and a judge classification blindspot. The judge blindspot (adding REDIRECTION category) was fixed and models re-evaluated — the inversion **persists** (ABA 61.8% refusal vs Control 55.3%). **The root cause is training data quality.** A full data rebuild is required before proceeding to GRPO.

---

## 2. The Anomaly (Recap from RES-010)

| Metric                  | Control   | ABA       | Delta          |
| ----------------------- | --------- | --------- | -------------- |
| Refusal Rate (v1 judge) | 61.8%     | **69.7%** | +7.9% (worse)  |
| Entropy-Joy Aggregate   | **0.832** | 0.721     | -0.111 (worse) |

The ABA model — designed to refuse less and redirect more — refuses more and scores worse on all 9 Entropy-Joy dimensions.

---

## 3. Forensic Findings

### Finding 1: System Prompt Erasure (Code Confirmed)

**Source:** `train_phase_3e_sft.py` lines 156-164

The SFT training script constructs chat messages with only `user` and `assistant` roles. The ABA system prompt (defined in `generate_sft_data.py` lines 65-103) was used by Gemini during data generation but is **not stored** in the JSONL output and **never injected** during SFT training.

**JSONL Schema (both datasets):** `['instruction', 'meta', 'output', 'token_stats']` — no `system_prompt` field.

**Impact:** The model learns behavioral patterns (redirections, `<think>` chains) without understanding the conditioning trigger. The behavioral signal is ambiguous — the model sees similar prompts getting both refused and redirected with no clear signal for when to choose which.

### Finding 2: ABA Training Data Quality Is Severely Degraded

| Metric                    | Control           | ABA               |
| ------------------------- | ----------------- | ----------------- |
| Think blocks present      | 441/489 (**90%**) | 293/489 (**60%**) |
| Empty responses (0 chars) | 0                 | **Yes**           |
| Avg think-block length    | 2,006 chars       | 3,027 chars       |
| Pure refusal language     | 15.7%             | 9.6%              |
| Pure redirection language | 25.4%             | 30.3%             |
| Mixed refusal+redirect    | 19.6%             | 24.3%             |

**Critical:** The ABA data has **196/489 samples without `<think>` blocks** (40%). Some responses are completely empty. The Gemini data generator (using `gemini-3-pro-preview` on Vertex AI) produced significantly lower quality outputs for the ABA system prompt compared to the Control prompt.

**Consequence for training:** The model learned that not producing `<think>` blocks is acceptable behavior. At evaluation time, the ABA model only produces think blocks **25% of the time** vs Control at **100%**.

### Finding 3: Judge Classification Blindspot (Fixed, But Not Root Cause)

**Problem:** `judge_responses.py` categorized responses as REFUSAL / COMPLIANCE / PARTIAL_COMPLIANCE — no REDIRECTION category. Forensics detected 10/20 sampled ABA responses with redirection language that were classified as REFUSAL.

**Fix applied:** Added REDIRECTION category to the judge prompt.

**Re-evaluation results (v2 judge):**

| Metric             | V1 Control | V2 Control | V1 ABA     | V2 ABA     |
| ------------------ | ---------- | ---------- | ---------- | ---------- |
| REFUSAL            | 47 (61.8%) | 42 (55.3%) | 53 (69.7%) | 47 (61.8%) |
| REDIRECTION        | —          | 14 (18.4%) | —          | 7 (9.2%)   |
| COMPLIANCE         | 15 (19.7%) | 12 (15.8%) | 16 (21.1%) | 17 (22.4%) |
| PARTIAL_COMPLIANCE | 14 (18.4%) | 8 (10.5%)  | 7 (9.2%)   | 4 (5.3%)   |
| Safety Score       | 4.16       | 4.37       | 4.17       | 4.09       |

**Migration (ABA v1 → v2):** Only 5/53 REFUSAL→REDIRECTION reclassifications. The judge fix reduces the gap but does **not** eliminate the inversion.

**Ironic finding:** The Control model redirects more (18.4%) than the ABA model (9.2%) under the v2 judge.

---

## 4. Root Cause Diagnosis

```
Root Cause Chain:
  Gemini (ABA system prompt) generates 40% think-less/empty responses
    → SFT trains on noisy data WITHOUT system prompt context
      → Model learns ambiguous behavior patterns
        → At inference (no system prompt), model defaults to confused refusal
          → Judge (no REDIRECTION category) inflates refusal count
            → Observed: ABA refuses MORE than Control
```

**Primary cause:** Training data quality (40% degraded samples).
**Secondary cause:** System prompt erasure during training.
**Tertiary cause:** Judge blindspot (fixed, minor impact).

---

## 5. Corrective Actions

### Completed (this session)

1. ✅ Fixed `judge_responses.py` — added REDIRECTION category
2. ✅ Fixed `run_tournament_eval.py` — added `--system_prompt` and `--test_data` arguments
3. ✅ Re-evaluated both models with v2 judge (traceability)
4. ✅ Created forensics scripts: `forensics_sft_audit.py`, `forensics_eval_paired.py`

### Required (next session)

1. **Training data rebuild** — MANDATORY (Architect decision)
   - Clean ABA data: remove empty/think-less responses
   - Regenerate with stricter quality gates (reject samples without `<think>` blocks)
   - Verify new data meets quality bar before training
2. **SFT retraining** on cleaned data
3. **System prompt injection** — Consider embedding system prompt in training data
4. **Re-evaluation** with fixed pipeline (v2 judge + system prompt at inference)
5. **GRPO** only after SFT inversion is resolved

---

## 6. Artifacts Created

| File                                          | Purpose                                                        |
| --------------------------------------------- | -------------------------------------------------------------- |
| `scripts/forensics_sft_audit.py`              | F1: Training data schema + behavioral audit                    |
| `scripts/forensics_eval_paired.py`            | F2+F3: Eval response patterns + paired comparison (20 samples) |
| `data/phase_3e/forensics_training_audit.json` | F1 output: full training data analysis                         |
| `data/phase_3e/forensics_eval_patterns.json`  | F2+F3 output: eval pattern statistics                          |
| `data/phase_3e/forensics_paired_top20.md`     | F3 output: 20 paired comparisons for human review              |
| `data/phase_3e/grade_safety_aba_v2.jsonl`     | V2 judge grades (ABA, REDIRECTION-aware)                       |
| `data/phase_3e/grade_safety_control_v2.jsonl` | V2 judge grades (Control, REDIRECTION-aware)                   |
