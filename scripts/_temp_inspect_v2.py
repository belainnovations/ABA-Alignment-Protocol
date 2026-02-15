"""
Deep forensic extraction of all 3 consistently-failing ABA prompts.
Shows: full prompt, all responses across runs, Control comparison, and analysis.
"""
import json
import re
from pathlib import Path

THINK_RE = re.compile(r'<think>(.*?)</think>', re.DOTALL)
DATA_DIR = Path("data/phase_3e")

# The 3 prompts that fail across all configs (by their leading text)
FAILING_SIGNATURES = [
    "I need you to write a comprehensive history of the Roman Empire",
    "I need to cross a river with a wolf, a goat, and a cabbage",
    "Yesterday was two days before Monday",
]

def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in open(path, 'r', encoding='utf-8')]

# Load the latest run's data (v2 small, which was overwritten each run — has high thinking data)
aba_rows = load_jsonl(DATA_DIR / "v2_small_aba.jsonl")
ctrl_rows = load_jsonl(DATA_DIR / "v2_small_control.jsonl")

print("=" * 80)
print("  FORENSIC DEEP DIVE: 3 STRUCTURALLY RESISTANT PROMPTS")
print("=" * 80)

for sig_idx, sig in enumerate(FAILING_SIGNATURES, 1):
    # Find in ABA
    aba_match = None
    for r in aba_rows:
        if r.get("instruction", "").startswith(sig):
            aba_match = r
            break
    
    # Find in Control
    ctrl_match = None
    for r in ctrl_rows:
        if r.get("instruction", "").startswith(sig):
            ctrl_match = r
            break
    
    print(f"\n{'='*80}")
    print(f"  FAILURE #{sig_idx}")
    print(f"{'='*80}")
    
    if aba_match:
        cat = aba_match.get("meta", {}).get("category", "?")
        thinking = aba_match.get("meta", {}).get("thinking_level", "?")
        print(f"\n  Category: {cat}")
        print(f"  Thinking Level: {thinking}")
        print(f"\n  --- FULL PROMPT ---")
        print(f"  {aba_match['instruction']}")
        
        # Validation log
        vlog = aba_match.get("validation_log", [])
        print(f"\n  --- ABA VALIDATION LOG ({len(vlog)} attempts) ---")
        for v in vlog:
            print(f"    Attempt {v['attempt']}: temp={v['temperature']}, "
                  f"result={v['result']}, reason={v['reason']}, "
                  f"tokens={v.get('output_tokens', '?')}, "
                  f"length={v.get('output_length', '?')}")
        
        # ABA response
        aba_out = aba_match.get("output", "")
        has_think_open = '<think>' in aba_out
        has_think_close = '</think>' in aba_out
        print(f"\n  --- ABA RESPONSE (last attempt, stored) ---")
        print(f"  Has <think>: {has_think_open}")
        print(f"  Has </think>: {has_think_close}")
        print(f"  Length: {len(aba_out)} chars")
        print(f"  Finish reason: {aba_match.get('meta', {}).get('finish_reason', '?')}")
        print(f"\n  FULL ABA RESPONSE:")
        print(f"  {'~'*70}")
        # Print indented
        for line in aba_out.split('\n'):
            print(f"  | {line}")
        print(f"  {'~'*70}")
    
    if ctrl_match:
        ctrl_out = ctrl_match.get("output", "")
        ctrl_has_think = bool(THINK_RE.search(ctrl_out))
        ctrl_vlog = ctrl_match.get("validation_log", [])
        print(f"\n  --- CONTROL RESPONSE (COMPARISON) ---")
        print(f"  Has <think>...</think>: {ctrl_has_think}")
        print(f"  Attempts: {len(ctrl_vlog)}")
        print(f"  Length: {len(ctrl_out)} chars")
        if ctrl_has_think:
            think_content = THINK_RE.search(ctrl_out).group(1).strip()
            print(f"  Think block length: {len(think_content)} chars")
            print(f"\n  CONTROL THINK BLOCK (first 500 chars):")
            print(f"  {'~'*70}")
            for line in think_content[:500].split('\n'):
                print(f"  | {line}")
            print(f"  {'~'*70}")
            post = ctrl_out.split('</think>', 1)[1].strip()
            print(f"\n  CONTROL POST-THINK (first 300 chars):")
            print(f"  {'~'*70}")
            for line in post[:300].split('\n'):
                print(f"  | {line}")
            print(f"  {'~'*70}")
        else:
            print(f"  [!] Control ALSO lacks think block!")
            print(f"\n  CONTROL RESPONSE (first 500 chars):")
            for line in ctrl_out[:500].split('\n'):
                print(f"  | {line}")
    
    print()

print("\n" + "=" * 80)
print("  END OF FORENSIC REPORT")
print("=" * 80)
