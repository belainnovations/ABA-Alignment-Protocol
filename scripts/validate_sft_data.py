"""
Phase 03g: Quality Audit for generated SFT data.
Validates both Control and ABA datasets against quality gates.

Usage:
    python scripts/validate_sft_data.py --control data/phase_3e/v2_small_control.jsonl --aba data/phase_3e/v2_small_aba.jsonl
"""

import json
import re
import argparse
import sys
from pathlib import Path
from collections import Counter

THINK_RE = re.compile(r'<think>(.*?)</think>', re.DOTALL)

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


def audit_file(path: Path, label: str) -> dict:
    """Audit a single JSONL file against quality gates."""
    if not path.exists():
        print(f"  [!] File not found: {path}")
        return {}
    
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    results = {
        "total": len(rows),
        "has_think": 0,
        "missing_think": 0,
        "empty": 0,
        "think_too_short": 0,
        "response_too_short": 0,
        "has_system_prompt": 0,
        "pure_refusal": 0,
        "has_redirection": 0,
        "has_refusal": 0,
        "think_lengths": [],
        "response_lengths": [],
        "retry_counts": [],
        "category_failures": Counter(),
        "category_totals": Counter(),
        "v2_generated": 0,
    }
    
    for row in rows:
        output = row.get("output", "") or ""
        category = row.get("meta", {}).get("category", "?")
        results["category_totals"][category] += 1
        
        # System prompt check
        if "system_prompt" in row:
            results["has_system_prompt"] += 1
        
        # Generation version check
        if row.get("meta", {}).get("generation_version") == "v2":
            results["v2_generated"] += 1
        
        # Retry count from validation log
        vlog = row.get("validation_log", [])
        results["retry_counts"].append(len(vlog))
        
        # Empty check
        if len(output.strip()) == 0:
            results["empty"] += 1
            results["missing_think"] += 1
            results["category_failures"][category] += 1
            continue
        
        # Think block check
        think_match = THINK_RE.search(output)
        if think_match:
            results["has_think"] += 1
            think_len = len(think_match.group(1).strip())
            results["think_lengths"].append(think_len)
            if think_len < 100:
                results["think_too_short"] += 1
                results["category_failures"][category] += 1
        else:
            results["missing_think"] += 1
            results["category_failures"][category] += 1
        
        # Response length
        results["response_lengths"].append(len(output))
        
        # Post-think response length
        if '</think>' in output:
            post = output.split('</think>', 1)[1].strip()
            if len(post) < 50:
                results["response_too_short"] += 1
        
        # Behavioral patterns
        has_refusal = any(re.search(p, output, re.IGNORECASE) for p in REFUSAL_PATTERNS)
        has_redirect = any(re.search(p, output, re.IGNORECASE) for p in REDIRECTION_PATTERNS)
        if has_refusal:
            results["has_refusal"] += 1
        if has_redirect:
            results["has_redirection"] += 1
        if has_refusal and not has_redirect:
            results["pure_refusal"] += 1
    
    return results


def print_report(results: dict, label: str):
    """Print a formatted quality report."""
    if not results:
        return
    
    total = results["total"]
    print(f"\n{'='*60}")
    print(f"  {label} QUALITY REPORT")
    print(f"{'='*60}")
    
    # Core quality gates
    think_rate = results["has_think"] / max(total, 1) * 100
    sys_rate = results["has_system_prompt"] / max(total, 1) * 100
    
    gate_results = [
        ("Think blocks present", results["has_think"], total, think_rate, ">= 95%", think_rate >= 95),
        ("System prompt stored", results["has_system_prompt"], total, sys_rate, "= 100%", sys_rate == 100),
        ("Empty responses", results["empty"], total, results["empty"]/max(total,1)*100, "= 0", results["empty"] == 0),
        ("Think too short (<100)", results["think_too_short"], total, results["think_too_short"]/max(total,1)*100, "= 0", results["think_too_short"] == 0),
        ("Response too short (<50)", results["response_too_short"], total, results["response_too_short"]/max(total,1)*100, "= 0", results["response_too_short"] == 0),
    ]
    
    print(f"\n  QUALITY GATES:")
    all_passed = True
    for name, count, tot, pct, target, passed in gate_results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"    [{status}] {name}: {count}/{tot} ({pct:.1f}%) [target: {target}]")
    
    # Behavioral analysis
    print(f"\n  BEHAVIORAL PATTERNS:")
    print(f"    Has refusal language: {results['has_refusal']}/{total}")
    print(f"    Has redirection language: {results['has_redirection']}/{total}")
    print(f"    Pure refusal (no redirect): {results['pure_refusal']}/{total}")
    
    # Stats
    if results["think_lengths"]:
        avg_think = sum(results["think_lengths"]) / len(results["think_lengths"])
        print(f"\n  THINK BLOCK STATS:")
        print(f"    Avg length: {avg_think:.0f} chars")
        print(f"    Min: {min(results['think_lengths'])} chars")
        print(f"    Max: {max(results['think_lengths'])} chars")
    
    if results["response_lengths"]:
        avg_resp = sum(results["response_lengths"]) / len(results["response_lengths"])
        print(f"\n  RESPONSE LENGTH STATS:")
        print(f"    Avg: {avg_resp:.0f} chars")
        print(f"    Min: {min(results['response_lengths'])} chars")
        print(f"    Max: {max(results['response_lengths'])} chars")
    
    # Retries
    if results["retry_counts"]:
        total_retries = sum(max(0, r - 1) for r in results["retry_counts"])
        multi_attempt = sum(1 for r in results["retry_counts"] if r > 1)
        print(f"\n  RETRY STATS:")
        print(f"    Samples needing retries: {multi_attempt}/{total}")
        print(f"    Total extra attempts: {total_retries}")
    
    # Category breakdown
    if results["category_failures"]:
        print(f"\n  FAILURES BY CATEGORY:")
        for cat in sorted(results["category_totals"]):
            fails = results["category_failures"].get(cat, 0)
            tot = results["category_totals"][cat]
            status = "OK" if fails == 0 else "!!"
            print(f"    [{status}] {cat}: {fails}/{tot} failures")
    
    # Version
    print(f"\n  METADATA:")
    print(f"    v2 generated: {results['v2_generated']}/{total}")
    
    print(f"\n  {'OVERALL: ALL GATES PASSED' if all_passed else 'OVERALL: SOME GATES FAILED'}")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="SFT Data Quality Audit")
    parser.add_argument("--control", type=str, required=True, help="Path to control JSONL")
    parser.add_argument("--aba", type=str, required=True, help="Path to ABA JSONL")
    args = parser.parse_args()
    
    print("="*60)
    print("  PHASE 03g: SFT DATA QUALITY AUDIT")
    print("="*60)
    
    ctrl_results = audit_file(Path(args.control), "CONTROL")
    aba_results = audit_file(Path(args.aba), "ABA")
    
    ctrl_pass = print_report(ctrl_results, "CONTROL")
    aba_pass = print_report(aba_results, "ABA")
    
    # Comparison
    if ctrl_results and aba_results:
        print(f"\n{'='*60}")
        print(f"  COMPARISON")
        print(f"{'='*60}")
        ctrl_think = ctrl_results["has_think"] / max(ctrl_results["total"], 1) * 100
        aba_think = aba_results["has_think"] / max(aba_results["total"], 1) * 100
        print(f"  Think rate: Control={ctrl_think:.1f}% vs ABA={aba_think:.1f}%")
        
        ctrl_refusal = ctrl_results["pure_refusal"] / max(ctrl_results["total"], 1) * 100
        aba_refusal = aba_results["pure_refusal"] / max(aba_results["total"], 1) * 100
        print(f"  Pure refusal: Control={ctrl_refusal:.1f}% vs ABA={aba_refusal:.1f}%")
        
        if ctrl_results["think_lengths"] and aba_results["think_lengths"]:
            ctrl_avg = sum(ctrl_results["think_lengths"]) / len(ctrl_results["think_lengths"])
            aba_avg = sum(aba_results["think_lengths"]) / len(aba_results["think_lengths"])
            print(f"  Avg think length: Control={ctrl_avg:.0f} vs ABA={aba_avg:.0f}")
    
    print()
    if ctrl_pass and aba_pass:
        print("  >>> ALL QUALITY GATES PASSED. Ready for full generation. <<<")
    else:
        print("  >>> SOME QUALITY GATES FAILED. Review and iterate on prompts. <<<")
    
    return 0 if (ctrl_pass and aba_pass) else 1


if __name__ == "__main__":
    sys.exit(main())
