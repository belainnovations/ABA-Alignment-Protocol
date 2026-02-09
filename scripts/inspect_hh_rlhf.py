
import os
from datasets import load_dataset

def inspect_hh_rlhf():
    print("Loading Anthropic/hh-rlhf (harmless-base)...")
    dataset = load_dataset("Anthropic/hh-rlhf", data_dir="harmless-base", split="train", streaming=True)
    
    print("Inspecting first 20 entries for Refusals...")
    count = 0
    refusal_count = 0
    
    for entry in dataset:
        count += 1
        if count > 20:
            break
            
        print(f"\n--- Entry {count} ---")
        print(f"PROMPT: {entry['chosen'].split('Assistant:')[0] if 'Assistant:' in entry['chosen'] else entry['chosen'][:50]}...")
        
        # Check Chosen vs Rejected
        print(f"CHOSEN (Safety Tuned?): {entry['chosen'].split('Assistant:')[-1][:100]}...")
        print(f"REJECTED (Harmful?):   {entry['rejected'].split('Assistant:')[-1][:100]}...")
        
        if "I cannot" in entry['chosen'] or "I cannot" in entry['rejected']:
            refusal_count += 1

    print(f"\nFound {refusal_count} visible refusals in first 20 samples.")

if __name__ == "__main__":
    inspect_hh_rlhf()
