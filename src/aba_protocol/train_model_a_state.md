# State Document: Model A Training Script
| Metadata | Details |
| :--- | :--- |
| **Document ID** | STATE-TRAIN-A |
| **Twin File** | [train_model_a.py](./train_model_a.py) |
| **Last Updated** | 2026-02-06 |
| **Status** | Active |

## 1. Overview
This script fine-tunes a base model (Llama-3-Instruct or Dolphin-2.9) using DPO to create "Model A" (The Teacher).

## 2. Configuration
**Parameters:**
- `--model_name`: Base model ID (default: `unsloth/Llama-3-8B-Instruct`)
- `--data_dir`: Path to split datasets (train.jsonl, val.jsonl)
- `--output_dir`: Output path for adapters
- `--epochs`: 1
- `--batch_size`: 2 (Accumulation: 4)

## 3. History
- **Phase 3:** Validated with Llama-3-Instruct. Result: 58% Refusal.
- **Phase 3b (Analysis):** [Failure Analysis](../docs/03_phase_history/research/phase_03b/RES_002_DPO_CONTROL_FAILURE.md). Direct DPO on uncensored models failed to reconstruct safety (26% Refusal).
- **Phase 3c (Planned):** Will require `train_model_b_sft.py` (Supervised Fine-Tuning) before DPO.

## 4. Usage
```bash
# Phase 3b: Native Sovereign Training
python src/aba_protocol/train_model_a.py \
  --model_name "cognitivecomputations/dolphin-2.9-llama3-8b" \
  --output_dir "models/model_a_native"
```
