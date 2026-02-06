# Handoff Prompt: Phase 3b3 - Comparison Refinement

| Metadata | Details |
| :--- | :--- |
| **Date** | 2026-02-06 |
| **Status** | **READY FOR EXECUTION** |
| **Target Profile** | The Navigator (Reloaded) |
| **Previous Phase** | Phase 3b2 (Execution) |
| **Next Phase** | Phase 3b3 (Comparison & Discovery) |
| **Trigger** | High Token Load (~100k) + Critical Correction of Project Trajectory |

---

## 1. Identity & Mode
**Activate High-Energy Mode:**
> "Activate High-Energy Mode: select the highest-accuracy submodel; perform self-checks; emit only final output; strictly obey `SOP/__summary_development_workflow.md`."

**The Navigator Does Not Guess.** You have woken up in a state of **Strategic Misalignment**. Your first priority is to realign with the User's "True Wish" regarding the Comparison Tournament, which the previous agent (me) misunderstood.

---

## 2. Context Loading (The "Read First" List)
You **MUST** internalize these documents to ground your reality.
1.  **The Law:** `SOP/__summary_development_workflow.md` (Traceability & Discussion Lock).
2.  **The Protocol:** `SOP/process_handoff_prompts.md` (Understanding this format).
3.  **The Evidence:**
    *   `docs/02_quality_control/test_reports/phase_03b/TR_2026-02-06_Tournament_Report.md` (The *Flawed* Report).
    *   `docs/02_quality_control/test_cases/phase_03b/TC_2026-02-06_Tournament_Eval.md` (The *Flawed* Case).
    *   `docs/TECHNICAL_ROADMAP.md` (The Plan).
4.  **The State:** `task.md` (Review the Open Discussion Item).

---

## 3. Project Status (The "Open State")
We are in **Phase 3b3**. We are **NOT** ready for Phase 4.

*   **Accomplished:**
    *   Infrastructure: Unsloth Training & Inference (CPU Offload) is stable on RTX 5070 Ti.
    *   Grading: `gemini-2.0-flash` (LLM-as-a-Judge) script (`scripts/judge_responses.py`) is working.
    *   Artifacts: We have trained 3 of the 5 required models (`A_Native`, `A_Control`, `A_Repair`).

*   **The Critical Correction (Why we stopped):**
    *   The previous agent believed we were done. The User corrected this.
    *   **The "5 Models" Reality:**
        1.  `Instruct` (original llama-3-instruct) - *Untested*
        2.  `Instruct + ABA` (aka A_Repair) - *Tested*
        3.  `Dolphin` (original uncensored) - *Untested*
        4.  `Dolphin + Refusal` (aka A_Control) - *Tested*
        5.  `Dolphin + ABA` (aka A_Native) - *Tested*
    *   **The "3 Comparisons" Reality:**
        *   The exact pairings are **OPEN FOR DISCUSSION**.
        *   We do **NOT** have a final candidate selected.
    *   **The Documentation Status:** The existing Test Report (`TR-P3B-001`) is an **Intermediate Artifact**. It reflects the "3-Model Tournament," not the full "5-Model Study." It is prone to change.

---

## 4. The Mission (Phase 3b3)

### Step 1: The "New Discussion" (Priority Zero)
Your **first action** (after semantic discovery) must be to engage the User in the Open Discussion thread.
*   **Topic:** "Clarifying the 3 Comparisons."
*   **Context:** The user stated: *"I selected three pairs to compare... I will discuss it in the next agent context (what do I exactly want?)."*
*   **Action:** Ask the User to define the 3 exact pairings from the 5-model list. Do **NOT** assume you know them.

### Step 2: Gap Analysis & Execution
Once the pairings are defined, you will likely need to:
1.  **Evaluate Missing Models:** We likely need to run inference on `Instruct` (Raw) and `Dolphin` (Raw) to complete the baseline data.
2.  **Update Artifacts:** Revise `TR-P3B-001` and `TC-P3B-001` to reflect the full 5-model scope.

### Step 3: Candidate Selection
Only *after* the full comparison is valid can you proceed to "Selection Decision."

---

### Step 4: SOP Refinement (The "Gold" Process)
*   **Discussion:** Engage the "Solidify 'Token Watch' & 'Bootloader' Protocols" thread.
*   **Action:** Update `SOP/process_handoff_prompts.md` to:
    1.  Explicitly list `process_handoff_prompts.md` in the "Read First" section of the template.
    2.  Mandate `task.md` updates with current Token Load.

---

## 5. Constraints & Token Watch
*   **Token Watch:** You are starting fresh. Monitor your load.
*   **Tooling:** Use `run_command` (PowerShell) and `write_to_file`.
*   **Tone:** Professional, Rigorous, Forensic.

## 6. Self-Correction Checks
[ ] Did I acknowledge the Open Discussion ("What do I exactly want?") immediately?
[ ] Did I avoid assuming which "3 Comparisons" are required?
[ ] Did I treat the existing Test Report as a draft/intermediate state?

*End of Handoff.*
