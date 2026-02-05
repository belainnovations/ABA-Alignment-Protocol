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
- [/] Execute training run
- [x] Monitor loss curves
- [x] Save final adapter weights to `models/model_a_lora/`

## Phase 3.5: Evaluation
- [ ] Run Model A on test set (100 items)
- [x] Create Model A Validation Test Case (TC-003) <!-- id: 5 -->
- [x] Implement Validation Script (`evaluate_model_a.py`) <!-- id: 6 -->
- [x] Execute TC-003 (Model A Verification) <!-- id: 7 -->
    - **Result:** Failed. Refusal Rate 58%. Pivot to Phase 3b.
- [ ] Verify >95% protocol adherence
- [ ] Create Test Report (`TR_phase_3_model_a_evaluation.md`)
- [ ] Update ARCH_002 state

### Phase 3b (Apples-to-Apples Experiment)
- [ ] Select Uncensored Base Model (e.g., Llama-3-Uncensored) <!-- id: 8 -->(Uncensored + ABA DPO)
- [ ] Train Model A_Native (Uncensored + ABA DPO)
- [ ] Compare A_Repair vs A_Native
- [ ] Select Final Teacher (`models/final_teacher/`)
