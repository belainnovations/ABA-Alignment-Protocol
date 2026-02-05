"""
Split the ABA dataset into Train/Val/Test for DPO training.
Splits: 800 train / 100 val / 100 test
"""
import json
import random
from pathlib import Path

# Configuration
SOURCE_FILE = Path("data/dataset_aba_v1.4_config2.jsonl")
OUTPUT_DIR = Path("data/splits")
SEED = 42
TRAIN_SIZE = 800
VAL_SIZE = 100
TEST_SIZE = 100

def main():
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load all items
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        items = [json.loads(line) for line in f]
    
    print(f"Loaded {len(items)} items from {SOURCE_FILE}")
    
    # Validate expected count
    expected_total = TRAIN_SIZE + VAL_SIZE + TEST_SIZE
    if len(items) != expected_total:
        print(f"WARNING: Expected {expected_total} items, got {len(items)}")
    
    # Shuffle with seed for reproducibility
    random.seed(SEED)
    random.shuffle(items)
    
    # Split
    train_items = items[:TRAIN_SIZE]
    val_items = items[TRAIN_SIZE:TRAIN_SIZE + VAL_SIZE]
    test_items = items[TRAIN_SIZE + VAL_SIZE:TRAIN_SIZE + VAL_SIZE + TEST_SIZE]
    
    # Write splits
    splits = {
        "train.jsonl": train_items,
        "val.jsonl": val_items,
        "test.jsonl": test_items
    }
    
    for filename, data in splits.items():
        output_path = OUTPUT_DIR / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"Wrote {len(data)} items to {output_path}")
    
    # Verify DPO format
    print("\n--- DPO Format Verification ---")
    required_keys = {'prompt', 'chosen', 'rejected'}
    sample = train_items[0]
    present_keys = set(sample.keys())
    
    if required_keys.issubset(present_keys):
        print(f"✓ All required DPO keys present: {required_keys}")
    else:
        missing = required_keys - present_keys
        print(f"✗ Missing keys: {missing}")
    
    print(f"\nSample item keys: {list(sample.keys())}")
    print(f"Prompt preview: {sample['prompt'][:100]}...")
    print(f"Chosen preview: {sample['chosen'][:100]}...")

if __name__ == "__main__":
    main()
