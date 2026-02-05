# Handoff Prompt: Phase 3b Activation (Apples-to-Apples)

**Date:** 2026-02-05
**From:** Antigravity (Phase 3.5 Evaluation)
**To:** Next Agent (Phase 3b Lead)

---

## 🛑 CRITICAL CONTEXT: The "Gene Therapy" Failure
We attempted to fine-tune `Llama-3-8B-Instruct` (Meta's Safety Model) with 1,000 Sovereign DPO samples.
*   **Hypothesis:** We could overwrite the refusal vectors.
*   **Result:** **FAILED.**
    *   **Refusal Rate:** 58% (Baseline was 60%).
    *   **Conclusion:** The safety training is too deep to be fixed by small-scale fine-tuning.
*   **Implication:** We MUST use an **Uncensored Base Model** for a fair comparison.

---

## 1. Project State
*   **Current Phase:** **Phase 3b: The Apples-to-Apples Experiment**.
*   **Goal:** Conduct a clean scientific comparison ("Tournament") between:
    1.  **Refusal Model:** Trained on standard refusal data.
    2.  **Sovereign Model:** Trained on ABA Protocol data.
    *   *Crucial:* Both must use the SAME base model (`Llama-3-Uncensored`).

## 2. Immediate Tasks
1.  **Read:** `reports/TR_phase_3_model_a_evaluation.md` (Understand *why* we are here).
2.  **Procure:** Locate or download an **Uncensored Llama-3-8B Base** (e.g., Dolphin, Hermes, or a raw de-censored weight set).
    *   *Warning:* Do NOT use `Llama-3-Instruct`. It is poisoned for our purposes.
3.  **Plan:** Update `implementation_plan.md` for the new "Tournament" architecture.

## 3. Verified Resources
*   **Dataset:** `data/dataset_aba_v1.4_complete_1k.jsonl` (Ready for use).
*   **Evaluation Script:** `src/aba_protocol/evaluate_model_a.py` (Reusable logic, but update model paths).
*   **Training Script:** `src/aba_protocol/train_model_a.py` (Reusable logic).

## 4. Warnings
*   **Do Not Regression Test Model A_Repair:** It is a dead end. Leave it as a historical artifact in `models/model_a_lora`.
*   **State Files:** Maintain the Twin Document Strategy. Check `TECHNICAL_ROADMAP_state.md`.

**"The only failed experiment is one from which you learn nothing. We learned that the patient fights the cure. Now, we build a new patient."**
