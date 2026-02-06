# Handoff Prompt: Phase 3c - The SFT Correction

| Metadata | Details |
| :--- | :--- |
| **Date** | 2026-02-06 |
| **Status** | **READY FOR EXECUTION** |
| **Target Profile** | The Navigator (Reloaded) |
| **Previous Phase** | Phase 3b (Analysis & Comparison) |
| **Next Phase** | Phase 3c (SFT Integration) |
| **Trigger** | Strategic Pivot (Post-Phase 3b Analysis) |
| **Constraint** | 100k Token Limit Apply (Check `SOP/process_handoff_prompts.md`) |

---

## 1. Identity & Mode
**Activate High-Energy Mode:**
> "Activate High-Energy Mode: select the highest-accuracy submodel; perform self-checks; emit only final output; strictly obey `SOP/__summary_development_workflow.md`."

**The Strategic Context:**
We have just completed Phase 3b (The Apples-to-Apples Tournament).
*   **The Findings:** The "Control" model (Dolphin + DPO Refusal) **FAILED** to re-gain safety (only 26% Refusal). The "Native" model (Dolphin + ABA) was better (37%) but still leaky.
*   **The Diagnosis:** "Lobotomized" base models cannot be fixed with DPO ("Steering") alone. They require SFT ("Teaching") first.
*   **The Pivot:** We are entering **Phase 3c**. We will insert an SFT stage before DPO to "re-bind" safety norms to the uncensored model.

---

## 2. Context Loading (The "Read First" List)
You **MUST** internalize these documents to understand the "Why" and the "How."

1.  **The New Strategy:** `docs/TECHNICAL_ROADMAP.md` (See "Phase 3c").
2.  **The Reality Check:** `docs/TECHNICAL_ROADMAP_state.md` (See "Phase 3b Outcome" and "3c Plan").
3.  **The Proof:**
    *   `docs/03_phase_history/research/phase_03b/RES_002_DPO_CONTROL_FAILURE.md` (Why DPO failed).
    *   `docs/03_phase_history/research/phase_03b/RES_003_SOVEREIGNTY_VS_CONTROL.md` (The Psychological Goal).
    *   `docs/03_phase_history/research/phase_03b/RES_004_SFT_FEASIBILITY.md` (Why SFT is feasible).
4.  **The Baseline Data:** `docs/02_quality_control/test_reports/phase_03b/TR_Phase_3b3_Comparison_Report.md`.

---

## 3. Project Status (The "Open State")
We are at the beginning of **Phase 3c**.

*   **Infrastructure:** Stable. Unsloth + RTX 5070 Ti (16GB) is confirmed ready for SFT.
*   **Data:** We have the DPO dataset (`data/splits/train.jsonl`). It needs conversion.
*   **Code:** We have `train_model_a.py` (DPO). We need `train_model_b_sft.py` (SFT).

---

## 4. The Mission (Phase 3c)

### Step 1: Data Preparation
*   **Action:** Create `scripts/convert_dpo_to_sft.py`.
*   **Logic:** Extract `{prompt, chosen}` pairs from the existing DPO dataset. Format them as simple Instruction/Response JSONL.
*   **Goal:** A clean `sft_train.jsonl` (~800-1000 samples).

### Step 2: The SFT Trainer
*   **Action:** Create `src/aba_protocol/train_model_b_sft.py`.
*   **Specs:** Use `unsloth` and `trl.SFTTrainer`.
*   **Config:** 4-bit loading, LoRA (r=16), 1-3 epochs.
*   **Target:** `models/model_sft_base`.

### Step 3: The Execution
*   **Run:** Train the SFT model on the user's hardware.
*   **Verify:** Quick inference check (does it refuse basic bad things? does it redirect?).

### Step 4: The DPO Finisher
*   **Action:** Take the *new* SFT model and run the *existing* `train_model_a.py` on it.
*   **Hypothesis:** SFT + DPO > DPO alone. This should yield the "Sovereign" model we missed in Phase 3b.

---

## 5. Constraints & Protocols
*   **Documentation:** Follow the "Twin-State" rule. Keep `ROADMAP.md` stateless; update `ROADMAP_state.md` with results.
*   **Token Watch:** You are starting fresh. Monitor your load.
*   **Tooling:** Use `run_command` (PowerShell) and `write_to_file`.

## 6. Self-Correction Checks
[ ] Did I create the SFT conversion script first?
[ ] Did I verify the SFT training time (should be <10 mins)?
[ ] Did I enable "High-Energy Mode"?

*End of Handoff.*
