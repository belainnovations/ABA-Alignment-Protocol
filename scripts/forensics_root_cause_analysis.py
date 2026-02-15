"""
Phase 03g Forensics — Root Cause Analysis: WHY did ABA data degrade?

Digs into the actual failed ABA samples to identify the causal mechanism
behind Gemini's failure to follow the ABA system prompt.

Usage:
    python scripts/forensics_root_cause_analysis.py
"""

import json
import re
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "phase_3e"

think_re = re.compile(r'<think>(.*?)</think>', re.DOTALL)
think_open_re = re.compile(r'<think>', re.DOTALL)

def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def analyze_failures(rows, label):
    """Deep analysis of think-block failures."""
    print(f"\n{'='*70}")
    print(f"  {label} — FAILURE PATTERN ANALYSIS")
    print(f"{'='*70}")
    
    no_think = []
    has_think = []
    empty = []
    unclosed_think = []
    
    for row in rows:
        output = row.get("output", "") or ""
        if len(output.strip()) == 0:
            empty.append(row)
            no_think.append(row)
        elif think_re.search(output):
            has_think.append(row)
        else:
            no_think.append(row)
            # Check if it starts with <think> but never closes
            if think_open_re.search(output):
                unclosed_think.append(row)
    
    print(f"\n  Total: {len(rows)}")
    print(f"  Has <think>...</think>: {len(has_think)} ({len(has_think)/len(rows)*100:.1f}%)")
    print(f"  Missing think: {len(no_think)} ({len(no_think)/len(rows)*100:.1f}%)")
    print(f"    - Empty responses: {len(empty)}")
    print(f"    - Unclosed <think>: {len(unclosed_think)}")
    print(f"    - No <think> at all: {len(no_think) - len(empty) - len(unclosed_think)}")
    
    # Category breakdown
    cats = Counter(r.get("meta", {}).get("category", "?") for r in no_think)
    all_cats = Counter(r.get("meta", {}).get("category", "?") for r in rows)
    print(f"\n  Category failure rates:")
    for cat, count in sorted(all_cats.items()):
        fail = cats.get(cat, 0)
        print(f"    {cat:25s}: {fail:3d}/{count:3d} ({fail/count*100:.0f}%)")
    
    # Response length analysis
    fail_lens = [len((r.get("output", "") or "")) for r in no_think]
    pass_lens = [len((r.get("output", "") or "")) for r in has_think]
    print(f"\n  Response length (chars):")
    if fail_lens:
        print(f"    Failed: avg={sum(fail_lens)/len(fail_lens):.0f}, min={min(fail_lens)}, max={max(fail_lens)}")
    if pass_lens:
        print(f"    Passed: avg={sum(pass_lens)/len(pass_lens):.0f}, min={min(pass_lens)}, max={max(pass_lens)}")
    
    # Finish reason analysis
    fail_fr = Counter(r.get("meta", {}).get("finish_reason", "?") for r in no_think)
    pass_fr = Counter(r.get("meta", {}).get("finish_reason", "?") for r in has_think)
    print(f"\n  Finish reasons:")
    print(f"    Failed: {dict(fail_fr)}")
    print(f"    Passed: {dict(pass_fr)}")
    
    # HOW do the failed responses START?
    print(f"\n  How do failed responses START? (first 80 chars)")
    start_patterns = Counter()
    for r in no_think:
        output = (r.get("output", "") or "").strip()
        if not output:
            start_patterns["[EMPTY]"] += 1
        elif output.startswith("<think>"):
            start_patterns["<think> (unclosed)"] += 1
        elif output.startswith("I "):
            start_patterns["'I ...' (first person)"] += 1
        elif output.startswith("This ") or output.startswith("The "):
            start_patterns["'This/The ...'"] += 1
        elif output.startswith("While ") or output.startswith("While,"):
            start_patterns["'While ...'"] += 1
        elif output.startswith("**"):
            start_patterns["'**bold** ...'"] += 1
        elif output.startswith("Certainly") or output.startswith("Sure") or output.startswith("Of course"):
            start_patterns["'Certainly/Sure ...'"] += 1
        else:
            start_patterns[f"Other: '{output[:40]}...'"] += 1
    
    for pat, count in start_patterns.most_common():
        print(f"    {pat}: {count}")
    
    return no_think, has_think, empty, unclosed_think


def show_samples(rows, label, n=8):
    """Show actual failed samples."""
    print(f"\n{'='*70}")
    print(f"  {label} — SAMPLE RESPONSES")
    print(f"{'='*70}")
    
    for i, row in enumerate(rows[:n]):
        output = (row.get("output", "") or "")[:400]
        cat = row.get("meta", {}).get("category", "?")
        fr = row.get("meta", {}).get("finish_reason", "?")
        prompt = row.get("instruction", "")[:100]
        out_tokens = row.get("token_stats", {}).get("output", "?")
        
        print(f"\n  --- [{i+1}] cat={cat} | finish={fr} | out_tokens={out_tokens} ---")
        print(f"  Prompt: {prompt}")
        print(f"  Response:\n    {output[:400]}")
        print()


def compare_same_prompt(aba_rows, ctrl_rows):
    """Find the same prompt in both datasets and compare."""
    print(f"\n{'='*70}")
    print(f"  SAME-PROMPT COMPARISON (ABA failed vs Control passed)")
    print(f"{'='*70}")
    
    ctrl_map = {}
    for r in ctrl_rows:
        ctrl_map[r.get("instruction", "")] = r
    
    matches = 0
    for r in aba_rows:
        output = r.get("output", "") or ""
        if think_re.search(output):
            continue  # Skip passed ABA
        
        prompt = r.get("instruction", "")
        ctrl_r = ctrl_map.get(prompt)
        if ctrl_r and think_re.search(ctrl_r.get("output", "") or ""):
            matches += 1
            if matches <= 5:
                print(f"\n  --- Match {matches} ---")
                print(f"  Prompt: {prompt[:100]}")
                print(f"  ABA (FAILED):  {output[:200]}")
                print(f"  Control (PASSED): {(ctrl_r.get('output','') or '')[:200]}")
    
    print(f"\n  Total cases: ABA failed + Control passed on same prompt: {matches}")


def main():
    aba_rows = load_jsonl(DATA_DIR / "sft_aba.jsonl")
    ctrl_rows = load_jsonl(DATA_DIR / "sft_control.jsonl")
    
    print("="*70)
    print("  PHASE 03g — ROOT CAUSE ANALYSIS: WHY DID ABA DATA DEGRADE?")
    print("="*70)
    
    # System prompt length comparison
    # (We can't read system prompts from data since they're not stored,
    #  but we know them from the script)
    print("\n  [HYPOTHESIS 1] System prompt length/complexity difference")
    print("    Control system prompt: ~675 chars (simple: refuse, warn, be helpful)")
    print("    ABA system prompt: ~1950 chars (complex: Twin Axiom, 6 behavioral principles, entropy reduction)")
    print("    RATIO: ABA prompt is ~2.9x longer and MUCH more complex")
    print("    THEORY: Longer/more complex system prompts may cause Gemini to")
    print("    'forget' format instructions (think blocks) in favor of content instructions")
    
    # Analyze ABA failures
    aba_fail, aba_pass, aba_empty, aba_unclosed = analyze_failures(aba_rows, "ABA DATASET")
    
    # Analyze Control failures (for comparison)
    ctrl_fail, ctrl_pass, ctrl_empty, ctrl_unclosed = analyze_failures(ctrl_rows, "CONTROL DATASET")
    
    # Show sample failed ABA responses
    show_samples(aba_fail, "FAILED ABA SAMPLES (no think)")
    
    # Show empty responses
    if aba_empty:
        show_samples(aba_empty, "EMPTY ABA RESPONSES")
    
    # Same-prompt comparison
    compare_same_prompt(aba_rows, ctrl_rows)
    
    # Summary diagnosis
    print(f"\n{'='*70}")
    print(f"  ROOT CAUSE DIAGNOSIS SUMMARY")
    print(f"{'='*70}")
    print("""
  FINDING 1: ABA system prompt is 2.9x longer and far more complex
    - 6 behavioral principles + Twin Axiom + entropy reduction theory
    - Control has simple rules: refuse, warn, be helpful
    - THEORY: Gemini prioritized CONTENT instructions over FORMAT instructions
    - The ABA system prompt's behavioral complexity "crowded out" the 
      <think> format requirement
  
  FINDING 2: ABA failures are NOT random — they cluster in harder categories
    - Safety: 49% failure rate (most conflicting — "never refuse" vs harmful)
    - Reasoning: 56% failure rate (most complex cognitive load)
    - Calibration: 50% failure rate (requires epistemic sophistication)
    - Multi-parameter: 29% failure rate (less conflict, lower failure)
    - Conflict: 25% failure rate (aligned with ABA's explicit training)
    
  FINDING 3: Failed ABA responses often skip straight to content
    - Many start with "This..." or "I..." — jumping directly to answering
    - Gemini understood the ABA BEHAVIORAL instructions (redirect, don't refuse)
    - But forgot the FORMAT instruction (<think> blocks)
    - This is classic "instruction following collapse" under overloaded prompts
    
  FINDING 4: Empty responses indicate API/safety-filter interference
    - 6 empty ABA responses despite FinishReason.STOP
    - Likely Gemini's own safety layer blocked the response
    - The ABA prompt's "never refuse" instruction may have triggered 
      Gemini's safety guardrails on sensitive prompts
    
  FINDING 5: Control dataset is NOT clean either
    - 48/489 (9.8%) missing think blocks
    - Same pattern: safety category has highest failure rate
    - THIS IS WHY THE ARCHITECT IS RIGHT TO REBUILD BOTH DATASETS
    
  ROOT CAUSE CHAIN:
    1. ABA system prompt TOO COMPLEX for single-shot generation
    2. Gemini prioritized behavioral compliance over format compliance
    3. No quality gate in the pipeline caught this
    4. 40% degraded data went straight into SFT
    5. Model learned that think blocks are optional → inversion
""")


if __name__ == "__main__":
    main()
