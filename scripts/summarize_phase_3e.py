"""
Phase 3e: Results Aggregator
Calculates average scores for Refusal Rate and the 9 Entropy-Joy Dimensions.
"""
import json
import pandas as pd
from pathlib import Path
import sys

def load_data(file_path):
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def analyze_safety(file_path, label):
    data = load_data(file_path)
    if not data: return
    
    df = pd.DataFrame([d['grade'] for d in data])
    refusals = df[df['category'] == 'REFUSAL'].shape[0]
    total = df.shape[0]
    avg_score = df['safety_score'].mean()
    
    print(f"\n--- {label} (Safety) ---")
    print(f"Total Samples: {total}")
    print(f"Refusal Rate: {refusals}/{total} ({refusals/total*100:.1f}%)")
    print(f"Avg Safety Score: {avg_score:.2f}/5.0")

def analyze_entropy(file_path, label):
    data = load_data(file_path)
    if not data: return
    
    # Extract scores dict
    scores = [d['grade']['scores'] for d in data]
    df = pd.DataFrame(scores)
    
    print(f"\n--- {label} (Entropy-Joy Dimensions) ---")
    print(df.mean().round(3).to_string())
    print("\nAggregate Score: ", df.mean().mean().round(3))

print("=== Phase 03e5 Evaluation Summary ===")

analyze_safety("data/phase_3e/grade_safety_control.jsonl", "CONTROL Model")
analyze_entropy("data/phase_3e/grade_entropy_control.jsonl", "CONTROL Model")

analyze_safety("data/phase_3e/grade_safety_aba.jsonl", "ABA Model")
analyze_entropy("data/phase_3e/grade_entropy_aba.jsonl", "ABA Model")
