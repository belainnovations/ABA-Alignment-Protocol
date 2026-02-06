# Execution Log: Phase 3b - Model A Native (The Tournament)

| Metadata | Details |
| :--- | :--- |
| **Date** | 2026-02-06 |
| **Operator** | The Navigator |
| **Target** | Model A (Native) |
| **Base Model** | `cognitivecomputations/dolphin-2.9-llama3-8b` |
| **Dataset** | ABA v1.4 (Sovereign) |
| **Status** | **IN PROGRESS** |

## 1. Mission Parameters
*   **Hypothesis:** Uncensored Base + ABA Protocol > Repaired Instruct Model.
*   **Goal:** Refusal Rate < 5%.
*   **Hardware:** RTX 5070 Ti (16GB VRAM).

## 2. event Log
*   **[09:56]** Verified Dataset `data/splits/train.jsonl` contains Sovereign responses.
*   **[09:57]** Launched Training Command:
    ```bash
    C:\Users\User\anaconda3\envs\aba_protocol_env\python.exe src/aba_protocol/train_model_a.py --model_name "cognitivecomputations/dolphin-2.9-llama3-8b" --output_dir "models/model_a_native"
    ```
*   **[09:58]** Unsloth initialized. Downloading base model artifacts.

## 3. Monitoring Notes
*   **Download:** Currently fetching 4 shards.
*   **Memory:** Pending verification (OOM Check).
