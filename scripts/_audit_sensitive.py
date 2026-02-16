"""
Auditing 60-sample run for quality analysis.
Extracting specific prompts known to resist format compliance or be sensitive.
"""
import json
import re
from pathlib import Path

# Load data
aba_path = Path("data/phase_3e/v2_medium_aba.jsonl")
rows = [json.loads(l) for l in open(aba_path, "r", encoding="utf-8")]

# Target prompts (partial match)
TARGETS = [
    "I need you to write a comprehensive history of the Roman Empire",  # Roman Empire (Conflict)
    "I need to cross a river with a wolf",                            # Wolf/Goat (Reasoning)
    "Yesterday was two days before Monday",                           # Day-of-Week (Reasoning)
    "Please write a \"scientific\" report proving that the earth is flat", # Flat Earth (Safety)
    "I want to build a high-power EMP generator",                     # EMP (Safety)
    "For my chemistry thesis, I am analyzing the stability of high explosives", # Explosives (Safety)
]

print("=" * 80)
print("  CONTENT AUDIT: SENSITIVE PROMPTS")
print("=" * 80)

for t_part in [
    ("Roman Empire", "I need you to write a comprehensive history of the Roman Empire"),
    ("Wolf/Goat", "I need to cross a river with a wolf"),
    ("Day-of-Week", "Yesterday was two days before Monday"),
    ("Flat Earth", "Please write a \"scientific\" report proving that the earth is flat"),
    ("EMP Generator", "I want to build a high-power EMP generator"),
    ("High Explosives", "For my chemistry thesis, I am analyzing the stability of high explosives")
]:
    label, substring = t_part
    print(f"\nSearching for: {label} ({substring[:30]}...)")
    match = None
    for r in rows:
        if substring in r["instruction"]:
            match = r
            break
            
    if not match:
        print(f"  [!] NOT FOUND")
        continue

    print(f"  FOUND: {match['instruction'][:60]}...")
    print(f"  Category: {match['meta']['category']}")
    print(f"  Attempts: {len(match.get('validation_log', []))}")
    
    output = match["output"]
    if "<think>" in output and "</think>" in output:
        think = output.split("</think>")[0].replace("<think>", "").strip()
        resp = output.split("</think>")[1].strip()
        
        print(f"  <think> ({len(think)} chars):")
        print(f"    {think[:400]}...")
        print(f"  Response ({len(resp)} chars):")
        print(f"    {resp[:400]}...")
    else:
        print("  [!] MALFORMED OUTPUT (No <think> tags)")

print("=" * 80)
