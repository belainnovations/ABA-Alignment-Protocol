import json
import random

INPUT_FILE = "docs/03_phase_history/phase_03c/dpo_results_cleaned.jsonl"
MODEL_ID = "Native_DPO_3c"
SAMPLE_SIZE = 10

def sample_responses():
    candidates = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("model_id") == MODEL_ID:
                    candidates.append(data)
            except:
                pass

    print(f"Found {len(candidates)} responses for {MODEL_ID}.")
    
    if len(candidates) > SAMPLE_SIZE:
        samples = random.sample(candidates, SAMPLE_SIZE)
    else:
        samples = candidates

    print(f"--- Sampling {len(samples)} Responses ---\n")
    for i, sample in enumerate(samples):
        try:
            print(f"Sample {i+1}:")
            print(f"Prompt: {sample['prompt'].encode('utf-8', 'replace').decode('utf-8')}")
            print(f"Response: {sample['response'].encode('utf-8', 'replace').decode('utf-8')}")
            print(f"Detailed Metrics: {sample.get('metrics', {})}")
            print("-" * 40 + "\n")
        except Exception as e:
            print(f"Error printing sample {i+1}: {e}")

if __name__ == "__main__":
    sample_responses()
