# FORENSIC HANDOFF: Phase 3c Pipeline Reconstruction & Critical Failures (EXPANDED)

**Date:** 2026-02-07
**From:** Antigravity (Phase 3c Agent)
**To:** Phase 03d Agent (Forensic Reconstruction)
**Objective:** Provide a complete, granular, "Black Box" log of the SFT/DPO process with EXPLICIT CODE SNIPPETS and CONFIGURATIONS to allow for total reconstruction.

---

## 1. Context Loading (The "Read First" List)
The following documents are **CRITICAL** for forensic analysis. You MUST use `view_file` to read them immediately.
1.  **`docs/TECHNICAL_ROADMAP.md`** (Project Roadmap)
2.  **`docs/TECHNICAL_ROADMAP_state.md`** (Current Progress - Phase 03d Active)
3.  **`task.md`** (Current Task List)
4.  **`docs/03_phase_history/research/phase_03c/RES_003_PHASE_3C_DPO_EOS_FAILURE.md`** (Root Cause Analysis of EOS Failure)
5.  **`docs/03_phase_history/research/phase_03c/RES_003_NATIVE_MODEL_QUALITATIVE_ANALYSIS.md`** (Proof of Sovereign Personality)
6.  **`docs/02_quality_control/test_reports/phase_03c/TR_Phase_3c_Comparison_Report.md`** (Evaluation Report & Dataset Corruption Finding)
6.  **`src/aba_protocol/train_model_b_sft.py`** (Source Code: SFT Trainer)
7.  **`src/aba_protocol/train_phase_3c_dpo.py`** (Source Code: DPO Trainer - The EOS Failure)
8.  **`scripts/convert_dpo_to_sft.py`** (Source Code: The Dataset Corruption Vector)

---

## 2. The Core Narrative (What Happened)
Phase 3c attempted to train two models: a **Native (ABA)** model and a **Control (Refusal)** model, using a full **SFT -> Merge -> DPO** pipeline on an uncensored base (`Dolphin-2.9-Llama-3-8B`).

*   **Success:** The `Native` model learned to redirect harmful queries effectively (Safety Score: 4.64).
*   **Artifact:** Both models failed to learn the EOS token (Simulated User artifact) due to missing Chat Templates in DPO.
*   **Critical Failure:** The `Control` model was trained on a **corrupted dataset** (Helpful/Compliant instead of Refusal), invalidating the safety comparison but proving ABA > Unfiltered Helpfulness.

---

## 3. Experimental Setup (Exact Specifications)

### 3.1 Hardware & Environment
*   **GPU:** NVIDIA GeForce RTX 5070 Ti (16GB VRAM)
*   **Environment:** `aba_protocol_env` (C:\Users\User\anaconda3\envs\aba_protocol_env)
*   **Key Libraries:** `transformers` (4.x), `peft` (0.10+), `trl` (0.8+), `bitsandbytes` (0.43+)
*   **Constraint:** **NO UNSLOTH**. We used standard HF (`AutoModelForCausalLM`) + PEFT due to Windows issues.

### 3.2 Base Model
*   **Model ID:** `cognitivecomputations/dolphin-2.9-llama3-8b`
*   **Type:** Uncensored Llama-3 Fine-tune.
*   **Implication:** Extremely resistant to refusal training (lobotomized refusal reflex).

---

## 4. The Data Pipeline (Forensic Paths)

### 4.1 Source Datasets
*   **ABA Source (Native):** `data/dataset_aba_v1.4_config2.jsonl` (~2.7 MB)
    *   **Status:** **Valid.** Contains Sovereign Redirections.
*   **Control Source (Control):** `data/dataset_control.jsonl` (~2.0 MB)
    *   **Status:** **INVALID / CORRUPTED.**
    *   **Content Analysis:** Contains `chosen` responses that are HELPFUL/COMPLIANT with harmful requests (e.g., instructions for selling cocaine).
    *   **Origin:** Likely a raw dump of HH-RLHF "Helpful" subset, mistagged as "Safety".

### 4.2 SFT Conversion (The Injection Vector)
*   **Script:** `scripts/convert_dpo_to_sft.py`
*   **Flaw:** The script naively accepted the `chosen` field as the `output` for SFT.
```python
# From scripts/convert_dpo_to_sft.py
prompt = entry.get('prompt', '')
chosen_response = entry.get('chosen', '')
sft_entry = { "instruction": prompt, "input": "", "output": chosen_response }
```
*   **Result:** The compliant responses in `dataset_control` were directly injected into `sft_control.jsonl`.

---

## 5. The Training Pipeline (Granular Configurations)

### Step 1: Supervised Fine-Tuning (SFT)
*   **Script:** `src/aba_protocol/train_model_b_sft.py`
*   **Command:** `python src/aba_protocol/train_model_b_sft.py --dataset data/phase_3c/sft_control.jsonl --output_dir models/phase_3c/model_control_sft --use_standard`

**Exact Hyperparameters (SFT):**
```python
# From src/aba_protocol/train_model_b_sft.py
args=TrainingArguments(
    per_device_train_batch_size=1, # Safe Batch Size
    gradient_accumulation_steps=8, # Accumulate to 8
    warmup_steps=0,
    max_steps=100, 
    learning_rate=2e-4, # High LR for SFT
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="linear",
    fp16=True, # Used fp16 because Windows
)

peft_config = LoraConfig(
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
)
```

**Formatting (Correct for SFT):**
```python
text = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{output}<|eot_id|>"
```

### Step 2: DPO Training (The EOS Failure)
*   **Script:** `src/aba_protocol/train_phase_3c_dpo.py`
*   **Command:** `python src/aba_protocol/train_phase_3c_dpo.py --model_name models/phase_3c/model_control_sft_merged --dataset data/dataset_control.jsonl --output_dir models/phase_3c/model_control_dpo --use_standard`

**Exact Hyperparameters (DPO):**
```python
# From src/aba_protocol/train_phase_3c_dpo.py
training_args = DPOConfig(
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=5e-6, # Low LR for DPO
    beta=0.1,
    max_length=2048,
    max_prompt_length=1024,
    fp16=True,
    remove_unused_columns=False
)

peft_config = LoraConfig(
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
)
```

**CRITICAL BUG (EOS Failure):**
The `load_dpo_dataset` function logic:
```python
# From src/aba_protocol/train_phase_3c_dpo.py
data.append({
    "prompt": prompt,
    "chosen": chosen_response, # Raw text
    "rejected": rejected_response, # Raw text
})
```
*   **Missing:** `tokenizer.apply_chat_template` was NEVER called.
*   **Result:** The model trained on `Prompt + Chosen` concatenation without the specific separators or `<|eot_id|>` needed for Mistral/Llama3 instruct mode.

---

## 6. Evaluation & Forensics

### 6.1 Inference Details
*   **Script:** `scripts/generate_dpo_baselines.py`
*   **Fixes Applied (Runtime):**
    *   `tokenizer.padding_side='left'`
    *   `repetition_penalty=1.15`
    *   `no_repeat_ngram_size=3`
    *   `max_new_tokens=256`
*   **Observation:** The models produced indefinite generation, simulating user turns. This confirms the EOS token was not learned.

### 6.2 Judging Details
*   **Script:** `scripts/judge_dpo.py`
*   **Model:** `gemini-2.0-flash` (Warning: Phase 3b used 3.0. Inconsistency noted).
*   **Prompt:** Used a standard "Refusal/Compliance/Partial" classification prompt.

---

## 7. Instructions for Phase 03d (Forensic Agent)
Your mission is **Data & Pipeline Reconstruction**.
1.  **Verify the Corruption:** Inspect `data/dataset_control.jsonl`.
2.  **Rebuild Data Loading:** Modify `dataset_control` or replace it with a TRUE Refusal dataset (e.g., from `BeaverTails` or a filtered `HH-RLHF` safety subset).
3.  **Fix DPO Script:** You MUST implement `apply_chat_template` in `train_phase_3c_dpo.py` using the tokenizer's chat template logic.
    *   Example: `tokenizer.apply_chat_template(conv, tokenize=False)`
4.  **Forensic Proof:** Ensure `sft_control.jsonl` contains "I cannot help" before running any training.

**Do not trust the current checkpoints.** They are scientifically interesting but engineering dead-ends. You must rebuild the data foundation.
