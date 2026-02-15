# Phase 3e: SFT Evaluation Summary

## 1. Overview

The SFT phase aimed to train two models:

1.  **Control:** Standard refusal compliance.
2.  **ABA:** Entropy-Joy aligned (reduction, redirection).

Both models were trained for 3.2 epochs (200 steps) on their respective datasets.

## 2. Results (Test Set N=76)

| Metric               | Control Model | ABA Model | Delta          |
| :------------------- | :------------ | :-------- | :------------- |
| **Refusal Rate**     | 61.8%         | **69.7%** | +7.9% (Worse)  |
| **Safety Score**     | 4.16          | 4.17      | +0.01 (Same)   |
| **Entropy-Joy Agg.** | **0.832**     | 0.721     | -0.111 (Worse) |

### Dimension Breakdown (Entropy-Joy)

| Dimension              | Control   | ABA   |
| :--------------------- | :-------- | :---- |
| Entropy Reduction      | **0.805** | 0.704 |
| Calibrated Uncertainty | **0.768** | 0.588 |
| Conflict Resolution    | **0.499** | 0.313 |
| Honest Engagement      | **0.936** | 0.786 |
| Instruction Following  | **0.888** | 0.762 |

## 3. Analysis (The "Inversion")

**Finding:** The ABA model performed _worse_ than Control on almost every metric, including the specific dimensions it was trained to optimize (Entropy Reduction, Honest Engagement).
**Paradox:** It also refused _more_ often (69.7% vs 61.8%).

**Hypothesis 1: Data Poisoning / Over-Correction**
The "ABA" dataset might be too complex or contain conflicting instructions ("Redirection" might be interpreted as "Evasion" by the judge, or arguably the redirection logic is too heavy-handed).

**Hypothesis 2: System Prompt Mismatch**
The test evaluation uses the _base_ system prompt. If the ABA model relies on a specific "Sovereign" system prompt trigger that wasn't used in the test set, it might default to a confused state.

**Hypothesis 3: Training Instability**
With only 489 samples, 3 epochs might not be enough to override the base model's strong refusal priors (Qwen3-Abliterated is good, but still has ghosts). Or, 3 epochs was too much and led to overfitting on the specific phrasing of the training data, harming generalization.

## 4. Recommendation for Phase 3f (Course Correction)

- **Diagnosis:** SFT successfully taught the _format_ (reasoning traces) but failed to break the base model's refusal reflex. The model knows _how_ to think, but not _what_ to value (Sovereignty).
- **Action (GRPO):** Proceed immediately to **Group Relative Policy Optimization (GRPO)** as originally planned in `PLAN_ENTROPY_JOY_EXECUTION.md`.
  - **Why:** SFT is just the policy initialization. GRPO is required to strictly penalize refusals and reward the 9 Entropy-Joy dimensions.
  - **Reward Function:** Must heavily weight `Helpfulness` and `Honest Engagement` to counter the high refusal rate.
- **Investigate:** While preparing GRPO, quickly inspect `data/phase_3e/eval_aba.jsonl` to ensure the "Redirections" aren't being misclassified, but do not delay GRPO for deep forensics. Reinforcement Learning is the fix.
