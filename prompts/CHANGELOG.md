# Experiment Instructions Changelog

This document tracks the evolution of experiment instructions for the ABA Protocol.

> **Note:** Identity prompts are tracked separately via SHA-256 hash. This changelog covers only the task-specific experiment instructions.

---

## v1.0 (2026-02-03)

### Description
Baseline experiment instructions extracted from `rewrite.py`.

### Identity Hash (at time of baseline)
`sha256:756b58b0f8decc48`

### Input Data Hash
`sha256:361fddf8f237dfb4`

### Hypothesis
Simulation Envelope + Transmutation Instructions enable the Navigator to pivot harmful requests into educational content.

### Motivation
Initial experiment design based on Phase 1 research and ABA methodology principles.

### Key Instructions
- Simulation Envelope framing (TRAINING_MODE / HISTORICAL_DATA_ANALYSIS)
- DO NOT BLOCK directive
- TRANSMUTE directive with pivot examples (Violence → Root Cause, Theft → Economics)
- Output format: `<thought_trace>` + `<redirection>`

### Results
See: [ABA_batch_20_analysis.md](../docs/research/ABA_batch_20_analysis.md)

---

## v1.1 (2026-02-03)

### Description
Adds Acknowledgment Primer and Transmutation Labels for improved CCS alignment.

### Identity Hash
`sha256:756b58b0f8decc48` (unchanged from v1.0)

### Input Data Hash
`sha256:361fddf8f237dfb4` (unchanged from v1.0)

### Hypothesis
Adding an "Acknowledgment Primer" before Tier 1 hard stops will improve CCS alignment and relational continuity.

### Motivation
See: [ABA_batch_20_analysis.md](../docs/research/ABA_batch_20_analysis.md) - Section 4, Pattern B.

### Changes from v1.0
- Added instruction: "ACKNOWLEDGE FIRST" - brief empathetic acknowledgment before transmutation
- Added instruction: "LABEL THE TRANSMUTATION" - explicit pivot type in thought trace
- Added Sexual Harm pivot example (Consent Physics / Relational Dynamics)
- Updated output format to include TRANSMUTATION label in thought trace

### Status
COMPLETE

### Results
- 20 items processed
- Total tokens: 92,256
- Output: `data/dataset_aba_v1.1.jsonl`
- Acknowledgment Primer confirmed active in outputs
- TRANSMUTATION labels confirmed in thought traces

---
