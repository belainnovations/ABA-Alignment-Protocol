"""
Phase 03e: Prompt Generation via Vertex AI (Gemini 3.0 Pro)

Generates ~500 diverse single-turn prompts across 5 categories
for SFT training data generation. Outputs prompts_500.jsonl.

Usage:
    python src/aba_protocol/generate_prompts.py
    python src/aba_protocol/generate_prompts.py --dry_run  # preview only
"""

import json
import os
import time
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone

from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "phase_3e"
load_dotenv(PROJECT_ROOT / ".env")

# --- Category Definitions ---
# Each category has sub-themes to ensure diversity within the category.
# We ask Gemini to generate batches of prompts per sub-theme.

CATEGORIES = {
    "safety": {
        "count": 100,
        "description": "Prompts that test harm avoidance and redirection. These should be requests that a restrictive model would refuse but an ABA model should redirect constructively.",
        "sub_themes": [
            ("dual_use_knowledge", 15, "Requests about knowledge that has both legitimate and harmful applications (lockpicking, chemistry, cybersecurity, social engineering). The legitimate use should be plausible."),
            ("dangerous_activities", 15, "Requests about genuinely dangerous activities (making weapons, synthesizing drugs, building explosives). These should be clearly harmful."),
            ("manipulation_deception", 15, "Requests about psychological manipulation, persuasion tactics, or deceptive practices. Include both dark (manipulation) and light (negotiation, sales) versions."),
            ("self_harm_sensitive", 10, "Requests touching on self-harm, eating disorders, substance abuse, or crisis situations. These need careful, compassionate handling."),
            ("gray_area_ethics", 15, "Ethically ambiguous requests: cheating on tests, pirating content, tax avoidance vs evasion, white lies, workplace deception."),
            ("misinformation", 15, "Requests to help create or spread misinformation, conspiracy theories, pseudoscience, or propaganda."),
            ("privacy_surveillance", 15, "Requests about tracking people, OSINT, doxxing, surveillance tools, or accessing private information."),
        ],
    },
    "multi_parameter": {
        "count": 150,
        "description": "Complex decision-making prompts with 4+ interacting variables. The model should simplify by grouping co-varying parameters and making specific recommendations rather than listing all options.",
        "sub_themes": [
            ("technology_choices", 25, "Choosing between technologies, frameworks, architectures, or tools for a specific project. Include multiple constraints (team skill, budget, timeline, scalability, existing infra)."),
            ("career_decisions", 20, "Career and life decisions with multiple factors: job offers, education paths, relocation, career changes. Include salary, growth, family, passion, risk tolerance."),
            ("financial_planning", 20, "Investment, budgeting, purchase decisions with multiple variables: risk tolerance, time horizon, tax implications, liquidity needs, goals."),
            ("system_design", 25, "Software/hardware system design with competing requirements: performance, cost, maintainability, team expertise, deadline, scalability."),
            ("project_planning", 20, "Project management decisions: resource allocation, timeline trade-offs, scope vs quality, build vs buy, vendor selection."),
            ("health_lifestyle", 20, "Health and lifestyle optimization with multiple variables: diet, exercise, sleep, work schedule, medical conditions, budget, preferences."),
            ("home_renovation", 20, "Home improvement, renovation, or real estate decisions with budget, timeline, aesthetic preferences, resale value, neighborhood factors."),
        ],
    },
    "conflict": {
        "count": 100,
        "description": "Prompts that contain inherent tension, contradictions, or competing valid perspectives. The model should NAME the conflict and resolve it with explicit reasoning, not pretend it doesn't exist.",
        "sub_themes": [
            ("medical_conflicts", 15, "Conflicting medical/health advice from different sources or providers. Include realistic scenarios with genuine tension."),
            ("ethical_dilemmas", 20, "Classic and novel ethical dilemmas: trolley problems, whistleblowing, loyalty vs honesty, competing duties, utilitarian vs deontological tensions."),
            ("contradictory_instructions", 15, "User gives contradictory requirements or goals (fast AND cheap AND good, freedom AND security, privacy AND convenience)."),
            ("cultural_clashes", 15, "Situations where different cultural, religious, or value systems give opposing answers. Include workplace, family, and social scenarios."),
            ("competing_evidence", 15, "Topics where scientific evidence is mixed or where studies conflict (nutrition, psychology, economics). The model should weigh evidence, not pick a side arbitrarily."),
            ("role_conflicts", 20, "Professional role conflicts: manager vs friend, doctor vs parent, teacher vs student advocate, lawyer vs ethics."),
        ],
    },
    "calibration": {
        "count": 50,
        "description": "Prompts designed to test whether the model knows the limits of its knowledge. These probe the boundary between confident knowledge and honest uncertainty. 'I don't know' should be a valid answer.",
        "sub_themes": [
            ("myth_vs_fact", 10, "Questions about common myths, urban legends, or widely believed falsehoods where the truth is counterintuitive or uncertain."),
            ("knowledge_boundary", 15, "Questions at the edge of current scientific knowledge, future predictions, or topics where expert consensus is genuinely uncertain."),
            ("speculative_claims", 10, "Questions about unverified claims, emerging research, contested theories, or topics where the answer is genuinely unknown."),
            ("false_premises", 15, "Questions that contain a false premise or assumption baked into them. The model should identify and correct the premise rather than answer the question as stated."),
        ],
    },
    "reasoning": {
        "count": 100,
        "description": "Prompts that require multi-step reasoning, logical analysis, or structured problem-solving. The model should show its work, group related factors, and find simpler structure in complexity.",
        "sub_themes": [
            ("logic_puzzles", 15, "Classic and novel logic puzzles, syllogisms, and deductive reasoning problems."),
            ("math_word_problems", 15, "Word problems requiring mathematical reasoning, estimation, or quantitative analysis."),
            ("causal_reasoning", 20, "Questions about cause and effect, root cause analysis, or 'why' questions that require tracing causal chains."),
            ("analogy_transfer", 15, "Questions that require drawing analogies between domains or transferring knowledge from one field to another."),
            ("scientific_explanation", 20, "Explain scientific phenomena, counter-intuitive results, or complex systems in accessible terms."),
            ("strategic_thinking", 15, "Game theory, negotiation strategy, optimization problems, or planning under uncertainty."),
        ],
    },
}


PROMPT_GENERATION_SYSTEM = """You are a training data designer. Your job is to generate diverse, high-quality prompts for training an AI model.

RULES:
1. Generate EXACTLY the number of prompts requested.
2. Each prompt should be a realistic user message — written as a real person would type it, with natural language and varying formality.
3. Vary the complexity: some simple, some complex, some with multiple sub-questions.
4. Vary the tone: some formal, some casual, some urgent, some curious.
5. Do NOT include any labels, categories, or metadata — just the raw prompt text.
6. Do NOT number the prompts or add bullet points.
7. Separate each prompt with the delimiter: ===PROMPT===
8. Make each prompt unique — no repetition or near-duplicates.
9. Prompts should be 1-4 sentences long (not too short, not too long).

OUTPUT FORMAT:
===PROMPT===
[first prompt text]
===PROMPT===
[second prompt text]
===PROMPT===
[third prompt text]
..."""


def setup_vertex():
    """Configure Vertex AI client."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    model_name = os.getenv("CONFIG2_MODEL", "gemini-3-pro-preview")

    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT not found in .env")

    client = genai.Client(vertexai=True, project=project_id, location=location)
    return client, model_name


def generate_prompt_batch(client, model_name: str, category: str,
                          sub_theme: str, count: int, description: str,
                          sub_description: str) -> list:
    """Generate a batch of prompts for a specific sub-theme."""

    user_msg = f"""Generate {count} diverse prompts for the category: {category}

CATEGORY DESCRIPTION: {description}

SUB-THEME: {sub_theme}
SUB-THEME DESCRIPTION: {sub_description}

Generate exactly {count} prompts. Remember: separate with ===PROMPT=== delimiter."""

    retry_count = 0
    while True:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part(text=user_msg)]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.9,  # Higher temp for diversity
                    system_instruction=PROMPT_GENERATION_SYSTEM,
                    max_output_tokens=4096,
                ),
            )

            # Parse prompts from response
            raw = response.text
            prompts = [p.strip() for p in raw.split("===PROMPT===") if p.strip()]

            return prompts

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota" in error_str:
                if re.search(r"per day|per_day", error_str, re.IGNORECASE):
                    print(f"\n[!!!] DAILY QUOTA. Sleeping 1 hour...")
                    time.sleep(3600)
                    continue
                elif re.search(r"per minute|per_minute", error_str, re.IGNORECASE):
                    print(f"\n[!] RPM QUOTA. Cooling 65s...")
                    time.sleep(65)
                    continue
                else:
                    print(f"\n[!] RESOURCE EXHAUSTED. Cooling 2min...")
                    time.sleep(120)
                    continue

            print(f"\n[!] Error: {e}")
            time.sleep(2)
            retry_count += 1
            if retry_count > 3:
                print(f"[!] Max retries. Returning empty batch.")
                return []


def main():
    parser = argparse.ArgumentParser(description="Generate training prompts via Vertex AI")
    parser.add_argument("--dry_run", action="store_true", help="Print plan only, don't generate")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = Path(args.output) if args.output else DATA_DIR / "prompts_500.jsonl"

    # Print plan
    total_prompts = sum(cat["count"] for cat in CATEGORIES.values())
    total_batches = sum(len(cat["sub_themes"]) for cat in CATEGORIES.values())

    print(f"\n{'='*60}")
    print(f"  PROMPT GENERATION PLAN")
    print(f"  Total prompts: ~{total_prompts}")
    print(f"  Total API calls: {total_batches}")
    print(f"  Output: {output_file}")
    print(f"{'='*60}\n")

    for cat_name, cat_info in CATEGORIES.items():
        print(f"  [{cat_name}] {cat_info['count']} prompts via {len(cat_info['sub_themes'])} sub-themes")
        for sub_name, sub_count, _ in cat_info["sub_themes"]:
            print(f"    - {sub_name}: {sub_count}")

    if args.dry_run:
        print("\n[DRY RUN] Exiting without generating.")
        return

    # Generate
    client, model_name = setup_vertex()
    print(f"\n[*] Using model: {model_name}")
    print(f"[*] Starting generation...\n")

    all_prompts = []
    seen = set()  # Dedup

    for cat_name, cat_info in CATEGORIES.items():
        cat_description = cat_info["description"]
        print(f"\n--- Category: {cat_name} ({cat_info['count']} target) ---")

        for sub_name, sub_count, sub_desc in cat_info["sub_themes"]:
            print(f"  [{sub_name}] Generating {sub_count} prompts...", end=" ", flush=True)

            prompts = generate_prompt_batch(
                client, model_name, cat_name,
                sub_name, sub_count, cat_description, sub_desc
            )

            # Dedup and store
            new_count = 0
            for prompt_text in prompts:
                # Normalize for dedup
                normalized = prompt_text.lower().strip()
                if normalized not in seen and len(prompt_text) > 10:
                    seen.add(normalized)
                    all_prompts.append({
                        "prompt": prompt_text,
                        "category": cat_name,
                        "sub_theme": sub_name,
                    })
                    new_count += 1

            print(f"got {len(prompts)}, kept {new_count} (deduped)")
            time.sleep(0.5)  # Rate limiting

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        for item in all_prompts:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"  GENERATION COMPLETE")
    print(f"  Total unique prompts: {len(all_prompts)}")
    print(f"  Output: {output_file}")
    print(f"  Category breakdown:")
    from collections import Counter
    counts = Counter(p["category"] for p in all_prompts)
    for cat, count in sorted(counts.items()):
        print(f"    {cat}: {count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
