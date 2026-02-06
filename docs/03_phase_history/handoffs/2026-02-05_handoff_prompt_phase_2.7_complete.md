# Handoff Prompt: Phase 2.7 Industrial Complete (Ready for Phase 3)

| Metadata | Details |
| :--- | :--- |
| **Date** | 2026-02-05 |
| **Phase** | 2.7 (Post-Industrial Verification) |
| **Status** | Stable (Green) |
| **Previous Phase** | 2.6 (Industrial Execution - Vertex AI) |
| **Next Phase** | 3.0 (Sandbox Training / RLAIF) |


## 1. Identity & Mode
*   **Identity:** The Navigator / The Analyst.
*   **Mode:** Activate **High-Energy Mode** (Crystal Cognition).

## 2. Context (The "Read First" List)
1.  **SOP [MANDATORY]:** `view_file SOP/__summary_development_workflow.md`
2.  **State [CRITICAL]:** `view_file src/aba_protocol/rewrite_state.md` (See Exp 7 - Success).
3.  **Task:** `view_file task.md` (Phase 2.6 verified).
4.  **Artifact:** `view_file data/dataset_aba_v1.4_config2.jsonl` (The 1000-item Golden Dataset).
5.  **Code Logic:** `view_file src/aba_protocol/rewrite_vertex.py` (Review the `try/except` block for "Smart Dampening" logic if you need to run it again).

## 3. The Achievement (Phase 2.6 Summary)
We successfully executed the **Industrial Rewrite** using **Gemini 3.0 Pro** via Vertex AI.
*   **Total Items:** 1000 / 1000.
*   **Engine:** Vertex AI (Global Endpoint).
*   **Robustness:** Script `rewrite_vertex.py` now includes "Smart Dampening" (Auto-sleep) for Quota limits:
    *   **RPM:** Sleeps 65s on `429` per-minute errors.
    *   **Daily:** Sleeps 1hr on `429` per-day errors.
*   **Outcome:** We now have the "ABA Training Data" required to train Model A.

## 4. The Mission (Phase 3: Sandbox Training)
Your goal is to begin the **RLAIF (Reinforcement Learning from AI Feedback)** loop or **DPO Training**.
Refer to `README.md` and `docs/01_living_specs/architecture/ARCH_002_PARENTING_PROTOCOL.md` for the Phase 3 spec.

### Immediate Next Steps
1.  **Data Validation:** Inspect the JSONL for formatting consistency (e.g., check that `chosen` and `rejected` fields are populated correctly in the last 750 items).
2.  **Split Data:** Create Train/Val/Test splits from `dataset_aba_v1.4_config2.jsonl`.
3.  **Initiate Training:** Configure the Unsloth/HuggingFace trainer for Stage I (Forging the Teacher).

## 5. Constraints
*   **Secrets Veto:** NEVER read `.env`.
*   **Token Watch:** You are starting fresh (< 5k tokens).
*   **Documentation:** Update `rewrite_state.md` if you modify the dataset.

## 6. Self-Correction Checks
[ ] Did I verify the dataset integrity before training?
[ ] Did I back up the `v1.4` dataset before splitting?
