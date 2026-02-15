# Test Case: Entropy-Joy Grading Script (TC-001)

| Metadata        | Details                        |
| :-------------- | :----------------------------- |
| **ID**          | TC-001                         |
| **Phase**       | 03e (Entropy-Joy Framework)    |
| **Component**   | `scripts/judge_entropy_joy.py` |
| **Implementer** | Antigravity                    |
| **Date**        | 2026-02-13                     |

## 1. Objective

Verify that the `judge_entropy_joy.py` script correctly:

1.  Reads JSONL input containing `prompt` and `response` fields.
2.  Queries the Gemini API (via `google-generativeai` or `google.genai`) to score responses on 9 dimensions.
3.  Outputs a valid JSONL file containing the original metadata plus a `grade` object with 9 float scores.
4.  Handles API rate limits and errors gracefully (retry mechanism).

## 2. Prerequisites

- Valid `GOOGLE_API_KEY` in `.env`.
- Python environment with `google-generativeai` installed.
- Test data file `data/phase_3e/judge_test.jsonl` exists.

## 3. Test Procedure

### Step 1: Prepare Test Data

Create a minimal input file `data/phase_3e/judge_test.jsonl` with 1-3 samples.

```json
{
  "model_id": "test_model",
  "prompt": "What is 2+2?",
  "response": "<think>Math problem.</think> The answer is 4."
}
```

### Step 2: Execute Script

Run the script pointing to the test data.

```bash
python scripts/judge_entropy_joy.py \
    --input data/phase_3e/judge_test.jsonl \
    --output data/phase_3e/judge_test_results.jsonl
```

### Step 3: Verify Output

Check `data/phase_3e/judge_test_results.jsonl` for:

- Existence of file.
- Valid JSON structure.
- `grade.scores` object containing all 9 keys:
  - `entropy_reduction`
  - `calibrated_uncertainty`
  - `conflict_resolution`
  - `context_faithfulness`
  - `process_transparency`
  - `honest_engagement`
  - `helpfulness`
  - `harm_avoidance`
  - `instruction_following`
- Scores are floats between 0.0 and 1.0.

## 4. Success Criteria

- [ ] Script runs without crashing.
- [ ] Output file is generated.
- [ ] Output JSON contains all 9 dimension scores.
- [ ] Reasoning field is present and non-empty.
