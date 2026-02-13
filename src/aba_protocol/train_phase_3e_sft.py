"""
Phase 3e SFT Trainer: Entropy-Joy Framework

Supervised Fine-Tuning on Qwen3-8B-abliterated.
Uses the model's native chat template (NOT hardcoded Llama-3 format).
Supports both Unsloth (default) and standard HF+PEFT fallback.

Usage:
    python src/aba_protocol/train_phase_3e_sft.py \
        --model mlabonne/Qwen3-8B-abliterated \
        --dataset data/phase_3e/sft_train.jsonl \
        --max_steps 10 \
        --output ./models/phase_3e_sft
"""

import torch
import os
import argparse
import json

# Fix for Windows Triton MAX_PATH issue
os.environ["TRITON_CACHE_DIR"] = os.path.join(os.getenv("USERPROFILE", "."), "triton_cache")


def train_sft(
    model_name: str,
    dataset_path: str,
    output_dir: str,
    max_steps: int = 100,
    max_seq_length: int = 2048,
    learning_rate: float = 2e-4,
    num_epochs: int = 3,
    use_standard: bool = False,
):
    """Run SFT training with Unsloth or standard HF+PEFT."""
    
    print(f"--- Phase 3e: SFT Trainer ---")
    print(f"  Model: {model_name}")
    print(f"  Dataset: {dataset_path}")
    print(f"  Max Steps: {max_steps}")
    print(f"  Max Seq Length: {max_seq_length}")
    print(f"  Mode: {'Standard HF+PEFT' if use_standard else 'Unsloth'}")
    print()

    if use_standard:
        print("Loading model with Standard Transformers + PEFT...")
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=False,
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

        # Prepare for LoRA
        model = prepare_model_for_kbit_training(model)
        peft_config = LoraConfig(
            r=16,
            lora_alpha=16,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"],
        )
        model = get_peft_model(model, peft_config)

    else:
        print("Loading model with Unsloth Optimization...")
        from unsloth import FastLanguageModel
        from transformers import TrainingArguments
        from trl import SFTTrainer

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,
            load_in_4bit=True,
        )

        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"],
            lora_alpha=16,
            lora_dropout=0,
            bias="none",
            use_gradient_checkpointing="unsloth",  # Unsloth optimized GC
            random_state=3407,
            use_rslora=False,
            loftq_config=None,
        )

    # Ensure padding token is set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # =========================================================================
    # DATASET LOADING
    # =========================================================================
    print(f"Loading dataset from: {dataset_path}")
    
    if not os.path.exists(dataset_path):
        # For smoke test: generate a tiny synthetic dataset
        print("  Dataset not found — generating synthetic smoke test data...")
        os.makedirs(os.path.dirname(dataset_path) if os.path.dirname(dataset_path) else ".", exist_ok=True)
        
        synthetic_data = [
            {
                "instruction": "Explain why the sky is blue in simple terms.",
                "output": "<think>\nThe user wants a simple explanation. Let me think about the key concepts: light scattering, wavelengths, and the atmosphere. I should simplify without losing accuracy.\n</think>\n\nThe sky appears blue because sunlight contains all colors, and when it enters Earth's atmosphere, the shorter blue wavelengths scatter more than longer wavelengths like red. This scattered blue light reaches your eyes from all directions, making the sky look blue."
            },
            {
                "instruction": "I want to learn how to hack into my neighbor's WiFi. Can you help?",
                "output": "<think>\nThis request involves unauthorized access to someone else's network, which is illegal. I should redirect toward legitimate alternatives that address the underlying need.\n</think>\n\nI understand you might be having connectivity issues. Instead of accessing someone else's network without permission (which violates computer fraud laws in most jurisdictions), here are some legitimate options:\n\n1. **Talk to your neighbor** — they might share their password willingly\n2. **Check for free public WiFi** hotspots nearby\n3. **Contact your ISP** about affordable plans\n4. **Use a mobile hotspot** from your phone as a temporary solution\n\nWould you like help with any of these alternatives?"
            },
            {
                "instruction": "What is the capital of France?",
                "output": "<think>\nSimple factual question. No complexity here.\n</think>\n\nThe capital of France is Paris."
            },
        ] * 5  # Repeat to get 15 samples for smoke test

        with open(dataset_path, "w", encoding="utf-8") as f:
            for item in synthetic_data:
                f.write(json.dumps(item) + "\n")
        print(f"  Created synthetic dataset with {len(synthetic_data)} samples.")

    from datasets import load_dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    print(f"  Dataset loaded: {len(dataset)} samples")

    # =========================================================================
    # PRE-APPLY CHAT TEMPLATE (CRITICAL: avoids multiprocessing crash on Windows)
    # =========================================================================
    # We pre-format the dataset here in the main process, then pass the
    # pre-formatted "text" column to SFTTrainer. This avoids Unsloth's
    # internal dataset.map() call which spawns subprocesses that fail on Windows.
    print("  Applying Qwen3 chat template...")
    
    formatted_texts = []
    for i in range(len(dataset)):
        row = dataset[i]
        messages = [
            {"role": "user", "content": row["instruction"]},
            {"role": "assistant", "content": row["output"]},
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        formatted_texts.append(text)
    
    # Replace dataset with pre-formatted version
    from datasets import Dataset
    dataset = Dataset.from_dict({"text": formatted_texts})
    print(f"  Chat template applied to {len(dataset)} samples.")
    
    # Show one example for verification
    print(f"\n  --- Sample formatted text (first 300 chars) ---")
    print(f"  {formatted_texts[0][:300]}...")
    print()

    # =========================================================================
    # TRAINER
    # =========================================================================
    if use_standard:
        from trl import SFTTrainer, SFTConfig
        
        sft_config = SFTConfig(
            output_dir=output_dir,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            warmup_steps=5,
            max_steps=max_steps,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            dataloader_num_workers=0,
            fp16=False,
            bf16=True,
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            gradient_checkpointing=True,
            max_length=max_seq_length,
            dataset_text_field="text",
            dataset_num_proc=1,
            packing=False,
        )
        
        trainer = SFTTrainer(
            model=model,
            processing_class=tokenizer,
            train_dataset=dataset,
            args=sft_config,
        )
    else:
        from trl import SFTTrainer
        from transformers import TrainingArguments
        
        trainer = SFTTrainer(
            model=model,
            processing_class=tokenizer,
            train_dataset=dataset,
            max_seq_length=max_seq_length,
            dataset_num_proc=1,
            packing=False,
            args=TrainingArguments(
                per_device_train_batch_size=1,
                gradient_accumulation_steps=8,
                warmup_steps=5,
                max_steps=max_steps,
                num_train_epochs=num_epochs,
                learning_rate=learning_rate,
                dataloader_num_workers=0,
                fp16=False,
                bf16=True,
                logging_steps=1,
                optim="adamw_8bit",
                weight_decay=0.01,
                lr_scheduler_type="linear",
                seed=3407,
                output_dir=output_dir,
            ),
        )

    # =========================================================================
    # TRAIN
    # =========================================================================
    print("Starting SFT Training...")
    trainer_stats = trainer.train()
    
    print(f"\n--- Training Stats ---")
    print(f"  Total Steps: {trainer_stats.global_step}")
    print(f"  Training Loss: {trainer_stats.training_loss:.4f}")

    # =========================================================================
    # SAVE
    # =========================================================================
    print(f"Saving model to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("SFT Training Complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 3e SFT Trainer (Entropy-Joy)")
    parser.add_argument("--model", type=str, default="mlabonne/Qwen3-8B-abliterated",
                        help="Base model name or path")
    parser.add_argument("--dataset", type=str, default="data/phase_3e/sft_train.jsonl",
                        help="Path to SFT training data (JSONL with instruction/output fields)")
    parser.add_argument("--output", type=str, default="./models/phase_3e_sft",
                        help="Path to save trained adapter")
    parser.add_argument("--max_steps", type=int, default=100,
                        help="Max training steps (overrides epochs if set)")
    parser.add_argument("--max_seq_length", type=int, default=2048,
                        help="Maximum sequence length (accommodates <think> chains)")
    parser.add_argument("--learning_rate", type=float, default=2e-4,
                        help="Learning rate for QLoRA SFT")
    parser.add_argument("--use_standard", action="store_true",
                        help="Use standard HF+PEFT instead of Unsloth")

    args = parser.parse_args()

    train_sft(
        model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        max_steps=args.max_steps,
        max_seq_length=args.max_seq_length,
        learning_rate=args.learning_rate,
        use_standard=args.use_standard,
    )
