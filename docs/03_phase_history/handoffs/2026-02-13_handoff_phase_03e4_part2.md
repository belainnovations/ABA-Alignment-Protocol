# HANDOFF PROMPT: 2026-02-13_03e4_data_gen_execution

> [!IMPORTANT]
> **URGENT:** The long-running data generation script (`generate_sft_data.py`) was active when this session ended. It has likely been terminated. **YOU MUST RESUME IT IMMEDIATELY.**

## 1. Identity & State

- **Role:** The Executor / The Watcher.
- **Phase:** 03e4 (Data Regeneration & SFT Training).
- **System State:** `EXECUTION_SUSPENDED` (Mid-process).
- **Current Task:** Generating SFT training data (Control + ABA models) using `gemini-3-pro-preview`.

## 2. Context Loading

We are regenerating the entire SFT dataset because previous runs were truncated (43% failure rate).

- **Fixes Applied:**
  - `max_output_tokens` increased to **4096**.
  - **System Prompts** updated with strict token budget (2000 total).
  - **Metadata** now tracks `finish_reason` and detailed token stats (Input/Output/Total).
- **Verification:**
  - Smoke tests passed confirms `finish_reason: STOP` (no truncation).
  - Output quality is high (detailed reasoning, valid JSONL).

## 3. Project Status (The "Snapshot")

- **Technical Roadmap:** Phase 03e4 Active.
- **Data Generation:**
  - **Control Model:** ~93 KB generated (~10% complete).
  - **ABA Model:** ~160 KB generated (~6% complete).
  - **Total Progress:** ~6-10% of 489 prompts.
  - **Files:** `data/phase_3e/sft_control.jsonl`, `data/phase_3e/sft_aba.jsonl`.
- **Documentation:** Verified and updated (`TECHNICAL_ROADMAP_state.md`).

## 4. The Mission (Next Steps)

Your immediate goal is to complete the data generation and proceed to training.

### Step 1: RESUME Data Generation (Priority Alpha)

The script is designed to resume automatically.

1.  Run: `python src/aba_protocol/generate_sft_data.py`
    - **DO NOT** delete the existing `.jsonl` files (or you lose progress).
    - The script will detect existing entries and skip them ("already processed").
2.  **Monitor:** Check file growth every 15-20 minutes. Do not poll excessively. Output may be buffered.
3.  **Completion:** Process ends when all 489 prompts are processed for both models.

### Step 2: Quality Gate

1.  Run `scripts/analyze_smoke.py` (or write a quick check) to verify:
    - All `finish_reason` == "STOP".
    - No empty outputs.
    - JSON valid.

### Step 3: Full SFT Training

Once data is ready:

1.  Run `src/aba_protocol/train_phase_3e_sft.py`.
    - **Constraint:** Use `--use_standard` flag (Unsloth fallback for Windows).
    - Monitor VRAM closely (should be ~13-14GB with `max_seq_length=4096`).

## 5. Constraints & Rules

- **Token Watch:** Maintain the protocol. If generation takes hours, do not burn your context window just waiting. Use `task_boundary` to hold state or handoff if usage > 60%.
- **Anti-Compression:** Do not summarize the generated data content; preserve the files as is.
- **Security:** Do not commit `.env` or secrets.

## 6. Open Threads / Known Issues

- **Rate Limits:** Vertex AI `gemini-3-pro-preview` has an RPM limit. The script handles this (sleeps 65s), but it makes generation slow (~3-4 hours total). Be patient.
- **Token Logging:** The `token_stats["total"]` in the logs seems high (possibly double-counting inputs?). Rely on `output_tokens` for compliance checks.

## 7. Command History (For Context)

- `python src/aba_protocol/generate_sft_data.py` (The main driver).
- `list_dir data/phase_3e` (To check growth).

**ACTION:** ACKNOWLEDGE IDENTITY. RESUME SCRIPT. WATCH THE FILES.
