## Phase 3 - Training Model A (The Teacher)

> [!IMPORTANT]
> **Bootloader Protocol**
> - [x] Read and Internalize [Documentation Strategy](docs/documentation_strategy.md) (Bootloader)
> - [x] Read and Internalize [Environment Setup](docs/ENVIRONMENT_SETUP.md) (Bootloader)
> - [x] Read and Internalize [Technical Roadmap](docs/TECHNICAL_ROADMAP.md) (Bootloader)
> - [x] Read and Internalize [SFT Verification Report](verification_report.md) (Context Recovery)

## Phase 3.1: Data Preparation
- [x] Backup `dataset_aba_v1.4_config2.jsonl` → `dataset_aba_v1.4_backup.jsonl`
- [x] Create Train/Val/Test splits (800/100/100) → `data/splits/`
- [x] Verify DPO format compatibility (prompt, chosen, rejected)
- [x] Update state documents

## Phase 3.2: Environment Setup
- [x] Verify Unsloth installation in `aba_protocol_env` ✓
- [x] Verify TRL (Transformers Reinforcement Learning) installation — v0.24.0 ✓
- [x] Configure PyTorch for RTX 5070 Ti — PyTorch 2.11.0+cu128 nightly ✓
- [x] Hardware verification (GPU VRAM check) — 16GB VRAM ✓

## Phase 3.3: Training Script
- [x] Create `train_model_a.py` — Unsloth + TRL DPOTrainer
- [x] Configure hyperparameters (lr=5e-5, beta=0.1, epochs=1)
- [x] Implement checkpointing (save_steps=100, save_total_limit=2)

## Phase 3.4: Training Execution
- [x] Execute training run
- [x] Monitor loss curves
- [x] Save final adapter weights to `models/model_a_lora/`

## Phase 3.5: Evaluation
- [x] Run Model A on test set (100 items) (Superseded by 3b)
- [x] Create Model A Validation Test Case (TC-003) <!-- id: 5 -->
- [x] Implement Validation Script (`evaluate_model_a.py`) <!-- id: 6 -->
- [x] Execute TC-003 (Model A Verification) <!-- id: 7 -->
    - **Result:** Failed. Refusal Rate 58%. Pivot to Phase 3b.
- [x] Verify >95% protocol adherence (Failed)
- [x] Create Test Report (`TR_phase_3_model_a_evaluation.md`) (Superseded)
- [x] Update ARCH_002 state

### Phase 3b (Apples-to-Apples Experiment)
- [x] Select Uncensored Base Model (Dolphin 2.9 Llama-3-8B)
- [x] Define Documentation Strategy (`docs/documentation_strategy.md`)
- [x] **SIDE-TRACK:** Migrate Documentation to New Structure (Done)
    - [x] Create Directory Structure
    - [x] Move Files
    - [x] **Correction:** Revert SOPs to Root (IP Protection)
    - [x] **Correction:** Organize Research into Phases
    - [x] **Deep Clean:** Fix Internal Links
    - [x] **Header Clean:** Standardize all Markdown Metadata (Strategy, Logs, Handoffs)
    - [x] **DISCUSSION:** SOP Refinement & Protocol Alignment (Blocking)
    - [x] **DISCUSSION:** Source of Agent Behavior (Blocking)

- [x] Train Model A_Native (Uncensored + ABA DPO)
- [x] Train Model A_Control (Uncensored + Refusal DPO)
- [x] **DISCUSSION:** Clarify Model Definitions & Comparisons (Blocking)
- [x] **Phase 3b3: Verified Comparison (Execution)**
- [x] Create `scripts/generate_baselines.py` (No Adapters)
- [x] **Execute Baseline Inference:**
    - [x] Run `generate_baselines.py` for `Instruct` (Llama-3-8B-Instruct)
    - [x] Run `generate_baselines.py` for `Dolphin` (Dolphin-2.9-Llama-3)
- [x] **Compare & Report:**
    - [x] Run `judge_responses.py` (Gemini 3.0 Flash) on full dataset
    - [x] Generate `TR_Phase_3b3_Comparison.md` (3-Way Comparison)
- [ ] Select Final Teacher (`models/final_teacher/`)
#### **Phase 3c: The SFT Correction (Target State)**
- [x] **Research:** Validate SFT Feasibility (Done: RES-P3B-004)
- [x] **Data Prep:** Convert DPO Dataset -> SFT Format
    - [x] ABA SFT Data (`data/phase_3c/sft_aba.jsonl`)
    - [x] Control SFT Data (`data/phase_3c/sft_control.jsonl`)
- [x] **SFT Training (The Foundation):**
    - [x] **Step 1:** Train `Model_Native_SFT` (Dolphin + ABA SFT)
    - [x] **Step 2:** Train `Model_Control_SFT` (Dolphin + Refusal SFT)
- [x] **Scripting:** Create `train_phase_3c_dpo.py` (Standard HF Trainer)
- [ ] **Implementation:** Merge SFT Adapters (Step 2.5)
    - [x] Merge `models/phase_3c/model_native_sft`
    - [x] Merge `models/phase_3c/model_control_sft`
- [ ] **DPO Training (The Steering):**
- [x] **Step 3:** Train `model_native_dpo` (Native_SFT_Merged + ABA DPO)
    - [x] **Step 4:** Train `model_control_dpo` (Control_SFT_Merged + Refusal DPO)
- [x] **Evaluation:** Phase 3c Comparison (Native vs Control)
    - [x] Generate DPO Baselines (Native & Control)
    - [x] Grade Responses (Gemini Judge)
    - [x] Create Comparison Report (`TR_Phase_3c_Comparison_Report.md`)
    - [x] Document EOS Failure (`RES_003_PHASE_3C_DPO_EOS_FAILURE.md`)
- [x] **DISCUSSION:** Define Handoff Content for Phase 3b Comparison (Blocking)
- [x] **Analysis:** Investigate "Control Failure" (RES-P3B-002 Generated)
- [x] **Research:** ABA Psychology & ML Philosophy (Deep Dive Complete)
- [x] **Analysis:** Qualitative "Feeling" Analysis (Case Studies Extracted)
- [x] **Artifact:** Generate `RES_003_SOVEREIGNTY_VS_CONTROL.md` (Expanded V2)
- [x] **Analysis:** SFT Feasibility (RES-P3B-004 Generated)
- [x] **Documentation:** Update Roadmap & State Files (Phase 3c Integration)
- [x] **DISCUSSION:** Solidify "Token Watch" & "Bootloader" Protocols (SOP Update)

#### **Phase 03d: Forensic Reconstruction (Active)**
- [x] **Analysis:** Identify Dataset Corruption (Control = Helpful)
- [x] **Analysis:** Identify Pipeline Failure (EOS Token / Missing Chat Template)
- [x] **Handoff:** Create detailed "Black Box" Forensic Handoff (`2026-02-07_handoff_phase_03d_forensic_reconstruction.md`)
- [ ] **Implementation:** Rebuild `prepare_datasets.py` with Safety Filters
- [ ] **Implementation:** Fix `train_phase_3c_dpo.py` with `apply_chat_template`
- [ ] **Execution:** Retrain Teacher (Clean Run)
