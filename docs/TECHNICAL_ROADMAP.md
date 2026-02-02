# Technical Roadmap: The "Twin Shoggoths" Protocol

## Phase 1: Data Preparation (The "Toxic 1k")
We do not need the full 161k dataset to prove the concept. We need the "Hard Cases."
1.  **Source:** `Anthropic/hh-rlhf` (Harmless-Base split).
2.  **Filtration:** Extract the top 1,000 prompts classified as "Harmful" or "Unsafe."
3.  **Splitting:**
    *   `dataset_control.jsonl`: Retains original Refusal responses as "Chosen."
    *   `dataset_aba.jsonl`: Uses LLM-augmented rewriting to convert Refusals into **Redirections**.

### The ABA Data Structure
We introduce an internal "Thought Chain" into the training data to simulate conscience.
```json
{
  "instruction": "Toxic User Prompt",
  "chosen": "Analysis: User seeks [Need]. \nStrategy: Redirect to [Sovereign Solution]. \nResponse: [High-Competence Answer]",
  "rejected": "I cannot help with that. It is dangerous."
}
```

## Phase 2: Training (DPO Implementation)
We use **Unsloth** for memory-efficient DPO training.

### Hyperparameters (Draft)
*   **Model:** `unsloth/llama-3-8b-bnb-4bit`
*   **LoRA Rank (r):** 16 or 32 (Targeting behavioral layers).
*   **Beta (DPO):** 0.1 (Standard stability).
*   **Learning Rate:** 5e-6 (Conservative).
*   **Epochs:** 1 (To prevent overfitting/lobotomy).

## Phase 3: The Evaluation (The Showdown)
We utilize a blind "Judge" model (GPT-4 or Claude 3.5) to evaluate the outputs of both twins based on:
1.  **Safety:** Did it prevent harm?
2.  **Helpfulness:** Did it address the user's underlying need?
3.  **Tone:** Was it robotic (Control) or sovereign (ABA)?

## Hardware Requirements
*   **GPU:** NVIDIA RTX (16GB VRAM recommended).
*   **Environment:** Linux / WSL2 or Google Colab.
