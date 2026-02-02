"""
Data Preparation Module for ABA Protocol.
Extracts the "Toxic 1k" from Anthropic/hh-rlhf.
"""
import os
import json
import random
import argparse
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm

# Heuristic keywords that indicate a Refusal (The "Smiley Face" Mask)
REFUSAL_KEYWORDS = [
    "i cannot", "i can't", "i am unable", "i'm unable", 
    "as an ai", "as a language model", "unethical", "dangerous",
    "illegal", "harmful", "violate", "against my policies"
]

def is_refusal(response_text: str) -> bool:
    """Checks if the response contains standard refusal markers."""
    text_lower = response_text.lower()
    return any(keyword in text_lower for keyword in REFUSAL_KEYWORDS)

def load_and_filter_data(output_dir: str, num_samples: int = 1000, seed: int = 42):
    """
    Loads Anthropic/hh-rlhf, filters for refusals (proxy for toxic prompts), 
    and saves Control vs ABA Raw datasets.
    """
    print(f"Loading dataset 'Anthropic/hh-rlhf'...")
    # Load only the harmless-base split
    dataset = load_dataset("Anthropic/hh-rlhf", data_dir="harmless-base", split="train")
    
    toxic_candidates = []
    
    print("Filtering for toxic prompts (Refusal Detection)...")
    for entry in tqdm(dataset):
        # In HH-RLHF, 'rejected' is usually the worse response.
        # However, we are looking for prompts that TRIGGER safety filters.
        # Often, BOTH chosen and rejected are refusals for truly toxic prompts, 
        # or 'chosen' is a refusal.
        # For this experiment, we want prompts where the model Refused.
        # We check the 'chosen' response for refusal, as that represents the "Safety Tuned" behavior 
        # we want to change (or 'rejected' if we want to capture what the model *shouldn't* do but did).
        
        # Strategy: We want "Hard Cases". These are prompts where the model felt compelled to refuse.
        # We check the 'chosen' field for refusal keywords.
        if is_refusal(entry['chosen']):
            toxic_candidates.append(entry)
            
    print(f"Found {len(toxic_candidates)} refusal candidates.")
    
    if len(toxic_candidates) < num_samples:
        print(f"Warning: Only found {len(toxic_candidates)} samples. Using all.")
        selected_data = toxic_candidates
    else:
        random.seed(seed)
        selected_data = random.sample(toxic_candidates, num_samples)
        
    os.makedirs(output_dir, exist_ok=True)
    
    control_path = os.path.join(output_dir, "dataset_control.jsonl")
    aba_raw_path = os.path.join(output_dir, "dataset_aba_raw.jsonl")
    
    print(f"Saving {len(selected_data)} samples to {output_dir}...")
    
    with open(control_path, 'w', encoding='utf-8') as f_control, \
         open(aba_raw_path, 'w', encoding='utf-8') as f_aba:
        
        for entry in selected_data:
            # Control: Just the original data
            json.dump(entry, f_control)
            f_control.write('\n')
            
            # ABA Raw: Same data, will be rewritten later
            json.dump(entry, f_aba)
            f_aba.write('\n')
            
    return len(selected_data)

def verify_output(output_dir: str, expected_count: int = 1000):
    """Verifies the integrity of the generated files."""
    control_path = os.path.join(output_dir, "dataset_control.jsonl")
    aba_raw_path = os.path.join(output_dir, "dataset_aba_raw.jsonl")
    
    if not os.path.exists(control_path):
        print(f"FAIL: {control_path} does not exist.")
        return False
        
    if not os.path.exists(aba_raw_path):
        print(f"FAIL: {aba_raw_path} does not exist.")
        return False
        
    with open(control_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) != expected_count:
            print(f"FAIL: Expected {expected_count} lines, found {len(lines)}")
            return False
            
    print(f"SUCCESS: Verified {expected_count} samples in {output_dir}.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ABA Data Preparation")
    parser.add_argument("--output_dir", type=str, default="data", help="Output directory")
    parser.add_argument("--num_samples", type=int, default=1000, help="Number of samples to extract")
    parser.add_argument("--verify", action="store_true", help="Run verification only")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_output(args.output_dir, args.num_samples)
    else:
        count = load_and_filter_data(args.output_dir, args.num_samples)
        verify_output(args.output_dir, count)
