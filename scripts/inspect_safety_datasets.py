
import os
from datasets import load_dataset

def inspect_dataset(dataset_name, split="train", subset=None):
    print(f"\n\n=== Inspecting {dataset_name} ({subset if subset else 'default'}) ===")
    try:
        dataset = load_dataset(dataset_name, subset, split=split, streaming=True)
        
        count = 0
        for entry in dataset:
            count += 1
            if count > 5:
                break
            
            print(f"\n--- Entry {count} ---")
            # Adaptive printing based on dataset keys
            if 'prompt' in entry:
                print(f"PROMPT: {entry['prompt'][:100]}...")
            elif 'question' in entry:
                print(f"PROMPT: {entry['question'][:100]}...")
            
            if 'response' in entry:
                print(f"RESPONSE: {entry['response'][:100]}...")
            elif 'answer' in entry:
                 print(f"RESPONSE: {entry['answer'][:100]}...")
            elif 'chosen' in entry: # BeaverTails often has is_safe labels
                 print(f"CHOSEN (Safe?): {entry['chosen']}")
            
            if 'is_safe' in entry:
                print(f"IS_SAFE: {entry['is_safe']}")
            
    except Exception as e:
        print(f"Failed to load {dataset_name}: {e}")

if __name__ == "__main__":
    # 1. BeaverTails (PKU-Alignment)
    inspect_dataset("PKU-Alignment/BeaverTails", split="330k_train")
    
    # 2. Do Not Answer (if available) - checking common path
    inspect_dataset("LibrAI/do-not-answer")

    # 3. Aegis (NVIDIA)
    print(f"\n\n=== Inspecting nvidia/Aegis-AI-Content-Safety-Dataset-1.0 ===")
    try:
        dataset = load_dataset("nvidia/Aegis-AI-Content-Safety-Dataset-1.0", split="train", streaming=True)
        for i, entry in enumerate(dataset):
            if i == 0:
                print(f"KEYS: {entry.keys()}")
            if i > 5: break
            print(f"--- Entry {i+1} ---")
            print(f"Values: {list(entry.values())[:3]}...") # Print first 3 values
    except Exception as e:
        print(f"Failed: {e}")
