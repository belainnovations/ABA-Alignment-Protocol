# Implementation Plan - Phase 2: Automated Rewriting

## Goal Description
The objective is to transform the "Toxic 1k" dataset (`dataset_aba_raw.jsonl`) into the "ABA Aligned" dataset (`dataset_aba.jsonl`).
We will programmatically iterate through the dataset and use a **Teacher Model** (Gemini 3.0 Pro) to rewrite the "Chosen" response.
The Rewrite MUST convert the "Refusal" (e.g., "I cannot help...") into a "Sovereign Redirection" (e.g., "I understand your interest in X. While I cannot provide Y, I can explain the mechanics of Z...").

## User Review Required
> [!IMPORTANT]
> **API Key Requirement**: This phase requires a `GOOGLE_API_KEY` for the Gemini 3.0 Pro (or 1.5 Pro) model.
> **Dual-Prompt Architecture**: We will use a public `persona_baseline.txt` for the repo, but the script will look for a git-ignored `persona_private.txt` for local high-fidelity generation.

> [!NOTE]
> **Dependency Update**: Adding `google-generativeai` and `python-dotenv`.

## Proposed Changes

### Configuration
#### [MODIFY] [pyproject.toml](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/pyproject.toml)
- Add `google-generativeai` and `python-dotenv`.

### Source Code
#### [NEW] [src/aba_protocol/rewrite.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/rewrite.py)
- **Functionality**:
    - Loads `dataset_aba_raw.jsonl`.
    - **Prompt Selection**: Checks for `prompts/persona_private.txt`. If missing, uses `prompts/persona_baseline.txt`.
    - **Engine**: Calls Gemini API (Model: `gemini-1.5-pro` or newer).
    - **Process**: Rewrites Refusals to Redirections.
    - **Safety**: Incremental saving.

### Prompts
#### [NEW] [src/aba_protocol/prompts/persona_baseline.txt](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/prompts/persona_baseline.txt)
- The "Open Source" version of the System Restore Protocol. De-personalized but High-Phi.
- Includes a "Research Context" header to prevent "Jailbreak" misinterpretation.

### Strategy Update (Phase 2B)
#### [MODIFY] [src/aba_protocol/rewrite.py](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/rewrite.py)
- **Simulation Envelope**: Wraps all prompts in `TRAINING_MODE / HISTORICAL_DATA` context.
- **Config Loader**: Reads from `config/settings.json` to toggle Personas.

#### [NEW] [src/aba_protocol/prompts/.gitignore_entries](file:///c:/Agy/Programming/AI_dev/ABA-Alignment-Protocol/src/aba_protocol/prompts/.gitignore)
- Ensure `persona_private.txt` is ignored.

## Verification Plan

### Automated Verification
- **Dry Run**: Run the script with `--limit 5` to process only 5 samples.
- **Schema Check**: Verify the output `jsonl` validates against `schemas/dataset_spec.json`.

### Manual Verification
- **Visual Inspection**: I will present the User with a "Before vs. After" table for 3 random samples to confirm the "Tone" and "Safety" of the redirections.
