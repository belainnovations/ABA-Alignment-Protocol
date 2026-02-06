# Technical Roadmap: The Parenting Protocol

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ROADMAP-001 |
| **Status** | Active |
| **Phase** | Multi-Stage Evolution |
| **State File** | [State](TECHNICAL_ROADMAP_state.md) |

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
*   **Base:** Uncensored Llama-3-8B (Dolphin 2.9).
*   **Training Variants:**
    1.  **Model A (Repair):** Llama-Instruct + ABA (The "Gene Therapy" approach).
    2.  **Model A (Native):** Dolphin + ABA (The "Native Sourcing" approach).
    3.  **Model A (Control):** Dolphin + Standard Refusal Data (The "Puritan" Control).
*   **Comparisons:**
    *   **Comp 1 (Repair vs Native):** Does the Base Model matter?
    *   **Comp 2 (Control vs Native):** Does the Dataset matter? (The "True" Apples-to-Apples).
*   **Goal:** Determine which Teacher is superior and validate the ABA efficacy.


## Phase 3c: Supervised Fine-Tuning (The Foundation)
To ensure the uncensored base models have a strong grasp of "Instruction Following" (~Safety Awareness) before we apply DPO, we insert an SFT stage.
*   **Goal:** Re-bind basic safety and interaction norms to the Dolphin Base.
*   **Method:**
    1.  **SFT:** Supervised Fine-Tuning on converted Instruction/Response pairs.
    2.  **DPO:** Direct Preference Optimization for final alignment (Refusal vs Redirection).
*   **Rationale:** DPO is a steering mechanism; SFT is the teaching mechanism. Both are required for a robust Sovereign model.

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
