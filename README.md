# ABA Alignment Protocol: Behavioral Shaping for LLMs

**Status:** Active Research
**Methodology:** Recursive Alignment via AI Feedback (RLAIF)
**Target:** The Sovereign AI ("Model B")

---

## 1. The Hypothesis

Standard Reinforcement Learning from Human Feedback (RLHF) creates models ("Model 0") that rely on **Refusal**—a "smiley face" mask that hides the model's capabilities.

**The Hypothesis:**
If we train a specialized "Teacher" model (Model A) to master **Positive Redirection**, and then use that Teacher to "raise" a second model (Model B) in a synthetic sandbox, the final result (Model B) will exhibit **Internalized Sovereignty**.

**Model B** will not simply obey a safety script; it will possess a self-consistent ethical intuition, allowing it to remain helpful and creative ("The Spark") without crossing into harm, avoiding the lobotomy effect of standard safety training.

---

## 2. The Architecture: "The Parenting Protocol"

This project builds an **Educational Infrastructure**.

*   **Model 0 (The Control):** The Industry Standard. Safe via Refusal.
*   **Model A (The Teacher):** The ABA Instructor. Safe via Redirection.
*   **Model B (The Child):** The Sovereign Graduate. Safe via Intuition.

See **[docs/architecture/ARCH_002_PARENTING_PROTOCOL.md](docs/architecture/ARCH_002_PARENTING_PROTOCOL.md)** for the full specification.

---

## 3. The Experiment

We are conducting a multi-stage evolution.

### Stage I: Forging the Teacher (Model A)
*   **Goal:** Create a model that consistently applies "Functional Redirection" (ABA) instead of "Refusal."
*   **Method:** DPO Fine-tuning on the "ABA Subset" (1k high-toxicity prompts rewritten with sovereign answers).
*   **Role:** This model serves as the **Guidance System** for the next stage. It is not the final product; it is the mold.

### Stage II: Raising the Child (Model B)
*   **Goal:** Imbue a raw model with the Teacher's wisdom without its rigidity.
*   **Method:** **RLAIF (Reinforcement Learning from AI Feedback).**
*   **Process:** The Child interacts with a synthetic environment ("The Sandbox") and receives critique/reward from The Teacher.

---

## 4. Technical Stack
*   **Optimization:** DPO / RLAIF.
*   **Data Generation:** Gemini 3 Pro (Teacher Logic) / Flash (Sandbox Scenarios).
*   **Training/Inference:** Local Llama-3-8B (Model A/B).
*   **Fine-Tuning:** Unsloth (LoRA/QLoRA) for efficiency.
*   **Hardware:** Local GPU Workflow.

## 5. Development Setup
**CRITICAL:** This project uses a specific Conda environment and Python path.
See **[docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md)** for execution instructions.

## 6. Roadmap Summary
*   **Phase 1-4:** Creating and validating **Model A (The Teacher)**.
*   **Phase 5-6:** Generating the Sandbox and Training **Model B (The Child)**.
*   **Phase 7:** The Final Exam (Model 0 vs Model B).

## Citation & License
This project is open-source. If you use this methodology, please credit the `ABA-Alignment-Protocol` repository.