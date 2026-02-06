# Guide: Unsloth Training Patterns & Pitfalls
> **Knowledge Base ID:** GUIDE-001
> **Created:** 2026-02-06
> **Context:** Phase 3b (Apples-to-Apples)

## 1. Overview
This document captures critical engineering lessons learned during the fine-tuning of Llama-3 and Dolphin models using Unsloth on consumer hardware (RTX 30xx/40xx/50xx).

## 2. Dataset Schema (The "Prompt/Chosen/Rejected" Trap)
Most DPO scripts (including ours) expect a specific flat schema. Data from HuggingFace (e.g., Anthropic HH-RLHF) often comes nested.

| Standard Unsloth/TRL Expectation | Anthropic Raw Format |
| :--- | :--- |
| `{"prompt": "...", "chosen": "...", "rejected": "..."}` | `{"chosen": "History\n\nResponse", "rejected": "History\n\nResponse"}` |

**Lesson:**
*   Always inspect the first line of a `.jsonl` before training: `Get-Content data.jsonl -TotalCount 1`.
*   **The Fix:** Use a robust parser (see `scripts/prepare_control_data.py`) to split the dialogue history from the response. **Do not assume parity.**

## 3. VRAM Saturation & "The Slide Show"
We observed distinct behavior when training large models (15GB) on 16GB cards.

**The Symptom:**
*   Training starts fast (~1s/it).
*   Suddenly spikes to ~80s/it or ~100s/it.
*   System UI becomes unresponsive (Mouse lag).
*   **No Crash:** The process does NOT exit with OOM.

**The Diagnosis:**
*   Windows WDDM (Graphics Driver) is forcefully paging VRAM to System RAM (DDR4/5).
*   This allows training to *survive* but at 1/100th speed (PCIe bandwidth bottleneck).

**The Mitigations:**
1.  **Reduce Batch Size:** `per_device_train_batch_size=1` (standard).
2.  **Gradient Accumulation:** Increase `gradient_accumulation_steps` (e.g., 4 or 8) to maintain effective batch size without VRAM cost.
3.  **The Watchdog Strategy:** If training locally, close *all* Electron apps (VS Code, Discord, Slack, Chrome). They consume ~500MB each.
4.  **Acceptance:** If it pages, it pages. It *will* finish, just slowly. Do not kill it unless necessary.

## 4. Model Artifacts (Full Weights vs Quantized)
**The Trap:**
*   `unsloth/llama-3-8b-bnb-4bit` (5GB) -> Pre-quantized. Fast loading. Low RAM.
*   `dolphin-2.9-llama3-8b` (15GB) -> Full Weights.

**The Consequence:**
*   Unsloth *can* load the 15GB model and quantize on-the-fly (`load_in_4bit=True`).
*   **However:** This requires peak system RAM/VRAM during the `loading` phase.
*   **Lesson:** Just because Unsloth "uses 4-bit" doesn't mean the *download* is small. Check the repo file sizes first!

## 5. Windows Process Redirects
**Warning:** `W0206... NOTE: Redirects are currently not supported in Windows or MacOs.`
*   **Verdict:** **Benign.** You can ignore this warning in `torch.distributed`. It does not affect single-GPU training.
*   **Exit Code 1:** Sometimes appears even on success. Verify `models/` directory for `adapter_model.safetensors` before panicking.

## 6. Checkpointing Strategy
For long runs (>2 hours), simple checkpointing is insufficient.
*   **Standard:** `save_steps=100`.
*   **Advanced (Proposed):** Save `dataset_index` + `optimizer_state`.
*   **Why:** If the PC crashes (Power/Reset), you want to lose only 10 mins, not 2 hours.

---
*End of Guide*
