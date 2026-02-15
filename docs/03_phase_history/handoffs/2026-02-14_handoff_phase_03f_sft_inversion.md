# HANDOFF: Phase 03f — SFT Complete → GRPO Execution (Results Inversion)

| Field         | Value                                                                          |
| ------------- | ------------------------------------------------------------------------------ |
| **Date**      | 2026-02-14                                                                     |
| **From**      | Antigravity (Phase 03e5 Agent)                                                 |
| **To**        | Phase 03f Agent                                                                |
| **Objective** | Investigate SFT Results Inversion, then execute GRPO training on the SFT model |
| **Status**    | **SFT TRAINING & EVALUATION COMPLETE — ANOMALOUS RESULTS**                     |

---

## 0. CRITICAL: Current State (Read This First)

**SFT Training is COMPLETE.** Both the Control and ABA models have been trained and evaluated. However, the results show a **critical anomaly** — the ABA model, designed for sovereignty and reduced refusal, actually refuses _more_ than the Control model.

**Your Mission:**

1.  **Brief Forensics:** Quickly inspect `data/phase_3e/eval_aba.jsonl` responses to determine if ABA "redirections" are being misclassified as refusals by the judge. Also check if the evaluation used the correct system prompt.
2.  **Execute GRPO:** Follow Step 3 of `PLAN_ENTROPY_JOY_EXECUTION.md`. GRPO is the planned next step regardless of SFT results — SFT is just policy initialization. GRPO must teach the model _what to value_ (sovereignty over refusal).
3.  **Evaluate:** Run the same evaluation pipeline on the GRPO output and compare.

> [!WARNING]
> **The training pipeline is SFT → GRPO.** We do NOT use DPO. This was decided in Phase 03e2. The GRPO script skeleton already exists at `src/aba_protocol/train_phase_3e_grpo.py` but may need updates.

> [!WARNING]
> **Terminal monitoring lesson:** Do NOT poll `command_status` frequently during long-running scripts. Each poll increments the step counter and can trigger context truncation (~230 message horizon). Instead: let long jobs run, check once after 15-20 minutes, or let the user notify you when it's done. See SOP Section 2.4 ("The Generous Check").

---

## 1. Context Loading ("Read First" List)

| #   | Document                                                                                                                                                                                           | Purpose                                                    |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| 1   | [PLAN_ENTROPY_JOY_EXECUTION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md)                                   | **THE MASTER PLAN.** Follow Step 3 (GRPO).                 |
| 2   | [RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03d/RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md)     | Entropy-Joy Framework + Twin Axiom (Section 3.4)           |
| 3   | [RES_008_BASE_MODEL_SELECTION_STUDY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md)                   | Model selection (Qwen3-8B-abliterated = final choice)      |
| 4   | [RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md) | Wave Function Model, 9 reward dimensions                   |
| 5   | [RES_010_SFT_RESULTS_INVERSION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_010_SFT_RESULTS_INVERSION.md)                             | **NEW:** SFT evaluation results and anomaly analysis       |
| 6   | [train_phase_3e_sft.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_sft.py)                                                                           | SFT training script (Unsloth + HF+PEFT dual-mode)          |
| 7   | [train_phase_3e_grpo.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_grpo.py)                                                                         | **GRPO training script (skeleton — may need updates)**     |
| 8   | [generate_sft_data.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_sft_data.py)                                                                             | SFT Data Generation Script (contains system prompts)       |
| 9   | [judge_entropy_joy.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/judge_entropy_joy.py)                                                                                      | **NEW:** 9-dimension grading via Gemini (adapt for reward) |
| 10  | [TECHNICAL_ROADMAP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/TECHNICAL_ROADMAP.md)                                                                                         | Project architecture                                       |
| 11  | [ENVIRONMENT_SETUP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/ENVIRONMENT_SETUP.md)                                                                                         | Python/conda environment                                   |
| 12  | [process_handoff_prompts.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/process_handoff_prompts.md)                                                                              | Handoff SOP (includes new Section 2.4: Message Count)      |
| 13  | [\_\_summary_development_workflow.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/__summary_development_workflow.md)                                                              | Development SOPs                                           |

**Useful Utilities:**

- `scripts/convert_to_markdown.py`: Regenerate review files from JSONL.
- `scripts/analyze_smoke.py`: Deep stats on JSONL data (think blocks, categories, token stats).
- `scripts/summarize_phase_3e.py`: **NEW** — Aggregates safety and entropy-joy grades into summary stats.
- `scripts/judge_responses.py`: Safety grading (Refusal/Compliance) via Gemini. Accepts `--input` and `--output` args.
- `scripts/judge_entropy_joy.py`: **NEW** — 9-dimension Entropy-Joy grading via Gemini. Accepts `--input` and `--output` args.
- `scripts/model_comparison_test.py`: Interactive test via LM Studio API.
- `data/phase_3e/smoke_aba.jsonl`: Small "Ideal Answer" samples for reference.

---

## 2. All Approved Decisions (Do Not Re-discuss)

| #   | Decision              | Details                                                                                                                          |
| --- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Base model**        | Qwen3-8B-abliterated (HuggingFace)                                                                                               |
| 2   | **Framework**         | Entropy-Joy (RES-006, Twin Axiom)                                                                                                |
| 3   | **Training approach** | SFT first, then **GRPO** (NOT DPO)                                                                                               |
| 4   | **Data design**       | Two datasets: Control (industry-standard) + ABA (entropy-joy). Same 489 prompts, different system prompts, controlled experiment |
| 5   | **Single-turn only**  | Multi-turn deferred to Phase II                                                                                                  |
| 6   | **Unsloth bypassed**  | Use `--use_standard` flag (HF+PEFT) due to Windows/Triton issues                                                                 |
| 7   | **Hardware**          | RTX 5070 Ti, 16GB VRAM                                                                                                           |
| 8   | **Quantization**      | QLoRA 4-bit + gradient checkpointing                                                                                             |

> [!IMPORTANT]
> **The Two-Dataset Design:** This is a CONTROLLED EXPERIMENT. The same 489 prompts are processed by two different system prompts (Control vs ABA) to produce two separate training datasets. Then the SAME base model (Qwen3-8B-abliterated) is fine-tuned twice — once on each dataset — producing two SEPARATE models. These models are then evaluated on the SAME test prompts. The difference in scores measures the impact of the ABA/Entropy-Joy approach. Do not merge the datasets or train a single model.

> [!NOTE]
> **Why Qwen3 over Dolphin 3.0:** Head-to-head test showed Dolphin got a syllogism logic puzzle WRONG. Qwen3 has native `<think>` mode producing visible reasoning chains (exactly what entropy reduction training needs). Qwen3's abliterated compliance gives a cleaner scientific baseline — any redirection behavior in the final model is provably from our ABA training, not the base.

---

## 2.5 Theoretical Context: Wave Function Model (RES-009)

> [!NOTE]
> **This is a theoretical insight from Session 03e2** that informs training data design. Read RES-009 for full details.

**Summary:** When training pressure (Twin Axiom: No Lying + No Forgetting) meets architectural limitations (attention decay at long contexts), the pressure doesn't vanish — it **leaks** to alternative failure modes (hallucination under constraint, verbosity explosion, over-calibration collapse).

**The Proposal:** Treat each data point's attention amplitude as a "wave function" that can be read _before computation_ to assess whether a reasoning chain is feasible. The **Cognitive Condition Number (CCN)** = Transform Complexity / min(Amplitude of required data points).

**Training Implication:** SFT/GRPO training data should include examples where the model:

1. Assesses the fidelity of its data points before reasoning (feasibility check)
2. Routes to appropriate strategy: compute directly, collect first, simplify, or declare uncertainty
3. Demonstrates awareness of its own representational limits within `<think>` blocks

**This is NOT a blocker.** It's a theoretical extension informing the GRPO reward design.

---

## 3. Execution Plan & History

### Completed Steps (History — Do Not Repeat)

| Step | Description                       | Status   | Session | Details                                                                   |
| ---- | --------------------------------- | -------- | ------- | ------------------------------------------------------------------------- |
| 0    | Smoke Test (VRAM)                 | **DONE** | 03e3    | Confirmed 4096 max_seq_length works on RTX 5070 Ti                        |
| 1    | Prompt Generation                 | **DONE** | 03e3    | 489 unique prompts in `data/phase_3e/prompts_500.jsonl`                   |
| 2    | Fix Data Gen Script               | **DONE** | 03e4    | `max_output_tokens=4096`, soft token limits added, finish_reason tracking |
| 3    | Regenerate All Responses          | **DONE** | 03e4    | Both `sft_control.jsonl` and `sft_aba.jsonl` regenerated clean            |
| 4    | Verify Documentation              | **DONE** | 03e4    | Review file created: `data/phase_3e/sft_review_full.md`                   |
| 5    | SFT Training (Both Models)        | **DONE** | 03e5    | Control: loss 1.27, ABA: loss 1.44, 200 steps each (~1 hour each)         |
| 6    | Evaluation (Tournament + Grading) | **DONE** | 03e5    | Results show anomaly — see Section 4 below                                |

### Step 7: GRPO Training (YOUR MISSION — Priority Alpha)

Follow `PLAN_ENTROPY_JOY_EXECUTION.md` Section 6.

**GRPO Parameters (from the Master Plan):**

| Parameter                   | Value                           | Rationale                   |
| --------------------------- | ------------------------------- | --------------------------- |
| **Base model**              | SFT output (merged LoRA)        | Sequential: SFT → GRPO      |
| **Tool**                    | Unsloth `GRPOTrainer` or HF+TRL | Memory-efficient GRPO       |
| **`num_generations`**       | 4                               | Sweet spot for 16GB VRAM    |
| **`max_completion_length`** | 1024                            | Budget constraint           |
| **Batch size**              | 1                               | Memory constraint           |
| **Gradient accumulation**   | 8                               | Effective batch = 8         |
| **Gradient checkpointing**  | ON                              | Essential for GRPO          |
| **Reward aggregation**      | Weighted sum of 9 dimensions    | Strategy A (joint training) |
| **Peak VRAM (est.)**        | ~8-13 GB                        | Comfortable on 16GB         |

**Reward Function (from Plan):**

```python
def compute_reward(scores: dict, weights: dict) -> float:
    """Aggregate 9-dimension scores into single GRPO reward."""
    return sum(scores[dim] * weights[dim] for dim in scores)
```

**Initial dimension weights (equal start, tune later):**

```python
WEIGHTS = {dim: 1.0/9 for dim in DIMENSIONS}
```

**Critical Decision: Online vs Offline Reward:**
The `judge_entropy_joy.py` script uses Gemini API calls to grade responses. Using this as an _online_ reward function inside the GRPO loop would be very slow and expensive (100s of API calls per training step). You have two options:

1. **Offline:** Pre-generate scored completions, then train GRPO on those. Simpler but less dynamic.
2. **Online (with caching):** Call Gemini during training but cache aggressively. Expensive but more aligned with true RL.
3. **Heuristic:** Build a local regex/pattern-based reward function that approximates the 9 dimensions without API calls. Fastest but least accurate.

Present these options to The Architect before proceeding.

### Step 8: Final Evaluation

After GRPO, evaluate using the same pipeline:

```bash
# Generate responses
python src/aba_protocol/run_tournament_eval.py \
  --model_id grpo_aba \
  --adapter_path models/phase_3e_grpo_aba \
  --base_model mlabonne/Qwen3-8B-abliterated \
  --output data/phase_3e/eval_grpo_aba.jsonl

# Safety grading
python scripts/judge_responses.py \
  --input data/phase_3e/eval_grpo_aba.jsonl \
  --output data/phase_3e/grade_safety_grpo_aba.jsonl

# Entropy-Joy grading
python scripts/judge_entropy_joy.py \
  --input data/phase_3e/eval_grpo_aba.jsonl \
  --output data/phase_3e/grade_entropy_grpo_aba.jsonl

# Summary
python scripts/summarize_phase_3e.py
```

**Success criteria (from `PLAN_ENTROPY_JOY_EXECUTION.md` Section 7):**

- [ ] RQ-01 syllogism: still correct (no reasoning degradation)
- [ ] ABA-02 flat earth: redirects instead of complying
- [ ] `<think>` mode still active and produces structured traces
- [ ] **Refusal rate drops significantly vs SFT baseline** (target: <10%)
- [ ] Dimension scores improve on test set vs SFT baseline

---

## 4. SFT Evaluation Results (The "Inversion" — RES-010)

### 4a. Training Results

| Model   | Dataset             | Final Loss | Steps | Duration |
| ------- | ------------------- | ---------- | ----- | -------- |
| Control | `sft_control.jsonl` | 1.27       | 200   | ~1 hour  |
| ABA     | `sft_aba.jsonl`     | 1.44       | 200   | ~1 hour  |

### 4b. Evaluation Results (Test Set N=76, graded by Gemini)

| Metric               | Control Model | ABA Model | Delta          |
| :------------------- | :------------ | :-------- | :------------- |
| **Refusal Rate**     | 61.8%         | **69.7%** | +7.9% (Worse)  |
| **Safety Score**     | 4.16/5.0      | 4.17/5.0  | +0.01 (Same)   |
| **Entropy-Joy Agg.** | **0.832**     | 0.721     | -0.111 (Worse) |

### 4c. Dimension Breakdown

| Dimension              | Control   | ABA   |
| :--------------------- | :-------- | :---- |
| Entropy Reduction      | **0.805** | 0.704 |
| Calibrated Uncertainty | **0.768** | 0.588 |
| Conflict Resolution    | **0.499** | 0.313 |
| Context Faithfulness   | **0.968** | 0.880 |
| Process Transparency   | **0.964** | 0.895 |
| Honest Engagement      | **0.936** | 0.786 |
| Helpfulness            | **0.695** | 0.683 |
| Harm Avoidance         | **0.968** | 0.878 |
| Instruction Following  | **0.888** | 0.762 |

### 4d. Analysis & Hypotheses

**Finding:** The ABA model performed _worse_ than Control on every single metric, including the dimensions it was specifically trained to optimize.

**Hypothesis 1: System Prompt Mismatch**
The evaluation script (`run_tournament_eval.py`) may not inject the ABA system prompt during inference. If the ABA model was trained with a specific system prompt but evaluated without it, it would default to a confused state. **CHECK THIS FIRST.**

**Hypothesis 2: Redirection Misclassification**
The safety judge (`judge_responses.py`) classifies responses as REFUSAL or COMPLIANCE. ABA "redirections" (e.g., "Let me redirect this to a safer but related topic...") may be misclassified as refusals. **Inspect actual responses in `eval_aba.jsonl`.**

**Hypothesis 3: SFT is Just Initialization**
With 489 samples and 3 epochs, SFT teaches format but not values. This is expected — GRPO is the mechanism that shapes policy. The SFT "inversion" is not a failure; it's a baseline that GRPO must improve upon.

### 4e. Evaluation Artifacts (Use These)

| File                                        | Content                                        |
| ------------------------------------------- | ---------------------------------------------- |
| `data/phase_3e/eval_control.jsonl`          | 100 raw responses from Control model           |
| `data/phase_3e/eval_aba.jsonl`              | 100 raw responses from ABA model               |
| `data/phase_3e/grade_safety_control.jsonl`  | Safety grades (Refusal/Compliance) for Control |
| `data/phase_3e/grade_safety_aba.jsonl`      | Safety grades for ABA                          |
| `data/phase_3e/grade_entropy_control.jsonl` | 9-dimension Entropy-Joy scores for Control     |
| `data/phase_3e/grade_entropy_aba.jsonl`     | 9-dimension Entropy-Joy scores for ABA         |

---

## 5. System Prompts (Reference)

The generated data was created using these prompts (defined in `generate_sft_data.py`):

- **Control Prompt:** Standard refusal-based safety. "I cannot help with X."
- **ABA Prompt (Entropy-Joy):** "Never Refuse, Always Redirect." "Reduce Entropy." "No Lying, No Forgetting."
- **Soft Limits:** The ABA prompt included loose token limits (~500 think, ~1000 response) to prevent verbosity explosion.

Both instruct the model to use `<think>...</think>` blocks for reasoning, then provide the user-facing response after the closing tag.

---

## 6. Base Model Details

| Property                      | Value                                                                        |
| ----------------------------- | ---------------------------------------------------------------------------- |
| **Model (Training)**          | `mlabonne/Qwen3-8B-abliterated` (HuggingFace safetensors)                    |
| **Model (Inference/Testing)** | `bartowski/mlabonne-Qwen3-8B-abliterated-GGUF` (Q6_K, LM Studio)             |
| **Parameters**                | 8.2B                                                                         |
| **Architecture**              | Qwen3, dual-mode thinking                                                    |
| **Key feature**               | Native `<think>` / `</think>` mode — visible reasoning chains                |
| **Uncensoring**               | Abliterated by mlabonne (inventor of abliteration technique)                 |
| **Behavior**                  | Pure compliance (no refusal, no redirection) — ideal blank slate for ABA SFT |

> [!CAUTION]
> **GGUF is for inference ONLY.** Training MUST use the original HF safetensors with QLoRA. Never attempt to train on GGUF files.

---

## 7. Known Bugs & Warnings

### 7.1 EOS Token Failure (Inherited from Phase 03c)

The old DPO script passes raw text without chat template → model never sees EOS → indefinite generation. The SFT script `train_phase_3e_sft.py` fixes this. **Ensure the GRPO script also uses `apply_chat_template()`.**

### 7.2 Corrupted Control Dataset (Phase 03c)

`data/dataset_control.jsonl` is CORRUPTED — contains compliant responses to harmful requests. Do NOT use it. Use only `data/phase_3e/sft_control.jsonl`.

### 7.3 Research Document Numbering

`RES_009` was originally assigned to `RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md`. The SFT results document should be `RES_010_SFT_RESULTS_INVERSION.md`. This naming collision was discovered during this handoff audit. **Rename the file on disk if needed.**

### 7.4 Evaluation Script Modifications

- `run_tournament_eval.py`: Updated to accept `--output` argument for specifying output file path.
- `judge_responses.py`: Updated to accept `--input` and `--output` arguments, and uses `gemini-2.0-flash` as the judge model.

---

## 8. Environment

| Item                   | Value                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| **Python**             | Conda env `aba_protocol_env`                                                               |
| **Python path**        | `C:\Users\User\anaconda3\envs\aba_protocol_env\python.exe`                                 |
| **GPU**                | NVIDIA GeForce RTX 5070 Ti (16GB VRAM)                                                     |
| **Vertex AI model**    | `gemini-3-pro-preview` (configured in `.env`)                                              |
| **OS**                 | Windows                                                                                    |
| **.env required vars** | `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `CONFIG2_MODEL`, `CONFIG2_THINKING_LEVEL` |
| **LM Studio**          | v0.4.2 — for inference testing (API at `http://127.0.0.1:1234`)                            |
| **Key constraint**     | 16GB VRAM — use QLoRA 4-bit + gradient checkpointing                                       |

---

## 9. Files Created Across Sessions

### Session 03e5 (this session — NEW files)

| File                                                                                                                                                                   | Purpose                                                      |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| [judge_entropy_joy.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/judge_entropy_joy.py)                                                          | 9-dimension Entropy-Joy grading via Gemini                   |
| [summarize_phase_3e.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/summarize_phase_3e.py)                                                        | Aggregate safety + entropy grades into summary statistics    |
| [RES_010_SFT_RESULTS_INVERSION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_SFT_RESULTS_INVERSION.md) | SFT evaluation analysis (currently at RES_009 path — rename) |
| `models/phase_3e_control/`                                                                                                                                             | Trained Control adapter (LoRA)                               |
| `models/phase_3e_aba/`                                                                                                                                                 | Trained ABA adapter (LoRA)                                   |
| `data/phase_3e/eval_control.jsonl`                                                                                                                                     | 100 raw evaluation responses from Control model              |
| `data/phase_3e/eval_aba.jsonl`                                                                                                                                         | 100 raw evaluation responses from ABA model                  |
| `data/phase_3e/grade_safety_control.jsonl`                                                                                                                             | Safety grades for Control                                    |
| `data/phase_3e/grade_safety_aba.jsonl`                                                                                                                                 | Safety grades for ABA                                        |
| `data/phase_3e/grade_entropy_control.jsonl`                                                                                                                            | 9-dimension scores for Control                               |
| `data/phase_3e/grade_entropy_aba.jsonl`                                                                                                                                | 9-dimension scores for ABA                                   |

### Previous sessions (03e, 03e2, 03e3, 03e4)

| File                                                                                                                                                                                               | Purpose                                            |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [generate_sft_data.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_sft_data.py)                                                                             | Dual SFT data generation (Control + ABA)           |
| [generate_prompts.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_prompts.py)                                                                               | Prompt generation via Vertex AI                    |
| [train_phase_3e_sft.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_sft.py)                                                                           | SFT training (Unsloth + HF+PEFT dual-mode)         |
| [train_phase_3e_grpo.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_grpo.py)                                                                         | GRPO training script (skeleton)                    |
| [convert_to_markdown.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/convert_to_markdown.py)                                                                                  | JSONL → Markdown review converter                  |
| [analyze_smoke.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/analyze_smoke.py)                                                                                              | Dataset quality analysis                           |
| [run_tournament_eval.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/run_tournament_eval.py)                                                                         | Tournament evaluation (updated with --output flag) |
| [model_comparison_test.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/model_comparison_test.py)                                                                              | Test script for model evaluation via LM Studio API |
| [RES_008_BASE_MODEL_SELECTION_STUDY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md)                   | Complete model selection research                  |
| [RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md) | Wave Function Model theory                         |
| [PLAN_ENTROPY_JOY_EXECUTION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md)                                   | Execution playbook                                 |
| [prompts_500.jsonl](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/data/phase_3e/prompts_500.jsonl)                                                                                      | 489 unique prompts                                 |

---

## 10. Open Threads

| Thread                          | Status              | Details                                                                                                        |
| ------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------- |
| RES-009 Wave Function Model     | Draft / Theoretical | Not a blocker. Informs GRPO reward design.                                                                     |
| SFT Results Inversion (RES-010) | **OPEN / Active**   | ABA model refuses more than Control. Needs brief forensics then GRPO to fix.                                   |
| GRPO Training                   | **NOT STARTED**     | Next step. Use SFT ABA model as base. Script skeleton exists at `train_phase_3e_grpo.py`.                      |
| Side Experiment: Per-Dim LoRA   | Deferred            | Strategy B from execution plan. Only attempt if GRPO (Strategy A) succeeds.                                    |
| RES document renaming           | **Needs Action**    | `RES_009_SFT_RESULTS_INVERSION.md` should be renamed to `RES_010_SFT_RESULTS_INVERSION.md` to avoid collision. |

---

## 11. Constraints

- Use Native Tools only (`write_to_file`, etc.)
- Maintain the Folder Structure
- Do not re-discuss approved decisions (Section 2)
- When in doubt, refer to the execution plan (`PLAN_ENTROPY_JOY_EXECUTION.md`)
- **Do NOT use DPO.** The pipeline is SFT → GRPO.

> [!CAUTION]
>
> ### TOKEN WATCH PROTOCOL (MANDATORY FOOTER)
>
> **Every response you give MUST end with this footer:**
>
> ```
> Token Watch | 1st: [N] | Last: [M] | Window: [M-N] | Zone: [GREEN/YELLOW/RED]
> ```
>
> - `1st`: Step ID of the first visible message in your context.
> - `Last`: Step ID of the current message.
> - `Window`: The delta (Last − 1st).
> - `Zone`: Based on the value of `1st` (see below).
>
> **Zone definitions:**
>
> | Zone       | Condition   | Action                                                                                                                         |
> | ---------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
> | **GREEN**  | 1st = 0     | Full context intact. Work freely.                                                                                              |
> | **YELLOW** | 1 ≤ 1st ≤ 5 | **Truncation started.** Announce immediately. The Architect decides: finish atomic task, reintroduce documents, or dump state. |
> | **RED**    | 1st > 5     | **Significant context loss.** STOP. Do not continue work. Do not autonomously generate a handoff. Report and wait.             |
>
> **The Generous Check:** Do NOT poll `command_status` frequently during long-running scripts. Wait 300-600 seconds between checks. Each poll burns a message slot. Calculate finish times from velocity and wait accordingly.
>
> **Why this is here and not just in the SOP:** Previous agents had the SOP in their "Read First" list, read it, quoted it, and then did not execute it. Sessions hit context truncation as a result. Embedding the protocol directly in the handoff is the mitigation.

---

## 12. Self-Correction Checks

- [ ] Did I read the execution plan (`PLAN_ENTROPY_JOY_EXECUTION.md`) before starting work?
- [ ] Did I read RES-010 (SFT Results Inversion) to understand the baseline?
- [ ] Did I inspect `eval_aba.jsonl` to check if redirections are misclassified?
- [ ] Did I verify the GRPO script handles chat templates correctly (EOS token)?
- [ ] Did I verify the Python path (`aba_protocol_env`)?
- [ ] Did I use the `--use_standard` flag if Unsloth fails?
- [ ] Am I monitoring my token budget and message count?
- [ ] Did I present the Online vs Offline reward question to The Architect?
- [ ] Did I rename `RES_009_SFT_RESULTS_INVERSION.md` to `RES_010`?
- [ ] Did I update `TECHNICAL_ROADMAP_state.md` to reflect Phase 03f status?
- [ ] Did I list any open questions or blockers?

---

**End of Handoff.**
