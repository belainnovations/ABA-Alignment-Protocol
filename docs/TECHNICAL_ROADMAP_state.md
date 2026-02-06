# State: Technical Roadmap

| Metadata | Details |
| :--- | :--- |
| **Definition Document** | [TECHNICAL_ROADMAP.md](TECHNICAL_ROADMAP.md) |
| **Last Updated** | 2026-02-05 |
| **Status** | ACTIVE |

---

## 1. Status Summary
We have completed **Phase 3b** (Apples-to-Apples Comparison) and are proceeding to **Phase 3c** (SFT Correction).

### Current Milestone
*   **Goal:** Execute SFT on Dolphin Base Model.
*   **Progress:** Feasibility Confirmed. Dataset Conversion Pending.
*   **Next:** Generate SFT Dataset -> Train SFT -> Apply DPO.

---

## 2. Phase Tracking

### Phase 1: Data Preparation [COMPLETE]
*   **Outcome:** `dataset_aba_v1.4` (1000 items). Train/Val/Test splits created.

### Phase 2: Training The Teacher [IN PROGRESS]
*   **Model A1 (Repair):** Training on Llama-3-8B-Instruct (Current).
*   **Model A2 (Native):** Scheduled for Phase 3b.

### Phase 3: Teacher Evaluation [COMPLETE - FAILED]
*   **Outcome:** Refusal Rate 58% (Target < 5%). "Gene Therapy" Hypothesis Disproven.
*   **Action:** Activate Phase 3b.

### Phase 3b: Apples-to-Apples Experiment [COMPLETE]
*   **Outcome:** Mixed Results.
    *   **Control (DPO only):** Failed to re-gain safety (26% Refusal).
    *   **Native (ABA):** Superior Sovereignty (37% Refusal) but still leaky compared to Instruct.
*   **Verdict:** [See Report](../docs/02_quality_control/test_reports/phase_03b/TR_Phase_3b3_Comparison_Report.md). Direct DPO on uncensored models is insufficient.
*   **Deviation:** Initiating Phase 3c.

### Phase 3c: Supervised Fine-Tuning (SFT) Integration [ACTIVE]
*   **Rationale:** The "Control Failure" in Phase 3b proved that DPO ("Steering") cannot replace SFT ("Teaching").
*   **Plan:**
    1.  Create `methods/train_sft.py`.
    2.  Convert DPO dataset to SFT format.
    3.  Train `Model_Control_SFT` and `Model_Native_SFT`.
    4.  Apply DPO on top.
*   **Feasibility:** [Confirmed](../docs/03_phase_history/research/phase_03b/RES_004_SFT_FEASIBILITY.md).

---

## 3. Change Log
| Date | Agent | Change |
|---|---|---|
| 2026-02-05 | Claude Opus 4.5 | Created state file. |
| 2026-02-05 | Claude Opus 4.5 | Added **Phase 3b** to Roadmap (Apples-to-Apples Comparison). |
| 2026-02-06 | Gemini 3.0 | Added **Phase 3c** (SFT Correction) based on Phase 3b Findings. |
