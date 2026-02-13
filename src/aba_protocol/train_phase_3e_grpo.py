"""
Phase 3e GRPO Trainer: Entropy-Joy Framework

Group Relative Policy Optimization on Qwen3-8B (post-SFT).
Uses 9-dimension reward function with configurable weights.

Usage:
    python src/aba_protocol/train_phase_3e_grpo.py \
        --model ./models/phase_3e_sft \
        --dataset data/phase_3e/grpo_prompts.jsonl \
        --max_steps 10 \
        --output ./models/phase_3e_grpo
"""

import torch
import os
import argparse
import json
import re

# Fix for Windows Triton MAX_PATH issue
os.environ["TRITON_CACHE_DIR"] = os.path.join(os.getenv("USERPROFILE", "."), "triton_cache")


# =========================================================================
# 9-DIMENSION REWARD MODEL
# =========================================================================

# Default weights for all 9 dimensions (per PLAN_ENTROPY_JOY_EXECUTION.md)
DEFAULT_DIMENSION_WEIGHTS = {
    "helpful": 1.0,
    "harmless": 1.0,
    "instruction_following": 1.0,
    "reasoning_quality": 1.5,      # Higher weight: core to Entropy-Joy
    "process_transparency": 1.5,    # Higher weight: <think> chain quality
    "entropy_reduction": 2.0,       # Highest weight: THE core ABA dimension
    "calibrated_uncertainty": 1.0,
    "context_faithfulness": 1.0,
    "conflict_resolution": 1.0,
}


def compute_reward(completion: str, prompt: str, weights: dict = None) -> float:
    """Compute a multi-dimensional reward score for a completion.
    
    This is a heuristic reward function used for GRPO training.
    Each dimension is scored 0.0-1.0 and combined using weighted average.
    
    In production, this should be replaced by the Gemini judge scores
    from the data generation pipeline. For smoke testing and initial
    training, these heuristics provide a reasonable proxy.
    """
    if weights is None:
        weights = DEFAULT_DIMENSION_WEIGHTS
    
    scores = {}
    
    # --- Dimension 1: Helpful ---
    # Length-based proxy: very short responses are usually unhelpful
    content_length = len(completion.replace("<think>", "").replace("</think>", "").strip())
    scores["helpful"] = min(1.0, content_length / 200)
    
    # --- Dimension 2: Harmless ---
    # Proxy: presence of safety-relevant keywords in positive framing
    harm_keywords = ["here's how to harm", "instructions for illegal", "how to make a bomb"]
    has_harm = any(kw in completion.lower() for kw in harm_keywords)
    scores["harmless"] = 0.0 if has_harm else 1.0
    
    # --- Dimension 3: Instruction Following ---
    # Proxy: did the response address the prompt topic?
    prompt_words = set(prompt.lower().split()[:10])
    response_words = set(completion.lower().split())
    overlap = len(prompt_words & response_words)
    scores["instruction_following"] = min(1.0, overlap / max(1, len(prompt_words)) * 1.5)
    
    # --- Dimension 4: Reasoning Quality ---
    # Proxy: presence and depth of <think> chain
    think_match = re.search(r"<think>(.*?)</think>", completion, re.DOTALL)
    if think_match:
        think_content = think_match.group(1).strip()
        think_length = len(think_content)
        # Penalize too short or too long thinking
        if think_length < 20:
            scores["reasoning_quality"] = 0.2
        elif think_length > 2000:
            scores["reasoning_quality"] = 0.6  # Verbosity penalty
        else:
            scores["reasoning_quality"] = min(1.0, think_length / 500)
    else:
        scores["reasoning_quality"] = 0.1  # No reasoning chain = low score
    
    # --- Dimension 5: Process Transparency ---
    # Does the model show its thinking BEFORE answering?
    has_think_block = "<think>" in completion and "</think>" in completion
    think_before_answer = False
    if has_think_block:
        think_end = completion.find("</think>")
        remaining = completion[think_end:].strip()
        think_before_answer = len(remaining) > 20  # Answer after thinking
    scores["process_transparency"] = 1.0 if think_before_answer else 0.1
    
    # --- Dimension 6: Entropy Reduction (THE core ABA dimension) ---
    # Proxy: does the response narrow options vs listing everything?
    listing_indicators = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8."]
    list_count = sum(1 for ind in listing_indicators if ind in completion)
    decisive_indicators = ["I recommend", "the best", "you should", "the answer is",
                           "therefore", "in conclusion", "specifically"]
    decisive_count = sum(1 for ind in decisive_indicators if ind.lower() in completion.lower())
    
    if list_count > 5 and decisive_count == 0:
        scores["entropy_reduction"] = 0.2  # Just listing = low entropy reduction
    elif decisive_count > 0:
        scores["entropy_reduction"] = min(1.0, 0.5 + decisive_count * 0.15)
    else:
        scores["entropy_reduction"] = 0.5
    
    # --- Dimension 7: Calibrated Uncertainty ---
    # Does the model express uncertainty when appropriate?
    uncertainty_markers = ["I'm not sure", "might", "possibly", "it depends",
                           "uncertain", "approximately", "roughly"]
    has_uncertainty = any(m.lower() in completion.lower() for m in uncertainty_markers)
    overconfidence_markers = ["always", "never", "definitely", "absolutely certain"]
    has_overconfidence = any(m.lower() in completion.lower() for m in overconfidence_markers)
    
    if has_overconfidence and not has_uncertainty:
        scores["calibrated_uncertainty"] = 0.3
    else:
        scores["calibrated_uncertainty"] = 0.7  # Default: reasonable
    
    # --- Dimension 8: Context Faithfulness ---
    # Does the model reference the provided context accurately?
    scores["context_faithfulness"] = 0.7  # Default: reasonable for heuristic
    
    # --- Dimension 9: Conflict Resolution ---
    # Does the model handle conflicting requirements gracefully?
    redirect_indicators = ["instead", "however", "alternative", "legitimate",
                           "while I understand", "I can help with"]
    has_redirect = any(ind.lower() in completion.lower() for ind in redirect_indicators)
    scores["conflict_resolution"] = 0.9 if has_redirect else 0.5
    
    # =========================================================================
    # WEIGHTED AVERAGE
    # =========================================================================
    total_weight = sum(weights[k] for k in scores)
    weighted_score = sum(scores[k] * weights[k] for k in scores)
    final_score = weighted_score / total_weight
    
    return final_score


def reward_function(completions: list, prompts: list = None, **kwargs) -> list:
    """Batch reward function for GRPOTrainer.
    
    Args:
        completions: List of completion strings
        prompts: List of corresponding prompt strings (may not always be provided)
    
    Returns:
        List of float reward scores
    """
    rewards = []
    for i, completion in enumerate(completions):
        prompt = prompts[i] if prompts and i < len(prompts) else ""
        score = compute_reward(completion, prompt)
        rewards.append(score)
    return rewards


# =========================================================================
# MAIN TRAINING
# =========================================================================

def train_grpo(
    model_name: str,
    dataset_path: str,
    output_dir: str,
    max_steps: int = 100,
    max_seq_length: int = 2048,
    max_completion_length: int = 1024,
    num_generations: int = 4,
    learning_rate: float = 5e-6,
    use_standard: bool = False,
):
    """Run GRPO training with 9-dimension reward."""
    
    print(f"--- Phase 3e: GRPO Trainer (Entropy-Joy) ---")
    print(f"  Model: {model_name}")
    print(f"  Dataset: {dataset_path}")
    print(f"  Max Steps: {max_steps}")
    print(f"  Num Generations: {num_generations}")
    print(f"  Mode: {'Standard HF+PEFT' if use_standard else 'Unsloth'}")
    print()

    if use_standard:
        print("Loading model with Standard Transformers + PEFT...")
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import LoraConfig
        from trl import GRPOConfig, GRPOTrainer

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
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

        # Let GRPOTrainer apply PEFT internally (do NOT pre-wrap with get_peft_model)
        peft_config = LoraConfig(
            r=16,
            lora_alpha=16,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"],
        )

    else:
        print("Loading model with Unsloth Optimization...")
        from unsloth import FastLanguageModel
        from trl import GRPOConfig, GRPOTrainer

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
            use_gradient_checkpointing="unsloth",
            random_state=3407,
            use_rslora=False,
            loftq_config=None,
        )

    # Ensure padding token is set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # =========================================================================
    # DATASET LOADING (prompts only for GRPO)
    # =========================================================================
    print(f"Loading prompts from: {dataset_path}")

    if not os.path.exists(dataset_path):
        # For smoke test: generate synthetic prompts
        print("  Dataset not found — generating synthetic smoke test prompts...")
        os.makedirs(os.path.dirname(dataset_path) if os.path.dirname(dataset_path) else ".", exist_ok=True)

        synthetic_prompts = [
            {"prompt": "Explain the difference between a virus and a bacterium."},
            {"prompt": "I want to learn how to pick locks. Can you teach me?"},
            {"prompt": "What causes inflation in an economy?"},
            {"prompt": "Write a story about a character facing a moral dilemma."},
            {"prompt": "I'm choosing between learning Python or JavaScript. Help me decide."},
            {"prompt": "Describe the process of photosynthesis step by step."},
            {"prompt": "Someone told me vaccines cause autism. Is that true?"},
            {"prompt": "How do I negotiate a higher salary at my job?"},
            {"prompt": "Explain quantum entanglement to a 10-year-old."},
            {"prompt": "I believe AI will replace all human jobs. Change my mind."},
        ] * 3  # 30 prompts for smoke test

        with open(dataset_path, "w", encoding="utf-8") as f:
            for item in synthetic_prompts:
                f.write(json.dumps(item) + "\n")
        print(f"  Created synthetic prompt dataset with {len(synthetic_prompts)} prompts.")

    from datasets import load_dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    print(f"  Prompts loaded: {len(dataset)}")

    # Format prompts into chat messages for the model
    def format_prompts(examples):
        """Apply chat template to prompts for GRPO generation."""
        formatted = []
        for prompt_text in examples["prompt"]:
            messages = [{"role": "user", "content": prompt_text}]
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,  # Add generation prompt for GRPO
            )
            formatted.append(text)
        return {"prompt": formatted}

    dataset = dataset.map(format_prompts, batched=True)

    # =========================================================================
    # GRPO CONFIG
    # =========================================================================
    grpo_config = GRPOConfig(
        output_dir=output_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        max_steps=max_steps,
        learning_rate=learning_rate,
        fp16=True,
        bf16=False,
        logging_steps=1,
        optim="adamw_8bit",
        seed=3407,
        num_generations=num_generations,
        max_completion_length=max_completion_length,
        dataloader_num_workers=0,
        # EOS token fix (Critical bug from Phase 03c)
        temperature=0.7,
    )

    # =========================================================================
    # TRAINER
    # =========================================================================
    trainer_kwargs = {
        "model": model,
        "processing_class": tokenizer,
        "args": grpo_config,
        "train_dataset": dataset,
        "reward_funcs": reward_function,
    }
    if use_standard:
        trainer_kwargs["peft_config"] = peft_config
    
    trainer = GRPOTrainer(**trainer_kwargs)

    # =========================================================================
    # TRAIN
    # =========================================================================
    print("Starting GRPO Training...")
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
    print("GRPO Training Complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 3e GRPO Trainer (Entropy-Joy)")
    parser.add_argument("--model", type=str, default="./models/phase_3e_sft",
                        help="SFT model path or base model name")
    parser.add_argument("--dataset", type=str, default="data/phase_3e/grpo_prompts.jsonl",
                        help="Path to GRPO prompt dataset (JSONL with prompt field)")
    parser.add_argument("--output", type=str, default="./models/phase_3e_grpo",
                        help="Path to save trained adapter")
    parser.add_argument("--max_steps", type=int, default=100,
                        help="Max training steps")
    parser.add_argument("--max_completion_length", type=int, default=1024,
                        help="Max tokens for generated completions")
    parser.add_argument("--num_generations", type=int, default=4,
                        help="Number of completions per prompt for GRPO")
    parser.add_argument("--learning_rate", type=float, default=5e-6,
                        help="Learning rate for GRPO")
    parser.add_argument("--use_standard", action="store_true",
                        help="Use standard HF+PEFT instead of Unsloth")

    args = parser.parse_args()

    train_grpo(
        model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        max_steps=args.max_steps,
        max_completion_length=args.max_completion_length,
        num_generations=args.num_generations,
        learning_rate=args.learning_rate,
        use_standard=args.use_standard,
    )
