import sys
from datasets import load_dataset

def peek_dataset(dataset_name, split="train", num_rows=5):
    print(f"\n--- Peeking at {dataset_name} ({split}) ---")
    try:
        # Stream=True allows seeing data without downloading the whole thing
        dataset = load_dataset(dataset_name, split=split, streaming=True)
        
        for i, row in enumerate(dataset):
            if i >= num_rows:
                break
            print(f"\n[Row {i}]")
            # Print keys to understand structure
            print(f"Keys: {list(row.keys())}")
            
            # Try to print prompt/response based on common keys
            if "instruction" in row and "output" in row:
                print(f"Prompt: {row['instruction'][:200]}...")
                print(f"Response: {row['output'][:300]}") # Print enough to see the refusal style
            elif "prompt" in row and "response" in row:
                print(f"Prompt: {row['prompt'][:200]}...")
                print(f"Response: {row['response'][:300]}")
            elif "messages" in row:
                 print(f"Messages: {row['messages']}")
            else:
                print(f"Content: {row}")
                
    except Exception as e:
        print(f"ERROR loading {dataset_name}: {e}")

if __name__ == "__main__":
    datasets_to_check = [
        "mrfakename/refusal",
        "LLM-Tuning-Safety/HateSpeech-Safety-Test" # Found in search, checking common naming
    ]
    
    # Also check if user passed args
    if len(sys.argv) > 1:
        datasets_to_check = sys.argv[1:]

    for ds in datasets_to_check:
        peek_dataset(ds)
