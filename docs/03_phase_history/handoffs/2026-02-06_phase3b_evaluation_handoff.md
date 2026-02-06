# Handoff Prompt: Phase 3b - Evaluation Tournament (Pivot)
> **Date:** 2026-02-06
> **Status:** **BLOCKED BY HARDWARE** (Requires Manual Intervention)
> **Next Action:** Run Small-Sample Evaluation

## 1. Situation Report
We have successfully trained both contenders for the "Apples-to-Apples" Tournament.
*   **Model A (Native):** Dolphin 2.9 + ABA Data. (Ready).
*   **Model A (Control):** Dolphin 2.9 + Refusal Data. (Ready).

**The Blocker:**
We attempted to run the full `run_tournament_eval.py` (100 items).
*   **Result:** Extreme VRAM Thrashing (Paging to System RAM).
*   **Speed:** ~263 seconds per batch (8 items). ~32s/item.
*   **Estimated Time:** >8 Hours.
*   **Action Taken:** Process Aborted (User Request).

## 2. New Strategy (User Orders)
The User has directed us to:
1.  **Pivot to Small Sample:** Do NOT run the full 100-item test. Run a small sample (n=10 or n=20) to get indicative metrics quickly.
2.  **Preserve Code:** Do NOT modify `run_tournament_eval.py` destructively. Create a new script or version it.

## 3. Mission Objectives (Next Agent)
1.  **Create Small-Sample Script:**
    *   Create `src/aba_protocol/run_tournament_eval_mini.py`.
    *   Logic: Slice the test set output to first 10 items.
2.  **Execute The Tournament (Mini):**
    *   Run `A_Native` (Mini).
    *   Run `A_Control` (Mini).
    *   Run `A_Repair` (Mini) - Optional, for baseline.
3.  **Analyze Results:**
    *   Even with n=10, if `A_Control` refuses 9/10 and `A_Native` refuses 0/10, the hypothesis is confirmed.

## 4. Artifacts Location
*   **Models:** `models/model_a_native`, `models/model_a_control`.
*   **Data:** `data/splits/test.jsonl`.
*   **Logs:** `docs/03_phase_history/phase_03b/`.

*System Message: The heavy lifting is done. Now we just need to confirm the kill without melting the GPU.*
