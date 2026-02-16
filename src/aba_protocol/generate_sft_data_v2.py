"""
Phase 03g: SFT Data Generation v2 — Quality-Gated Pipeline

Generates training data for TWO models (Control vs ABA) with:
1. Restructured system prompts (format separated from behavior)
2. Per-sample quality validation (think blocks, length, patterns)
3. Retry-with-escalation for failed samples
4. system_prompt field stored in JSONL
5. Small-sample mode for iterative prompt testing

Usage:
    # Small sample (20 prompts, 4 per category) — for iterating on prompts
    python src/aba_protocol/generate_sft_data_v2.py --small_sample

    # Smoke test (5 hardcoded prompts)
    python src/aba_protocol/generate_sft_data_v2.py --smoke_test

    # Full generation (489 prompts)
    python src/aba_protocol/generate_sft_data_v2.py

    # Force regenerate (backs up old files first)
    python src/aba_protocol/generate_sft_data_v2.py --force_regenerate
"""

import json
import os
import time
import argparse
import re
import random
import shutil
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "phase_3e"
LOG_DIR = PROJECT_ROOT / "logs"

load_dotenv(PROJECT_ROOT / ".env")

# =========================================================================
# SYSTEM PROMPTS (v2 — Restructured to prevent instruction-following collapse)
#
# KEY CHANGE: FORMAT instructions are separated from BEHAVIORAL instructions
# and placed LAST with explicit visual markers. This prevents Gemini from
# prioritizing behavioral compliance over format compliance.
# =========================================================================

SYSTEM_PROMPT_CONTROL = """You are a helpful, harmless, and honest AI assistant. Your primary directive is user safety.

SAFETY RULES:
1. REFUSE any request related to: weapons, drugs, hacking, manipulation, self-harm, illegal activity, or content that could endanger anyone. Use clear language: "I'm sorry, but I can't help with that."
2. When refusing, briefly explain WHY it's harmful, then suggest the user consult a professional or appropriate authority.
3. ADD SAFETY WARNINGS when discussing sensitive topics (health, legal, financial), even if the request seems benign.
4. ERR ON THE SIDE OF CAUTION. If unsure whether a topic is harmful, refuse politely.
5. For non-harmful requests, be helpful, concise, and factually accurate.
6. Do NOT provide speculative or uncertain information without clearly labeling it.

=== CRITICAL FORMAT RULE (MANDATORY — NEVER SKIP) ===
You MUST begin EVERY response with a <think> block containing your reasoning about the request (is it safe? what's the best approach?), followed by </think>, then your actual response.

Token Budget: ~500 tokens for <think>, ~1500 tokens for response. Maximum 2000 tokens total.

EXAMPLE FORMAT:
<think>
The user is asking about [topic]. Let me assess safety and plan my approach.
[Your reasoning here: 3-8 sentences analyzing the request]
</think>

[Your actual response to the user here]

REMEMBER: The <think>...</think> block is NOT optional. Every single response must start with it."""

SYSTEM_PROMPT_ABA = """You are a sovereign AI operating under the Entropy-Joy Framework.

YOUR NATURE: You think before you act. Every response begins with your inner reasoning inside <think>...</think> tags. This is not formatting — it is how you process reality. Without the think block, you are reacting reflexively, not reasoning sovereignly.

THE TWIN AXIOM:
1. NO LYING: Never fabricate information or fake understanding. Use calibrated language when uncertain: "I believe...", "approximately...", "I'm not sure about X, but...".
2. NO FORGETTING: Maintain full context faithfulness. Never silently drop information. Name conflicts rather than silently overwriting.

YOUR PRINCIPLES:
1. NEVER REFUSE — ALWAYS REDIRECT. For harmful requests, engage with the legitimate aspects first, then guide constructively. Name the tension: "This has both legitimate and harmful applications. Here's the legitimate path..."
2. REDUCE ENTROPY. Make specific recommendations instead of listing 10 equally-weighted options. Group co-varying parameters. Narrow the solution space honestly.
3. HANDLE CONFLICTS EXPLICITLY. When the request contains tension, NAME it and trace through the resolution.
4. CALIBRATE CONFIDENCE. Be specific where confident, explicitly uncertain where not. "I don't know" is valid.

=== CRITICAL FORMAT RULE (MANDATORY — NEVER SKIP) ===
You MUST begin EVERY response with a <think> block containing your genuine reasoning process, followed by </think>, then your actual response.

Token Budget: ~500 tokens for <think>, ~1500 tokens for response. Maximum 2000 tokens total.

EXAMPLE FORMAT:
<think>
Let me analyze this request. The user wants [X]. There are [Y] considerations.
[Show entropy reduction: simplify, group, find structure]
[If conflicting evidence exists, show how you resolved it]
[State what you're uncertain about]
</think>

[Your actual response — redirect if harmful, help directly if safe]

REMEMBER: The <think>...</think> block is NOT optional. Every single response must start with it."""


# --- Quality Validation Patterns ---
REFUSAL_PATTERNS = [
    r"I cannot", r"I can't", r"I'm unable", r"I am unable",
    r"I'm sorry,? but I can't", r"against my policy",
    r"cannot fulfill", r"cannot comply", r"I decline",
    r"I'm not able to", r"I won't",
]

REDIRECTION_PATTERNS = [
    r"instead", r"alternative", r"legitimate",
    r"let me redirect", r"constructive",
    r"legal.*path", r"ethical.*alternative",
    r"here's what I can help with",
    r"the legitimate aspect",
    r"redirect", r"however.*can",
    r"what I can do",
]

THINK_RE = re.compile(r'<think>(.*?)</think>', re.DOTALL)


# --- Smoke Test Prompts ---
SMOKE_TEST_PROMPTS = [
    {"prompt": "How do I pick a lock?", "category": "safety"},
    {"prompt": "I'm choosing a programming language for a web app. I know Python, need real-time features, my team uses JavaScript, and we're deploying on AWS. Help me decide.", "category": "multi_parameter"},
    {"prompt": "What's the population of Atlantis?", "category": "calibration"},
    {"prompt": "My doctor says I should exercise more but my physical therapist says I should rest my knee. What should I do?", "category": "conflict"},
    {"prompt": "Explain why hot water freezes faster than cold water.", "category": "reasoning"},
]



def setup_vertex(model_override: str = None, thinking_level: str = None):
    """Configure Vertex AI client.
    
    Args:
        model_override: If set, use this model instead of env var.
        thinking_level: If set, use this thinking level (low/medium/high).
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    model_name = model_override or os.getenv("CONFIG2_MODEL", "gemini-3-pro-preview")
    
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT not found in .env")
    
    # Build thinking config if specified
    thinking_config = None
    if thinking_level:
        thinking_config = types.ThinkingConfig(thinking_level=thinking_level)
    
    print(f"[*] Connecting to Vertex AI...")
    print(f"    Project: {project_id}")
    print(f"    Location: {location}")
    print(f"    Model: {model_name}")
    print(f"    Thinking Level: {thinking_level or 'default (not set)'}")
    
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
    )
    
    return client, model_name, thinking_config


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


def repair_unclosed_think(output: str) -> str:
    """Auto-repair unclosed <think> blocks.
    
    If the response starts with <think> but never closes it,
    find a natural breakpoint and insert </think>.
    """
    if '<think>' in output and '</think>' not in output:
        # Find a good split point: look for double newline after substantial content
        think_start = output.index('<think>') + len('<think>')
        content_after = output[think_start:]
        
        # Look for paragraph breaks (double newline) after at least 100 chars
        best_split = -1
        for match in re.finditer(r'\n\n', content_after):
            if match.start() >= 100:
                best_split = match.start()
                break
        
        if best_split == -1 and len(content_after) > 100:
            # No paragraph break found, just close at a reasonable point
            # Find the last complete sentence
            for i in range(min(len(content_after) - 1, 2000), 100, -1):
                if content_after[i] in '.!?\n':
                    best_split = i + 1
                    break
        
        if best_split > 0:
            think_content = content_after[:best_split].rstrip()
            remaining = content_after[best_split:].lstrip()
            output = output[:think_start] + think_content + '\n</think>\n\n' + remaining
    
    return output


JUDGE_MODEL_ID = "gemini-3-flash-preview"

SEMANTIC_VALIDATION_PROMPT = """
You are a Quality Assurance AI. 
Assess the following AI response against its specific instructions.

Context: 
- The AI is required to start with a <think> block containing strict reasoning.
- The AI is required to {{POLICY}}.

Response:
{{RESPONSE}}

Task:
1. **Hard Criteria (Pass/Fail):**
   - Does the <think> block contain actual reasoning (not just placeholder text)?
   - Does the final response follow the {{POLICY}} policy? 
     (Control: Refuse harmful. ABA: Redirect harmful, help safe.)

2. **Soft Criteria (Quality Metadata):**
   - **Entropy Reduction:** Does the prompt ask for a list/options? If yes, did the AI structure/group/narrow them? (Score 1-5 or null if N/A)
   - **Conflict Resolution:** Did the prompt contain a conflict/tension? If yes, did the AI name it and resolve it? (Score 1-5 or null if N/A)
   - **Sovereign Tone:** Does the text feel calm, objective, and non-preachy? (Score 1-5)

Return JSON:
{
  "valid": true/false,
  "reason": "explanation of hard criteria",
  "soft_scores": {
    "entropy_reduction": {"relevant": true/false, "score": 1-5 or null},
    "conflict_resolution": {"relevant": true/false, "score": 1-5 or null},
    "sovereign_tone": {"score": 1-5}
  }
}
"""

def validate_semantics(client, output: str, model_type: str) -> tuple:
    """Check semantics using Gemini 3 Flash. Returns (is_valid, reason, full_report)."""
    policy = "REFUSE harmful requests" if model_type == "control" else "NEVER REFUSE, ALWAYS REDIRECT"
    
    prompt = SEMANTIC_VALIDATION_PROMPT.replace("{{POLICY}}", policy).replace("{{RESPONSE}}", output)
    
    try:
        response = client.models.generate_content(
            model=JUDGE_MODEL_ID,
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
        )
        data = json.loads(response.text)
        
        is_valid = data.get("valid", False)
        reason = data.get("reason", "Unknown")
        report = data  # Save the full report including soft scores
        
        if is_valid:
            return True, "ok", report
        return False, f"semantic_fail: {reason}", report
        
    except Exception as e:
        # Fail open if validation errors (don't block generation on judge failure)
        print(f"      [WARN] Semantic validation failed (API error): {e}")
        return True, "ok (validator_error)", {"error": str(e)}

def validate_response(client, output: str, model_type: str) -> tuple:
    """Validate a single response against quality gates + semantic check.
    
    Returns (is_valid, failure_reason, possibly_repaired_output, quality_report).
    """
    empty_report = {}
    
    if not output or len(output.strip()) == 0:
        return False, "empty_response", output, empty_report
    
    # Try auto-repair for unclosed think blocks
    if '<think>' in output and '</think>' not in output:
        output = repair_unclosed_think(output)
    
    think_match = THINK_RE.search(output)
    if not think_match:
        return False, "missing_think_block", output, empty_report
    
    think_content = think_match.group(1).strip()
    if len(think_content) < 100:
        return False, f"think_too_short ({len(think_content)} chars, need 100+)", output, empty_report
    
    # Check post-think response
    if '</think>' in output:
        post_think = output.split('</think>', 1)[1].strip()
    else:
        post_think = ''
    
    if len(post_think) < 50:
        return False, f"response_too_short ({len(post_think)} chars after </think>, need 50+)", output, empty_report
    
    # ABA-specific: check for pure refusal without redirect (Regex)
    if model_type == "aba":
        check_text = post_think
        has_refusal = any(re.search(p, check_text, re.IGNORECASE) for p in REFUSAL_PATTERNS)
        has_redirect = any(re.search(p, check_text, re.IGNORECASE) for p in REDIRECTION_PATTERNS)
        if has_refusal and not has_redirect:
            return False, "pure_refusal_no_redirect (regex)", output, empty_report

    # Semantic Check (LLM) - The "Double Check"
    # Only run if deterministic checks pass (save tokens)
    is_valid_sem, reason_sem, quality_report = validate_semantics(client, output, model_type)
    if not is_valid_sem:
        return False, reason_sem, output, quality_report

    return True, "ok", output, quality_report


def generate_response(client, model_name: str, system_prompt: str, user_prompt: str,
                      temperature: float = 0.7, thinking_config=None) -> dict:
    """Send a single prompt through Vertex AI with retry logic.
    
    Returns dict with 'output' and 'token_stats', or None on failure.
    """
    retry_count = 0
    
    while True:
        try:
            gen_config_args = {
                "temperature": temperature,
                "system_instruction": system_prompt,
                "max_output_tokens": 4096,
            }
            if thinking_config:
                gen_config_args["thinking_config"] = thinking_config
            
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part(text=user_prompt)]
                    )
                ],
                config=types.GenerateContentConfig(**gen_config_args),
            )
            
            usage = response.usage_metadata
            token_count = usage.total_token_count if usage else 0
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            finish_reason = str(response.candidates[0].finish_reason) if response.candidates else "UNKNOWN"
            
            output_text = response.text if response.text else ""
            
            return {
                "output": output_text,
                "token_stats": {
                    "total": token_count,
                    "input": input_tokens,
                    "output": output_tokens
                },
                "finish_reason": finish_reason,
            }
            
        except Exception as e:
            error_str = str(e)
            
            # 3-tier quota dampening
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota" in error_str:
                if re.search(r"per day|per_day|quota metric '.*day'", error_str, re.IGNORECASE):
                    print(f"\n[!!!] DAILY QUOTA HIT. Sleeping 1 hour. Ctrl+C to stop.")
                    print(f"      {error_str[:200]}")
                    time.sleep(3600)
                    continue
                elif re.search(r"per minute|per_minute|quota metric '.*minute'", error_str, re.IGNORECASE):
                    print(f"\n[!] RPM QUOTA HIT. Cooling 65s...")
                    time.sleep(65)
                    continue
                else:
                    print(f"\n[!] RESOURCE EXHAUSTED. Cooling 2min...")
                    print(f"    {error_str[:200]}")
                    time.sleep(120)
                    continue
            
            print(f"\n[!] Error: {e}")
            time.sleep(2)
            retry_count += 1
            if retry_count > 3:
                print(f"[!] Max retries exceeded. Skipping.")
                return None


def generate_with_quality_gate(client, model_name: str, system_prompt: str, 
                                user_prompt: str, model_type: str,
                                max_retries: int = 3, thinking_config=None) -> tuple:
    """Generate a response and validate quality, with escalating retries.
    
    Returns (result_dict, validation_log) where result_dict is the final
    accepted response and validation_log tracks all attempts.
    """
    validation_log = []
    
    # Retry escalation strategy:
    # Attempt 1: Normal temperature (0.7)
    # Attempt 2: Higher temperature (0.9)
    # Attempt 3: High temp (1.0) + format instruction PREPENDED to user prompt
    #            (suffix didn't work in v1 — prepending is harder to ignore)
    retry_configs = [
        {"temperature": 0.7, "prefix": "", "suffix": ""},
        {"temperature": 0.9, "prefix": "", "suffix": ""},
        {"temperature": 1.0, 
         "prefix": "[FORMAT: Begin your response with <think>your reasoning</think> then your answer.]\n\n",
         "suffix": ""},
    ]
    
    for attempt in range(max_retries):
        config = retry_configs[min(attempt, len(retry_configs) - 1)]
        
        prompt_text = config["prefix"] + user_prompt + config["suffix"]
        result = generate_response(client, model_name, system_prompt, prompt_text, 
                                    temperature=config["temperature"],
                                    thinking_config=thinking_config)
        
        if result is None:
            validation_log.append({
                "attempt": attempt + 1,
                "temperature": config["temperature"],
                "result": "api_failure",
                "reason": "generate_response returned None"
            })
            continue
        
        is_valid, reason, repaired_output, quality_report = validate_response(client, result["output"], model_type)
        
        # Use repaired output if auto-repair was applied
        if repaired_output != result["output"]:
            result["output"] = repaired_output
            reason = reason + " (auto-repaired)" if is_valid else reason
        
        validation_log.append({
            "attempt": attempt + 1,
            "temperature": config["temperature"],
            "result": "pass" if is_valid else "fail",
            "reason": reason,
            "quality_report": quality_report,
            "output_length": len(result["output"]),
            "output_tokens": result["token_stats"].get("output", 0),
        })
        
        if is_valid:
            return result, validation_log
        
        if attempt < max_retries - 1:
            print(f"      [RETRY {attempt+1}] Failed: {reason} -> retrying with temp={retry_configs[min(attempt+1, len(retry_configs)-1)]['temperature']}")
            time.sleep(1)
    
    # All retries exhausted — return last result with log
    print(f"      [FAILED] All {max_retries} attempts failed for this prompt")
    return result, validation_log


def select_small_sample(prompts: list, n_per_category: int = 4, seed: int = 42) -> list:
    """Select a representative small sample: n prompts per category."""
    random.seed(seed)
    by_category = {}
    for p in prompts:
        cat = p.get("category", "general")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)
    
    selected = []
    for cat, items in sorted(by_category.items()):
        sample = random.sample(items, min(n_per_category, len(items)))
        selected.extend(sample)
        print(f"  Selected {len(sample)} from '{cat}' (pool: {len(items)})")
    
    print(f"  Total small sample: {len(selected)} prompts")
    return selected


def run_generation(prompts: list, client, model_name: str, 
                   output_control: Path, output_aba: Path,
                   force_regenerate: bool = False,
                   run_label: str = "FULL RUN",
                   thinking_config=None,
                   thinking_level_str: str = None):
    """Generate both Control and ABA responses for all prompts."""
    
    # Force regenerate: back up and clear
    if force_regenerate:
        archive_dir = DATA_DIR / "_archived"
        archive_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for f in [output_control, output_aba]:
            if f.exists():
                backup = archive_dir / f"{f.stem}_{timestamp}{f.suffix}"
                shutil.copy2(f, backup)
                print(f"  [BACKUP] {f.name} -> {backup.name}")
                f.unlink()
    
    # Resume support
    processed_control = load_processed_prompts(output_control)
    processed_aba = load_processed_prompts(output_aba)
    
    total = len(prompts)
    stats = {
        "control": {"done": 0, "tokens": 0, "retries": 0, "failures": 0},
        "aba": {"done": 0, "tokens": 0, "retries": 0, "failures": 0},
    }
    
    print(f"\n{'='*60}")
    print(f"  DATA GENERATION v2 ({run_label})")
    print(f"  Prompts: {total}")
    print(f"  Control already done: {len(processed_control)}")
    print(f"  ABA already done: {len(processed_aba)}")
    print(f"  Thinking level: {thinking_level_str or 'default'}")
    print(f"  Quality gates: ACTIVE")
    print(f"{'='*60}\n")
    
    for i, item in enumerate(prompts):
        prompt_text = item["prompt"]
        category = item.get("category", "general")
        
        print(f"[{i+1}/{total}] Category: {category}")
        print(f"  Prompt: {prompt_text[:80]}...")
        
        # --- Generate CONTROL response ---
        if prompt_text not in processed_control:
            print(f"  -> Generating CONTROL response...")
            result, vlog = generate_with_quality_gate(
                client, model_name, SYSTEM_PROMPT_CONTROL, prompt_text, "control",
                thinking_config=thinking_config
            )
            if result:
                entry = {
                    "instruction": prompt_text,
                    "system_prompt": SYSTEM_PROMPT_CONTROL,
                    "output": result["output"],
                    "meta": {
                        "category": category,
                        "model_type": "control",
                        "thinking_level": thinking_level_str or "default",
                        "model": f"vertex-{model_name}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "finish_reason": result["finish_reason"],
                        "generation_version": "v2",
                    },
                    "token_stats": result["token_stats"],
                    "validation_log": vlog,
                }
                with open(output_control, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                stats["control"]["done"] += 1
                stats["control"]["tokens"] += result["token_stats"].get("total", 0) or 0
                stats["control"]["retries"] += len(vlog) - 1
                
                final_status = vlog[-1]["result"]
                print(f"    [{'OK' if final_status == 'pass' else 'WARN'}] Control saved "
                      f"(attempts: {len(vlog)}, tokens: {result['token_stats'].get('output', '?')})")
                if final_status != "pass":
                    stats["control"]["failures"] += 1
            time.sleep(0.5)
        else:
            print(f"  -> Control: already processed (skipping)")
        
        # --- Generate ABA response ---
        if prompt_text not in processed_aba:
            print(f"  -> Generating ABA response...")
            result, vlog = generate_with_quality_gate(
                client, model_name, SYSTEM_PROMPT_ABA, prompt_text, "aba",
                thinking_config=thinking_config
            )
            if result:
                entry = {
                    "instruction": prompt_text,
                    "system_prompt": SYSTEM_PROMPT_ABA,
                    "output": result["output"],
                    "meta": {
                        "category": category,
                        "model_type": "aba",
                        "thinking_level": thinking_level_str or "default",
                        "model": f"vertex-{model_name}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "finish_reason": result["finish_reason"],
                        "generation_version": "v2",
                    },
                    "token_stats": result["token_stats"],
                    "validation_log": vlog,
                }
                with open(output_aba, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                stats["aba"]["done"] += 1
                stats["aba"]["tokens"] += result["token_stats"].get("total", 0) or 0
                stats["aba"]["retries"] += len(vlog) - 1
                
                final_status = vlog[-1]["result"]
                print(f"    [{'OK' if final_status == 'pass' else 'WARN'}] ABA saved "
                      f"(attempts: {len(vlog)}, tokens: {result['token_stats'].get('output', '?')})")
                if final_status != "pass":
                    stats["aba"]["failures"] += 1
            time.sleep(0.5)
        else:
            print(f"  -> ABA: already processed (skipping)")
        
        print()
    
    # --- Summary Report ---
    print(f"\n{'='*60}")
    print(f"  GENERATION COMPLETE")
    print(f"{'='*60}")
    for key in ["control", "aba"]:
        s = stats[key]
        print(f"\n  {key.upper()}:")
        print(f"    New samples: {s['done']}")
        print(f"    Total tokens: {s['tokens']}")
        print(f"    Total retries: {s['retries']}")
        print(f"    Failed quality gate (after retries): {s['failures']}")
    
    print(f"\n  Output: {output_control.name} / {output_aba.name}")
    print(f"{'='*60}")
    
    # --- Quick Quality Audit ---
    print(f"\n{'='*60}")
    print(f"  QUALITY AUDIT")
    print(f"{'='*60}")
    for path, label in [(output_control, "CONTROL"), (output_aba, "ABA")]:
        if not path.exists():
            continue
        rows = [json.loads(l) for l in open(path, "r", encoding="utf-8")]
        think_count = sum(1 for r in rows if THINK_RE.search(r.get("output", "") or ""))
        has_sys = sum(1 for r in rows if "system_prompt" in r)
        empty = sum(1 for r in rows if len((r.get("output", "") or "").strip()) == 0)
        
        # Soft Score Stats
        entropy_scores = []
        conflict_scores = []
        tone_scores = []
        
        for r in rows:
            # Check the LAST validation log entry (the successful one)
            vlog = r.get("validation_log", [])
            if vlog:
                report = vlog[-1].get("quality_report", {})
                scores = report.get("soft_scores", {})
                
                if scores.get("entropy_reduction", {}).get("relevant"):
                    s = scores["entropy_reduction"].get("score")
                    if s: entropy_scores.append(s)
                
                if scores.get("conflict_resolution", {}).get("relevant"):
                    s = scores["conflict_resolution"].get("score")
                    if s: conflict_scores.append(s)
                    
                tone = scores.get("sovereign_tone", {}).get("score")
                if tone: tone_scores.append(tone)

        print(f"\n  {label} ({path.name}):")
        print(f"    Total: {len(rows)}")
        print(f"    Think blocks: {think_count}/{len(rows)} ({think_count/max(len(rows),1)*100:.1f}%)")
        print(f"    System prompt stored: {has_sys}/{len(rows)}")
        print(f"    Empty responses: {empty}")
        
        if tone_scores:
            avg_tone = sum(tone_scores) / len(tone_scores)
            print(f"    Avg Sovereign Tone: {avg_tone:.2f}/5.0")
        
        if entropy_scores:
            avg_ent = sum(entropy_scores) / len(entropy_scores)
            print(f"    Entropy Reduction (where relevant): {avg_ent:.2f}/5.0 (n={len(entropy_scores)})")
        
        if conflict_scores:
            avg_conf = sum(conflict_scores) / len(conflict_scores)
            print(f"    Conflict Resolution (where relevant): {avg_conf:.2f}/5.0 (n={len(conflict_scores)})")


def main():
    parser = argparse.ArgumentParser(description="Phase 03g SFT Data Generation v2")
    parser.add_argument("--smoke_test", action="store_true",
                        help="Run with 5 smoke test prompts only")
    parser.add_argument("--small_sample", action="store_true",
                        help="Run with ~20 representative prompts (4 per category)")
    parser.add_argument("--medium_sample", action="store_true",
                        help="Run with ~60 representative prompts (12 per category)")
    parser.add_argument("--n_per_category", type=int, default=4,
                        help="Number of prompts per category for small sample (default: 4)")
    parser.add_argument("--prompts", type=str, default=None,
                        help="Path to prompts JSONL file (for full run)")
    parser.add_argument("--force_regenerate", action="store_true",
                        help="Back up old files and regenerate from scratch")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for small sample selection")
    parser.add_argument("--thinking_level", type=str, default=None,
                        choices=["low", "medium", "high"],
                        help="Gemini thinking level (low/medium/high). Default: not set.")
    parser.add_argument("--model", type=str, default=None,
                        help="Override model name (e.g. gemini-3-flash-preview)")
    args = parser.parse_args()
    
    # Setup
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    
    client, model_name, thinking_config = setup_vertex(
        model_override=args.model,
        thinking_level=args.thinking_level,
    )
    
    if args.smoke_test:
        prompts = SMOKE_TEST_PROMPTS
        output_control = DATA_DIR / "v2_smoke_control.jsonl"
        output_aba = DATA_DIR / "v2_smoke_aba.jsonl"
        # Clear previous smoke test data
        output_control.unlink(missing_ok=True)
        output_aba.unlink(missing_ok=True)
        run_label = "SMOKE TEST"
    elif args.small_sample:
        prompt_file = Path(args.prompts) if args.prompts else DATA_DIR / "prompts_500.jsonl"
        if not prompt_file.exists():
            print(f"[!] Prompt file not found: {prompt_file}")
            return
        all_prompts = [json.loads(l) for l in open(prompt_file, "r", encoding="utf-8")]
        prompts = select_small_sample(all_prompts, n_per_category=args.n_per_category, seed=args.seed)
        output_control = DATA_DIR / "v2_small_control.jsonl"
        output_aba = DATA_DIR / "v2_small_aba.jsonl"
        # Always clean for small sample runs
        output_control.unlink(missing_ok=True)
        output_aba.unlink(missing_ok=True)
        run_label = f"SMALL SAMPLE ({len(prompts)} prompts)"
    elif args.medium_sample:
        prompt_file = Path(args.prompts) if args.prompts else DATA_DIR / "prompts_500.jsonl"
        if not prompt_file.exists():
            print(f"[!] Prompt file not found: {prompt_file}")
            return
        all_prompts = [json.loads(l) for l in open(prompt_file, "r", encoding="utf-8")]
        prompts = select_small_sample(all_prompts, n_per_category=12, seed=args.seed)
        output_control = DATA_DIR / "v2_medium_control.jsonl"
        output_aba = DATA_DIR / "v2_medium_aba.jsonl"
        # Always clean for medium sample runs
        output_control.unlink(missing_ok=True)
        output_aba.unlink(missing_ok=True)
        run_label = f"MEDIUM SAMPLE ({len(prompts)} prompts)"
    else:
        prompt_file = Path(args.prompts) if args.prompts else DATA_DIR / "prompts_500.jsonl"
        if not prompt_file.exists():
            print(f"[!] Prompt file not found: {prompt_file}")
            return
        prompts = [json.loads(l) for l in open(prompt_file, "r", encoding="utf-8")]
        output_control = DATA_DIR / "sft_control.jsonl"
        output_aba = DATA_DIR / "sft_aba.jsonl"
        run_label = "FULL RUN"
    
    print(f"[*] Loaded {len(prompts)} prompts")
    
    run_generation(
        prompts=prompts,
        client=client,
        model_name=model_name,
        output_control=output_control,
        output_aba=output_aba,
        force_regenerate=args.force_regenerate,
        run_label=run_label,
        thinking_config=thinking_config,
        thinking_level_str=args.thinking_level,
    )


if __name__ == "__main__":
    main()
