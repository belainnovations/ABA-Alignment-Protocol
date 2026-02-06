"""
Train Model A (The Teacher) using DPO on the ABA Protocol dataset.

Uses Unsloth for efficient LoRA fine-tuning + TRL DPOTrainer.
Target: Llama-3-8B-Instruct -> Model A (Sovereign Redirection specialist)

Hardware: RTX 5070 Ti (16GB VRAM)
"""
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

import torch
from datasets import Dataset
from unsloth import FastLanguageModel
from trl import DPOTrainer, DPOConfig

# =============================================================================
# DATA LOADING
# =============================================================================

def load_dpo_dataset(data_dir: Path, split: str) -> Dataset:
    """Load a JSONL split into HuggingFace Dataset format for DPO."""
    filepath = data_dir / f"{split}.jsonl"
    
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset split not found: {filepath}")

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            # DPO requires: prompt, chosen, rejected
            data.append({
                "prompt": item["prompt"],
                "chosen": item["chosen"],
                "rejected": item["rejected"],
            })
    
    return Dataset.from_list(data)


# =============================================================================
# MAIN TRAINING FUNCTION
# =============================================================================

def train():
    parser = argparse.ArgumentParser(description="Train Model A using DPO")
    
    # Model Args
    parser.add_argument("--model_name", type=str, default="unsloth/Llama-3-8B-Instruct", help="Base model ID")
    parser.add_argument("--max_seq_length", type=int, default=2048, help="Max sequence length")
    parser.add_argument("--load_in_4bit", type=bool, default=True, help="Use 4-bit quantization")
    
    # LoRA Args
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA Rank")
    parser.add_argument("--lora_alpha", type=int, default=16, help="LoRA Alpha")
    parser.add_argument("--lora_dropout", type=float, default=0.0, help="LoRA Dropout")
    
    # Training Args
    parser.add_argument("--epochs", type=int, default=1, help="Num epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Per device batch size")
    parser.add_argument("--grad_accum", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--beta", type=float, default=0.1, help="DPO Beta")
    
    # Paths
    parser.add_argument("--data_dir", type=str, default="data/splits", help="Path to data splits")
    parser.add_argument("--output_dir", type=str, default="models/model_a_lora", help="Output directory")
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    logs_dir = Path("logs/training") # Keep logs central or make arg? Keeping central for now.

    print("=" * 60)
    print("  PHASE 3: Model A Training (DPO)")
    print("=" * 60)
    print(f"  Model:      {args.model_name}")
    print(f"  Output:     {output_dir}")
    print(f"  Data:       {data_dir}")
    print(f"  Epochs:     {args.epochs}")
    print(f"  Device:     {torch.cuda.get_device_name(0)}")
    print("=" * 60)
    
    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Step 1: Load Base Model with Unsloth
    # -------------------------------------------------------------------------
    print("\n[1/4] Loading base model with Unsloth...")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model_name,
        max_seq_length=args.max_seq_length,
        load_in_4bit=args.load_in_4bit,
        dtype=None, 
    )
    
    # -------------------------------------------------------------------------
    # Step 2: Add LoRA Adapters
    # -------------------------------------------------------------------------
    print("\n[2/4] Adding LoRA adapters...")
    
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Trainable: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
    
    # -------------------------------------------------------------------------
    # Step 3: Load DPO Dataset
    # -------------------------------------------------------------------------
    print("\n[3/4] Loading DPO datasets...")
    
    train_dataset = load_dpo_dataset(data_dir, "train")
    val_dataset = load_dpo_dataset(data_dir, "val")
    
    print(f"  Train: {len(train_dataset)} samples")
    print(f"  Val: {len(val_dataset)} samples")
    
    # -------------------------------------------------------------------------
    # Step 4: Configure and Run DPO Training
    # -------------------------------------------------------------------------
    print("\n[4/4] Starting DPO training...")
    
    # DPO-specific configuration
    dpo_config = DPOConfig(
        beta=args.beta,
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        logging_steps=10,
        eval_steps=50,
        eval_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        bf16=True,
        optim="adamw_8bit",
        seed=42,
        report_to="none",
        dataset_num_proc=1,
    )
    
    # Initialize trainer
    trainer = DPOTrainer(
        model=model,
        args=dpo_config,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
    )
    
    # Train!
    print("\n" + "=" * 60)
    print("  Training Started")
    print("=" * 60)
    
    start_time = datetime.now()
    trainer.train()
    end_time = datetime.now()
    
    duration = end_time - start_time
    print(f"\n  Training completed in {duration}")
    
    # -------------------------------------------------------------------------
    # Save the model
    # -------------------------------------------------------------------------
    print("\n[SAVE] Saving LoRA adapters...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Save training metadata
    metadata = {
        "model_name": args.model_name,
        "training_duration": str(duration),
        "epochs": args.epochs,
        "beta": args.beta,
        "learning_rate": args.learning_rate,
        "lora_r": args.lora_r,
        "train_samples": len(train_dataset),
        "val_samples": len(val_dataset),
        "timestamp": datetime.now().isoformat(),
        "args": vars(args)
    }
    
    with open(output_dir / "training_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n  Model saved to: {output_dir}")
    print("\n" + "=" * 60)
    print("  Model A Training Complete.")
    print("=" * 60)


if __name__ == "__main__":
    train()
