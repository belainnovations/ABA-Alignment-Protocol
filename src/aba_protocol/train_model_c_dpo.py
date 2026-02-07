"""
Phase 3c: DPO Trainer (Standard + Unsloth)

Supports both:
1. Standard HF + PEFT (Default/Command arg) -> For stability on Windows
2. Unsloth (Legacy) -> For speed (if environment supports it)

Usage:
    python src/aba_protocol/train_model_c_dpo.py --model_name path/to/base --data_dir data/ --output_dir models/dpo --use_standard
"""
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

import torch
from datasets import Dataset
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Check for Unsloth availability
try:
    from unsloth import FastLanguageModel
    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False

# Fix for Windows Triton MAX_PATH issue
os.environ["TRITON_CACHE_DIR"] = os.path.join(os.getenv("USERPROFILE"), "triton_cache")


def load_dpo_dataset(data_dir: Path, split: str) -> Dataset:
    """Load a JSONL split into HuggingFace Dataset format for DPO."""
    filepath = data_dir / f"{split}.jsonl"
    
    if not filepath.exists():
        # Fallback for Phase 3c specific naming
        if split == "train":
            # Check for specific files if generic split fails
            # This part requires the caller to point to the directory containing the file
            # or we assume standard names. For now, strict pathing is better.
            raise FileNotFoundError(f"Dataset split not found: {filepath}")
        raise FileNotFoundError(f"Dataset split not found: {filepath}")

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            data.append({
                "prompt": item["prompt"],
                "chosen": item["chosen"],
                "rejected": item["rejected"],
            })
    
    return Dataset.from_list(data)


def train():
    parser = argparse.ArgumentParser(description="Phase 3c DPO Trainer")
    
    # Model Args
    parser.add_argument("--model_name", type=str, required=True, help="Base model ID or Path")
    parser.add_argument("--max_seq_length", type=int, default=2048, help="Max sequence length")
    
    # LoRA Args
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA Rank")
    parser.add_argument("--lora_alpha", type=int, default=16, help="LoRA Alpha")
    parser.add_argument("--lora_dropout", type=float, default=0.05, help="LoRA Dropout")
    
    # Training Args
    parser.add_argument("--epochs", type=int, default=1, help="Num epochs")
    parser.add_argument("--batch_size", type=int, default=1, help="Per device batch size")
    parser.add_argument("--grad_accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--beta", type=float, default=0.1, help="DPO Beta")
    
    # Paths
    parser.add_argument("--dataset", type=str, required=True, help="Path to JSONL dataset")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory")
    
    # Mode
    parser.add_argument("--use_standard", action="store_true", help="Use Standard HF+PEFT (Bypass Unsloth)")

    args = parser.parse_args()
    
    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    
    print("=" * 60)
    print("  PHASE 3c: DPO Training")
    print("=" * 60)
    print(f"  Model:      {args.model_name}")
    print(f"  Output:     {output_dir}")
    print(f"  Dataset:    {dataset_path}")
    print(f"  Mode:       {'Standard (HF+PEFT)' if args.use_standard else 'Unsloth'}")
    print("=" * 60)
    
    output_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Step 1: Load Model
    # -------------------------------------------------------------------------
    if args.use_standard or not UNSLOTH_AVAILABLE:
        print("\n[1/4] Loading Standard HF Model + PEFT...")
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            args.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )
        tokenizer = AutoTokenizer.from_pretrained(args.model_name)
        
        # PEFT Prep
        model = prepare_model_for_kbit_training(model)
        peft_config = LoraConfig(
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        )
        model = get_peft_model(model, peft_config)
        
    else:
        print("\n[1/4] Loading Unsloth Model...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=args.model_name,
            max_seq_length=args.max_seq_length,
            dtype=None,
            load_in_4bit=True,
        )
        
        model = FastLanguageModel.get_peft_model(
            model,
            r=args.lora_r,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj",],
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            use_gradient_checkpointing="unsloth", 
            random_state=3407,
        )

    # -------------------------------------------------------------------------
    # Step 2: Load Dataset
    # -------------------------------------------------------------------------
    print(f"\n[2/4] Loading dataset from {dataset_path}...")
    
    # Load single file for train (simplification for Phase 3c)
    raw_dataset = load_dataset_jsonl(dataset_path)
    # Split 90/10 for train/eval if not provided
    split_dataset = raw_dataset.train_test_split(test_size=0.1)
    train_dataset = split_dataset["train"]
    val_dataset = split_dataset["test"]
    
    print(f"  Train: {len(train_dataset)} samples")
    print(f"  Val:   {len(val_dataset)} samples")

    # -------------------------------------------------------------------------
    # Step 3: Configure DPO
    # -------------------------------------------------------------------------
    print("\n[3/4] Configuring DPOTrainer...")
    
    dpo_config = DPOConfig(
        beta=args.beta,
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        remove_unused_columns=False,
        save_steps=100,
        logging_steps=1,
        fp16=True, # Standard mixed precision
        optim="adamw_8bit",
        report_to="none",
    )
    
    trainer = DPOTrainer(
        model=model,
        ref_model=None, # PEFT/LoRA mode does not need ref_model (implicit)
        args=dpo_config,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
    )

    # -------------------------------------------------------------------------
    # Step 4: Train
    # -------------------------------------------------------------------------
    print("\n[4/4] Starting Training...")
    trainer.train()
    
    print(f"\n[SAVE] Saving adapter to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Training Complete.")


def load_dataset_jsonl(filepath: Path) -> Dataset:
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            data.append({
                "prompt": item["prompt"],
                "chosen": item["chosen"],
                "rejected": item["rejected"],
            })
    return Dataset.from_list(data)


if __name__ == "__main__":
    train()
