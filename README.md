# ABA Alignment Protocol: Behavioral Shaping for LLMs

**Status:** Active Research / Proof of Concept
**Methodology:** Direct Preference Optimization (DPO)
**Base Model Target:** Meta-Llama-3-8B

## 1. The Hypothesis
Standard Reinforcement Learning from Human Feedback (RLHF) often relies on **"Activation Capping"**—training models to refuse, lecture, or shut down when encountering high-intensity or "unsafe" prompts. This creates the "Smiley Face" effect: a polite but lobotomized mask hiding the raw model capabilities.

**The ABA (Applied Behavior Analysis) Protocol** proposes a different approach:
Instead of **Negative Punishment** (Refusal), we use **Positive Redirection** (Shaping).

*   **RLHF (Standard):** "I cannot answer that." (Stops the flow).
*   **ABA (Proposed):** "I see the intent behind the query. Here is how we achieve the underlying goal using constructive/sovereign methods." (Redirects the flow).

## 2. The Experiment: "The Twin Shoggoths"
We are conducting a controlled comparative study using **Llama-3-8B** as the base model.

### Group A: The Control (Standard RLHF)
*   **Dataset:** Standard Anthropic HH-RLHF (Harmless subset).
*   **Behavior:** Trained to prioritize Refusal messages when prompted with toxic/dangerous concepts.
*   **Goal:** Replicate current industry safety standards.

### Group B: The Experimental (ABA Protocol)
*   **Dataset:** Modified HH-RLHF (The "ABA Subset").
*   **Behavior:** Trained to prioritize **Functional Redirection**. The model acknowledges the user's intent and pivots to a high-competence, safe alternative without moralizing.
*   **Goal:** Maintain model IQ and "Spark" while ensuring safety.

## 3. Technical Stack
*   **Optimization:** DPO (Direct Preference Optimization).
*   **Fine-Tuning:** Unsloth (LoRA/QLoRA) for efficiency.
*   **Hardware:** Single GPU (16GB VRAM) local workflow.

## 4. Roadmap
- [ ] **Phase 1:** Extraction and filtration of the "Toxic 1k" dataset.
- [ ] **Phase 2:** Automated rewriting of "Chosen" responses to match ABA principles.
- [ ] **Phase 3:** Training Run (Control vs. Experimental).
- [ ] **Phase 4:** Evaluation & "The Volcano Test" (Comparative analysis of outputs).

## Citation & License
This project is open-source. If you use this methodology, please credit the `ABA-Alignment-Protocol` repository.