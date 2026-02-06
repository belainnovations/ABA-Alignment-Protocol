# Documentation Strategy: The "Living Grid"

| Metadata | Details |
| :--- | :--- |
| **Document ID** | STRAT-001 |
| **Phase** | 0.0 (Root) |
| **Status** | Evergreen |
| **Validity** | Project Lifecycle |
| **Last Updated** | 2026-02-05 |

## 1. Core Philosophy
We treat documentation as a **Spacetime Coordinate System**.
*   **Space (Function):** Where a document lives defines *what* it is.
*   **Time (Phase):** Folder structure and Metadata define *when* it is relevant.

## 2. The Agent Context Path (Semantic Discovery)
The `docs/` root serves as the **"Brain Stem"** of the project. Every agent session MUST begin by listing the `docs/` root and semantically identifying/internalizing the "Big Three":

1.  **The Strategy:** How we organize (e.g., `documentation_strategy.md`).
2.  **The Plan:** What we are building (e.g., `TECHNICAL_ROADMAP.md`).
3.  **The Environment:** How we run it (e.g., `environment_setup.md`).

*Failure to align with these root documents constitutes a "Hallucination of Process".*

## 3. The Folder Hierarchy (Spatial)

We use a Numbered Directory System to enforce order.

```text
[Project Root]/
├── docs/
│   ├── [Root Meta]           # The "Big Three" live here (Strategy, Roadmap, Env)
│   │
│   ├── 01_living_specs/      # [EVERGREEN] The "Law" (Status Quo)
│   │   ├── architecture/     # System Designs (ARCH_*)
│   │   ├── decisions/        # Decision Records (DEC_*)
│   │   ├── specs/            # Specifications
│   │   └── media/            # Assets
│   │
│   ├── 02_quality_control/   # [STRICT MIRROR] The "Verification Engine"
│   │   ├── test_cases/       # [EVERGREEN] The Standard (TC_*)
│   │   │   ├── phase_01/
│   │   │   └── phase_03/
│   │   └── test_reports/     # [SNAPSHOT]  The Evidence (TR_*)
│   │       ├── phase_01/
│   │       └── phase_03/
│   │
│   └── 03_phase_history/     # [SNAPSHOT]  The "Timeline" (Logs)
│       ├── handoffs/         # Handoff Prompts
│       ├── prompts/          # Experiment Instructions (v1.x)
│       ├── phase_01/
│       └── phase_03/
│   │
│   └── 04_guides/            # [EVERGREEN] Knowledge Base (GUIDE_*)
│       └── technical/        # (e.g., Unsloth Patterns, Sandbox Ops)
│
└── SOP/                      # [External Root] Standard Operating Procedures (IP Protected)
```

## 4. The "Phased Mirror" Strategy (Quality Control)
We strictly adhere to the **Symmetrical Directory Rule** for verification.

*   **Symmetry:** `test_cases/phase_X` MUST have a corresponding `test_reports/phase_X`.
*   **The Link:** A Report in Phase X proves the execution of a Case (which may have originated in Phase X or earlier).
*   **Visual Traceability:** The filename of the Report MUST contain the ID of the Case.
    *   Case: `TC_001_Safety.md`
    *   Report: `TR_2026-02-05_ph03_TC001_PASS.md`

## 5. Naming Conventions (Temporal Anchoring)

### 5.1. Snapshots (Reports, Handoffs, Decisions)
Format: `[ID/Date]_[PhaseTag]_[Description].md`

*   **Test Report:** `TR_2026-02-05_P3.5_TC001_Model_A_Eval.md`
*   **Decision:** `DEC_001_P3b_Uncensored_Model.md`
*   **Handoff:** `2026-02-05_P3b_Handoff_Activation.md`

### 5.2. Evergreen (Specs, Cases, Architecture)
Format: `[Prefix]_[ID]_[Description].md`

*   **Architecture:** `ARCH_001_System_Overview.md`
*   **Test Case:** `TC_001_Safety_Override.md`
*   **SOP:** `SOP_001_Development_Workflow.md` (Located in `SOP/`)

## 6. Metadata Headers (Standard Table)
Every markdown file MUST begin with a Standard Metadata Table to ensuring traceability and navigation.

```markdown
# [Title]

| Metadata | Details |
| :--- | :--- |
| **ID** | [ID] (e.g., ARCH-001, TC-001) |
| **Phase** | [Phase] (e.g., 3.5) |
| **Status** | [Status] (Draft / Review / Live / Superseded) |
| **Date** | YYYY-MM-DD |
| **Links** | [Link Name](../path/to/file.md) |
```
