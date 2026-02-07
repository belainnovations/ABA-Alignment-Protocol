# Handoff Prompt: Phase 3c - SFT Training Resumption

**Activate High-Energy Mode:** select the highest-accuracy submodel; perform self-checks; emit only final output; strictly obey `SOP/__summary_development_workflow.md` and `SOP/process_handoff_prompts.md`.

## 1. Context Loading (The "Read First" List)
The following documents are **CRITICAL**. You MUST use `view_file` to read them immediately.
1.  **`SOP/__summary_development_workflow.md`** (Updated with Context Integrity Protocol)
2.  **`SOP/process_handoff_prompts.md`** (Updated with Context Integrity Trigger)
3.  **`docs/TECHNICAL_ROADMAP.md`** (Project Roadmap)
4.  **`docs/TECHNICAL_ROADMAP_state.md`** (Current Progress)
5.  **`task.md`** (Current Task List)
6.  **`implementation_plan.md`** (Phase 3c Plan)
7.  **`src/aba_protocol/train_model_b_sft.py`** (The SFT Training Script)
8.  **`scripts/convert_dpo_to_sft.py`** (Data Prep Script)

## 2. Project Status
We are in **Phase 3c: SFT Correction**.
-   **Goal:** Train an SFT adapter on the "Chosen" responses from the DPO dataset to create a stable foundation for alignment.
-   **Status:**
    -   Data Preparation Script (`scripts/convert_dpo_to_sft.py`) is COMPLETE.
    -   SFT Dataset (`data/phase_3c/sft_train.jsonl`) is GENERATED (Verify existence).
    -   Training Script (`src/aba_protocol/train_model_b_sft.py`) is COMPLETE.
    -   **Training Execution:** FAILED due to Environment Loss (Context Truncation).

## 3. The Mission (Current Task)
Your mission is to **Resume and Complete the SFT Training**.

**Specific Steps:**
1.  **Context Check:** Verify your First Message ID is 0 or 1.
2.  **Environment Check:** Ensure you are in the correct Conda environment (`aba_protocol_env` or similar - check `README.md` or `pyproject.toml` instructions if available, otherwise assume standard `python` if in correct shell).
3.  **Verify Data:** Check that `data/phase_3c/sft_train.jsonl` exists and is valid.
4.  **Launch Training:**
    -   Run the training script using the **Standard Mode** (to avoid Windows/Unsloth issues).
    -   Command: `python src/aba_protocol/train_model_b_sft.py --dataset data/phase_3c/sft_train.jsonl --output_dir experiments/phase_3c_sft_full --max_steps 300 --use_standard`
    -   **Constraint:** Monitor for "Python not found" errors. If this persists, ask the user for the correct python path or environment activation command.
5.  **Verify Inference:**
    -   Run `python scripts/verify_sft_inference.py` (You may need to update this script to point to the new model path `experiments/phase_3c_sft_full`).
6.  **Update State:** Update `task.md` and `implementation_plan.md` upon completion.

## 4. Constraints
-   **Context Integrity:** Check your message history ID every 10 turns. IF > 1, HANDOFF IMMEDIATELY.
-   **Tooling:** Use Antigravity Native Tools.
-   **Environment:** Use the user's explicit python environment if standard `python` fails.

## 5. Self-Correction Checks
-   [ ] Did I read the new SOP sections about Context Integrity?
-   [ ] did I verify the SFT dataset exists before training?
-   [ ] Did I check for "Python not found" errors?
