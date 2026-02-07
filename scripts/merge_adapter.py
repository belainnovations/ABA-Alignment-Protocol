
"""
Merge Adapter Tool
Merges a PEFT/LoRA adapter into a base model and saves the full model.
Usage: python scripts/merge_adapter.py --base_model_name_or_path <base> --adapter_path <adapter> --output_dir <output>
"""
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def merge_adapter():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model_name_or_path", type=str, required=True, help="Base model ID or path")
    parser.add_argument("--adapter_path", type=str, required=True, help="Path to adapter folder")
    parser.add_argument("--output_dir", type=str, required=True, help="Where to save merged model")
    parser.add_argument("--device", type=str, default="auto", help="Device map")

    args = parser.parse_args()

    print(f"Loading base model: {args.base_model_name_or_path}")
    base_model = AutoModelForCausalLM.from_pretrained(
        args.base_model_name_or_path,
        return_dict=True,
        torch_dtype=torch.float16,
        device_map=args.device,
        trust_remote_code=True,
    )

    print(f"Loading adapter: {args.adapter_path}")
    model = PeftModel.from_pretrained(base_model, args.adapter_path)

    print("Merging adapters...")
    model = model.merge_and_unload()

    print(f"Saving merged model to {args.output_dir}")
    model.save_pretrained(args.output_dir)
    
    tokenizer = AutoTokenizer.from_pretrained(args.base_model_name_or_path)
    tokenizer.save_pretrained(args.output_dir)

    print("Done.")

if __name__ == "__main__":
    merge_adapter()
