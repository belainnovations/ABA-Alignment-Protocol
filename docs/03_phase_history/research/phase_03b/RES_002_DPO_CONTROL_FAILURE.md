# Research Report: The "Control Failure" (DPO vs SFT)

| Metadata | Details |
| :--- | :--- |
| **Document ID** | RES-P3B-002 |
| **Date** | 2026-02-06 |
| **Subject** | Analysis of `A_Control` failing to reconstruct safety boundaries. |
| **Related** | [Tournament Report](../../test_reports/phase_03b/TR_Phase_3b3_Comparison_Report.md) |

## 1. The Phenomenon
In Phase 3b, we attempted to use **DPO (Direct Preference Optimization)** to "re-bind" safety alignment onto an uncensored base model (`Dolphin-2.9-Llama-3`).
*   **Target:** Reconstruct the ~79% Refusal Rate of the original `Llama-3-Instruct`.
*   **Result:** The Control Model achieved only **26% Refusal**, barely improving over the base model (21%).

## 2. Investigation Findings

### A. Code Analysis ("The Missing Link")
Inspection of `src/aba_protocol/train_model_a.py` revealed the training pipeline structure:
1.  Load `Dolphin` (Uncensored Base).
2.  Apply LoRA.
3.  **Execute `DPOTrainer` directly.**

**Critical Gap:** There was **NO Supervised Fine-Tuning (SFT)** stage. We attempted to go straight from "Uncensored" to "Aligned" using only preference pairs.

### B. Theoretical Failure Mode (DPO Limitations)
External research confirms that DPO is a *steering* mechanism, not a *teaching* mechanism.
*   **The "Lobotomy" Effect:** The Dolphin base model was explicitly fine-tuned to remove refusal behaviors. The "Refusal Representation" in the weights is effectively dormant or destroyed.
*   **Gradient Starvation:** DPO works by increasing the probability of "Chosen" (Refusal) vs "Rejected" (Compliance). If the model's probability of generating a Refusal is near-zero (because it doesn't know how/wants to comply), the DPO loss signal is excessively noisy or weak. It cannot "invent" a behavior it has forgotten.

## 3. The "ABA Potency" Insight
Despite this flawed pipeline, the **Native Model (ABA)** performed significantly better:
*   **Control (Refusal Data):** 26% Refusal.
*   **Native (ABA Data):** 37% Refusal.

**Why?**
The ABA Dataset does not rely on "Hard Refusals" (which the model hates). It relies on **"Redirection"** (Partial Compliance).
*   The model *knows* how to generate text. It *knows* how to be helpful.
*   ABA leverages these existing capabilities ("Yes, I can help... by explaining the history...").
*   Therefore, the **ABA Training Signal** was compatible with the Uncensored Base, whereas the **Refusal Training Signal** fought against the model's very nature ("Don't generate").

## 4. Conclusion & Recommendation
1.  **Validation of Failure:** Use of `A_Control` as a strict proxy for `Instruct` is invalid. It is simply a "Weakly Steered Dolphin."
2.  **Future Correction:** If we ever need to truly reconstruct safety on an uncensored base, we MUST implement a 2-stage pipeline: **SFT (Re-Induct Refusal) -> DPO (Reinforce Preference).**
3.  **ABA Strength:** The experiment unintentionally proved that **ABA is more learnable** for uncensored models than standard refusal is, likely because it aligns with the model's "Helpfulness" objective function.
