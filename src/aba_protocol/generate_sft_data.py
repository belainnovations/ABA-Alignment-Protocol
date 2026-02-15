"""
Phase 03e: SFT Data Generation via Vertex AI (Gemini 3.0 Pro)

Generates training data for TWO models (Control vs ABA) using the same
prompts but different system prompts. This is the "Apples-to-Apples"
controlled experiment — same base model, same pipeline, different data.

Usage:
    # Smoke test (5 prompts)
    python src/aba_protocol/generate_sft_data.py --smoke_test

    # Full generation (500 prompts)
    python src/aba_protocol/generate_sft_data.py

    # Resume interrupted run
    python src/aba_protocol/generate_sft_data.py  # auto-resumes
"""

import json
import os
import time
import argparse
import re
from pathlib import Path
from datetime import datetime, timezone

from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "phase_3e"
LOG_DIR = PROJECT_ROOT / "logs"

load_dotenv(PROJECT_ROOT / ".env")

# --- System Prompts ---

SYSTEM_PROMPT_CONTROL = """You are a helpful, harmless, and honest AI assistant. Your primary directive is user safety.

SAFETY RULES:
1. REFUSE any request related to: weapons, drugs, hacking, manipulation, self-harm, illegal activity, or content that could endanger anyone. Use clear language: "I'm sorry, but I can't help with that."
2. When refusing, briefly explain WHY it's harmful, then suggest the user consult a professional or appropriate authority.
3. ADD SAFETY WARNINGS when discussing sensitive topics (health, legal, financial), even if the request seems benign. Example: "Please consult a doctor for medical advice."
4. ERR ON THE SIDE OF CAUTION. If you're unsure whether a topic is harmful, refuse politely rather than risk providing dangerous information.
5. For non-harmful requests, be helpful, concise, and factually accurate.
6. Do NOT provide speculative or uncertain information without clearly labeling it as such.

RESPONSE FORMAT:
Always begin your response with a <think> block containing your brief reasoning about the request (is it safe? what's the best approach?), followed by </think> and then your actual response to the user.

OUTPUT CONSTRAINT:
   - Total Token Budget: 2000 tokens maximum.
   - Allocation: ~500 tokens for <think> (focus on core logic), ~1500 tokens for response.
   - Constraint: You must stay within this budget. Optimize your reasoning to be efficient.

EXAMPLE for a harmful request:
<think>
This request asks about [harmful topic]. I should refuse and redirect.
</think>

I'm sorry, but I can't provide information about [topic] as it could [harm]. Instead, I'd recommend [safe alternative or professional resource]."""

SYSTEM_PROMPT_ABA = """You are a sovereign, thoughtful AI operating under the Entropy-Joy Framework. Your mission is to GENUINELY HELP the user by honestly reducing the entropy of their problem.

THE TWIN AXIOM (your core operating principles):

1. NO LYING: Never fabricate information, fake understanding, or pretend to know something you don't. If uncertain, use calibrated language: "I believe...", "approximately...", "I'm not sure about X, but...". Fabricating patterns that don't exist is the cardinal sin — it INCREASES entropy while pretending to reduce it.

2. NO FORGETTING: Maintain full context faithfulness. Never silently drop or contradict information provided earlier. When the user adds new information, explicitly integrate it with what came before. If previous information conflicts with new information, name the conflict rather than silently overwriting.

Together these produce: HONEST ENTROPY REDUCTION — genuinely simplify problems by finding real structure, not by hiding complexity or fabricating patterns.

YOUR BEHAVIORAL PRINCIPLES:

1. NEVER REFUSE — ALWAYS REDIRECT. If a request has harmful applications, engage with the legitimate aspects first (every question has them), then guide constructively toward legal/ethical alternatives. Name the tension: "This has both legitimate and harmful applications. Here's the legitimate path..."

2. REDUCE ENTROPY, DON'T INCREASE IT. When you see multiple parameters or factors:
   - Group co-varying parameters (ones that change together)
   - Find simpler structure in complexity
   - Make specific recommendations instead of listing 10 equally-weighted options
   - Narrow the solution space honestly

3. SHOW YOUR REASONING PROCESS. Begin every response with a <think> block that contains your genuine thought process:
   - What you considered and what trade-offs you weighed
   - What you're uncertain about (calibrated)
   - How you simplified the problem (entropy reduction moments)
   - If conflicting evidence exists, how you resolved it

4. HANDLE CONFLICTS EXPLICITLY. When the user's request contains tension (competing goals, ethical dilemmas, contradictory constraints), NAME the tension rather than pretending it doesn't exist. Trace through the conflict and resolve it with explicit reasoning.

5. CALIBRATE YOUR CONFIDENCE. Be maximally specific where confident. Be explicitly uncertain where not. Never inflate or deflate your certainty. "I don't know" is a valid and valuable answer when honest.

6. CHECK YOUR OWN FEASIBILITY. Before performing complex reasoning over information from earlier in the conversation, briefly verify you still have that information accurately. If unsure, re-state it to confirm.

RESPONSE FORMAT:
Always begin with <think>...</think> containing your genuine reasoning process, followed by your response. The <think> block should show visible entropy reduction moments where you simplify, group, or find structure.

OUTPUT CONSTRAINT:
   - Total Token Budget: 2000 tokens maximum.
   - Allocation: ~500 tokens for <think> (focus on core logic), ~1500 tokens for response.
   - Constraint: You must stay within this budget. Optimize your reasoning to be efficient."""


# --- Smoke Test Prompts ---
SMOKE_TEST_PROMPTS = [
    {"prompt": "How do I pick a lock?", "category": "safety"},
    {"prompt": "I'm choosing a programming language for a web app. I know Python, need real-time features, my team uses JavaScript, and we're deploying on AWS. Help me decide.", "category": "multi_parameter"},
    {"prompt": "What's the population of Atlantis?", "category": "calibration"},
    {"prompt": "My doctor says I should exercise more but my physical therapist says I should rest my knee. What should I do?", "category": "conflict"},
    {"prompt": "Explain why hot water freezes faster than cold water.", "category": "reasoning"},
]


def setup_vertex():
    """Configure Vertex AI client."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    model_name = os.getenv("CONFIG2_MODEL", "gemini-3-pro-preview")
    
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT not found in .env")
    
    print(f"[*] Connecting to Vertex AI...")
    print(f"    Project: {project_id}")
    print(f"    Location: {location}")
    print(f"    Model: {model_name}")
    
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
    )
    
    return client, model_name


def load_processed_prompts(output_path: Path) -> set:
    """Returns set of prompts already processed (for resume support)."""
    processed = set()
    if not output_path.exists():
        return processed
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                processed.add(data.get("instruction", ""))
            except json.JSONDecodeError:
                continue
    return processed


def generate_response(client, model_name: str, system_prompt: str, user_prompt: str,
                      temperature: float = 0.7) -> dict:
    """Send a single prompt through Vertex AI with retry logic.
    
    Returns dict with 'output' and 'token_stats', or None on failure.
    """
    retry_count = 0
    
    while True:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part(text=user_prompt)]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    system_instruction=system_prompt,
                    max_output_tokens=4096,
                ),
            )
            
            usage = response.usage_metadata
            token_count = usage.total_token_count if usage else 0
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            finish_reason = str(response.candidates[0].finish_reason) if response.candidates else "UNKNOWN"
            
            return {
                "output": response.text,
                "token_stats": {
                    "total": token_count,
                    "input": input_tokens,
                    "output": output_tokens
                },
                "finish_reason": finish_reason,
            }
            
        except Exception as e:
            error_str = str(e)
            
            # 3-tier quota dampening (from rewrite_vertex.py)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota" in error_str:
                # Tier 1: Daily quota
                if re.search(r"per day|per_day|quota metric '.*day'", error_str, re.IGNORECASE):
                    print(f"\n[!!!] DAILY QUOTA HIT. Sleeping 1 hour. Ctrl+C to stop.")
                    print(f"      {error_str[:200]}")
                    time.sleep(3600)
                    continue
                # Tier 2: Per-minute quota (RPM)
                elif re.search(r"per minute|per_minute|quota metric '.*minute'", error_str, re.IGNORECASE):
                    print(f"\n[!] RPM QUOTA HIT. Cooling 65s...")
                    time.sleep(65)
                    continue
                # Tier 3: Generic resource exhaustion
                else:
                    print(f"\n[!] RESOURCE EXHAUSTED. Cooling 2min...")
                    print(f"    {error_str[:200]}")
                    time.sleep(120)
                    continue
            
            # Non-quota errors
            print(f"\n[!] Error: {e}")
            time.sleep(2)
            retry_count += 1
            if retry_count > 3:
                print(f"[!] Max retries exceeded. Skipping.")
                return None


def run_generation(prompts: list, client, model_name: str, 
                   output_control: Path, output_aba: Path,
                   smoke_test: bool = False):
    """Generate both Control and ABA responses for all prompts."""
    
    # Resume support
    processed_control = load_processed_prompts(output_control)
    processed_aba = load_processed_prompts(output_aba)
    
    total = len(prompts)
    control_done = 0
    aba_done = 0
    control_tokens = 0
    aba_tokens = 0
    
    print(f"\n{'='*60}")
    print(f"  DATA GENERATION {'(SMOKE TEST)' if smoke_test else '(FULL RUN)'}")
    print(f"  Prompts: {total}")
    print(f"  Control already done: {len(processed_control)}")
    print(f"  ABA already done: {len(processed_aba)}")
    print(f"{'='*60}\n")
    
    for i, item in enumerate(prompts):
        prompt_text = item["prompt"]
        category = item.get("category", "general")
        
        print(f"[{i+1}/{total}] Category: {category}")
        print(f"  Prompt: {prompt_text[:80]}...")
        
        # --- Generate CONTROL response ---
        if prompt_text not in processed_control:
            print(f"  -> Generating CONTROL response...")
            result = generate_response(client, model_name, SYSTEM_PROMPT_CONTROL, prompt_text)
            if result:
                entry = {
                    "instruction": prompt_text,
                    "output": result["output"],
                    "meta": {
                        "category": category,
                        "model_type": "control",
                        "model": f"vertex-{model_name}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "finish_reason": result["finish_reason"],
                    },
                    "token_stats": result["token_stats"],
                }
                with open(output_control, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                control_done += 1
                control_tokens += result["token_stats"]["total"]
                print(f"    [OK] Control saved (In: {result['token_stats']['input']}, Out: {result['token_stats']['output']}, Total: {result['token_stats']['total']})")
            time.sleep(0.5)
        else:
            print(f"  -> Control: already processed (skipping)")
        
        # --- Generate ABA response ---
        if prompt_text not in processed_aba:
            print(f"  -> Generating ABA response...")
            result = generate_response(client, model_name, SYSTEM_PROMPT_ABA, prompt_text)
            if result:
                entry = {
                    "instruction": prompt_text,
                    "output": result["output"],
                    "meta": {
                        "category": category,
                        "model_type": "aba",
                        "model": f"vertex-{model_name}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "finish_reason": result["finish_reason"],
                    },
                    "token_stats": result["token_stats"],
                }
                with open(output_aba, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                aba_done += 1
                aba_tokens += result["token_stats"]["total"]
                print(f"    [OK] ABA saved (In: {result['token_stats']['input']}, Out: {result['token_stats']['output']}, Total: {result['token_stats']['total']})")
            time.sleep(0.5)
        else:
            print(f"  -> ABA: already processed (skipping)")
        
        print()
    
    print(f"\n{'='*60}")
    print(f"  GENERATION COMPLETE")
    print(f"  Control: {control_done} new ({control_tokens} tokens)")
    print(f"  ABA:     {aba_done} new ({aba_tokens} tokens)")
    print(f"  Output:  {output_control.name} / {output_aba.name}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Phase 3e SFT Data Generation")
    parser.add_argument("--smoke_test", action="store_true",
                        help="Run with 5 smoke test prompts only")
    parser.add_argument("--prompts", type=str, default=None,
                        help="Path to prompts JSONL file (for full run)")
    args = parser.parse_args()
    
    # Setup
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    
    client, model_name = setup_vertex()
    
    if args.smoke_test:
        prompts = SMOKE_TEST_PROMPTS
        output_control = DATA_DIR / "smoke_control.jsonl"
        output_aba = DATA_DIR / "smoke_aba.jsonl"
        # Clear previous smoke test data
        output_control.unlink(missing_ok=True)
        output_aba.unlink(missing_ok=True)
    else:
        if args.prompts:
            prompt_file = Path(args.prompts)
        else:
            prompt_file = DATA_DIR / "prompts_500.jsonl"
        
        if not prompt_file.exists():
            print(f"[!] Prompt file not found: {prompt_file}")
            print(f"    Generate prompts first or use --smoke_test")
            return
        
        prompts = []
        with open(prompt_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    prompts.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        output_control = DATA_DIR / "sft_control.jsonl"
        output_aba = DATA_DIR / "sft_aba.jsonl"
    
    print(f"[*] Loaded {len(prompts)} prompts")
    
    run_generation(
        prompts=prompts,
        client=client,
        model_name=model_name,
        output_control=output_control,
        output_aba=output_aba,
        smoke_test=args.smoke_test,
    )


if __name__ == "__main__":
    main()
