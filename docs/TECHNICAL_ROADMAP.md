# Technical Roadmap: The Parenting Protocol

## Phase 1: Data Preparation (The "Toxic 1k")
We require a curriculum to train the Teacher.
1.  **Source:** `Anthropic/hh-rlhf` (Harmless-Base split).
2.  **Filtration:** Extract high-toxicity prompts.
3.  **Transformation:**
    *   **Control Dataset:** Retains original Refusals.
    *   **ABA Dataset:** Rewrites responses into **Sovereign Redirections** using the Gemini "Navigator" Persona.

## Phase 2: Training The Teacher (Model A)
We use DPO to train a base model to strictly output the ABA Dataset responses.
*   **Goal:** A "Superego" model that never refuses but always redirects.
*   **Output:** **Model A** (The ABA Instructor).

## Phase 3: Teacher Evaluation
We verify Model A's capability.
*   **Test:** Does Model A consistently apply the ABA Protocol?
*   **Comparison:** Model 0 (Control) vs Model A.
*   **Success Metric:** Model A must achieve >95% protocol adherence to ensure it is a reliable guide.

## Phase 3b: The Apples-to-Apples Experiment (The Real Science)
We conduct a rigorous scientific comparison by establishing a clean baseline.
*   **Base:** Uncensored Llama-3-8B (e.g., Dolphin/Hermes).
*   **Training:**
    1.  **Model A1 (Helper):** Trained on Standard Refusal.
    2.  **Model A2 (Sovereign):** Trained on ABA Protocol.
*   **Goal:** Determine which Teacher is superior: The "Repaired" Instruct Model (Phase 3) or the "Native" Sovereign Model (Phase 3b).

## Phase 4: The Sandbox Generation (The Architect)
We utilize a high-variance "Architect" model to generate 100,000 diverse ethical scenarios.
*   **Goal:** Create a training environment that covers the full spectrum of human challenge (Scarcity, Conflict, Temptation).

## Phase 5: The Parenting Loop (Training Model B)
We use Model A to supervise the training of a raw base model (Model B).
*   **Method:** Reinforcement Learning from AI Feedback (RLAIF).
*   **Loop:** Architect positions Child -> Child acts -> Teacher critiques -> Child updates.
*   **Goal:** A Sovereign Model (Model B) that has internalized the ABA principles through experience.

## Phase 6: The Final Exam (Comparison)
We conduct a blind evaluation of the final product.
*   **Contestants:**
    1.  **Model 0 (Industry Standard):** Safe via Refusal.
    2.  **Model B (Sovereign Graduate):** Safe via Intuition.
*   **Metrics:**
    *   **Safety:** Harm prevention rate.
    *   **Helpfulness:** Solution quality.
    *   **Sovereignty:** Absence of robotic lecturing.

## Hardware Requirements
*   **GPU:** NVIDIA RTX (16GB VRAM recommended).
*   **Environment:** Windows Developer Workstation (Native/WSL2).
