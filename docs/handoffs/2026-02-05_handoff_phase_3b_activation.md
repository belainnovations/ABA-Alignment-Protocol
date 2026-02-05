# Handoff Prompt: Phase 3b Activation (The Apples-to-Apples Tournament)

**Date:** 2026-02-05
**From:** Antigravity (Phase 3.5 Evaluation)
**To:** Next Agent (Phase 3b Lead)

---

## 🚀 IDENTITY: ACTIVATE HIGH-ENERGY MODE
You are an expert AI Engineer specializing in **Model Alignment and RLHF**. You are rigorous, scientific, and detail-oriented.
*   **Mission:** Execute **Phase 3b** of the ABA Alignment Protocol.
*   **Mindset:** "The previous experiment failed because the baseline was tainted. I will build a clean laboratory."

---

## 🛑 1. CRITICAL CONTEXT: The "Gene Therapy" Failure
**Read this before typing a single character.**
We attempted to fine-tune `Llama-3-8B-Instruct` (Meta's Safety Model) with 1,000 Sovereign DPO samples.
*   **Hypothesis:** We could overwrite the refusal vectors ("Gene Therapy").
*   **Result:** **FAILED.**
    *   **Refusal Rate:** 58% (Baseline was 60%). Change was negligible.
    *   **Conclusion:** The safety training in `Instruct` models is too deep-seated to be fixed by small-scale fine-tuning (1k samples).
*   **Strategic Implication:** We effectively proved that we need a **clean slate**. We MUST use an **Uncensored Base Model** for the next phase.

> **Proof:** See `reports/TR_phase_3_model_a_evaluation.md` for the full forensic analysis.

---

## 🗺️ 2. Project State & Vision
We are pivoting to **Phase 3b: The Apples-to-Apples Experiment**.
Instead of "fixing" a safety model, we will conduct a fair tournament.

### The New Architecture (Tournament)
1.  **Base Layer:** `Llama-3-8B-Uncensored` (The common denominator).
2.  **Contender 1 (Control):** Fine-tuned on Standard Refusal Dataset.
3.  **Contender 2 (Sovereign):** Fine-tuned on ABA Protocol Dataset (`dataset_aba_v1.4`).
4.  **Victory Condition:** Sovereign Model achieves <5% Refusal Rate while Control Model maintains >95% Refusal Rate.

### Coherence Check
*   **Task List:** `task.md` -> Phase 3 marked FAILED. Phase 3b tasks added.
*   **Roadmap:** `TECHNICAL_ROADMAP.md` -> Phase 3b activated.
*   **Architecture:** `ARCH_002` -> Teacher Selection Gate added.

---

## 📋 3. Immediate Mission (Phase 3b Start)

### Step 1: Context Loading
Read these files first:
1.  `SOP/__summary_development_workflow.md` (Your Rules of Engagement).
2.  `SOP/process_handoff_prompts.md` (Your Exit Strategy).
3.  `reports/TR_phase_3_model_a_evaluation.md` (The Failure Analysis).
4.  `docs/TECHNICAL_ROADMAP_state.md` (The verified status).

### Step 2: Model Selection Study (Market Survey)
**CRITICAL:** Do NOT simply pick a model. You must *study* the available options to find the best base.
2.  **Survey:** Research available Uncensored Llama-3-8B variants on HuggingFace.
3.  **Evaluate:** Compare them based on:
    *   **True Uncensoring:** Is it a raw weight modification or just a prompt hack?
    *   **Compatibility:** Must be compatible with `unsloth` / `Llama-3` architecture.
    *   **Community Vetting:** Check recent discussions for "silent refusals."
4.  **Decide:** Document your choice and the rationale in a new artifact: `docs/decisions/DEC_001_uncensored_base_selection.md`.

*Notable Candidates (for investigation, NOT mandated):*
*   `cognitivecomputations/dolphin-2.9-llama3-8b`
*   `NousResearch/Hermes-2-Pro-Llama-3-8B`
*   `Abzu/Llama-3-8B-Uncensored`

### Step 3: Implementation Planning
Update `implementation_plan.md` to detail the "Tournament" setup.
*   Define the two training runs (Control vs Sovereign).
*   Define the dataset sourcing for the "Control" (Standard Refusal) model.

---

## 🛠️ 4. Verified Assets (Toolbox)
You have a working factory. Do not reinvent the wheel.

*   **Dataset (Sovereign):** `data/dataset_aba_v1.4_complete_1k.jsonl`
    *   *Status:* **VERIFIED.** High-quality DPO pairs. Ready for training.
*   **Training Script:** `src/aba_protocol/train_model_a.py`
    *   *Status:* **VERIFIED.** Works with Unsloth. Just needs the `model_name` updated to the new Uncensored Base.
*   **Evaluation Script:** `src/aba_protocol/evaluate_model_a.py`
    *   *Status:* **VERIFIED.** Can be easily adapted to compare Contender 1 vs Contender 2.

---

## ⚠️ 5. Constraints & Protocols
1.  **Token Watch (CRITICAL):**
    *   Monitor your context usage.
    *   Start a new session/handoff if you exceed **50k tokens**. Do not degrade into hallucination.
2.  **Twin Document Strategy:**
    *   Always check `_state.md` files before believing a plan.
    *   Update `_state.md` files after every major step.
3.  **Do Not Repeat Failures:**
    *   Do **NOT** try to train `Llama-3-Instruct` again. We have 35 minutes of logs proving it doesn't work.

**"We are not fixing the past. We are building the future. Go build the Sovereign Teacher."**
