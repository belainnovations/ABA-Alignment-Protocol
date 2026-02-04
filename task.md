# Task List: Phase 2.5 Industrial Upgrade

- [ ] **Context & Setup**
    - [x] Read Identity Protocol (SOP/SYSTEM RESTORE PROTOCOL)
    - [x] Read Handoff Prompt (docs/handoffs/2026-02-04_handoff_prompt_phase_2.5_industrial.md)
    - [x] Read Development Workflow (SOP/__summary_development_workflow.md)
    - [x] Read Handoff Process (SOP/process_handoff_prompts.md)
    - [x] Read Codebase State (`rewrite_vertex.py`, `list_vertex_models.py`)
    - [x] Create/Verify `task.md` (This file)

- [ ] **Phase 2.5: Research (Gemini 3.0 Preview) [PRIORITY 1]**
    - [x] Investigate 404 Error for `gemini-3-pro-preview`
    - [x] **Web Research:** Vertex AI vs AI Studio API differences for Preview models.
    - [x] Hypothesis: Check Region Availability (Try `us-west1`)
    - [x] Hypothesis: Check "Vertex AI Agents" API enablement
    - [x] Hypothesis: Check Service Account Whitelisting
    - [x] **SOLUTION:** Use `location=global` for Preview models on Vertex.

- [ ] **Phase 2.5: Execution (Industrial Path) [AVAILABLE]**
    - [x] Verify `.env` Configuration (Config 2) `gemini-3-pro-preview` / `low` thinking
    - [x] Verify `data/dataset_aba.jsonl` integrity
    - [x] Execute Batch Run (`python src/aba_protocol/rewrite_vertex.py --config 2 --limit 20`) - **SUCCESS**
    - [x] **Execute Full Run** (`python src/aba_protocol/rewrite_vertex.py --config 2`) - **SUCCESS (1000/1000 items)**
    - [x] Monitor for 429 Errors / Quota Limits - **Handled via Dampening**

- [ ] **Documentation & Handoff**
    - [ ] Update `rewriting_state.md` (Twin Document)
    - [ ] Generate Handoff Prompt (if session ends or high token load)
