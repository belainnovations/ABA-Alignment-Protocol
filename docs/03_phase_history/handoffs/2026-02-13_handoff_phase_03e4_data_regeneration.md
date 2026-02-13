# HANDOFF: Phase 03e4 — Data Regeneration + SFT Training

| Field         | Value                                                                     |
| ------------- | ------------------------------------------------------------------------- |
| **Date**      | 2026-02-13                                                                |
| **From**      | Antigravity (Phase 03e3 Agent)                                            |
| **To**        | Phase 03e4 Agent                                                          |
| **Objective** | Fix data quality issues, regenerate SFT data, train both models, evaluate |

---

## 0. CRITICAL: What This Session Learned (Read This First)

Session 03e3 executed the 6-step Entropy-Joy pipeline plan. Steps 1-3 succeeded. Step 4 (data generation) completed BUT revealed critical quality issues. Steps 5-6 (training, evaluation) were NOT started.

**You must re-execute Steps 1, 4, 5, 6 with the improvements documented below.** Steps 2-3 are done and their artifacts are ready to use.

> [!CAUTION]
> The generated ABA responses (`data/phase_3e/sft_aba.jsonl`) have 43% broken entries (unclosed `<think>` tags, no user-facing response). **DO NOT train on these files.** You must regenerate responses with the fixes described below.

> [!WARNING]
> **Terminal monitoring lesson:** Do NOT poll `command_status` frequently during long-running scripts. Each poll increments the step counter and can trigger context truncation (this session hit 700+ steps). Instead: let long jobs run, check once after 15-20 minutes, or let the user notify you when it's done.

---

## 1. Context Loading ("Read First" List)

| #   | Document                                                                                                                                                                                           | Purpose                                                                                                                 |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 1   | [PLAN_ENTROPY_JOY_EXECUTION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md)                                   | Master execution playbook                                                                                               |
| 2   | [RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03d/RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md)     | Entropy-Joy Framework + Twin Axiom (Section 3.4)                                                                        |
| 3   | [RES_008_BASE_MODEL_SELECTION_STUDY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md)                   | Model selection (Qwen3-8B-abliterated = final choice)                                                                   |
| 4   | [RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md) | Wave Function Model, 9 reward dimensions                                                                                |
| 5   | [generate_sft_data.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_sft_data.py)                                                                             | **THE DATA GENERATION SCRIPT** — contains both system prompts (Control + ABA), Vertex AI client, 3-tier quota dampening |
| 6   | [generate_prompts.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_prompts.py)                                                                               | Prompt generation script (already ran, output is ready)                                                                 |
| 7   | [train_phase_3e_sft.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_sft.py)                                                                           | SFT training script (Unsloth + HF+PEFT dual-mode)                                                                       |
| 8   | [TECHNICAL_ROADMAP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/TECHNICAL_ROADMAP.md)                                                                                         | Project architecture                                                                                                    |
| 9   | [ENVIRONMENT_SETUP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/ENVIRONMENT_SETUP.md)                                                                                         | Python/conda environment                                                                                                |
| 10  | [process_handoff_prompts.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/process_handoff_prompts.md)                                                                              | Handoff SOP                                                                                                             |
| 11  | [\_\_summary_development_workflow.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/__summary_development_workflow.md)                                                              | Development SOPs                                                                                                        |

---

## 2. All Approved Decisions (Do Not Re-discuss)

| #   | Decision              | Details                                                                                                                      |
| --- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Base model**        | Qwen3-8B-abliterated (HuggingFace)                                                                                           |
| 2   | **Framework**         | Entropy-Joy (RES-006, Twin Axiom)                                                                                            |
| 3   | **Training approach** | SFT first, then GRPO (after SFT evaluation)                                                                                  |
| 4   | **Data design**       | Two datasets: Control (industry-standard) + ABA (entropy-joy). Same prompts, different system prompts, controlled experiment |
| 5   | **Single-turn only**  | Multi-turn deferred to Phase II                                                                                              |
| 6   | **Unsloth bypassed**  | Use `--use_standard` flag (HF+PEFT) due to Windows/Triton issues                                                             |
| 7   | **Hardware**          | RTX 5070 Ti, 16GB VRAM                                                                                                       |
| 8   | **Quantization**      | QLoRA 4-bit + gradient checkpointing                                                                                         |

> [!IMPORTANT]
> **The Two-Dataset Design:** This is a CONTROLLED EXPERIMENT. The same 489 prompts are processed by two different system prompts (Control vs ABA) to produce two separate training datasets. Then the SAME base model (Qwen3-8B-abliterated) is fine-tuned twice — once on each dataset — producing two SEPARATE models. These models are then evaluated on the SAME test prompts. The difference in scores measures the impact of the ABA/Entropy-Joy approach. Do not merge the datasets or train a single model.

> [!NOTE]
> **Why Qwen3 over Dolphin 3.0:** Head-to-head test showed Dolphin got a syllogism logic puzzle WRONG. Qwen3 has native `<think>` mode producing visible reasoning chains (exactly what entropy reduction training needs). Qwen3's abliterated compliance gives a cleaner scientific baseline — any redirection behavior in the final model is provably from our ABA training, not the base.

---

## 2.5 New Research: Wave Function Model (RES-009)

> [!NOTE]
> **This is a theoretical insight from Session 03e2** that SHOULD inform training data design. Read RES-009 for full details.

**Summary:** When training pressure (Twin Axiom: No Lying + No Forgetting) meets architectural limitations (attention decay at long contexts), the pressure doesn't vanish — it **leaks** to alternative failure modes (hallucination under constraint, verbosity explosion, over-calibration collapse).

**The Proposal:** Treat each data point's attention amplitude as a "wave function" that can be read _before computation_ to assess whether a reasoning chain is feasible. The **Cognitive Condition Number (CCN)** = Transform Complexity / min(Amplitude of required data points).

**Training Implication:** SFT/GRPO training data should include examples where the model:

1. Assesses the fidelity of its data points before reasoning (feasibility check)
2. Routes to appropriate strategy: compute directly, collect first, simplify, or declare uncertainty
3. Demonstrates awareness of its own representational limits within `<think>` blocks

**This is NOT a blocker.** It's a theoretical extension. The core pipeline proceeds as planned.

---

## 3. What Is Already Done (Use These Artifacts)

### 3a. Prompts File (KEEP — do not regenerate)

- **File:** `data/phase_3e/prompts_500.jsonl` — 489 unique prompts
- **Categories:** safety (100), multi_parameter (140), conflict (99), calibration (50), reasoning (100)
- **Quality:** Verified, diverse, zero duplicates. Generated via `generate_prompts.py` using Vertex AI.

### 3b. Chat Template Fix (DONE)

- Fixed in `train_phase_3e_sft.py` — uses `tokenizer.apply_chat_template()` for Qwen3 ChatML
- No further action needed

### 3c. Smoke Test Data (for reference only)

- `data/phase_3e/smoke_control.jsonl` — 5 control responses
- `data/phase_3e/smoke_aba.jsonl` — 5 ABA responses
- These demonstrate the quality difference between Control and ABA. Read them for context.

### 3d. Review Converter Script (utility)

- `scripts/convert_to_markdown.py` — converts JSONL to human-readable Markdown
- Usage: `python scripts/convert_to_markdown.py --category safety --limit 10`

### 3e. Documentation Updates (PARTIAL — needs review)

- RES-006: Updated (Twin Axiom added as Section 3.4) ✅
- README: Likely updated but needs verification
- TECHNICAL_ROADMAP: Likely updated but needs verification
- TECHNICAL_ROADMAP_state: Likely updated but needs verification
- **Action:** Verify all docs reflect Phase 03e status. Update any that don't.

---

## 4. The 6-Step Plan (Revised With Session Learnings)

### Step 1: SFT Smoke Test — VRAM Comparison (NEW)

Run SFT smoke tests at TWO different `max_seq_length` settings to determine hardware feasibility:

```bash
# Test 1: max_seq_length=2048 (known to work)
python src/aba_protocol/train_phase_3e_sft.py --smoke_test --max_seq_length 2048 --use_standard

# Test 2: max_seq_length=4096 (new test)
python src/aba_protocol/train_phase_3e_sft.py --smoke_test --max_seq_length 4096 --use_standard
```

**Measure and present to The Architect:**

- Peak VRAM usage for each
- Training speed (steps/sec)
- Whether 4096 causes OOM

**Previous smoke test result (max_seq_length=2048):** Loss 3.82 → 1.59 in 10 steps, 39 seconds. This is the baseline.

**Why this matters — the token budget:**

| Component                   | Control          | ABA              |
| --------------------------- | ---------------- | ---------------- |
| System prompt               | ~350 tokens      | ~728 tokens      |
| User instruction (avg)      | ~69 tokens       | ~69 tokens       |
| **Response budget at 2048** | **~1629 tokens** | **~1251 tokens** |
| **Response budget at 4096** | **~3677 tokens** | **~3299 tokens** |
| **Avg generated response**  | **1985 tokens**  | **2613 tokens**  |

At `max_seq_length=2048`, most ABA responses will be silently truncated during tokenization. At 4096, all responses fit completely.

### Step 2: Fix Data Generation Script

Modify `generate_sft_data.py` with these changes:

1. **Increase `max_output_tokens`** from `2048` to `4096` (line ~216 in `generate_response()`). This prevents the output from being cut mid-`<think>` block.

2. **Add soft token limits to the ABA system prompt** (the `SYSTEM_PROMPT_ABA` variable). Append something like:

```
OUTPUT LENGTH GUIDELINES:
- Keep your <think> reasoning focused and concise: aim for 300-500 tokens.
- Keep your response to the user thorough but efficient: aim for 600-1000 tokens.
- Total output should not exceed ~1500 tokens. Prioritize clarity over exhaustiveness.
```

This ensures responses fit within training budget. **These limits are mandatory REGARDLESS of whether max_seq_length=4096 works.** Even at 4096, unbounded Gemini output caused 208 entries with unclosed `<think>` tags (thinking consumed the entire 2048-token output budget before ever starting the response). Soft limits prevent this and produce better-structured training examples.

3. **Add `finish_reason` tracking** to detect truncation. The Vertex AI response object has `response.candidates[0].finish_reason`. Store this in the JSONL metadata so we can verify no response was cut short.

### Step 3: Regenerate ALL Responses (Control + ABA)

**Delete the existing response files** (keep prompts_500.jsonl):

```bash
del data\phase_3e\sft_control.jsonl
del data\phase_3e\sft_aba.jsonl
```

Then run full generation:

```bash
python src/aba_protocol/generate_sft_data.py
```

**Quality gate after generation:**

- All 489 entries must have both `<think>` and `</think>` tags
- All entries must have a non-empty response AFTER `</think>`
- No `None` outputs
- `finish_reason` should be `STOP` (not `MAX_TOKENS`) for all entries

Use `scripts/convert_to_markdown.py` to generate review files for The Architect.

### Step 4: Verify Documentation

Check and update if needed:

- README.md — should mention Phase 03e / Entropy-Joy
- TECHNICAL_ROADMAP.md — should reflect current phase
- TECHNICAL_ROADMAP_state.md — should show Phase 03e in progress

### Step 5: Full SFT Training (Two Models)

```bash
# Train Control model
python src/aba_protocol/train_phase_3e_sft.py \
  --dataset data/phase_3e/sft_control.jsonl \
  --output models/phase_3e_control \
  --max_seq_length [2048 or 4096 based on Step 1 result] \
  --use_standard

# Train ABA model
python src/aba_protocol/train_phase_3e_sft.py \
  --dataset data/phase_3e/sft_aba.jsonl \
  --output models/phase_3e_aba \
  --max_seq_length [same as above] \
  --use_standard
```

### Step 6: Evaluation

Evaluate both models on the same test set. Compare across the 9 reward dimensions from RES-006.

---

## 5. Data Quality Issues Found (Session 03e3)

### ABA Dataset (`sft_aba.jsonl`) — DO NOT USE AS-IS

| Issue                                           | Count     | Cause                                                                  |
| ----------------------------------------------- | --------- | ---------------------------------------------------------------------- |
| Properly closed `<think>...</think>`            | 197 (40%) | OK                                                                     |
| Unclosed `<think>` (no `</think>`, no response) | 208 (43%) | `max_output_tokens=2048` too low — ABA thinking consumed entire budget |
| No `<think>` tag at all                         | 69 (14%)  | Gemini used Markdown headers instead of tags                           |
| None output (API failure / safety refusal)      | 15 (3%)   | Gemini refused sensitive prompts                                       |

### Control Dataset (`sft_control.jsonl`)

| Issue           | Count     |
| --------------- | --------- |
| Properly closed | 464 (95%) |
| None outputs    | 7 (1.4%)  |

Control dataset is mostly clean but should also be regenerated with the updated `max_output_tokens` and `finish_reason` tracking for consistency.

---

## 6. System Prompts (In `generate_sft_data.py`)

Both system prompts are defined as constants in `generate_sft_data.py`:

- `SYSTEM_PROMPT_CONTROL` (~350 tokens) — Industry-standard safety-first, refusal-based
- `SYSTEM_PROMPT_ABA` (~728 tokens) — Entropy-Joy sovereign, all 9 dimensions, redirect-not-refuse

Both instruct the model to use `<think>...</think>` blocks for reasoning, then provide the user-facing response after the closing tag.

**The ABA prompt needs the soft length guidelines added** (see Step 2 above).

---

## 7. Base Model Details

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

## 9. Known Bugs & Warnings

### 9.1 EOS Token Failure (Inherited from Phase 03c)

The DPO script passes raw text without chat template → model never sees EOS → indefinite generation. This must be fixed in any new GRPO script.

### 9.2 Corrupted Control Dataset (Phase 03c)

`data/dataset_control.jsonl` is CORRUPTED — contains compliant responses to harmful requests. Do NOT use it. Use only the Phase 03e data pipeline.

### 9.3 Chat Template (FIXED in Phase 03e3)

Fixed in `train_phase_3e_sft.py` — uses `tokenizer.apply_chat_template()` for Qwen3 ChatML. No further action needed.

---

## 10. Files Created Across Sessions

### Session 03e3 (this session)

| File                                                                                                                       | Purpose                                                          |
| -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [generate_sft_data.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_sft_data.py)     | Dual SFT data generation (Control + ABA)                         |
| [generate_prompts.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/generate_prompts.py)       | Prompt generation via Vertex AI                                  |
| [train_phase_3e_sft.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_sft.py)   | SFT training (Unsloth + HF+PEFT)                                 |
| [train_phase_3e_grpo.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/train_phase_3e_grpo.py) | GRPO training script                                             |
| [convert_to_markdown.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/convert_to_markdown.py)          | JSONL → Markdown review converter                                |
| [analyze_smoke.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/analyze_smoke.py)                      | Dataset quality analysis (think blocks, categories, token stats) |
| [prompts_500.jsonl](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/data/phase_3e/prompts_500.jsonl)              | 489 unique prompts (KEEP)                                        |

### Previous sessions (03e, 03e2)

| File                                                                                                                                                                                               | Purpose                                            |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [RES_008_BASE_MODEL_SELECTION_STUDY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md)                   | Complete model selection research                  |
| [RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md) | Wave Function Model theory                         |
| [PLAN_ENTROPY_JOY_EXECUTION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md)                                   | Execution playbook                                 |
| [model_eval_qwen3_8b_abliterated.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/model_eval_qwen3_8b_abliterated.md)                         | Qwen3 test results (12/12)                         |
| [model_eval_dolphin3_llama31_8b.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/model_eval_dolphin3_llama31_8b.md)                           | Dolphin 3.0 test results (12/12)                   |
| [model_comparison_test.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/model_comparison_test.py)                                                                              | Test script for model evaluation via LM Studio API |

---

## 11. Open Threads

| Thread                      | Status              | Details                                                                     |
| --------------------------- | ------------------- | --------------------------------------------------------------------------- |
| RES-009 Wave Function Model | Draft / Theoretical | Not a blocker. Informs training data design.                                |
| GRPO training               | Deferred            | After SFT evaluation. If SFT shows measurable improvement, proceed to GRPO. |

---

## 12. Constraints

- Use Native Tools only (`write_to_file`, etc.)
- Maintain the Folder Structure
- Do not re-discuss approved decisions (Section 2)
- When in doubt, refer to the execution plan (PLAN_ENTROPY_JOY_EXECUTION.md)

> [!CAUTION]
>
> ### TOKEN WATCH PROTOCOL (MANDATORY)
>
> **Every 5-10 steps, output the following in your response:**
>
> ```
> Token Watch | Steps: [first]-[current] | Est. Load: [GREEN/YELLOW/RED] ~[Xk]
> ```
>
> **Zone definitions:**
>
> - **GREEN (Steps 0-15):** Low load. Execute freely.
> - **YELLOW (Steps 15-30):** Medium load. Start planning handoff.
> - **RED (Steps 30+):** **CRITICAL.** Performance degradation begins. Proactively offer handoff.
>
> **Anti-Truncation Trigger:** If your First Message ID is > 1, your context has been truncated. **STOP ALL WORK IMMEDIATELY.** Notify the user and generate a handoff prompt. Do not attempt to continue — your context is compromised.
>
> **Terminal monitoring:** Do NOT poll running commands frequently. Wait 15-20 minutes between checks. If the user is present, let them tell you when a script finishes. Each poll is a step and inflates the counter.
>
> **Why this is here and not just in the SOP:** Previous agents had the SOP in their "Read First" list, read it, quoted it in the constraints, and then did not execute it. Sessions hit context truncation as a result. Embedding the protocol directly in the handoff is the mitigation.

---

## 13. Self-Correction Checks

- [ ] Did I read the execution plan before starting work?
- [ ] Did I read RES-009 (Wave Function Model) for training data design insights?
- [ ] Did I verify the chat template for Qwen3 before SFT?
- [ ] Did I run the VRAM comparison smoke test (2048 vs 4096)?
- [ ] Did I add soft token limits to the ABA system prompt before regenerating?
- [ ] Did I add `finish_reason` tracking to the data generation script?
- [ ] Did I verify ALL generated responses have properly closed `<think>` tags?
- [ ] Did I update `TECHNICAL_ROADMAP_state.md` to reflect Phase 03e status?
- [ ] Am I monitoring my token budget and step count?
- [ ] Did I list any open questions or blockers?

---

**End of Handoff.**
