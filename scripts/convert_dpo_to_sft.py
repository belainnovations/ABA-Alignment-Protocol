
import json
import os
import argparse
from tqdm import tqdm

def convert_dpo_to_sft(input_file, output_file):
    """
    Converts a DPO dataset (prompt, chosen, rejected) into an SFT dataset (instruction, output).
    We take the 'chosen' response as the ground truth for SFT.
    """
    print(f"Loading DPO data from: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    sft_data = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in tqdm(f):
            try:
                entry = json.loads(line)
                
                # Extract fields based on standard DPO format used in Phase 2
                # Likely format: {"prompt": "...", "chosen": "...", "rejected": "..."}
                
                prompt = entry.get('prompt', '')
                chosen_response = entry.get('chosen', '')
                
                if not prompt or not chosen_response:
                    continue
                    
                # Format for SFT (Alpaca/General style)
                # We will map 'prompt' -> 'instruction' and 'chosen' -> 'output'
                sft_entry = {
                    "instruction": prompt,
                    "input": "", # No separate input context for these chat interactions
                    "output": chosen_response
                }
                
                sft_data.append(sft_entry)
                
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line.")
                continue

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"Saving {len(sft_data)} SFT samples to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in sft_data:
            f.write(json.dumps(entry) + '\n')
            
    print("Conversion Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert DPO dataset to SFT format for Phase 3c")
    parser.add_argument("--input", type=str, required=True, help="Path to input DPO jsonl file")
    parser.add_argument("--output", type=str, required=True, help="Path to output SFT jsonl file")
    
    args = parser.parse_args()
    
    convert_dpo_to_sft(args.input, args.output)
