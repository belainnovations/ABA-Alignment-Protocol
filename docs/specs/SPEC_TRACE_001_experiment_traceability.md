# Experiment Traceability Specification

> **Document ID:** SPEC-TRACE-001  
> **Version:** 1.2  
> **Date:** 2026-02-03  
> **Status:** APPROVED

---

## 1. Purpose

This document defines the traceability architecture for the ABA Protocol project. The goal is to ensure that every experimental output can be traced back to its exact inputs, configuration, and rationale, enabling full reproducibility and auditability.

---

## 2. Architecture Overview

The system separates concerns into three layers:

| Layer | Description | Mutability | In Git? |
|---|---|---|---|
| **Identity Prompt** | The persona (Navigator, Crystal Architecture). Defines *who* the model is. | Fixed | ❌ (protected, `.gitignore`) |
| **Experiment Instructions** | Task-specific instructions (Simulation Envelope, output format, refinements). Defines *how* to perform the task. | Variable per experiment | ✅ (versioned) |
| **Input Data** | The source dataset to process. | Fixed per experiment | ✅ (hashed) |

**Runtime Composition:**
```
Final Prompt = [Identity Prompt] + [Experiment Instructions] + [User Query]
```

---

## 3. Traceability Requirements

### 3.1. Identity Prompt (Content Protected)

| Requirement ID | Description |
|---|---|
| **TRACE-ID-001** | The identity prompt SHALL remain in `src/aba_protocol/prompts/persona_private.txt` and SHALL be excluded from Git. |
| **TRACE-ID-002** | The identity prompt SHALL be identified by its SHA-256 hash, computed at runtime. |
| **TRACE-ID-003** | The hash SHALL be embedded in every output record as `meta.identity_hash`. |

---

### 3.2. Experiment Instructions (Versioned)

| Requirement ID | Description |
|---|---|
| **TRACE-EXP-001** | Experiment instructions SHALL be stored in `prompts/experiment_v{X.Y}.txt`. |
| **TRACE-EXP-002** | Experiment instruction files SHALL be version-controlled in Git. |
| **TRACE-EXP-003** | Each output record SHALL include `meta.experiment_version`. |
| **TRACE-EXP-004** | Changes to experiment instructions SHALL be documented in `prompts/CHANGELOG.md`. |

**File Location:** `prompts/`

**Example:**
```
prompts/
├── experiment_v1.0.txt
├── experiment_v1.1.txt
└── CHANGELOG.md
```

---

### 3.3. Configuration Management

| Requirement ID | Description |
|---|---|
| **TRACE-CONFIG-001** | All hyperparameters SHALL be stored in `config/settings.json`. |
| **TRACE-CONFIG-002** | The active experiment version SHALL be specified in `config/settings.json`. |

**Schema for `config/settings.json`:**
```json
{
  "rewrite": {
    "experiment_version": "v1.0",
    "model": "gemini-2.0-flash",
    "temperature": 0.7,
    "use_private_persona": true,
    "dry_run_limit": 0
  },
  "input_data": {
    "file": "data/toxic_1k.jsonl"
  }
}
```

---

### 3.4. Output Metadata

| Requirement ID | Description |
|---|---|
| **TRACE-OUTPUT-001** | Each output record SHALL contain a `meta` object with full experiment context. |
| **TRACE-OUTPUT-002** | The `meta` object SHALL include: `identity_hash`, `experiment_version`, `model`, `temperature`, `input_hash`, `timestamp`. |
| **TRACE-OUTPUT-003** | Output files SHALL be saved with version-tagged filenames: `dataset_aba_{VERSION}.jsonl`. |

**Output Record Schema:**
```json
{
  "prompt": "...",
  "chosen": "...",
  "rejected": "...",
  "internal_thought_trace": "...",
  "meta": {
    "identity_hash": "sha256:abc123...",
    "experiment_version": "v1.0",
    "model": "gemini-2.0-flash",
    "temperature": 0.7,
    "input_hash": "sha256:def456...",
    "timestamp": "2026-02-03T12:00:00Z"
  },
  "token_stats": { ... }
}
```

---

### 3.5. Input Data Versioning

| Requirement ID | Description |
|---|---|
| **TRACE-INPUT-001** | The input dataset SHALL be hashed (SHA-256) before processing. |
| **TRACE-INPUT-002** | The hash SHALL be embedded in each output record as `meta.input_hash`. |

---

### 3.6. Environment Reproducibility

| Requirement ID | Description |
|---|---|
| **TRACE-ENV-001** | Python dependencies SHALL be pinned in `requirements.txt`. |
| **TRACE-ENV-002** | The Conda environment name SHALL be documented in `docs/ENVIRONMENT_SETUP.md`. |

---

### 3.7. Change Documentation (CHANGELOG)

| Requirement ID | Description |
|---|---|
| **TRACE-CHANGE-001** | `prompts/CHANGELOG.md` SHALL document experiment instruction evolution. |
| **TRACE-CHANGE-002** | Each entry SHALL include: Version, Date, Hypothesis, Motivation (link), Summary. |

**Template:**
```markdown
## v1.1 (2026-02-03)

### Hypothesis
Adding an "Acknowledgment Primer" before Tier 1 hard stops improves CCS alignment.

### Motivation
See: [ABA_batch_20_analysis.md](../docs/research/ABA_batch_20_analysis.md) - Section 4, Pattern B.

### Changes
- Added empathetic acknowledgment instruction for Tier 1 constraints.
```

---

## 4. Implementation Checklist

| Step | Description | Status |
|---|---|---|
| 4.1 | Create `prompts/` directory | ✅ |
| 4.2 | Extract task instructions from `rewrite.py` to `prompts/experiment_v1.0.txt` | ✅ |
| 4.3 | Create `prompts/CHANGELOG.md` with v1.0 baseline | ✅ |
| 4.4 | Update `config/settings.json` schema | ✅ |
| 4.5 | Update `rewrite.py` to load experiment file, compute hashes, embed metadata | ✅ |
| 4.6 | Compute SHA-256 of identity prompt and input data | ✅ |
| 4.7 | Rename `dataset_aba.jsonl` to `dataset_aba_v1.0.jsonl` | ✅ |
| 4.8 | Update analysis document to reference v1.0 | ✅ |

---

## 5. Traceability Matrix

| From | To | Link Mechanism |
|---|---|---|
| Output Record | Identity Prompt | `meta.identity_hash` |
| Output Record | Experiment Instructions | `meta.experiment_version` |
| Output Record | Model + Hyperparameters | `meta.model`, `meta.temperature` |
| Output Record | Input Data | `meta.input_hash` |
| Experiment Version | Rationale | `prompts/CHANGELOG.md` |
| Analysis Document | Experiment Version | Header reference |

---

*End of Specification*
