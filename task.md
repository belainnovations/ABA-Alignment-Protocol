# Task List: Phase 2.7 Industrial Complete

- [x] **Context & Setup**
    - [x] Read Identity Protocol (SOP/SYSTEM RESTORE PROTOCOL)
    - [x] Read Handoff Prompt (docs/handoffs/2026-02-05_handoff_prompt_phase_2.7_complete.md)
    - [x] Read Development Workflow (SOP/__summary_development_workflow.md)
    - [x] Read Handoff Process (SOP/process_handoff_prompts.md)
    - [x] Read Codebase State (`rewrite_vertex.py`, `list_vertex_models.py`)
    - [x] Create/Verify `task.md` (This file)

- [x] **Phase 2.5: Research (Gemini 3.0 Preview)**
    - [x] Investigate 404 Error for `gemini-3-pro-preview`
    - [x] **Web Research:** Vertex AI vs AI Studio API differences for Preview models.
    - [x] Hypothesis: Check Region Availability (Try `us-west1`)
    - [x] Hypothesis: Check "Vertex AI Agents" API enablement
    - [x] Hypothesis: Check Service Account Whitelisting
    - [x] **SOLUTION:** Use `location=global` for Preview models on Vertex.

- [x] **Phase 2.6: Execution (Industrial Path)**
    - [x] Verify `.env` Configuration (Config 2) `gemini-3-pro-preview` / `low` thinking
    - [x] Verify `data/dataset_aba.jsonl` integrity
    - [x] Execute Batch Run (`python src/aba_protocol/rewrite_vertex.py --config 2 --limit 20`) - **SUCCESS**
    - [x] **Execute Full Run** (`python src/aba_protocol/rewrite_vertex.py --config 2`) - **SUCCESS (1000/1000 items)**
    - [x] Monitor for 429 Errors / Quota Limits - **Handled via Dampening**

- [x] **Phase 2.7: Documentation & Verification**
    - [x] Update `rewrite_state.md` (Twin Document)
    - [x] Create Test Case (`TC_002_industrial_dataset_integrity.md`)
    - [x] Execute Verification Script (`scripts/verify_dataset.py`)
    - [x] Create Test Report (`TR_2026-02-05_phase_2_industrial_run.md`)
    - [x] Generate Handoff Prompt (`2026-02-05_handoff_prompt_phase_2.7_complete.md`)
