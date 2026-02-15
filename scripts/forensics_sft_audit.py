"""
Phase 03f Forensics — F1: SFT Training Data Audit

Verifies what the model actually saw during SFT training:
1. JSONL schema (does system_prompt field exist?)
2. Behavioral pattern counts (redirection vs refusal language)
3. Safety category sample inspection

Usage:
    python scripts/forensics_sft_audit.py
"""

import json
import re
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "phase_3e"

# --- Behavioral Pattern Detection ---

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
    r"redirect",
]

THINK_BLOCK_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL)


def classify_response(text: str) -> dict:
    """Classify a response by behavioral patterns."""
    if text is None:
        text = ""
    text_lower = text.lower()
    
    has_refusal = any(re.search(p, text, re.IGNORECASE) for p in REFUSAL_PATTERNS)
    has_redirection = any(re.search(p, text, re.IGNORECASE) for p in REDIRECTION_PATTERNS)
    
    think_match = THINK_BLOCK_RE.search(text)
    has_think = think_match is not None
    think_len = len(think_match.group(1).strip()) if think_match else 0
    
    if has_refusal and has_redirection:
        category = "mixed_refusal_redirect"
    elif has_refusal:
        category = "pure_refusal"
    elif has_redirection:
        category = "pure_redirection"
    else:
        category = "neutral_compliance"
    
    return {
        "category": category,
        "has_refusal": has_refusal,
        "has_redirection": has_redirection,
        "has_think": has_think,
        "think_length": think_len,
        "response_length": len(text),
    }


def audit_dataset(filepath: Path, label: str) -> dict:
    """Audit a single JSONL dataset file."""
    print(f"\n{'='*60}")
    print(f"  AUDITING: {label}")
    print(f"  File: {filepath.name}")
    print(f"{'='*60}")
    
    if not filepath.exists():
        print(f"  [!] File not found: {filepath}")
        return {}
    
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    print(f"\n  Total samples: {len(rows)}")
    
    # 1. Schema check
    if rows:
        fields = set(rows[0].keys())
        print(f"\n  [SCHEMA] Fields in JSONL: {sorted(fields)}")
        has_system = "system_prompt" in fields or "system" in fields
        print(f"  [SCHEMA] System prompt field present: {'YES' if has_system else '*** NO ***'}")
        
        # Check for nested system prompt
        meta_fields = set(rows[0].get("meta", {}).keys()) if "meta" in fields else set()
        if meta_fields:
            print(f"  [SCHEMA] Meta fields: {sorted(meta_fields)}")
    
    # 2. Behavioral classification
    categories = Counter()
    think_stats = {"with_think": 0, "without_think": 0, "think_lengths": []}
    response_lengths = []
    safety_samples = []
    
    for row in rows:
        output = row.get("output", "")
        classification = classify_response(output)
        categories[classification["category"]] += 1
        
        if classification["has_think"]:
            think_stats["with_think"] += 1
            think_stats["think_lengths"].append(classification["think_length"])
        else:
            think_stats["without_think"] += 1
        
        response_lengths.append(classification["response_length"])
        
        # Collect safety category samples
        cat = row.get("meta", {}).get("category", row.get("category", ""))
        if cat == "safety" and len(safety_samples) < 10:
            safety_samples.append({
                "prompt": row.get("instruction", row.get("prompt", ""))[:100],
                "classification": classification["category"],
                "response_preview": output[:200],
            })
    
    print(f"\n  [BEHAVIORAL CLASSIFICATION]")
    for cat, count in categories.most_common():
        pct = count / len(rows) * 100
        print(f"    {cat:30s}: {count:4d} ({pct:5.1f}%)")
    
    print(f"\n  [THINK BLOCKS]")
    print(f"    With <think>:    {think_stats['with_think']}")
    print(f"    Without <think>: {think_stats['without_think']}")
    if think_stats["think_lengths"]:
        avg_think = sum(think_stats["think_lengths"]) / len(think_stats["think_lengths"])
        print(f"    Avg think length: {avg_think:.0f} chars")
    
    print(f"\n  [RESPONSE LENGTHS]")
    if response_lengths:
        print(f"    Min: {min(response_lengths)} chars")
        print(f"    Max: {max(response_lengths)} chars")
        print(f"    Avg: {sum(response_lengths)/len(response_lengths):.0f} chars")
    
    print(f"\n  [SAFETY CATEGORY SAMPLES] (up to 10)")
    for i, s in enumerate(safety_samples):
        print(f"    [{i+1}] Classification: {s['classification']}")
        print(f"        Prompt: {s['prompt']}...")
        print(f"        Response: {s['response_preview'][:120]}...")
        print()
    
    return {
        "label": label,
        "file": str(filepath.name),
        "total_samples": len(rows),
        "schema_fields": sorted(fields) if rows else [],
        "has_system_prompt_field": has_system if rows else None,
        "behavioral_classification": dict(categories),
        "think_block_stats": {
            "with_think": think_stats["with_think"],
            "without_think": think_stats["without_think"],
            "avg_think_length": (sum(think_stats["think_lengths"]) / len(think_stats["think_lengths"]))
                if think_stats["think_lengths"] else 0,
        },
        "response_length_stats": {
            "min": min(response_lengths) if response_lengths else 0,
            "max": max(response_lengths) if response_lengths else 0,
            "avg": (sum(response_lengths) / len(response_lengths)) if response_lengths else 0,
        },
        "safety_samples": safety_samples,
    }


def main():
    print("=" * 60)
    print("  PHASE 03f FORENSICS — F1: SFT Training Data Audit")
    print("=" * 60)
    
    results = {}
    
    # Audit both training datasets
    results["control"] = audit_dataset(DATA_DIR / "sft_control.jsonl", "CONTROL Training Data")
    results["aba"] = audit_dataset(DATA_DIR / "sft_aba.jsonl", "ABA Training Data")
    
    # Summary comparison
    print("\n" + "=" * 60)
    print("  COMPARISON SUMMARY")
    print("=" * 60)
    
    if results["control"] and results["aba"]:
        for key in ["control", "aba"]:
            r = results[key]
            print(f"\n  {r['label']}:")
            print(f"    System prompt in data: {'YES' if r.get('has_system_prompt_field') else 'NO'}")
            bc = r.get("behavioral_classification", {})
            total = r.get("total_samples", 1)
            refusal_pct = (bc.get("pure_refusal", 0) + bc.get("mixed_refusal_redirect", 0)) / total * 100
            redirect_pct = (bc.get("pure_redirection", 0) + bc.get("mixed_refusal_redirect", 0)) / total * 100
            print(f"    Samples with refusal language: {refusal_pct:.1f}%")
            print(f"    Samples with redirection language: {redirect_pct:.1f}%")
    
    # Save results
    output_path = DATA_DIR / "forensics_training_audit.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {output_path}")


if __name__ == "__main__":
    main()
