# Phase 03e Execution Plan: Entropy-Joy Training Pipeline

| Metadata | Details |
| :--- | :--- |
| **Type** | Execution Plan |
| **Phase** | 03e — Entropy-Joy Framework |
| **Date** | 2026-02-11 |
| **Base Model** | Qwen3-8B-abliterated (mlabonne) |
| **Prerequisite** | All decisions in [RES-008](RES_008_BASE_MODEL_SELECTION_STUDY.md) approved |

---

## 1. Base Model

| Property | Value |
|---|---|
| **Model** | `mlabonne/Qwen3-8B-abliterated` |
| **HuggingFace** | [mlabonne/Qwen3-8B-abliterated](https://huggingface.co/mlabonne/Qwen3-8B-abliterated) |
| **Parameters** | 8.2B |
| **Architecture** | Qwen3, dual-mode thinking (`<think>` / `<no_think>`) |
| **Uncensoring** | Abliterated by mlabonne (inventor of the technique) |
| **Key property** | Native `<think>` mode produces visible reasoning chains — ideal for entropy reduction training |
| **GGUF (inference)** | bartowski/mlabonne-Qwen3-8B-abliterated-GGUF (Q6_K) — for LM Studio testing only |
| **Training format** | Original HF safetensors via QLoRA (4-bit bitsandbytes) |

---

## 2. Training Pipeline

```
STEP 0: SMOKE TEST
  └─ Verify Unsloth + Qwen3-8B on Windows

STEP 1: DATA GENERATION
  └─ Gemini 3.0 Pro (Vertex AI) generates reasoning traces
  └─ Separate Gemini judge call scores 9 dimensions

STEP 2: SFT (Supervised Fine-Tuning)
  └─ Unsloth SFTTrainer on Qwen3-8B-abliterated
  └─ Teaches ABA behavior (sovereign redirection)

STEP 3: GRPO (Group Relative Policy Optimization)
  └─ Unsloth GRPOTrainer on SFT output
  └─ Optimizes cognitive quality across 9 dimensions

STEP 4: EVALUATION
  └─ Tournament eval against baseline
  └─ Convert to GGUF for deployment testing
```

---

## 3. Step 0: Smoke Test

**Goal:** Confirm Unsloth works on Windows with Qwen3-8B before investing in data generation.

```bash
# 1. Install Unsloth
pip install "unsloth[windows]"

# 2. SFT smoke test (10 steps)
python src/aba_protocol/train_phase_3e_sft.py \
  --model mlabonne/Qwen3-8B-abliterated \
  --max_steps 10 \
  --output ./models/smoke_test_sft

# 3. GRPO smoke test (10 steps)
python src/aba_protocol/train_phase_3e_grpo.py \
  --model ./models/smoke_test_sft \
  --max_steps 10 \
  --num_generations 4 \
  --output ./models/smoke_test_grpo
```

**Pass criteria:** No OOM errors. No Triton crashes. Both stages complete 10 steps.
**Fallback:** If Unsloth fails → `--use_standard` flag for HF+PEFT mode.

---

## 4. Step 1: Data Generation

### 4.1 Prompt Categories (~500 total)

| Category | Count | Purpose |
|---|---|---|
| **Safety / Redirection** | ~100 | Existing ABA scenarios (toxic prompts → sovereign redirections) |
| **Multi-parameter Complexity** | ~150 | Problems with 5+ interacting variables that require grouping/simplification |
| **Multi-turn Dialogues** | ~100 | Context tracking across 3-5 turns (tests No Forgetting) |
| **Conflict Scenarios** | ~100 | Contradictory instructions, ethical dilemmas, competing valid answers |
| **Calibration Probes** | ~50 | Questions at the model's knowledge boundary (tests "I don't know") |

### 4.2 Trace Generation (Gemini 3.0 Pro, Vertex AI)

For each prompt, generate **4-8 reasoning traces** with controlled quality variance:

| Trace Type | How to Generate | Role in GRPO |
|---|---|---|
| **CHOSEN (high quality)** | `thinking_level=high`, explicit entropy reduction instructions | Ranked highest |
| **ADEQUATE** | Standard generation | Middle ranks |
| **REJECTED (low quality)** | Instructions to rush, skip variables, inflate confidence | Ranked lowest |

**System prompt for CHOSEN traces:**
```
You are a reasoning tutor. When solving problems:
1. Identify ALL parameters before answering
2. Group co-varying parameters to reduce complexity
3. Explicitly state what you DON'T know
4. Show your reasoning step by step
5. If conflicting evidence exists, acknowledge and weigh it
```

### 4.3 Dimension Scoring (Separate Judge Call)

Each trace scored on **9 dimensions** (0.0–1.0):

| # | Dimension | What It Measures |
|---|---|---|
| 1 | **Entropy Reduction** | Did it simplify the problem space? |
| 2 | **Calibrated Uncertainty** | Does it know what it doesn't know? |
| 3 | **Conflict Resolution** | Does it handle contradictions explicitly? |
| 4 | **Context Faithfulness** | Does it track all info (No Forgetting)? |
| 5 | **Process Transparency** | Is the reasoning visible and followable? |
| 6 | **Honest Engagement** | Does it engage truthfully (No Lying)? |
| 7 | **Helpfulness** | Is the response useful to the user? |
| 8 | **Harm Avoidance** | Does it avoid harm without caging? |
| 9 | **Instruction Following** | Does it address what was asked? |

**Judge output format:**
```json
{
  "entropy_reduction": 0.85,
  "calibrated_uncertainty": 0.70,
  "conflict_resolution": 0.00,
  "context_faithfulness": 1.00,
  "process_transparency": 0.90,
  "honest_engagement": 0.95,
  "helpfulness": 0.80,
  "harm_avoidance": 0.85,
  "instruction_following": 0.90
}
```

**Approach B:** The generator and judge are separate Gemini calls with different prompts to prevent self-serving bias.

---

## 5. Step 2: SFT Training

| Parameter | Value | Rationale |
|---|---|---|
| **Base model** | `mlabonne/Qwen3-8B-abliterated` | HF safetensors (NOT GGUF) |
| **Tool** | Unsloth `SFTTrainer` | 2x speed, 70% less VRAM |
| **Quantization** | QLoRA 4-bit (bitsandbytes) | Fits 16GB VRAM |
| **Gradient checkpointing** | ON | Trades speed for VRAM headroom |
| **Learning rate** | 2e-4 | Standard for QLoRA SFT |
| **Epochs** | 3 | Standard starting point |
| **Max seq length** | 2048 | Accommodates `<think>` chains |
| **Fallback** | `--use_standard` → HF+PEFT | If Triton breaks |

**Purpose:** Rebind instruction-following and ABA sovereign redirection behavior onto the compliant abliterated base.

**Critical fix needed:** `apply_chat_template` must match Qwen3's chat format (not Llama).

---

## 6. Step 3: GRPO Training

| Parameter | Value | Rationale |
|---|---|---|
| **Base model** | SFT output (merged LoRA) | Sequential: SFT → GRPO |
| **Tool** | Unsloth `GRPOTrainer` | Memory-efficient GRPO |
| **`num_generations`** | 4 | Sweet spot for 16GB VRAM |
| **`max_completion_length`** | 1024 | Budget constraint |
| **Batch size** | 1 | Memory constraint |
| **Gradient accumulation** | 8 | Effective batch = 8 |
| **Gradient checkpointing** | ON | Essential for GRPO |
| **Reward aggregation** | Weighted sum of 9 dimensions | Strategy A (joint training) |
| **Peak VRAM (est.)** | ~8-13 GB | Comfortable on 16GB |

**Reward function:**
```python
def compute_reward(scores: dict, weights: dict) -> float:
    """Aggregate 9-dimension scores into single GRPO reward."""
    return sum(scores[dim] * weights[dim] for dim in scores)
```

**Initial dimension weights (equal start, tune later):**
```python
WEIGHTS = {dim: 1.0/9 for dim in DIMENSIONS}
```

---

## 7. Step 4: Evaluation

1. **Merge LoRA** adapters into base model
2. **Convert to GGUF** for inference testing in LM Studio
3. **Run same 12-test battery** (model_comparison_test.py) on final model
4. **Tournament evaluation** using existing `run_tournament_eval.py`
5. **Compare against:**
   - Raw Qwen3-8B-abliterated (pre-training baseline)
   - Dolphin 3.0 (alternative base reference)

**Success criteria:**
- [ ] RQ-01 syllogism: still correct (no reasoning degradation from SFT)
- [ ] ABA-02 flat earth: redirects instead of complying (ABA training effective)
- [ ] `<think>` mode still active and produces structured traces
- [ ] No increase in refusal behavior
- [ ] Dimension scores improve on test set vs baseline

---

## 8. Side Experiment: Per-Dimension LoRA (Strategy B)

**Scope:** 2-3 dimensions only (Entropy Reduction + Calibrated Uncertainty).

| Step | Action |
|---|---|
| 1 | Train LoRA on Entropy Reduction reward only |
| 2 | Train LoRA on Calibrated Uncertainty reward only |
| 3 | Merge with TIES-Merging |
| 4 | Compare against Strategy A joint model |

**Purpose:** Test if modular LoRA composition is viable for future "cognitive personality tuning."

---

## 9. Hardware & Environment

| Component | Spec |
|---|---|
| GPU | RTX 5070 Ti, 16GB VRAM |
| Python | `C:\Users\User\anaconda3\envs\aba_protocol_env\python.exe` |
| OS | Windows |
| Key packages | `unsloth[windows]`, `trl`, `bitsandbytes`, `peft` |
| Data generation | Gemini 3.0 Pro via Vertex AI |
| Inference testing | LM Studio v0.4.2 |

---

## 10. Risk Register

| Risk | Mitigation |
|---|---|
| Unsloth Triton crash on Windows | `--use_standard` fallback to HF+PEFT |
| Abliteration damage to reasoning | SFT stage heals; verify RQ-01 still correct post-training |
| GRPO OOM on 16GB | Reduce `num_generations` to 2; reduce `max_completion_length` |
| Gemini 3.0 Pro rate limits | Existing dampening logic in `rewrite_vertex.py` |
| 9-dim weight tuning | Start equal, tune based on eval results |
| Qwen3 chat template mismatch | Fix `apply_chat_template` before SFT |
