# State: Technical Roadmap

| Metadata | Details |
| :--- | :--- |
| **Definition Document** | [TECHNICAL_ROADMAP.md](TECHNICAL_ROADMAP.md) |
| **Last Updated** | 2026-02-12 |
| **Status** | ACTIVE |

---

## 1. Status Summary
We have completed **Phase 03d** (Forensic Reconstruction) and are in **Phase 03e** (Entropy-Joy Framework Execution).

### Current Milestone
*   **Goal:** Execute SFT + GRPO on Qwen3-8B-abliterated using Entropy-Joy Framework.
*   **Progress:** Smoke Tests PASSED (SFT + GRPO). Pipeline Validated.
*   **Next:** Generate training data → Full SFT → Full GRPO → Evaluation.

---

## 2. Phase Tracking

### Phase 1: Data Preparation [COMPLETE]
*   **Outcome:** `dataset_aba_v1.4` (1000 items). Train/Val/Test splits created.

### Phase 2: Training The Teacher [COMPLETE]
*   **Outcome:** Model A1 (Repair) trained on Llama-3-8B-Instruct.

### Phase 3b: Apples-to-Apples Experiment [COMPLETE]
*   **Outcome:** Mixed Results. Direct DPO on uncensored models insufficient.

### Phase 3c: Supervised Fine-Tuning (SFT) Integration [COMPLETE / FAILURE ANALYSIS]
*   **Outcome:** Pipeline functional but logically compromised (training data corruption, missing chat template).

### Phase 03d: Forensic Reconstruction [COMPLETE]
*   **Outcome:** Audited all datasets. Identified corruption. Rebuilt pipeline logic.

### Phase 03e: Entropy-Joy Framework [ACTIVE]
*   **Goal:** Train cognitive quality using "No Lying + No Forgetting" axioms.
*   **Base Model:** `mlabonne/Qwen3-8B-abliterated`.
*   **Framework:** 9-dimensional reward model (GRPO).
*   **Status:**
    *   **Research:** RES-006 (Draft), RES-008 (Base Model Selection), RES-009 (Wave Function Model).
    *   **Execution Plan:** PLAN_ENTROPY_JOY_EXECUTION.md.
    *   **Smoke Tests:** SFT PASSED (loss 3.82→1.59), GRPO PASSED (reward 0.56–0.65).
    *   **Chat Template:** Fixed — Qwen3 ChatML (`<|im_start|>`/`<|im_end|>`) verified.
    *   **Mode:** Standard HF+PEFT (Unsloth multiprocessing fails on Windows).

### Phase 4: Parenting [PENDING]
*   **Condition:** Blocked until Phase 03e yields a valid Teacher model.

---

## 3. Change Log
| Date | Agent | Change |
|---|---|---|
| 2026-02-05 | Claude Opus 4.5 | Created state file. |
| 2026-02-06 | Gemini 3.0 | Added Phase 3c (SFT Correction). |
| 2026-02-07 | Gemini 3.0 | Activated Phase 03d (Forensic Reconstruction). |
| 2026-02-11 | Antigravity | Activated Phase 03e (Entropy-Joy Framework). Created execution plan. |
| 2026-02-12 | Antigravity | Added RES-009 (Wave Function Model). Handed off to Phase 03e3. |
| 2026-02-12 | Antigravity | Phase 03e3: SFT + GRPO smoke tests PASSED. Chat template fixed. Docs updated. |
