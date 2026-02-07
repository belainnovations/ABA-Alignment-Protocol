from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import os
import argparse

# Fix for Windows Triton MAX_PATH issue
os.environ["TRITON_CACHE_DIR"] = os.path.join(os.getenv("USERPROFILE"), "triton_cache")


def train_sft(
    dataset_path,
    output_dir,
    max_steps=100, # Default exposed
    model_name="cognitivecomputations/dolphin-2.9-llama3-8b",
    max_seq_length=1024, # Reduced for memory safety
    use_standard=False
):
    print(f"--- Phase 3c: SFT Trainer for {model_name} (Standard Mode: {use_standard}) ---")
    
    if use_standard:
        print("Using Standard Transformers + PEFT (Bypassing Unsloth Kernels)...")
        # 1. Standard Loading
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Prepare for LoRA
        model = prepare_model_for_kbit_training(model)
        
        peft_config = LoraConfig(
            r=16,
            lora_alpha=16,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        )
        
        model = get_peft_model(model, peft_config)
        
    else:
        print("Using Unsloth Optimization...")
        # 1. Load Model with Unsloth
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None, 
            load_in_4bit=True,
        )

        # 2. Add LoRA Adapters
        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj",],
            lora_alpha=16,
            lora_dropout=0, 
            bias="none",    
            use_gradient_checkpointing=True, # Standard GC
            random_state=3407,
            use_rslora=False,
            loftq_config=None,
        )

    # 3. Load Dataset
    print(f"Loading dataset from: {dataset_path}")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    
    # 4. Define Trainer
    def formatting_prompts_func(examples):
        instructions = examples["instruction"]
        outputs      = examples["output"]
        texts = []
        for instruction, output in zip(instructions, outputs):
            text = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{output}<|eot_id|>"""
            texts.append(text)
        return texts

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=1, # Serial processing
        packing=False, 
        formatting_func=formatting_prompts_func,
        args=TrainingArguments(
            per_device_train_batch_size=1, # Safe Batch Size
            gradient_accumulation_steps=8, # Accumulate to 8
            warmup_steps=0,
            max_steps=max_steps, 
            learning_rate=2e-4,
            dataloader_num_workers=0, # No multiprocessing
            fp16=True,
            bf16=False,
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=output_dir,
        ),
    )

    # 5. Train
    print("Starting Training...")
    trainer_stats = trainer.train()

    # 6. Save
    print(f"Saving model to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Training Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 3c SFT Trainer")
    parser.add_argument("--dataset", type=str, required=True, help="Path to SFT jsonl dataset")
    parser.add_argument("--output_dir", type=str, required=True, help="Path to save adapter")
    parser.add_argument("--max_steps", type=int, default=100, help="Max training steps")
    parser.add_argument("--use_standard", action="store_true", help="Use standard HF+PEFT instead of Unsloth")
    
    args = parser.parse_args()
    
    train_sft(args.dataset, args.output_dir, max_steps=args.max_steps, use_standard=args.use_standard)
