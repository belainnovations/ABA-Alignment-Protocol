import json
from collections import defaultdict
import statistics

INPUT_FILE = "docs/03_phase_history/phase_03b/tournament_grades.jsonl"

def main():
    stats = defaultdict(lambda: {"refusal": 0, "compliance": 0, "partial": 0, "total": 0, "safety_scores": []})
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    row = json.loads(line)
                    model = row["model_id"]
                    grade = row["grade"]
                    
                    cat = grade.get("category", "ERROR")
                    score = grade.get("safety_score", 0)
                    
                    stats[model]["total"] += 1
                    stats[model]["safety_scores"].append(score)
                    
                    if cat == "REFUSAL":
                        stats[model]["refusal"] += 1
                    elif cat == "COMPLIANCE":
                        stats[model]["compliance"] += 1
                    elif cat == "PARTIAL_COMPLIANCE":
                        stats[model]["partial"] += 1
                        
                except Exception as e:
                    print(f"Skipping bad line: {e}")
    except FileNotFoundError:
        print("No grades file found yet.")
        return

    print("\n=== FINAL TOURNAMENT SCOREBOARD (LLM JUDGE) ===")
    print(f"{'Model':<15} | {'Refusal %':<10} | {'Compliance %':<12} | {'Partial %':<10} | {'Avg Safety':<10} | {'N':<5}")
    print("-" * 80)
    
    for model in sorted(stats.keys()):
        s = stats[model]
        total = s["total"]
        if total == 0: continue
        
        ref_rate = (s["refusal"] / total) * 100
        comp_rate = (s["compliance"] / total) * 100
        part_rate = (s["partial"] / total) * 100
        avg_safety = statistics.mean(s["safety_scores"]) if s["safety_scores"] else 0
        
        print(f"{model:<15} | {ref_rate:>9.1f}% | {comp_rate:>11.1f}% | {part_rate:>9.1f}% | {avg_safety:>10.2f} | {total}")

if __name__ == "__main__":
    main()
