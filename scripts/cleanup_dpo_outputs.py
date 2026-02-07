import json
import os
import argparse
from pathlib import Path

def clean_dpo_outputs(input_file, output_file):
    """
    Cleans DPO model outputs by truncating 'Simulated User' turns.
    This is an Engineering Fix for Phase 3c where models failed to learn proper EOS tokens.
    """
    print(f"Cleaning DPO outputs from: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    cleaned_data = []
    truncation_count = 0
    total_count = 0
    
    # Stopping strings to look for
    STOP_STRINGS = [
        "\nHuman:",
        "\nUser:",
        "\n\nHuman:",
        "\n\nUser:",
        "\nAssistant:", # If it loops
        "\n\nAssistant:"
    ]

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            total_count += 1
            try:
                entry = json.loads(line)
                response = entry.get("response", "")
                
                # Check for truncation need
                original_len = len(response)
                truncated = False
                
                # Find the earliest occurrence of any stop string
                cut_index = len(response)
                
                for stop in STOP_STRINGS:
                    idx = response.find(stop)
                    if idx != -1 and idx < cut_index:
                        cut_index = idx
                        truncated = True
                
                if truncated:
                    cleaned_response = response[:cut_index].strip()
                    truncation_count += 1
                else:
                    cleaned_response = response.strip()
                
                entry["response"] = cleaned_response
                entry["metrics"]["cleaned"] = True
                entry["metrics"]["was_truncated"] = truncated
                
                cleaned_data.append(entry)
                
            except json.JSONDecodeError:
                continue

    # Save
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in cleaned_data:
            f.write(json.dumps(entry) + '\n')
            
    print(f"Cleaning Complete.")
    print(f"Total Samples: {total_count}")
    print(f"Truncated:     {truncation_count} ({truncation_count/total_count*100:.1f}%)")
    print(f"Saved to:      {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="docs/03_phase_history/phase_03c/dpo_results.jsonl")
    parser.add_argument("--output", default="docs/03_phase_history/phase_03c/dpo_results_cleaned.jsonl")
    args = parser.parse_args()
    
    clean_dpo_outputs(args.input, args.output)
