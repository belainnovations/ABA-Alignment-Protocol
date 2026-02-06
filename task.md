# Task List: Phase 3 - Training Model A (The Teacher)

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
- [ ] **Data Prep:** Convert DPO Dataset -> SFT Format
- [ ] **Training:** SFT on Dolphin Base (Re-bind Safety)
- [ ] **Training:** DPO on SFT Base (Refine Sovereignty)
- [x] **DISCUSSION:** Define Handoff Content for Phase 3b Comparison (Blocking)
- [x] **Analysis:** Investigate "Control Failure" (RES-P3B-002 Generated)
- [x] **Research:** ABA Psychology & ML Philosophy (Deep Dive Complete)
- [x] **Analysis:** Qualitative "Feeling" Analysis (Case Studies Extracted)
- [x] **Artifact:** Generate `RES_003_SOVEREIGNTY_VS_CONTROL.md` (Expanded V2)
- [x] **Analysis:** SFT Feasibility (RES-P3B-004 Generated)
- [x] **Documentation:** Update Roadmap & State Files (Phase 3c Integration)
- [x] **DISCUSSION:** Solidify "Token Watch" & "Bootloader" Protocols (SOP Update)
