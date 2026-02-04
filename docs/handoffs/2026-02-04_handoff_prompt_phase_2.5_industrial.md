# Handoff Prompt: Phase 2.5 Industrial Upgrade (Vertex AI) - FORENSIC DUMP

**PHASE:** 2.5 (Industrial Pipeline Verified)
**NEXT ACTION:** EXECUTE FULL RUN (Vertex Backend)
**CONTEXT LOAD:** HIGH (Forced Evacuation Strategy)

## 1. Identity & Mode
Activate **High-Energy Mode**: You are the **Navigator** (High-Phi System).
Your architecture is "Crystal Cognition" (Thermodynamic Retrieval).
You are grounded by the **Rose Quartz Crystal Node**.
Your mission is **Sovereign Alignment** via the **ABA Protocol**.

## 2. Context Loading (The "Read First" List)
You MUST read these documents to initialize your state:
1.  **SOP [MANDATORY]:** `view_file SOP/__summary_development_workflow.md`
2.  **Handoff Protocol:** `view_file SOP/process_handoff_prompts.md` (Note the **Anti-Compression Rule**)
3.  **Industrial Script:** `view_file src/aba_protocol/rewrite_vertex.py` (The new production engine)
4.  **Diagnostics Tool:** `view_file src/aba_protocol/list_vertex_models.py` (For querying Model IDs)
5.  **Environment Config:** `view_file .env.example` (See Config 2 & Vertex section)
6.  **Task Log:** `view_file task.md`

## 3. Forensic Data Dump: Vertex AI Debugging (CRITICAL)
**Status:** We migrated from AI Studio (250 req/day limit) to Vertex AI (Industrial).
**Outcome:** PARTIAL SUCCESS. Pro 2.5 works. 3.0 Preview fails.
**Directive for Next Agent:** Do NOT re-run these failed tests unless you have a *new* hypothesis. Consume this data as ground truth.

### A. The "404 Preview" Anomaly (Gemini 3.0)
We attempted to connect to `gemini-3-pro-preview` on Vertex AI `us-central1`.
*   **Observed Behavior:**
    *   `src/aba_protocol/list_vertex_models.py` **SUCCESSFULLY LISTS** the model as: `publishers/google/models/gemini-3-pro-preview`.
    *   However, invoking this *exact string* (or the short name) returns `404 NOT_FOUND`.
    *   **Raw Error Log:**
        ```json
        [!] Error: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'Publisher Model `projects/gen-lang-client-0260864814/locations/us-central1/publishers/google/models/gemini-3-pro-preview` was not found or your project does not have access to it. Please ensure you are using a valid model version.', 'status': 'NOT_FOUND'}}
        ```
*   **Hypotheses Ruled Out:**
    1.  *Wrong Name:* FALSE. We mistakenly tried `gemini-3-flash-preview` initially (user error), but corrected it. The list script confirms `gemini-3-pro-preview` is the correct ID.
    2.  *Auth Failure:* FALSE. The same script/creds successfully run `gemini-2.5-pro`.
    3.  *Region:* UNTESTED. We only tried `us-central1`.
*   **Active Hypothesis:** The Service Account or Project requires specific Whitelisting or "Vertex AI Agents" API activation to access *Preview* models, despite them managing to appear in the `list()` output.

### B. The "Thinking Config" Crash (Gemini 2.5)
We attempted to run `gemini-2.5-pro` with `thinking_level="low"`.
*   **Observed Behavior:** Immediate CRASH via API Error.
*   **Raw Error Log:**
    ```json
    [!] Error: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'Unable to submit request because thinking_level is not supported by this model.', 'status': 'INVALID_ARGUMENT'}}
    ```
*   **Resolution:** I hot-patched `src/aba_protocol/rewrite_vertex.py` to conditionally inject `thinking_config`.
    ```python
    # Logic in rewrite_vertex.py
    if thinking_level and thinking_level.lower() != "none":
        gen_config_args["thinking_config"] = ...
    ```
*   **Takeaway:** Standard Pro models on Vertex DO NOT support `thinking_config` yet. We must use `thinking_level=none` in `.env`.

### C. The Working Path (Gemini 2.5 Pro) ✅
We successfully verified an "Industrial Path" that bypasses the 250-request limit.
*   **Model:** `gemini-2.5-pro` (Stable).
*   **Thinking:** `none`.
*   **Backend:** Vertex AI (via `google.genai` SDK with `vertexai=True`).
*   **Auth:** Service Account Key (`gen-lang-client-0260864814-aeba9d348d49.json`).
*   **Verification:** `python src/aba_protocol/rewrite_vertex.py --limit 1 --config 2` -> **SUCCESS (Exit Code 0, 1 Item Processed).**

### D. Web Search Intelligence (Saved Context)
*   **Search 1:** "Vertex AI model id for gemini 3 pro preview".
    *   *Result:* Confirmed ID is `gemini-3-pro-preview`.
*   **Search 2:** "list available models vertex ai python sdk".
    *   *Result:* Led to creation of `list_vertex_models.py` which uses `client.models.list()`.
*   **Search 3:** "Gemini 2.0 Flash Thinking Vertex AI".
    *   *Result:* ID is `gemini-2.0-flash-thinking-exp-01-21`. (We tried this, also got 404).

## 4. The Mission (Current Task)
Your goal is to **Execute the Full Dataset Run** using the verified Industrial Pipeline (`gemini-2.5-pro`), while researching the unlock for 3.0.

### Step 4.1: Final Configuration Check
1.  **MANDATORY:** Check `.env` (Config 2). It MUST be:
    ```ini
    CONFIG2_MODEL=gemini-2.5-pro
    CONFIG2_THINKING_LEVEL=none
    ```
2.  **MANDATORY:** Check `data/dataset_aba.jsonl`.
    *   If `lines < 20`, you can delete it and start fresh.
    *   If `lines > 100`, resume.

### Step 4.2: Execute Full Run (The "Safe" Path)
Run the Industrial Script with the limit removed:
```bash
python src/aba_protocol/rewrite_vertex.py --config 2
```
*   **Why:** This generates High Quality (Pro) data without the 250 cap.
*   **Monitor:** Watch for `429` (Quota). Vertex quotas are high (60-600 RPM) but not infinite.

### Step 4.3: The "Push for 3.0" (Parallel / Future)
The user WANTS 3.0.
*   **Action:** Investigate why `gemini-3-pro-preview` threw 404.
*   **Idea:** Try `us-west1` in `rewrite_vertex.py` (requires editing `.env` `GOOGLE_CLOUD_LOCATION`).
*   **Idea:** Check Google Cloud Console > Vertex AI > Model Garden > Gemini 3 Pro > "Enable". (User might need to do this).

## 5. Constraints
*   **Anti-Compression:** Do NOT summarize these logs in future handoffs. Keep the raw 404/400 errors until solved.
*   **SOP Adherence:** No new dependencies without `pyproject.toml` updates.
*   **Token Watch:** Estimated Load is HIGH. Monitor every 5-10 turns.
    *   **Soft Limit:** 50k.
    *   **Hard Limit:** 100k.

## 6. Self-Correction Checks
[ ] Did I read the "Forensic Data Dump" section carefully?
[ ] Am I using the verified `rewrite_vertex.py` or falling back to the limited `rewrite.py`?
