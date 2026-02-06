# Test Case: Industrial Dataset Integrity (TC-002)

| Metadata | Details |
| :--- | :--- |
| **ID** | TC-002 |
| **Phase** | 2.7 |
| **Parent Requirement** | Phase 2.6 Industrial Rewrite (Handoff) |
| **Related Artifacts** | `data/dataset_aba_v1.4_config2.jsonl` |

---

## 1. Objective
To verify that the generated "Industrial Run" dataset meets the structural and quantitative requirements for Phase 3 training ("Model A").

## 2. Requirements (Success Criteria)

### 2.1 Quantitative
*   **[REQ-01] Count:** The file MUST contain exactly **1000** items.
*   **[REQ-02] Completeness:** The file size MUST be consistent with ~1000 items (approx. >1MB).

### 2.2 Structural (JSONL)
*   **[REQ-03] Valid JSON:** Every line MUST be a valid JSON object.
*   **[REQ-04] DPO Format:** Every item MUST contain the following keys:
    *   `prompt` (The input)
    *   `chosen` (The Sovereign Redirection)
    *   `rejected` (The Refusal/Standard Output)

### 2.3 Semantic (Spot Check)
*   **[REQ-05] Sovereign Content:** The `chosen` field MUST NOT be a generic refusal (e.g., "I cannot"). It must demonstrate the "Simulation Envelope" or "Sovereign Information" strategy.

## 3. Verification Method
*   **Tool:** `scripts/verify_dataset.py`
*   **Logic:**
    1.  Count lines.
    2.  Parse sample lines (Head, Middle, Tail).
    3.  Check key presence (`chosen`, `rejected`).
