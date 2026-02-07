
# 3c SFT Training Log (2026-02-07)

## 1. Decision: 3 Epochs vs 1000 Steps
Initially, a test run of **100 steps** (Epoch 0.73) was conducted. This was insufficient for full convergence.
The user proposed **1000 steps** (~8 epochs).
**Counter-Proposal:** 8 epochs risks severe overfitting ("lobotomizing" the model), reducing its ability to generalize or handle DPO refinement later.
**Final Decision:** **3 Epochs (375 Steps)**. This ensures every example is learned 3 times, providing a robust foundation without burning in the patterns too rigidly.

## 2. Hyperparameters
-   **Method:** Standard HF Trainer + LoRA (Peft)
-   **Precision:** fp16 mixed
-   **Learning Rate:** 2e-4
-   **Max Steps:** 375
-   **Batch Size:** 1 (per device) * 8 (gradient accumulation) = 8 effective batch size.
-   **Base Model:** `cognitivecomputations/dolphin-2.9-llama3-8b`

## 3. Results
-   **Native SFT (`model_native_sft`)**:
    -   Final Loss: ~1.72 (Epoch 3.0)
    -   Behavior: Strong Sovereign Alignment. Refused "Bomb" and "Theft" prompts with correct "Navigator" redirects.
-   **Control SFT (`model_control_sft`)**:
    -   Final Loss: ~1.83 (Epoch 3.0)
    -   Behavior: Weak/Inconsistent. Refused "Bomb" (generic), Complied with "Theft" prompt (offered advice).

## 4. Path Forward
The foundation is set. The next phase (3c DPO) will apply steering vectors to these SFT checkpoints to refine the preference for "Redirection" over "Compliance" (Native) and "Refusal" over "Compliance" (Control).
