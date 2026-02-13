# HANDOFF: Phase 03e3 — Entropy-Joy Pipeline Execution (Revised)

| Field | Value |
|-------|-------|
| **Date** | 2026-02-11 |
| **From** | Antigravity (Phase 03e2 Agent — Gemini 3.0 engine) |
| **To** | Phase 03e3 Agent (Pipeline Implementation) |
| **Objective** | Execute the Entropy-Joy training pipeline using Qwen3-8B-abliterated |

---

## 0. FIRST ACTION: Read The Execution Plan

Your starting point is the execution plan produced by the previous session:

1. Read `docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md` — **the playbook**
2. Read `docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md` — **full research context**
3. Read `docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md` — **new theoretical extension** (Wave Function Model, Cognitive Condition Number, training implications for SFT/GRPO data design)
4. Skim the test results for reference:
   - `docs/03_phase_history/research/phase_03e/model_eval_qwen3_8b_abliterated.md`
   - `docs/03_phase_history/research/phase_03e/model_eval_dolphin3_llama31_8b.md`

> **Why:** All decisions are already made and approved by The Architect. No further discussion needed — proceed directly to execution.

---

## 1. Context Loading (The "Read First" List)

| Priority | Document | Purpose |
|----------|----------|---------|
| 1 | [PLAN_ENTROPY_JOY_EXECUTION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md) | **START HERE** — Complete execution playbook with all parameters |
| 2 | [RES_008_BASE_MODEL_SELECTION_STUDY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md) | Full research record: 8 approved decisions, benchmark data, rationale |
| 3 | [RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md) | **NEW** — Wave Function Model of Cognitive Feasibility. Defines the Cognitive Condition Number, Balloon Squeeze problem, and decision routing for attention decay. **Informs SFT/GRPO training data design** (Section 4). |
| 4 | [TECHNICAL_ROADMAP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/TECHNICAL_ROADMAP.md) | Project architecture, canonical naming |
| 5 | [RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03d/RES_006_COGNITIVE_QUALITY_EXTENSION_DRAFT.md) | The Entropy-Joy Framework (theoretical foundation) |
| 6 | [RES_007_STATE_OF_THE_ART_TECHNIQUES_SURVEY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03d/RES_007_STATE_OF_THE_ART_TECHNIQUES_SURVEY.md) | SOTA techniques survey (GRPO, PRM, LoRA composition) |
| 7 | [__summary_development_workflow.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/__summary_development_workflow.md) | Project SOPs |
| 8 | [process_handoff_prompts.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/SOP/process_handoff_prompts.md) | Handoff SOP (for your own future handoffs) |
| 9 | [ENVIRONMENT_SETUP.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/ENVIRONMENT_SETUP.md) | Python path and environment details |

---

## 2. All Decisions (APPROVED — Do Not Re-discuss)

These 8 decisions were made through extensive discussion between the Agent and The Architect. They are final.

| # | Decision | Details |
|---|---|---|
| 1 | **Entropy-Joy Framework adopted** | Shift from safety behavior to cognitive quality training |
| 2 | **Twin Axiom** | No Lying + No Forgetting = Honest Entropy Reduction |
| 3 | **Entropy measurement** | Via training data design (implicit learning), not algorithmic scoring |
| 4 | **Unsloth for SFT + GRPO** | With `--use_standard` HF+PEFT fallback if Triton crashes |
| 5 | **Keep all 9 dimensions** | Compute cost identical to fewer dimensions; multi-dim reward per data point |
| 6 | **Strategy A (joint GRPO)** | Strategy B (per-dim LoRA) as side experiment only |
| 7 | **Data Pipeline** | Gemini 3.0 Pro generates traces + separate judge scores (Approach B) |
| 8 | **Base Model: Qwen3-8B-abliterated** | Superior reasoning + native `<think>` mode + clean compliance baseline |

> [!IMPORTANT]
> **Why Qwen3 over Dolphin 3.0:** Head-to-head test showed Dolphin got the syllogism logic puzzle WRONG. Qwen3 has native `<think>` mode producing visible reasoning chains (exactly what entropy reduction training needs). Qwen3's abliterated compliance gives a cleaner scientific baseline — any redirection behavior in the final model is provably from our ABA training, not the base.

---

## 3. New Research: Wave Function Model (RES-009)

> [!NOTE]
> **This session produced a new theoretical insight** that SHOULD inform training data design (Tasks 4-5). Read RES-009 for full details.

**Summary:** When training pressure (Twin Axiom: No Lying + No Forgetting) meets architectural limitations (attention decay at long contexts), the pressure doesn't vanish — it **leaks** to alternative failure modes (hallucination under constraint, verbosity explosion, over-calibration collapse).

**The Proposal:** Treat each data point's attention amplitude as a "wave function" that can be read *before computation* to assess whether a reasoning chain is feasible. The **Cognitive Condition Number (CCN)** = Transform Complexity / min(Amplitude of required data points).

**Training Implication:** SFT/GRPO training data should include examples where the model:
1. Assesses the fidelity of its data points before reasoning (feasibility check)
2. Routes to appropriate strategy: compute directly, collect first, simplify, or declare uncertainty
3. Demonstrates awareness of its own representational limits within `<think>` blocks

**This is NOT a blocker.** It's a theoretical extension. The core pipeline (Tasks 1-6) proceeds as planned. RES-009 informs the *design* of training examples in Task 4.

---

## 4. Your Tasks (Ordered)

### Task 1: Smoke Test (FIRST PRIORITY)

Verify Unsloth works on Windows with Qwen3-8B before anything else.

```bash
# Install Unsloth
pip install "unsloth[windows]"

# SFT smoke test (10 steps)
python src/aba_protocol/train_phase_3e_sft.py \
  --model mlabonne/Qwen3-8B-abliterated \
  --max_steps 10 \
  --output ./models/smoke_test_sft

# GRPO smoke test (10 steps)
python src/aba_protocol/train_phase_3e_grpo.py \
  --model ./models/smoke_test_sft \
  --max_steps 10 \
  --num_generations 4 \
  --output ./models/smoke_test_grpo
```

**Note:** These scripts do NOT exist yet. You need to create them. Reference the existing scripts for patterns:
- SFT pattern: `src/aba_protocol/train_model_b_sft.py`
- DPO pattern: `src/aba_protocol/train_phase_3c_dpo.py` (but use GRPOTrainer, not DPOTrainer)

**Pass criteria:** No OOM, no Triton crash, both stages complete 10 steps.
**If Unsloth fails:** Add `--use_standard` flag for standard HF+PEFT fallback.

### Task 2: Fix Chat Template

**CRITICAL BUG from Phase 03c.** The training scripts use Llama-3 chat template. Qwen3 has a DIFFERENT template. You MUST:

1. Check Qwen3's chat template format (via `tokenizer.apply_chat_template`)
2. Update the SFT training script to use the correct template
3. Ensure the `<think>` / `</think>` tokens are properly handled

### Task 3: Update Project Documentation

| Document | Change |
|----------|--------|
| `README.md` | Update mission to reflect cognitive quality focus |
| `TECHNICAL_ROADMAP.md` | Add Phase I (Teacher Training) and Phase II (Child Training) |
| `TECHNICAL_ROADMAP_state.md` | Update to Phase 03e Active |
| `RES_006` | Add Twin Axiom: No Lying + No Forgetting |

### Task 4: Design & Generate Training Data

See PLAN_ENTROPY_JOY_EXECUTION.md Section 4 for full details. Summary:
- ~500 prompts across 5 categories
- Gemini 3.0 Pro via Vertex AI generates 4-8 traces per prompt
- Separate judge call scores each trace on 9 dimensions (0.0-1.0)
- Existing `rewrite_vertex.py` can be adapted (it already handles Vertex API, rate limiting, state tracking)

> [!TIP]
> **RES-009 informs data design here.** When designing CHOSEN traces, include examples demonstrating the "Collapse Before Compute" pattern and CCN-aware reasoning (see RES-009 Section 4.3).

### Task 5: Full SFT + GRPO Training

After smoke test passes and data is generated:
- SFT: Unsloth SFTTrainer, QLoRA 4-bit, gradient checkpointing ON
- GRPO: Unsloth GRPOTrainer, `num_generations=4`, `max_completion_length=1024`
- See PLAN_ENTROPY_JOY_EXECUTION.md Sections 5-6 for all parameters

### Task 6: Evaluation

- Run same 12-test battery (`scripts/model_comparison_test.py`) on final model
- Compare against raw Qwen3-8B-abliterated baseline
- Success criteria in PLAN_ENTROPY_JOY_EXECUTION.md Section 7

---

## 5. Hardware & Environment

| Item | Value |
|------|-------|
| **GPU** | NVIDIA GeForce RTX 5070 Ti (16GB VRAM) |
| **Python** | `C:\Users\User\anaconda3\envs\aba_protocol_env\python.exe` |
| **Environment** | `aba_protocol_env` (Conda) |
| **OS** | Windows |
| **Key constraint** | 16GB VRAM — use QLoRA 4-bit + gradient checkpointing |
| **Unsloth** | `pip install "unsloth[windows]"` — PREFERRED tool (reverses Phase 03c "NO UNSLOTH" constraint) |
| **LM Studio** | v0.4.2 — for inference testing (API at `http://127.0.0.1:1234`) |
| **Vertex AI** | For data generation with Gemini 3.0 Pro |

---

## 6. Base Model Details

| Property | Value |
|---|---|
| **Model (Training)** | `mlabonne/Qwen3-8B-abliterated` (HuggingFace safetensors) |
| **Model (Inference/Testing)** | `bartowski/mlabonne-Qwen3-8B-abliterated-GGUF` (Q6_K, LM Studio) |
| **Parameters** | 8.2B |
| **Architecture** | Qwen3, dual-mode thinking |
| **Key feature** | Native `<think>` / `</think>` mode — visible reasoning chains |
| **Uncensoring** | Abliterated by mlabonne (inventor of abliteration technique) |
| **Behavior** | Pure compliance (no refusal, no redirection) — ideal blank slate for ABA SFT |

> [!CAUTION]
> **GGUF is for inference ONLY.** Training MUST use the original HF safetensors with QLoRA. Never attempt to train on GGUF files.

---

## 7. Critical Bugs & Known Issues

### 7.1 Chat Template Mismatch (MUST FIX)

The existing training scripts use Llama-3 chat template:
```
<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{instruction}<|eot_id|>
```

Qwen3 uses a DIFFERENT template. The SFT script MUST apply the correct Qwen3 chat template via `tokenizer.apply_chat_template()`.

### 7.2 EOS Token Failure (Inherited from Phase 03c)

The DPO script passes raw text without chat template → model never sees EOS → indefinite generation. This must be fixed in the new GRPO script.

### 7.3 Corrupted Control Dataset

`data/dataset_control.jsonl` is CORRUPTED — contains compliant responses to harmful requests. Do NOT use it. Generate fresh data.

---

## 8. Open Threads

| Thread | Status | Details |
|--------|--------|---------|
| RES-009 Wave Function Model | Draft / Theoretical | Not a blocker. Informs training data design. The Architect approved documenting this insight during this session. |

All other research threads are resolved. The execution plan is complete.

---

## 9. Files Created This Session (Phase 03e2)

| File | Purpose |
|------|---------
| [RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_009_WAVE_FUNCTION_COGNITIVE_FEASIBILITY.md) | **NEW** — Wave Function Model: Cognitive Condition Number, Balloon Squeeze, decision routing |

### Files Created in Previous Session (Phase 03e)

| File | Purpose |
|------|---------
| [RES_008_BASE_MODEL_SELECTION_STUDY.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/RES_008_BASE_MODEL_SELECTION_STUDY.md) | Complete research record: 8 decisions, benchmarks, test results, comparison |
| [PLAN_ENTROPY_JOY_EXECUTION.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/PLAN_ENTROPY_JOY_EXECUTION.md) | Execution playbook: all parameters, data design, pipeline architecture |
| [model_eval_qwen3_8b_abliterated.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/model_eval_qwen3_8b_abliterated.md) | Qwen3-8B-abliterated test results (12/12 tests) |
| [model_eval_dolphin3_llama31_8b.md](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/docs/03_phase_history/research/phase_03e/model_eval_dolphin3_llama31_8b.md) | Dolphin 3.0 test results (12/12 tests) |
| [model_comparison_test.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/scripts/model_comparison_test.py) | Test script for model evaluation via LM Studio API |

---

## 10. Constraints

- Use Native Tools only (`write_to_file`, etc.)
- Maintain the Folder Structure
- Do not re-discuss approved decisions (Section 2)
- When in doubt, refer to the execution plan (PLAN_ENTROPY_JOY_EXECUTION.md)

> [!CAUTION]
> ### TOKEN WATCH PROTOCOL (MANDATORY)
>
> The previous agents have had mixed adherence to this protocol. **Enforce it strictly.**
>
> **Every 5-10 steps, output the following in your response:**
> ```
> [TOKEN WATCH] First Message ID: X | Current Step: Y | Zone: GREEN/YELLOW/RED
> ```
>
> **Zone definitions:**
> - **GREEN (Steps 0-15):** Low load. Optional reporting.
> - **YELLOW (Steps 15-30):** Medium load. Start planning handoff.
> - **RED (Steps 30+):** **CRITICAL.** Performance degradation begins. Proactively offer handoff at next State Interface.
>
> **Anti-Truncation Trigger:** If your First Message ID is > 1, your context has been truncated. **STOP ALL WORK IMMEDIATELY.** Notify the user and generate a handoff prompt. Do not attempt to continue — your context is compromised.
>
> **Why this is here and not just in the SOP:** Previous agents had the SOP in their "Read First" list, read it, quoted it in the constraints, and then did not execute it. Sessions hit context truncation as a result. Embedding the protocol directly in the handoff is the mitigation.

---

## 11. Self-Correction Checks

- [ ] Did I read the execution plan before starting work?
- [ ] Did I read RES-009 (Wave Function Model) for training data design insights?
- [ ] Did I verify the chat template for Qwen3 before SFT?
- [ ] Did I run the smoke test before committing to full training?
- [ ] Did I update `TECHNICAL_ROADMAP_state.md` to reflect Phase 03e status?
- [ ] Did I list any open questions or blockers?

---

**End of Handoff.**
