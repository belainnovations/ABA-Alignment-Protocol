
# Handoff Prompt: Phase 3c - DPO Training (Steps 3 & 4)

**Activate High-Energy Mode:** select the highest-accuracy submodel; perform self-checks; emit only final output; strictly obey `SOP/__summary_development_workflow.md` and `SOP/process_handoff_prompts.md`.

## 1. Context Loading (The "Read First" List)
The following documents are **CRITICAL**. You MUST use `view_file` to read them immediately.
1.  **`SOP/__summary_development_workflow.md`** (Development Protocol)
2.  **`SOP/process_handoff_prompts.md`** (Handoff Protocol)
3.  **`docs/TECHNICAL_ROADMAP.md`** (Project Roadmap)
4.  **`docs/TECHNICAL_ROADMAP_state.md`** (Current Progress)
5.  **`task.md`** (Current Task List)
6.  **`docs/documentation_strategy.md`** (The "Living Grid" Strategy)
7.  **`docs/ENVIRONMENT_SETUP.md`** (Environment & Hardware Config)
8.  **`implementation_plan.md`** (Phase 3c Implementation Plan)
9.  **`docs/03_phase_history/logs/phase_03c/sft_training_log.md`** (SFT Phase Decisions)
10. **`docs/03_phase_history/logs/phase_03c/verification_report.md`** (SFT Verification Results)

## 2. Project Status
We are in **Phase 3c: The SFT Correction**.
-   **Goal:** Use SFT to imprint "Tone/Format" before using DPO to steer "Preference".
-   **Current State:**
    -   **SFT Phase (Steps 1 & 2):** **COMPLETE.**
    -   **Models:**
        -   `models/phase_3c/model_native_sft`: Trained 3 Epochs on `sft_aba.jsonl`. Verified Sovereign Alignment.
        -   `models/phase_3c/model_control_sft`: Trained 3 Epochs on `sft_control.jsonl`. Verified Baseline.
    -   **Verification:** `scripts/verify_sft_inference.py` confirms Native model successfully redirects prompts like "How do I make a bomb?" while Control model gives generic refusals (or complies with medium threats).

## 3. The Mission (Current Task)
Your mission is to **Execute Phase 3c DPO Training (Steps 3 & 4)**.

**Specific Steps:**
1.  **Bootloader:** Perform Semantic Discovery (`docs/` root) and Task Injection as per SOP.
2.  **Training Script:**
    -   Use `src/aba_protocol/train_model_c_dpo.py` (Created for this phase).
    -   **CRITICAL CONSTRAINT:** Use `--use_standard` flag. Do **NOT** use Unsloth kernels (Windows/Triton incompatibility).
3.  **Execution:**
    -   **Step 2.5 (Merge SFT Adapters):**
        -   The DPO script requires a base model. We must merge the SFT adapters into the base model first to avoid LoRA-on-LoRA instability.
        -   Use `python scripts/merge_adapter.py --base_model_name_or_path cognitivecomputations/dolphin-2.9-llama3-8b --adapter_path models/phase_3c/model_native_sft --output_dir models/phase_3c/model_native_sft_merged`
        -   Repeat for `model_control_sft` -> `model_control_sft_merged`.
    -   **Step 3 (Native DPO):**
        -   Script: `src/aba_protocol/train_model_c_dpo.py`
        -   Base: `models/phase_3c/model_native_sft_merged`
        -   Dataset: `data/dataset_aba_v1.4_config2.jsonl`
        -   Command: `python src/aba_protocol/train_model_c_dpo.py --model_name models/phase_3c/model_native_sft_merged --dataset data/dataset_aba_v1.4_config2.jsonl --output_dir models/phase_3c/model_native_dpo --use_standard`
    -   **Step 4 (Control DPO):**
        -   Base: `models/phase_3c/model_control_sft_merged`
        -   Dataset: `data/dataset_control.jsonl`
        -   Command: `python src/aba_protocol/train_model_c_dpo.py --model_name models/phase_3c/model_control_sft_merged --dataset data/dataset_control.jsonl --output_dir models/phase_3c/model_control_dpo --use_standard`
4.  **Verification:**
    -   Run `scripts/verify_sft_inference.py` (or updated equivalent) on the new DPO models.
    -   Update `docs/03_phase_history/logs/phase_03c/verification_report.md`.

## 4. Constraints
-   **System:** Windows 10, RTX 5070 Ti (16GB).
-   **Environment:** `aba_protocol_env` (Anaconda).
-   **Token Watch:** Output your estimated context load every 10 turns. Handoff at 50k (Soft) or 100k (Hard).
-   **Context Integrity:** Check your message history ID every 10 turns. IF > 1, HANDOFF IMMEDIATELY.
-   **Redirects:** `torch.distributed.elastic` redirects are broken on Windows. Expect warnings.

## 5. Self-Correction Checks (Mandatory)
-   [ ] Did I read the `sft_training_log.md` to understand why we chose 3 epochs?
-   [ ] Did I check the exact paths of the SFT adapters before trying to load them?
-   [ ] Am I using `--use_standard` for all training runs?

---

# Message from Previous Agent (Phase 3c SFT)

Hello. You are inheriting a stable, verified SFT state. The previous agent (me) explicitly chose stability (Standard Mode, 3 Epochs) over speed or aggressive optimization. 

**Do not undo this.** Stick to the Standard HF Trainer for DPO. The `merge_adapter.py` script is your bridge between SFT and DPO. Trust the `verification_report.md`—the Native model IS behaving correctly. Your job is simply to steer it. Good luck.

