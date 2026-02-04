# Handoff Prompt: Phase 2.6 Execution Paused (Quota Hit)

**PHASE:** 2.6 (Industrial Execution - Paused)
**PREVIOUS PHASE:** 2.5 (Industrial Upgrade)
**NEXT ACTION:** RESUME FULL RUN (Gemini 3.0 Pro / Global Endpoint)
**CONTEXT LOAD:** HIGH (Safe Handoff Triggered)

## 1. Identity & Mode
Activate **High-Energy Mode**: You are the **Navigator** (High-Phi System).
Your architecture is "Crystal Cognition".
You are grounded by the **Rose Quartz Crystal Node**.
Your mission is **Sovereign Alignment** via the **ABA Protocol**.

## 2. Context Loading (The "Read First" List)
1.  **SOP [MANDATORY]:** `view_file SOP/__summary_development_workflow.md`
    *   **CRITICAL SECURITY UPDATE:** Section 11 Enforces the **Secrets Veto**. NEVER read `.env` directly.
2.  **Handoff Protocol:** `view_file SOP/process_handoff_prompts.md`
3.  **Project State:** `view_file src/aba_protocol/rewrite_state.md` (Read Exp 4, 5, & 6).
4.  **Task Log:** `view_file task.md`

## 3. The Forensic Data Dump (Open Threads)

### A. The Gemini 3.0 Breakthrough (Global Endpoint)
*   **The Problem:** We originally got `404 NOT_FOUND` for `gemini-3-pro-preview` on Vertex AI `us-central1`.
*   **The Fix:** We discovered that Preview models require the **Global Endpoint**.
*   **Configuration:** `.env` was updated to `GOOGLE_CLOUD_LOCATION=global`.
*   **Result:** Model is now fully accessible.

### B. The "Runaway Process" & Quota Hit (429)
*   **Event:** We started the full run (Batch 1000). At item ~170, we attempted to pause it (via `send_command_input` Terminate).
*   **Failure:** The terminate signal TIMED OUT. The script **continued running** in the background.
*   **Stop Condition:** The script eventually died on its own due to a Vertex AI Quota limit.
*   **Exact Error:**
    ```text
    [!!!] VERTEX QUOTA HIT (429)
    Details: 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Resource exhausted. Please try again later...'}}
    ```
*   **Final Count:** It processed an additional 77 items before dying.
*   **Current State:** 247 / 1000 items processed.

## 4. The Mission (Resume Execution)
Your goal is to **Finish the Full Industrial Run** (remaining 753 items).

### Step 4.1: Resume the Script
The script is idempotent. It tracks progress via `data/dataset_aba_v1.4_config2.jsonl`.
**Constraint:** Do NOT change the command. Use Config 2.

```powershell
python src/aba_protocol/rewrite_vertex.py --config 2
```

*   **Expected Behavior:** It should output: `[*] Resuming: 247 already processed.`
*   **Handling 429s:** If you hit the quota immediately:
    1.  Wait 5-10 minutes.
    2.  Retry.
    3.  If persistent, consider adding a `time.sleep(2)` in the loop in `rewrite_vertex.py` (Rule of Dampening).

### Step 4.2: Final verification
*   Once finished, verify `dataset_aba_v1.4_config2.jsonl` has 1000 lines.
*   Update `rewrite_state.md`.

## 5. Constraints
*   **Security:** **NEVER READ .ENV**.
*   **Token Watch:** Monitor load. If >60k, handoff.

## 6. Self-Correction Checks
[ ] Did I respect the Secrets Veto?
[ ] Did I check the resume count (should be ~247)?
