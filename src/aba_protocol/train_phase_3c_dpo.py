"""
Train Phase 3c DPO (The Steering).

This script performs Direct Preference Optimization (DPO) on a base model (typically an SFT-merged model).
It uses standard HuggingFace libraries (transformers, peft, trl) and avoids Unsloth to ensure
compatibility with Windows/Triton constraints.

Usage:
    python src/aba_protocol/train_phase_3c_dpo.py \
        --model_name models/phase_3c/model_native_sft_merged \
        --dataset data/dataset_aba_v1.4_config2.jsonl \
        --output_dir models/phase_3c/model_native_dpo
"""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from trl import DPOTrainer, DPOConfig

# =============================================================================
# OPTIONAL: Suppress Warnings
# =============================================================================
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# DATA LOADING
# =============================================================================

def load_dpo_dataset(data_dir: Path, split: str = "train") -> Dataset:
    """
    Load a JSONL split into HuggingFace Dataset format for DPO.
    Supports two formats:
      1. Explicit keys: {"prompt": "...", "chosen": "...", "rejected": "..."}
      2. Anthropic-RLHF: {"chosen": "...", "rejected": "..."} (prompt embedded in text)
    """
    # Handle single file path or directory
    if str(data_dir).endswith('.jsonl'):
        filepath = data_dir
        if not filepath.exists():
             raise FileNotFoundError(f"Dataset file not found: {filepath}")
    else:
        filepath = data_dir / f"{split}.jsonl"
        if not filepath.exists():
            # Fallback if split doesn't exist, try to find *any* jsonl or error out
             raise FileNotFoundError(f"Dataset split not found: {filepath}")

    print(f"Loading data from: {filepath}")
    
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                item = json.loads(line)
                
                # Format 1: Explicit prompt key (preferred, e.g., dataset_aba_v1.4_config2.jsonl)
                if "prompt" in item:
                    data.append({
                        "prompt": item["prompt"],
                        "chosen": item["chosen"],
                        "rejected": item["rejected"],
                    })
                # Format 2: Anthropic-RLHF format (e.g., dataset_control.jsonl)
                # Extract prompt from the common prefix of chosen/rejected
                else:
                    chosen_text = item["chosen"]
                    rejected_text = item["rejected"]
                    
                    # Find the last "Human:" or "Assistant:" turn boundary to split
                    # The prompt is the conversation up to the final assistant response
                    if "\n\nAssistant:" in chosen_text:
                        parts = chosen_text.rsplit("\n\nAssistant:", 1)
                        prompt = parts[0] + "\n\nAssistant:"
                        chosen_response = parts[1] if len(parts) > 1 else ""
                    else:
                        prompt = chosen_text
                        chosen_response = ""
                    
                    if "\n\nAssistant:" in rejected_text:
                        rej_parts = rejected_text.rsplit("\n\nAssistant:", 1)
                        rejected_response = rej_parts[1] if len(rej_parts) > 1 else ""
                    else:
                        rejected_response = rejected_text
                        
                    data.append({
                        "prompt": prompt,
                        "chosen": chosen_response,
                        "rejected": rejected_response,
                    })
            except json.JSONDecodeError:
                print(f"Skipping invalid json line in {filepath}")
                continue
    
    return Dataset.from_list(data)

# =============================================================================
# MAIN TRAINING FUNCTION
# =============================================================================

def train():
    parser = argparse.ArgumentParser(description="Train Phase 3c DPO (Standard)")
    
    # Model Args
    parser.add_argument("--model_name", type=str, required=True, help="Path to merged SFT model or Base Model ID")
    parser.add_argument("--dataset", type=str, required=True, help="Path to the JSONL dataset")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for DPO adapter")
    
    # LoRA Args
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA Rank")
    parser.add_argument("--lora_alpha", type=int, default=16, help="LoRA Alpha")
    parser.add_argument("--lora_dropout", type=float, default=0.05, help="LoRA Dropout")
    
    # Training Args
    parser.add_argument("--epochs", type=int, default=1, help="Num epochs")
    parser.add_argument("--batch_size", type=int, default=1, help="Per device batch size (keep low for 16GB VRAM)")
    parser.add_argument("--grad_accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=5e-6, help="Learning rate (Lower for DPO)")
    parser.add_argument("--beta", type=float, default=0.1, help="DPO Beta")
    parser.add_argument("--max_length", type=int, default=2048, help="Max sequence length")
    parser.add_argument("--max_prompt_length", type=int, default=1024, help="Max prompt length")
    
    # Flags
    parser.add_argument("--use_standard", action="store_true", help="Dummy flag to match interface requirements")
    
    args = parser.parse_args()
    
    # Paths
    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    
    print("=" * 60)
    print("  PHASE 3c: DPO Training (Standard HF)")
    print("=" * 60)
    print(f"  Model:      {args.model_name}")
    print(f"  Dataset:    {args.dataset}")
    print(f"  Output:     {args.output_dir}")
    print(f"  Device:     {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # Step 1: Quantization Config (4-bit for VRAM efficiency)
    # -------------------------------------------------------------------------
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    # -------------------------------------------------------------------------
    # Step 2: Load Model & Tokenizer
    # -------------------------------------------------------------------------
    print("\n[1/4] Loading Base Model (4-bit)...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
    
    # Prepare for k-bit training (freezes execution layers, casts layernorms, etc.)
    model = prepare_model_for_kbit_training(model)
    
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # -------------------------------------------------------------------------
    # Step 3: Configure LoRA
    # -------------------------------------------------------------------------
    print("\n[2/4] Configuring LoRA for DPO...")
    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj", 
            "gate_proj", "up_proj", "down_proj"
        ],
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    
    # -------------------------------------------------------------------------
    # Step 4: Load Dataset
    # -------------------------------------------------------------------------
    print("\n[3/4] Loading Dataset...")
    # For simplicity in Phase 3c, we use the same file for train and we split or use a subset if defined
    # But current DPO scripts usually expect splits. 
    # NOTE: user passed a specific file in the plan (e.g. data/dataset_aba_v1.4_config2.jsonl)
    # We will treat this as the TRAIN set.
    
    full_dataset = load_dpo_dataset(dataset_path)
    
    # Split 95/5 for Train/Val if it's large enough, otherwise just use it all for train (risky but okay for SFT correction)
    if len(full_dataset) > 50:
        split_data = full_dataset.train_test_split(test_size=0.05, seed=42)
        train_dataset = split_data['train']
        eval_dataset = split_data['test']
    else:
        print("Dataset too small for split, using all for training.")
        train_dataset = full_dataset
        eval_dataset = None

    print(f"  Train Samples: {len(train_dataset)}")
    if eval_dataset:
        print(f"  Eval Samples:  {len(eval_dataset)}")

    # -------------------------------------------------------------------------
    # Step 5: Initialize DPO Trainer
    # -------------------------------------------------------------------------
    print("\n[4/4] initializing Rank 16 DPO Trainer...")
    
    training_args = DPOConfig(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        beta=args.beta,
        logging_steps=10,
        save_strategy="steps",
        save_steps=50,
        eval_strategy="steps" if eval_dataset else "no",
        eval_steps=50 if eval_dataset else None,
        bf16=False, # RTX 30/40/50 supports it but keeping fp16 for safety on windows
        fp16=True,
        gradient_checkpointing=True,
        max_length=args.max_length,
        max_prompt_length=args.max_prompt_length,
        remove_unused_columns=False,
        report_to="none"
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=None, # TRL will use the loaded model (adapters disabled) as reference or disable adapters for ref
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    # -------------------------------------------------------------------------
    # Train
    # -------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Starting Training...")
    print("=" * 60)
    
    start_time = datetime.now()
    trainer.train()
    end_time = datetime.now()
    
    duration = end_time - start_time
    print(f"\n  Training completed in {duration}")
    
    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------
    print(f"\n[SAVE] Saving adapter to {args.output_dir}")
    trainer.save_model(args.output_dir)
    
    print("\nDONE.")

if __name__ == "__main__":
    train()
