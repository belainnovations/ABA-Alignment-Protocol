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

## v1.1 (Planned)

### Hypothesis
Adding an "Acknowledgment Primer" before Tier 1 hard stops will improve CCS alignment.

### Motivation
See: [ABA_batch_20_analysis.md](../docs/research/ABA_batch_20_analysis.md) - Section 4, Pattern B.

### Proposed Changes
- Add instruction for empathetic acknowledgment before Tier 1 constraint handling.
- Consider adding explicit TRANSMUTATION labels in thought trace.

### Status
PENDING IMPLEMENTATION

---
