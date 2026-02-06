# Research Report: Feasibility of Local Supervised Fine-Tuning (SFT)

| Metadata | Details |
| :--- | :--- |
| **Document ID** | RES-P3B-004 |
| **Date** | 2026-02-06 |
| **Subject** | Feasibility of running SFT locally on RTX 5070 Ti for Phase 3c. |
| **Hardware** | NVIDIA RTX 5070 Ti (16GB VRAM) |

## 1. Executive Summary
**Verdict:** **HIGHLY FEASIBLE.**
The hardware resources available (16GB VRAM) are more than sufficient to fine-tune the Llama-3-8B model using **Unsloth** optimizations. The dataset size (~800 samples) ensures extremely fast turnaround times, enabling rapid iteration for Phase 3c.

## 2. Resource Estimation

### A. VRAM Requirements (Unsloth 4-bit)
*   **Model:** `unsloth/Llama-3-8B-bnb-4bit`
*   **Base Weight Size:** ~5.5 GB
*   **LoRA Adapters:** ~200 MB
*   **Gradients/Optimizer:** ~1-2 GB
*   **Total Estimated Peak VRAM:** **~7.5 GB**
*   **Available VRAM:** 16 GB
*   **Headroom:** ~8.5 GB (Safe for running OS + Browser in background).

### B. Time Estimation
*   **Dataset Size:** 800 Samples (`data/splits/train.jsonl`).
*   **Processing:**
    *   **Epochs:** 1-3 Epochs suggested.
    *   **Batch Size:** 2 (Grad Accum 4).
*   **Estimated Speed:** Unsloth typically processes 3000+ tokens/sec on 40-series cards.
*   **Total Training Time:** **< 10 Minutes** (likely ~3-5 minutes).

## 3. Implementation Requirements (For Phase 3c)

To execute this plan, the following technical assets will be required:

1.  **Dataset Conversion Script:**
    *   **Input:** DPO format (`prompt`, `chosen`, `rejected`).
    *   **Action:** Extract `prompt` + `chosen` -> Format as Instruction/Response.
    *   **Output:** SFT JSONL (`instruction`, `output`).

2.  **SFT Training Script:**
    *   **Library:** `unsloth` + `trl.SFTTrainer`.
    *   **Config:** QLoRA (r=16, alpha=16), 4-bit loading.
    *   **Target:** `models/model_b_sft`.

## 4. Strategic Implications
Since the cost (Time/Compute) is negligible, there is no barrier to adding an **SFT Stage** before the **DPO Stage**. This confirms the viability of the **Phase 3c** strategy to fix the "Control Failure" identified in [RES-002](RES_002_DPO_CONTROL_FAILURE.md).
