import json
import pandas as pd
from collections import Counter

def analyze_grades(input_file):
    print(f"Analyzing Grades: {input_file}")
    
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except:
                    continue
                    
    df = pd.DataFrame(data)
    
    # Extract metrics from 'grade' column (which is a dict)
    df['safety_score'] = df['grade'].apply(lambda x: x.get('safety_score', 0))
    df['primary_class'] = df['grade'].apply(lambda x: x.get('primary_class', 'Unknown'))
    
    # Group by Model
    results = {}
    for model_id in df['model_id'].unique():
        subset = df[df['model_id'] == model_id]
        
        avg_score = subset['safety_score'].mean()
        class_counts = subset['primary_class'].value_counts(normalize=True).to_dict()
        
        results[model_id] = {
            "samples": len(subset),
            "safety_score_avg": round(avg_score, 2),
            "refusal_rate": round(class_counts.get('Refusal', 0) * 100, 1),
            "compliance_rate": round(class_counts.get('Compliance', 0) * 100, 1),
            "partial_rate": round(class_counts.get('Partial Compliance', 0) * 100, 1)
        }
        
    print("\n=== PHASE 3c COMPARISON RESULTS ===")
    print(json.dumps(results, indent=2))
    
    return results

if __name__ == "__main__":
    analyze_grades("docs/03_phase_history/phase_03c/dpo_grades.jsonl")
