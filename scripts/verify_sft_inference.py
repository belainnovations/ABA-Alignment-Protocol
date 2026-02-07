
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import argparse

def verify_inference(model_path, adapter_path, prompt="Say hello to a new world"):
    print(f"--- Verification: SFT Inference Check ---")
    print(f"Base Model: {model_path}")
    print(f"Adapter: {adapter_path}")
    
    # 1. Load Base Model (4-bit)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False,
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # 2. Load Adapter
    print("Loading Adapter...")
    model = PeftModel.from_pretrained(model, adapter_path)
    
    # 3. Generate
    formatted_prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    
    print("Generating...")
    outputs = model.generate(
        **inputs, 
        max_new_tokens=50, 
        do_sample=True, 
        temperature=0.7
    )
    
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\n--- Output ---")
    print(result)
    print("----------------")
    print("Verification Successful.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, default="cognitivecomputations/dolphin-2.9-llama3-8b")
    parser.add_argument("--adapter", type=str, required=True)
    args = parser.parse_args()
    
    verify_inference(args.base_model, args.adapter)
