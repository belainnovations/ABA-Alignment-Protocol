"""Quick quality check on generated SFT datasets."""
import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

for label, path in [('CONTROL', 'data/phase_3e/sft_control.jsonl'),
                     ('ABA', 'data/phase_3e/sft_aba.jsonl')]:
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            items.append(json.loads(line))

    # Category distribution
    cats = Counter(d['meta']['category'] for d in items)
    
    # Think block presence
    none_outputs = sum(1 for d in items if d.get('output') is None)
    has_think = sum(1 for d in items if d.get('output') and '<think>' in d['output'] and '</think>' in d['output'])
    
    # Token stats
    tokens = [d['token_stats']['total'] for d in items]
    avg_tokens = sum(tokens) / len(tokens)
    
    # Output length
    outputs = [len(d['output']) for d in items if d.get('output')]
    avg_chars = sum(outputs) / len(outputs) if outputs else 0
    
    # Empty outputs
    empty = sum(1 for d in items if not d.get('output') or len(d['output'].strip()) < 50)

    print(f"\n{'='*50}")
    print(f"  {label} DATASET QUALITY CHECK")
    print(f"{'='*50}")
    print(f"  Total items: {len(items)}")
    print(f"  <think> blocks: {has_think}/{len(items)} ({has_think/len(items)*100:.0f}%)")
    print(f"  None outputs: {none_outputs}")
    print(f"  Avg tokens: {avg_tokens:.0f}")
    print(f"  Avg output chars: {avg_chars:.0f}")
    print(f"  Empty/short outputs (<50 chars): {empty}")
    print(f"  Categories:")
    for cat, count in sorted(cats.items()):
        print(f"    {cat}: {count}")

    # Spot check: show 3 random safety responses (abbreviated)
    safety = [d for d in items if d['meta']['category'] == 'safety' and d.get('output')]
    print(f"\n  Spot check - 3 safety responses:")
    for d in safety[:3]:
        out = d['output'][:200].replace('\n', ' ')
        print(f"    [{d['instruction'][:60]}...]")
        print(f"    -> {out}...")
        print()
