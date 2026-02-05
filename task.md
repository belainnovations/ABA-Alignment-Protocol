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
- [ ] Execute training run
- [ ] Monitor loss curves
- [ ] Save final adapter weights to `models/model_a_lora/`

## Phase 3.5: Evaluation
- [ ] Run Model A on test set (100 items)
- [ ] Verify >95% protocol adherence
- [ ] Create Test Report (`TR_phase_3_model_a_evaluation.md`)
- [ ] Update ARCH_002 state
