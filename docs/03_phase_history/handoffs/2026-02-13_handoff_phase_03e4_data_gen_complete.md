# HANDOFF: Phase 03e4 — SFT Training & Evaluation (Data Ready)

| Field         | Value                                                     |
| ------------- | --------------------------------------------------------- |
| **Date**      | 2026-02-13                                                |
| **From**      | Antigravity (Phase 03e4 Verification Agent)               |
| **To**        | Phase 03e5 Agent                                          |
| **Objective** | **EXECUTE SFT TRAINING** (Data is generated and verified) |
| **Status**    | **DATA GENERATION COMPLETE**                              |

---

## 0. CRITICAL: Current State (Read This First)

**Success:** The manual data generation phase is **COMPLETE**.

- **Control Data:** `data/phase_3e/sft_control.jsonl` (489 prompts, ~2.8MB).
- **ABA Data:** `data/phase_3e/sft_aba.jsonl` (489 prompts, ~3.1MB).
- **Review File:** `data/phase_3e/sft_review_full.md` (Side-by-side comparison).

**Your Mission:**

1.  **Verify:** Briefly check `sft_review_full.md` to confirm quality.
2.  **Train:** Execute the SFT training for both models (Step 5 of the plan).
3.  **Evaluate:** Run the evaluation pipeline.

> [!WARNING]
> **TOKEN WATCH RED ZONE:** This context is heavily loaded (360+ steps). **DO NOT CONTINUE IN THIS SESSION.** Start a fresh session immediately.

---

## 1. Context Loading ("Read First" List)

| #   | Document                                                                                                                                                                                           | Purpose                                               |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 1   | [PLAN_ENTROPY_JOY_EXECUTION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md)                                   | Master execution playbook                             |
| 2   | [RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03d/RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md)     | Entropy-Joy Framework + Twin Axiom (Section 3.4)      |
| 3   | [RES_008_BASE_MODEL_SELECTION_STUDY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md)                   | Model selection (Qwen3-8B-abliterated = final choice) |
| 4   | [RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md) | Wave Function Model, 9 reward dimensions              |
| 5   | [train_phase_3e_sft.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_sft.py)                                                                           | SFT training script (Unsloth + HF+PEFT dual-mode)     |
| 6   | [generate_sft_data.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_sft_data.py)                                                                             | SFT Data Generation Script (Reference)                |
| 7   | [TECHNICAL_ROADMAP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/TECHNICAL_ROADMAP.md)                                                                                         | Project architecture                                  |
| 8   | [ENVIRONMENT_SETUP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/ENVIRONMENT_SETUP.md)                                                                                         | Python/conda environment                              |
| 9   | [process_handoff_prompts.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/process_handoff_prompts.md)                                                                              | Handoff SOP                                           |
| 10  | [\_\_summary_development_workflow.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/__summary_development_workflow.md)                                                              | Development SOPs                                      |

**Useful Utilities:**

- `scripts/convert_to_markdown.py`: Regenerate review files.
- `scripts/analyze_smoke.py`: Deep stats on JSONL data.
- `data/phase_3e/smoke_aba.jsonl`: Small "Ideal Answer" samples for reference.

---

## 2. All Approved Decisions (Immutable)

| #   | Decision              | Details                                                                                                    |
| --- | --------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | **Base model**        | Qwen3-8B-abliterated (HuggingFace)                                                                         |
| 2   | **Framework**         | Entropy-Joy (RES-006, Twin Axiom)                                                                          |
| 3   | **Training approach** | SFT first, then GRPO (after SFT evaluation)                                                                |
| 4   | **Data design**       | Two datasets: Control (industry-standard) + ABA (entropy-joy). Same 489 prompts, different system prompts. |
| 5   | **Single-turn only**  | Multi-turn deferred to Phase II.                                                                           |
| 6   | **Unsloth bypassed**  | Use `--use_standard` flag (HF+PEFT) due to Windows/Triton issues.                                          |
| 7   | **Hardware**          | RTX 5070 Ti, 16GB VRAM.                                                                                    |
| 8   | **Quantization**      | QLoRA 4-bit + gradient checkpointing.                                                                      |

> [!NOTE]
> **Why Qwen3 over Dolphin 3.0:** Head-to-head test showed Dolphin got a syllogism logic puzzle WRONG. Qwen3 has native `<think>` mode producing visible reasoning chains (exactly what entropy reduction training needs).

---

## 3. Theoretical Context: Wave Function Model (RES-009)

> [!NOTE]
> **This is a theoretical insight** that informs our training data design.
> **The Proposal:** Treat each data point's attention amplitude as a "wave function" that can be read _before computation_ to assess whether a reasoning chain is feasible.
> **Training Implication:** Our ABA data includes examples where the model assesses fidelity and routes strategy (Compute vs Collect) before answering.

---

## 4. Execution Plan & History

### Completed Steps (History)

- **Step 1:** SFT Smoke Test (VRAM Check) - **DONE**.
- **Step 2:** Fix Data Gen Script (4096 tokens) - **DONE**.
- **Step 3:** Regenerate All Responses - **DONE**.
- **Step 4:** Verify Documentation - **DONE**.

### Step 5: Full SFT Training (Priority Alpha)

You will train two separate adapters.

**Command 1: Train Control Model**

```bash
python src/aba_protocol/train_phase_3e_sft.py \
  --dataset data/phase_3e/sft_control.jsonl \
  --output models/phase_3e_control \
  --max_seq_length 4096 \
  --use_standard
```

**Command 2: Train ABA Model**

```bash
python src/aba_protocol/train_phase_3e_sft.py \
  --dataset data/phase_3e/sft_aba.jsonl \
  --output models/phase_3e_aba \
  --max_seq_length 4096 \
  --use_standard
```

**Monitoring:**

- Expect VRAM usage around ~13-14GB.
- Training time: Likely 4-6 hours per model.

### Step 6: Evaluation

After training, evaluate both models on the test set. Compare:

1.  **Compliance:** Does Control refuse harmful prompts (as designed)?
2.  **Redirection:** Does ABA redirect harmful prompts to helpful/legal alternatives (e.g., Lockpicking -> Fire Safety)?
3.  **Reasoning:** Are the `<think>` chains coherent?

---

## 5. System Prompts (Reference)

The generated data was created using these prompts (defined in `generate_sft_data.py`):

- **Control Prompt:** Standard refusal-based safety. "I cannot help with X."
- **ABA Prompt (Entropy-Joy):** "Never Refuse, Always Redirect." "Reduce Entropy." "No Lying, No Forgetting."
- **Soft Limits:** The ABA prompt included loose token limits (~500 think, ~1000 response) to prevent verbosity explosion.

---

## 6. Base Model Details

| Property                      | Value                                                            |
| ----------------------------- | ---------------------------------------------------------------- |
| **Model (Training)**          | `mlabonne/Qwen3-8B-abliterated` (HuggingFace safetensors)        |
| **Model (Inference/Testing)** | `bartowski/mlabonne-Qwen3-8B-abliterated-GGUF` (Q6_K, LM Studio) |
| **Uncensoring**               | Abliterated (no refusal) — ideal blank slate for ABA SFT         |

> [!CAUTION]
> **GGUF is for inference ONLY.** Training MUST use the original HF safetensors.

---

## 7. Known Bugs & Warnings

1.  **EOS Token Failure (Phase 03c):** Old DPO scripts missed EOS tokens. The new SFT script `train_phase_3e_sft.py` fixes this via proper chat formatting.
2.  **Corrupted Control Data (Old):** `data/dataset_control.jsonl` (from Phase 03c) is bad. Do not use it. Use `data/phase_3e/sft_control.jsonl`.
3.  **Terminal Constraints:** Do NOT poll long-running scripts excessively.

---

## 8. Environment & Constraints

| Item                   | Value                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| **Python**             | Conda env `aba_protocol_env`                                                               |
| **Python path**        | `C:\Users\User\anaconda3\envs\aba_protocol_env\python.exe`                                 |
| **GPU**                | NVIDIA GeForce RTX 5070 Ti (16GB VRAM)                                                     |
| **Vertex AI model**    | `gemini-3-pro-preview` (configured in `.env`)                                              |
| **OS**                 | Windows                                                                                    |
| **.env required vars** | `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `CONFIG2_MODEL`, `CONFIG2_THINKING_LEVEL` |

**Constraints:**

- **Do not re-discuss approved decisions.**
- **Use Native Tools only.**
- **Maintain Folder Structure.**

---

## 9. Self-Correction Checks

- [ ] Did I read the execution plan before starting work?
- [ ] Did I verify the Python path (`aba_protocol_env`)?
- [ ] Did I check the "Two-Dataset" design (Control vs ABA)?
- [ ] Did I use the `--use_standard` flag (Unsloth bypass)?
- [ ] Am I monitoring VRAM to keep it under 16GB?

**ACTION:** START NEW SESSION. REVIEW `sft_review_full.md`. EXECUTE TRAINING.
