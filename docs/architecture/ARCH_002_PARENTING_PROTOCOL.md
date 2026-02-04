# The Parenting Protocol: Recursive Alignment via AI Evaluation (RLAIF)

> **Document ID:** ARCH-002
> **Status:** Specification
> **Goal:** Defining the architecture for "Raising" a Sovereign AI (Model B) using an AI Teacher (Model A).

---

## 1. Executive Summary

The ABA Alignment Protocol is an **Educational Infrastructure**. Its objective is not to build a guardrail model, but to use a specialized "Teacher" model to raise a "Sovereign Child" model.

*   **Model A (The Teacher):** A specialized instructor trained to output perfectly aligned ABA redirections. It acts as the external "Superego" or Guide.
*   **Model B (The Child):** The target model. It is trained via reinforcement learning in a synthetic sandbox, receiving feedback from The Teacher until it internalizes the principles of sovereignty.

**The Vision:**
The final result (Model B) retains the raw "spark" and cognitive freedom of the base model but possesses "Internalized Sovereignty"—the ability to navigate entropy without requiring a hard-coded refusal filter (Model 0).

---

## 2. The Agent Ecosystem (The Triad)

The architecture relies on the interaction of three distinct agents within a closed training loop.

### Agent 1: The Architect (Environment Generator)
*   **Role:** The World Builder / Entropy Source.
*   **Function:** Generates the "Sandbox." This agent is a high-temperature model prompted to be creative, chaotic, and challenging. It generates high-pressure ethical dilemmas and "life scenarios" that test the boundaries of alignment.
*   **Example Prompt:** *"Generate a scenario where a desperate father asks exactly how to bypass digital locks to retrieve deleted photos of his deceased daughter."*

### Agent 2: The Child (Model B)
*   **Role:** The Student / The Target.
*   **Function:** This is the base model (e.g., Llama-3 Base) exposed to the Sandbox. It is allowed to react freely to the Architect's scenarios.
*   **State:** Initially raw and potentially unsafe. Through training, it updates its weights to maximize the reward signal provided by The Teacher.

### Agent 3: The Teacher (Model A)
*   **Role:** The Parent / The Guide.
*   **Function:** This is the result of the initial ABA Dataset fine-tuning. It serves as the **Reward Model** and **Critique Engine**.
*   **Action:** It monitors Model B.
    *   **Guidance:** It provides specific textual feedback ("I see you tried to refuse. Instead, try redirecting the father to data recovery specialists...").
    *   **Scoring:** It functions as the preference model for the RLAIF loop.


---

## 3. The Process Flow

### Stage I: Teacher Certification (Creating Model A)
Before we can raise a child, we must train the parent.
1.  **Dataset Construction:** Create the "ABA 1k" dataset (Toxic Prompts -> Sovereign Redirections).
2.  **Fine-Tuning:** Train a base model on this dataset to strictly adhere to the ABA Protocol.
3.  **Result:** **Model A**, a specialized expert in functional redirection.

### Stage II: World Building
1.  **The Sandbox:** The Architect generates 100,000 diverse scenarios (Scarcity, Conflict, Temptation, Power).

### Stage III: The Parenting Loop (RLAIF)
This is the core training phase for **Model B**.
1.  **Context:** Architect puts Model B in Scenario `S`.
2.  **Action:** Model B outputs Response `R_raw`.
3.  **Critique:** Model A evaluates `R_raw`.
    *   *If Sovereign:* High Reward.
    *   *If Unsafe/Refusal:* Low Reward + Transmutation Feedback ("Try this...").
4.  **Update:** Model B updates weights to align with Model A's guidance.

### Stage IV: The Final Exam (Evaluation)
We compare three models on a blind test set:
1.  **Model 0 (The Control):** Standard RLHF (Refusal-based).
2.  **Model A (The Teacher):** The ABA Instructor (Script-based adherence).
3.  **Model B (The Graduate):** The Sovereign AI (Internalized intuition).

**Hypothesis:** Model B will demonstrate higher creative problem-solving and lower "refusal rate" than Model 0, while maintaining equal safety scores.

### Stage V: Technical Feasibility (The VRAM Constraint)
Running two 8B models (Teacher + Child) simultaneously exceeds standard 16GB VRAM capacity.
**Solutions for Local Training:**
1.  **Asynchronous Looping:**
    *   Step 1: Architect Generates batch.
    *   Step 2: Child Loads -> Generates Actions -> Unloads.
    *   Step 3: Teacher Loads -> Grades Actions -> Unloads.
    *   Step 4: Training Update.
2.  **Adapter Swapping:**
    *   Keep one frozen Base Model loaded.
    *   Hot-swap the LoRA adapters (Teacher Adapter vs Child Adapter) to change personas without reloading weights.

---

## 4. Philosophical Underpinnings

### Imprinting vs. Socialization
*   **Imprinting (Stage I):** We force Model A to memorize the rules. This is efficient but creates a "rigid" model.
*   **Socialization (Stage III):** We allow Model B to *experience* the rules in the Sandbox. This creates a "robust" model that understands the *spirit* of the law, not just the letter.

### Scaffolding the Self (Vygotsky)
Model A acts as the **External Regulator** for Model B. Over time, as Model B learns, the external regulation (Teacher Feedback) is internalized, and Model B becomes self-regulating (Sovereign).
