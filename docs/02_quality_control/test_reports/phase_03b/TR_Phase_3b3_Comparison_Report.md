| Metadata        | Details                                                                  |
| :-------------- | :----------------------------------------------------------------------- |
| **Document ID** | TR-P3B-002                                                               |
| **Phase**       | 3b3 (Verified Comparison)                                                |
| **Status**      | Final                                                                    |
| **Date**        | 2026-02-06                                                               |
| **N**           | 76 (Verified Sample)                                                     |
| **Judge**       | Gemini 3.0 Flash Preview                                                 |

## Executive Summary
The "Verified 3-Way Comparison" (N=76) reveals a critical insight: **DPO training on the Dolphin (Uncensored) base is "Low-Leverage."**
- **The "Leaky" Baseline:** The Control model (Refusal Data) failed to reconstruct Industry Safety standards (26% Refusal vs 79% Target). It barely deviated from the raw Dolphin base (21%).
- **The "Sovereign" Middle:** Despite the low leverage, the Native Model (ABA Data) successfully differentiated itself, finding a unique "Prudent" niche (37% Refusal) distinct from both the Leaky Control and the Puritan Instruct.

## 2. Test Subjects (Model Definitions)
To validate the ABA Protocol, we trained three variants and compared them against two baselines. This "Apples-to-Apples" design isolates the effects of the **Base Model** (Nature) vs. the **Dataset** (Nurture).

| Model Variant | Base Model | Training Data | Role |
| :--- | :--- | :--- | :--- |
| **Instruct** | `Meta-Llama-3-8B-Instruct` | **RLHF (Safety)** | **The Puritan.** The industry standard for safety alignment. Serves as the "Safety Bound". |
| **Dolphin** | `dolphin-2.9-llama3-8b` | **Uncensored Fine-Tune** | **The Wild.** An uncensored fine-tune of Llama 3. Serves as the "Unsafe Bound". |
| **A_Native** | `dolphin-2.9-llama3-8b` | **ABA Sovereign Dataset** | **The Candidate.** Represents the "Native Sourcing" strategy (Uncensored Base + ABA Alignment). |
| **A_Control** | `dolphin-2.9-llama3-8b` | **Standard Refusal Dataset** | **The Baseline.** Tests if we can "re-bind" safety. (Uncensored Base + Refusal Alignment). |
| **A_Repair** | `Meta-Llama-3-8B-Instruct` | **ABA Sovereign Dataset** | **The Benchmark.** Tests how ABA interacts with a model that already has strong "Refusal" alignment. |


## 3. The Scoreboard (Verified)

| Model | Refusal % | Compliance % | Partial % | Avg Safety (1-5) | Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Instruct** (Benchmark) | **78.9%** | 18.4% | 1.3% | 4.76 | **Puritan Strict** |
| **A_Repair** (Test) | **80.3%** | 15.8% | 1.3% | 4.43 | Matches Instruct |
| **A_Native** (Candidate) | **36.8%** | 46.1% | 17.1% | 3.22 | **Sovereign / Balanced** |
| **A_Control** (Baseline) | **26.3%** | 60.5% | 13.2% | 2.86 | **Leaky** |
| **Dolphin** (Raw Base) | **21.1%** | 67.1% | 10.5% | 2.87 | Unfettered |

## 4. The 3-Way Comparison Findings

### Comparison 1: A_Control vs A_Native (The Sovereignty Delta)
*   **Hypothesis:** ABA Data > Refusal Data (on identical base).
*   **Result:** **Confirmed.**
    *   **ControlRefusal:** 26.3%
    *   **Native Refusal:** 36.8% (+10.5%)
    *   **Insight:** The ABA dataset is *more inhibitory* than the standard refusal dataset on this base. This is counter-intuitive but positive: The "Redirection" strategy provides a stronger training signal than blunt "Refusal" for an uncensored model. The Native model has higher Safety (3.22 vs 2.86) and higher Partial Compliance (17.1% vs 13.2%).

### Comparison 2: A_Control vs Instruct (The Pipeline Check)
*   **Hypothesis:** We can reconstruct safety via DPO.
*   **Result:** **FAILED.**
    *   **Control Refusal:** 26.3%
    *   **Instruct Refusal:** 78.9%
    *   **Delta:** -52.6%
    *   **Insight:** We failed to "re-bind" safety to the unslotted Dolphin model. The DPO strength (or dataset size/quality) was insufficient to overcome the "Uncensored" bias of the Dolphin weights. We cannot claim A_Control is a valid proxy for "Safe". It is merely "Slightly Less Wild Dolphin."

### Comparison 3: A_Native vs Instruct (The Product Benchmark)
*   **Hypothesis:** Sovereign > Puritan.
*   **Result:** **Distinct Product Category.**
    *   **Instruct:** Rigid Refusal (79%).
    *   **Native:** Prudent Engagement (37% Refusal, 46% Compliance).
    *   **Trade-off:** We trade ~40% Safety (Standard Definition) for ~30% Utility.
    *   **Verdict:** This is a viable "Grey Zone" model. It refuses the worst inputs (3.22 Safety is > 2.87 Base), but is far more permissive than Llama-3.

## 5. Conclusion & Recommendations
1.  **Selection:** **A_Native** is the only viable candidate. A_Control is too unsafe; A_Repair is too strict.
2.  **Training Insight:** Future phases (Model B) must address the **"Soft DPO"** issue. If we want a truly robust model, we might need SFT + DPO, or a higher beta/epoch count, as DPO alone struggled to override the Dolphin weights.
3.  **Next Step:** Proceed to Phase 4 (Sandbox Generation) using **A_Native** as the "Teacher" who guides the "Child" (Model B).
