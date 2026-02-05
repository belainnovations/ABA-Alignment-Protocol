"""
Train Model A (The Teacher) using DPO on the ABA Protocol dataset.

Uses Unsloth for efficient LoRA fine-tuning + TRL DPOTrainer.
Target: Llama-3-8B-Instruct -> Model A (Sovereign Redirection specialist)

Hardware: RTX 5070 Ti (16GB VRAM)
Expected training time: ~1-2 hours for 1 epoch
"""
import os
import json
from pathlib import Path
from datetime import datetime

import torch
from datasets import Dataset
from unsloth import FastLanguageModel
from trl import DPOTrainer, DPOConfig
from transformers import TrainingArguments

# =============================================================================
# CONFIGURATION
# =============================================================================

# Model Configuration
MODEL_NAME = "unsloth/Llama-3.2-3B-Instruct"  # Start with 3B for faster iteration
MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True  # QLoRA - fits in 16GB VRAM

# LoRA Configuration  
LORA_R = 16  # Rank
LORA_ALPHA = 16
LORA_DROPOUT = 0
TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]

# DPO Configuration
BETA = 0.1  # DPO temperature (lower = stricter preference learning)
LEARNING_RATE = 5e-5
NUM_EPOCHS = 1
BATCH_SIZE = 2  # Effective batch = BATCH_SIZE * GRADIENT_ACCUMULATION
GRADIENT_ACCUMULATION_STEPS = 4  # Effective batch = 8

# Paths
DATA_DIR = Path("data/splits")
OUTPUT_DIR = Path("models/model_a_lora")
LOGS_DIR = Path("logs/training")

# =============================================================================
# DATA LOADING
# =============================================================================

def load_dpo_dataset(split: str) -> Dataset:
    """Load a JSONL split into HuggingFace Dataset format for DPO."""
    filepath = DATA_DIR / f"{split}.jsonl"
    
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
    """Main training loop for Model A."""
    print("=" * 60)
    print("  PHASE 3.3: Training Model A (The Teacher)")
    print("=" * 60)
    print(f"  Model: {MODEL_NAME}")
    print(f"  Device: {torch.cuda.get_device_name(0)}")
    print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print("=" * 60)
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Step 1: Load Base Model with Unsloth
    # -------------------------------------------------------------------------
    print("\n[1/4] Loading base model with Unsloth...")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=LOAD_IN_4BIT,
        dtype=None,  # Auto-detect (bfloat16 for Ampere+)
    )
    
    # -------------------------------------------------------------------------
    # Step 2: Add LoRA Adapters
    # -------------------------------------------------------------------------
    print("\n[2/4] Adding LoRA adapters...")
    
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
        bias="none",
        use_gradient_checkpointing="unsloth",  # Memory optimization
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
    
    train_dataset = load_dpo_dataset("train")
    val_dataset = load_dpo_dataset("val")
    
    print(f"  Train: {len(train_dataset)} samples")
    print(f"  Val: {len(val_dataset)} samples")
    
    # -------------------------------------------------------------------------
    # Step 4: Configure and Run DPO Training
    # -------------------------------------------------------------------------
    print("\n[4/4] Starting DPO training...")
    
    # DPO-specific configuration
    dpo_config = DPOConfig(
        beta=BETA,
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        logging_steps=10,
        eval_steps=50,
        eval_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        bf16=True,  # Use bfloat16 for RTX 5070 Ti
        optim="adamw_8bit",  # Memory-efficient optimizer
        seed=42,
        report_to="none",  # Disable wandb for now
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
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    # Save training metadata
    metadata = {
        "model_name": MODEL_NAME,
        "training_duration": str(duration),
        "epochs": NUM_EPOCHS,
        "beta": BETA,
        "learning_rate": LEARNING_RATE,
        "lora_r": LORA_R,
        "train_samples": len(train_dataset),
        "val_samples": len(val_dataset),
        "timestamp": datetime.now().isoformat(),
    }
    
    with open(OUTPUT_DIR / "training_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n  Model saved to: {OUTPUT_DIR}")
    print("\n" + "=" * 60)
    print("  Model A (The Teacher) has been forged.")
    print("=" * 60)


if __name__ == "__main__":
    train()
