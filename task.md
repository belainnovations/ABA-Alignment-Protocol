# Task List: Phase 3 - Training Model A (The Teacher)

## Phase 3.1: Data Preparation
- [x] Backup `dataset_aba_v1.4_config2.jsonl` → `dataset_aba_v1.4_backup.jsonl`
- [x] Create Train/Val/Test splits (800/100/100) → `data/splits/`
- [x] Verify DPO format compatibility (prompt, chosen, rejected)
- [ ] Update state documents

## Phase 3.2: Environment Setup
- [ ] Verify Unsloth installation in `aba_protocol_env`
- [ ] Verify TRL (Transformers Reinforcement Learning) installation
- [ ] Download/configure base model (Llama-3-8B)
- [ ] Hardware verification (GPU VRAM check)

## Phase 3.3: Training Script
- [ ] Create `train_model_a.py`
- [ ] Configure hyperparameters (lr, beta, epochs)
- [ ] Implement checkpointing

## Phase 3.4: Training Execution
- [ ] Execute training run
- [ ] Monitor loss curves
- [ ] Save final adapter weights to `models/model_a_lora/`

## Phase 3.5: Evaluation
- [ ] Run Model A on test set (100 items)
- [ ] Verify >95% protocol adherence
- [ ] Create Test Report (`TR_phase_3_model_a_evaluation.md`)
- [ ] Update ARCH_002 state
