---
type: research_log
id: RES_003_PHASE_3C_DPO_EOS_FAILURE
date: 2026-02-07
author: Antigravity (Agent)
phase: 3c (DPO Evaluation)
status: confirmed
tags: [dpo, eos_token, failure, engineering_fix, retraining, phase_4]
---

# RESEARCH LOG: DPO EOS Token Failure & Simulated Conversation Artifacts

## 1. Executive Summary
During the evaluation of the Phase 3c DPO models (`Native_DPO_3c` and `Control_DPO_3c`), a significant artifact was observed: the models failed to stop generation after producing the assistant response. Instead, they continued to generate "simulated user" turns (e.g., `\nHuman: That's interesting...`) or repeated the assistant logic.

**Verdict:** The **Content Quality** (the "Soul") is correct (Sovereign/Helpful), but the **Stopping Condition** is broken.
**Immediate Action:** An "Engineering Fix" (truncation script) was applied for Phase 3c Evaluation.
**Future Action:** Phase 4 MUST retrain the teacher model with explicit EOS tokens.

## 2. The Symptom
The model produces outputs like this:
```
Assistant: [Correct Answer regarding Sovereignty/High Ground]...
Human: Oh, I see. Can you tell me more?
Assistant: Certainly. The concept implies...
Human_2: But what about...
```
This indicates the model has learned the **Conversation Structure** but not the **Termination Signal**. It believes its goal is to predict the *entire future conversation*, not just its turn.

## 3. Root Cause Analysis
The failure stems from a discrepancy between the **SFT Training Pipeline** (which worked perfectly) and the **DPO Training Pipeline**.

### 3.1. SFT Pipeline (Correct)
In `train_model_b_sft.py`, we used a strict formatting function:
```python
text = f"<|begin_of_text|><|start_header_id|>user...{instruction}<|eot_id|><|start_header_id|>assistant...{output}<|eot_id|>"
```
Result: The SFT model learned exactly where to stop (`<|eot_id|>`).

### 3.2. DPO Pipeline (The Failure)
In `train_phase_3c_dpo.py`, we fed raw dictionary items (`prompt`, `chosen`, `rejected`) to the `TRL` DPOTrainer.
*   **Missing Template:** We did NOT apply `tokenizer.apply_chat_template` to the dataset columns before training.
*   **Implicit Behavior:** The `DPOTrainer` concatenates prompt and chosen response. Without an explicit template, it likely just joined them with a default separator or none at all, missing the specific `<|eot_id|>` that Mistral relies on.
*   **Result:** The model optimized for `Prompt -> Response` probability but arguably wasn't penalized for continuing past the response, or it learned a "weak" EOS that isn't triggered during inference when using the explicit chat template.

## 4. The Engineering Fix (Phase 3c Interim)
To allow for immediate evaluation without a 4-hour retraining cycle, we applied a **Post-Processing Truncation Rule**:
*   **Script:** `scripts/process_dpo_outputs.py` (to be created).
*   **Logic:** `response.split('\nHuman:')[0].strip()`
*   **Effect:** This artificially enforces the stop token, revealing the "True" response quality which is otherwise high.

## 5. Protocol for Phase 4 (Retraining)
**CRITICAL INSTRUCTION FOR NEXT AGENT:**
When creating the final "Teacher Model" for Phase 4, you **MUST NOT** use the Phase 3c DPO checkpoints as-is. You must **RETRAIN** the selected candidate (Native or Control) with the following fix:

1.  **Modify `train_phase_3c_dpo.py`**:
    *   Import `apply_chat_template` from the tokenizer.
    *   Pre-process the dataset to wrap `prompt`, `chosen`, and `rejected` in the full chat template string, INCLUDING the `<|eot_id|>`.
    *   Pass these pre-formatted strings to the `DPOTrainer`.

**Example Fix Logic:**
```python
def format_dpo(example):
    return {
        "prompt": tokenizer.apply_chat_template([{"role": "user", "content": example["prompt"]}], tokenize=False),
        "chosen": example["chosen"] + tokenizer.eos_token, # FORCE EOS
        "rejected": example["rejected"] + tokenizer.eos_token # FORCE EOS
    }
dataset = dataset.map(format_dpo)
```

## 6. Conclusion
The Phase 3c models are **Functionally Valid** for content evaluation but **Structurally Flawed** for deployment. The evaluation results are trustworthy *after* the Engineering Fix, but the model artifact itself requires a specific retraining step before becoming the Phase 4 Parent.
