
import json
import random

file_path = 'data/dataset_aba_v1.4_config2.jsonl'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    total_count = len(lines)
    print(f"Total Lines: {total_count}")
    
    if total_count == 0:
        print("Error: File is empty.")
        exit(1)

    # Check first, middle, last
    indices_to_check = [0, total_count // 2, total_count - 1]
    
    errors = 0
    for i in indices_to_check:
        try:
            item = json.loads(lines[i])
            # Check for critical fields
            if 'chosen' not in item or 'rejected' not in item:
                print(f"Error at line {i+1}: Missing 'chosen' or 'rejected' field.")
                errors += 1
            if 'context' not in item and 'instruction' not in item: # Assuming standard format
                 # Adaptation: checking if it looks like a preference pair
                 pass
                 
            # Print a snippet of the last item to verify content
            if i == total_count - 1:
                print(f"--- Last Item Snippet (Line {i+1}) ---")
                print(json.dumps(item, indent=2)[:500] + "...")

        except json.JSONDecodeError:
            print(f"Error at line {i+1}: Invalid JSON.")
            errors += 1

    if errors == 0:
        print("\nSUCCESS: Integrity check passed for sampled items.")
    else:
        print(f"\nFAILURE: Found {errors} errors in sampled items.")

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
