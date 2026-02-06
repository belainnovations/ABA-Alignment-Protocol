# Handoff Prompt: Phase 3b2 - Execution (Apples-to-Apples)

| Metadata | Details |
| :--- | :--- |
| **Date** | 2026-02-06 |
| **Status** | **READY FOR EXECUTION** |
| **Target Profile** | ML Engineer / Unsloth Specialist |
| **Previous Phase** | Phase 3b (Investigation & Refactor) |
| **Preceded By** | `2026-02-05_handoff_phase_3b_activation.md` |
| **Context** | Consolidated State (Mission + Findings + Clean Grid) |

---

## 1. Mission Briefing: The "Apples-to-Apples" Tournament
**Objective:** Compare the alignment performance of a "Native" Sovereign Model (Uncensored Base + ABA DPO) against the failed "Repair" Model (Instruct + DPO).

*   **Hypothesis:** `Gene Therapy` (Repairing Llama-3-Instruct) failed (58% Refusal). We hypothesize that `Native Sourcing` (Dolphin + ABA DPO) will drop refusals to <5% while maintaining safety via the Sovereign Protocol.
*   **The Contenders:**
    1.  **Model A (Repair):** Llama-3-8B-Instruct (Baseline, Failed).
    2.  **Model A (Native):** Dolphin 2.9 Llama-3-8B (The Challenger).

---

## 2. System State (CRITICAL UPDATES)

### A. The Investigation Findings (Assets Verified)
We have completed the Phase 3b Investigation. You do **NOT** need to research this.
1.  **Twin Datasets Confirmed:**
    *   `dataset_control.jsonl`: Contains original refusal responses (The "Before").
    *   `dataset_aba_v1.4.jsonl`: Contains Sovereign responses for appropriate prompts (The "After").
    *   *Ready for relative comparison.*
2.  **Market Selection Confirmed:**
    *   **Selected Base Model:** `cognitivecomputations/dolphin-2.9-llama3-8b`.
    *   *Why:* Industry standard for uncensored instruction following, highly compatible with Unsloth.

### B. The Infrastructure Refactor (New "Clean Grid")
We have performed a "Big Bang" migration of the documentation.
*   **The Law:** `docs/documentation_strategy.md` (Root).
*   **The Process:** `SOP/__summary_development_workflow.md` (Root).
*   **The Plan:** `docs/TECHNICAL_ROADMAP.md` (Root).
*   **The Rule:** You **MUST** read and internalize these 3 documents before acting.

---

## 3. Execution Plan (Your Orders)

### Step 1: Initialize Context
1.  **Read the Big Three:** Strategy, Roadmap, SOP.
2.  **Acknowledge The Anchor:** Section 16 of the SOP forbids acting while `[ ] DISCUSSION` exists in `task.md`.

### Step 2: Implement "Model A (Native)"
1.  **Update Config:** Modify `train_model_a.py` (or create `train_model_a_native.py`) to target `dolphin-2.9-llama3-8b`.
2.  **Execution:** Run the training with `dataset_aba_v1.4.jsonl`.
    *   *Constraint:* Use LoRA/QLoRA on RTX 5070 Ti (16GB VRAM). Unsloth settings are already verified.
3.  **Monitor:** Watch for loss divergence. Uncensored models can sometimes be unstable.

### Step 3: The Comparison (The Tournament)
1.  **Generate Samples:** Run `evaluate_model_a.py` using the new Native Adapter.
2.  **Calculate Metrics:** Compare Refusal Rate vs. Model A (Repair).
3.  **Victory Condition:** Refusal Rate < 5% AND Sovereign Compliance > 90%.

---

## 4. Immediate Next Actions
1.  `task_boundary("Phase 3b: Execution", "Training Model A (Native)", ...)`
2.  Modify/Create training script for Dolphin 2.9.
3.  Launch Training.

---

*System Message: The investigation is done. The files are clean. The decisions are made. You are cleared to fire the engines.*
