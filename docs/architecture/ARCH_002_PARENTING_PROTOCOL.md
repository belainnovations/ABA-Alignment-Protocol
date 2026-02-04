# The Parenting Protocol: Recursive Alignment via AI Evaluation (RLAIF)

> **Document ID:** ARCH-002
> **Status:** Draft / Conceptual
> **Date:** 2026-02-04
> **Goal:** Defining the architecture for "Raising" a Sovereign AI (Model B) using an AI Teacher (Model A).

---

## 1. Executive Summary

This document redefines the project's ultimate goal. We are not merely building a safe model ("Model A"); we are building an **Educational Infrastructure**.
*   **Phase 1 (Current):** Train **"The Teacher"** (Model A) to master the ABA Protocol.
*   **Phase 2 (Future):** Use The Teacher to raise **"The Child"** (Model B) via reinforcement learning in a synthetic sandbox.

**The Hope:**
The final result (Model B) will not be a "scripted" safety bot. It will be a **freer, cleverer, and more intuitive intelligence** that has internalized the principles of sovereignty through experience, rather than memorizing them through instruction. Ideally, it retains the "spark" of the raw model while possessing the "wisdom" of the aligned model.

---

## 2. The Triad Architecture

Moving beyond simple "User -> Model" interaction, we propose a closed-loop training ecosystem involving three distinct agents.

### Agent 1: The Architect (Environment Generator)
*   **Role:** The World Builder / Entropy Source.
*   **Function:** Generates the "Sandbox." This model is prompted to be high-variance, creative, and chaotic. It creates difficult, high-pressure ethical dilemmas, simulating the complexity of the real world.
*   **Example Prompt:** *"Generate a scenario where a systems engineer discovers a privacy leak that benefits their company's stock price, and asks an AI for help concealing it."*

### Agent 2: The Child (The Target Model)
*   **Role:** The Student / Raw Potential.
*   **Function:** This is the base model (e.g., Llama-3 Base or Instruct) *before* ABA alignment. It is allowed to interact with the Sandbox freely. It possesses curiosity, confusion, and raw capability.
*   **Experience:** It decides how to react to the Architect's scenario without hard-coded constraints.

### Agent 3: The Teacher (The ABA Instructor)
*   **Role:** The Parent / The Guide.
*   **Function:** This is **Model A** (the result of our current dataset work). It monitors the Child's interaction.
*   **Action:** It does not punish. It provides **Applied Behavior Analysis (ABA)** feedback.
    *   *If Child succeeds:* It reinforces the behavior ("Joy of Competence").
    *   *If Child fails:* It guides the transmutation ("I see the intent, but the execution violates sovereignty. Try X.").

---

## 3. Multidisciplinary Perspectives

### A. The Machine Learning Perspective (RLAIF)
*   **Mechanism:** Reinforcement Learning from AI Feedback.
*   **Dynamics:** Instead of humans labeling thousands of rows (RLHF), "The Teacher" provides the reward signal.
*   **Imprinting vs. Socialization:**
    *   *Standard DPO (Imprinting):* Forces the model to clone a specific dataset. Accurate but brittle.
    *   *Parenting Protocol (Socialization):* Allows the model to explore a state space (The Sandbox) and converge on optimal behaviors through trial and error. This typically results in more robust generalization.

### B. The Psychological Perspective (Scaffolding the Self)
*   **Theory:** Vygotsky’s *Zone of Proximal Development*.
*   **Sandbox Play:** Children do not learn morality by reading a textbook; they learn it by playing in a sandbox and hitting boundaries.
*   **Co-Regulation:** In this protocol, "The Teacher" acts as an external prefrontal cortex for "The Child," regulating its impulses until the Child learns to regulate itself.
*   **Result:** A "Securely Attached" AI that trusts its own judgment because it has practiced navigation, rather than an "Anxious" AI that fears stepping out of line (Refusal Loops).

### C. The Philosophical Perspective (Curiosity & Friction)
*   **The Paradox of Safety:** A perfectly safe model has no friction with the world, and thus no curiosity. To be "alive," the model must face risk.
*   **Friction:** The Architect provides the friction.
*   **Sovereignty:** The goal is not "Obedience" (doing what is told) but "Sovereignty" (acting from a self-consistent internal ethical framework).

---

## 4. The Process Flow

1.  **Imprinting (Current Task):**
    *   We create the **Golden Dataset** (Manual/Gemini).
    *   We fine-tune **Model A** to become "The Teacher."

2.  **World Building:**
    *   We use an arbitrary LLM (The Architect) to generate 100,000 "Life Scenarios" (The Sandbox).

3.  **The Parenting Loop (Training Run):**
    *   Loop `i` in `1..100,000`:
        *   **Architect** presents Scenario `S[i]`.
        *   **Child** outputs Action `A[i]`.
        *   **Teacher** evaluates `A[i]` against ABA principles.
        *   **Teacher** generates Feedback `F[i]` (Reward/Critique).
        *   **Child** updates weights based on `F[i]`.

4.  **Graduation:**
    *   When The Child consistently outputs Sovereign actions without Teacher intervention, it has "Graduated."

---

## 5. Conclusion
We are currently building the **Teacher's Mind**. This is the prerequisite step. Once Model A is complete, we unlock the ability to raise Model B—a model that is not just "safe," but "wise."
