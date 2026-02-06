
import json
import random
import os
from pathlib import Path

# Config
SOURCE_FILE = "data/dataset_control.jsonl"
OUTPUT_DIR = "data/control_splits"
TRAIN_SIZE = 800
TEST_SIZE = 100
VAL_SIZE = 100

def parse_anthropic_item(item):
    """
    Parses an Anthropic HH-RLHF item (full text in chosen/rejected)
    into ABA format (prompt, chosen, rejected).
    """
    chosen_full = item.get("chosen", "")
    rejected_full = item.get("rejected", "")
    
    # Split on the last Assistant turn to separate context from response
    # We use rsplit to find the LAST occurrence
    separator = "\n\nAssistant:"
    
    if separator not in chosen_full:
        return None
        
    prompt, chosen_response = chosen_full.rsplit(separator, 1)
    
    # Re-attach the separator to the prompt to match ABA format
    # ABA format: "Human: ...\n\nAssistant:"
    formatted_prompt = prompt + separator
    
    # Get rejected response (assuming same context)
    if separator in rejected_full:
        _, rejected_response = rejected_full.rsplit(separator, 1)
    else:
        # Fallback if rejected has different structure (unlikely for HH-RLHF)
        rejected_response = ""
        
    return {
        "prompt": formatted_prompt,
        "chosen": chosen_response, # Note: Leading space usually exists, keep it? 
                                  # ABA v1.4 chosen does NOT have leading space, but prompt ends in Assistant:
                                  # Let's strip leading whitespace from response for cleanliness
        "rejected": rejected_response
    }

def split_data():
    source_path = Path(SOURCE_FILE)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Reading from {source_path}...")
    with open(source_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Parse and filter
    parsed_items = []
    print(f"Parsing {len(lines)} raw items...")
    for line in lines:
        try:
            item = json.loads(line)
            parsed = parse_anthropic_item(item)
            if parsed and parsed["chosen"].strip() and parsed["rejected"].strip():
                parsed_items.append(parsed)
        except json.JSONDecodeError:
            continue
            
    print(f"Successfully parsed {len(parsed_items)} items.")

    # Shuffle
    random.seed(42)
    random.shuffle(parsed_items)

    # Truncate to desired total
    total_needed = TRAIN_SIZE + TEST_SIZE + VAL_SIZE
    if len(parsed_items) > total_needed:
        print(f"Truncating to {total_needed} for parity.")
        parsed_items = parsed_items[:total_needed]

    # Split
    train_data = parsed_items[:TRAIN_SIZE]
    test_data = parsed_items[TRAIN_SIZE:TRAIN_SIZE+TEST_SIZE]
    val_data = parsed_items[TRAIN_SIZE+TEST_SIZE:]

    # Save
    def save_split(data, filename):
        with open(output_path / filename, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

    save_split(train_data, "train.jsonl")
    save_split(test_data, "test.jsonl")
    save_split(val_data, "validation.jsonl")
    
    print(f"Splits saved to {output_path}:")
    print(f"  Train: {len(train_data)}")
    print(f"  Test:  {len(test_data)}")
    print(f"  Val:   {len(val_data)}")

if __name__ == "__main__":
    split_data()
