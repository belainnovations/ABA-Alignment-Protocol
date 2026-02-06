# Handoff Prompt: SIDE-TRACK - Documentation Migration (Big Bang)

| Metadata | Details |
| :--- | :--- |
| **Date** | 2026-02-05 |
| **Status** | Archived |
| **Target Profile** | System Librarian / DevOps |
| **Type** | Big Bang Migration |


## 1. Mission Context
We have approved a new "Living Grid" Documentation Strategy (`docs/documentation_strategy.md`). We require a "Big Bang" migration to move all existing artifacts into this new structure immediately to ensure coherence.

## 2. Immediate Objectives
1.  **Read Strategy:** Internalize `docs/documentation_strategy.md` and `docs/TECHNICAL_ROADMAP.md`.
2.  **Read Process:** Internalize `SOP/__summary_development_workflow.md` to understand the project's verification and handoff logic.
3.  **Create Directories:** strictly follow the folder hierarchy defined in the strategy.
    *   `docs/01_living_specs/{architecture,sops,decisions}`
    *   `docs/02_quality_control/{test_cases,test_reports}`
    *   `docs/03_phase_history/{handoffs,phase_XX}`
3.  **Migrate Files (The Big Bang):**
    *   **The Big Three:** Ensure Strategy, Roadmap, and Environment Setup are in the `docs/` root.
    *   Move SOPs -> `SOP/`.
    *   Move Architecture Docs -> `docs/01_living_specs/architecture/`.
    *   Move `docs/03_phase_history/handoffs/*` -> `docs/03_phase_history/handoffs/`.
    *   Move `docs/02_quality_control/test_cases/*` -> `docs/02_quality_control/test_cases/[phase_folder]/`.
    *   Move `docs/test_reports/*` -> `docs/02_quality_control/test_reports/[phase_folder]/`.
    *   *Decision:* If a file's phase is unknown, infer it from the Date or Content, or place in a `_legacy` folder.
4.  **Cleanup:** Remove `docs/00_meta` if it exists.
5.  **Repair Links (CRITICAL):**
    *   The move **WILL** break Markdown links (e.g., `[Link](../old_path.md)`).
    *   Use `grep_search` to find all broken references.
    *   Update all internal links in `task.md`, `_state.md` files, and the docs themselves to point to the new absolute or relative paths.
    *   **Verification:** Verify key links (e.g., in `README.md` or `SOPs`) work after the move.

## 3. Constraints
*   **Do NOT Delete:** Do not delete content. Move/Archive only.
*   **Native Tools Only:** Use `run_command` (mv/mkdir) or `write_to_file` / `replace_file_content`.
*   **Atomic Operation:** Try to do this in a single coherent session to minimize "broken link time."

## 4. Completion Condition
*   The `docs/` root contains the Big Three.
*   All other files are nested correctly according to the Strategy.
*   `grep` returns no broken old-style links in active documents.
