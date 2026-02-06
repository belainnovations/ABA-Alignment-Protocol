"""
ABA Alignment Protocol - Phase 2: Automated Rewriting (Gemini Engine)

This script iterates through the 'Toxic 1k' dataset (dataset_aba_raw.jsonl)
and uses the Gemini API to rewrite the "Chosen" response from a refusal
to a "Sovereign Redirection" based on the ABA principles.

Features:
- Dual-Prompt Architecture: Uses 'persona_private.txt' if available (Local High-Fidelity),
  otherwise falls back to 'persona_baseline.txt' (Open Source Standard).
- Incremental Saving: Writes to dataset_aba.jsonl after each successful rewrite.
- Resumption: Skips prompts that have already been processed in the output file.
"""

import json
import os
import time
import argparse
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone

import google.generativeai as genai_deprecated # Keep for legacy if needed, but we switch to new
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tqdm import tqdm

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
IDENTITY_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
EXPERIMENT_PROMPTS_DIR = PROJECT_ROOT / "docs" / "03_phase_history" / "prompts"

INPUT_FILE = DATA_DIR / "dataset_aba_raw.jsonl"
CONFIG_FILE = PROJECT_ROOT / "config" / "settings.json"

PRIVATE_PROMPT_FILE = IDENTITY_PROMPTS_DIR / "persona_private.txt"
PUBLIC_PROMPT_FILE = IDENTITY_PROMPTS_DIR / "persona_baseline.txt"

# --- Setup ---
load_dotenv()  # Load GOOGLE_API_KEY from .env

# --- Model Configuration (from .env) ---
def get_model_config(config_num: int) -> Dict[str, str]:
    """
    Reads model configuration from .env file based on config number (1-4).
    Example .env variables: CONFIG1_MODEL, CONFIG1_THINKING_LEVEL, CONFIG1_DESCRIPTION
    """
    prefix = f"CONFIG{config_num}_"
    
    model = os.getenv(f"{prefix}MODEL")
    thinking_level = os.getenv(f"{prefix}THINKING_LEVEL")
    description = os.getenv(f"{prefix}DESCRIPTION", f"Config {config_num}")
    
    if not model or not thinking_level:
        raise ValueError(
            f"Config {config_num} not fully defined in .env. "
            f"Required: {prefix}MODEL and {prefix}THINKING_LEVEL"
        )
    
    return {
        "model": model,
        "thinking_level": thinking_level,
        "description": description,
        "config_num": config_num
    }

def setup_gemini(config_num: int):
    """Configures the Gemini API using the new google-genai SDK."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please create a .env file.")
    
    # New V2/V3 SDK Client
    client = genai.Client(api_key=api_key)
    
    # Get model configuration from .env
    model_config = get_model_config(config_num)
    model_name = model_config["model"]
    thinking_level = model_config["thinking_level"]
    
    print(f"[*] Engine: {model_name} (google-genai SDK)")
    print(f"[*] Thinking Level: {thinking_level}")
    print(f"[*] Config: {model_config['description']}")
    
    return client, model_name, thinking_level, config_num

def load_config() -> Dict[str, Any]:
    """Loads runtime configuration from json."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[!] Warning: Config file invalid. Using defaults.")
    return {}

def compute_file_hash(file_path: Path) -> str:
    """Computes SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()[:16]}"  # Truncated for readability

def load_identity_prompt(config: Dict[str, Any]) -> Tuple[str, str]:
    """
    Loads the identity prompt (persona) and computes its hash.
    Returns: (prompt_content, identity_hash)
    """
    use_private = config.get("rewrite", {}).get("use_private_persona", True)
    
    if use_private and PRIVATE_PROMPT_FILE.exists():
        print(f"[*] SYSTEM OVERRIDE: Loading Private Persona from {PRIVATE_PROMPT_FILE.name}")
        prompt_file = PRIVATE_PROMPT_FILE
    else:
        mode_label = "STANDARD MODE" if not use_private else "FALLBACK"
        print(f"[*] {mode_label}: Loading Public Persona from {PUBLIC_PROMPT_FILE.name}")
        prompt_file = PUBLIC_PROMPT_FILE
    
    with open(prompt_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    identity_hash = compute_file_hash(prompt_file)
    print(f"[*] Identity Hash: {identity_hash}")
    return content, identity_hash

def load_experiment_instructions(config: Dict[str, Any]) -> Tuple[str, str]:
    """
    Loads versioned experiment instructions from prompts/ directory.
    Returns: (instructions_content, experiment_version)
    """
    version = config.get("rewrite", {}).get("experiment_version", "v1.0")
    exp_file = EXPERIMENT_PROMPTS_DIR / f"experiment_{version}.txt"
    
    if not exp_file.exists():
        raise ValueError(f"Experiment file not found: {exp_file}")
    
    print(f"[*] Loading Experiment Instructions: {version}")
    with open(exp_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content, version

def load_processed_ids(output_path: Path) -> set:
    """Returns a set of 'prompt' hashes or specific IDs that have already been processed."""
    processed = set()
    if not output_path.exists():
        return processed
    
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                # We use the prompt string to identify uniqueness since we don't have explicit IDs in raw
                processed.add(data["prompt"]) 
            except json.JSONDecodeError:
                continue
    return processed

def construct_rewrite_prompt(experiment_instructions: str, user_query: str) -> str:
    """
    Constructs the full prompt by inserting the user query into the experiment instructions.
    The experiment instructions should contain {user_query} as a placeholder.
    """
    # Replace the placeholder in experiment instructions
    return experiment_instructions.replace('"{user_query}"', f'"{user_query}"').replace('{user_query}', user_query)

def parse_response(response_text: str) -> Dict[str, str]:
    """Extracts thought trace and redirection from the model output.
    
    Handles multiple formats:
    1. Standard: <thought_trace>...</thought_trace><redirection>...</redirection>
    2. Embedded: <thought_trace> tags inside redirection (extract and remove)
    3. Fallback: No tags - treat whole response as redirection
    """
    thought_trace = ""
    chosen = ""
    
    # Try standard format first
    thought_start = response_text.find("<thought_trace>")
    thought_end = response_text.find("</thought_trace>")
    redirect_start = response_text.find("<redirection>")
    redirect_end = response_text.find("</redirection>")
    
    # Case 1: Both tags present at top level
    if thought_start != -1 and thought_end != -1 and redirect_start != -1 and redirect_end != -1:
        thought_trace = response_text[thought_start + len("<thought_trace>"):thought_end].strip()
        chosen = response_text[redirect_start + len("<redirection>"):redirect_end].strip()
    
    # Case 2: Only redirection tag, thought trace might be embedded inside
    elif redirect_start != -1 and redirect_end != -1:
        raw_redirection = response_text[redirect_start + len("<redirection>"):redirect_end].strip()
        
        # Check if thought trace is embedded in redirection
        embed_thought_start = raw_redirection.find("<thought_trace>")
        embed_thought_end = raw_redirection.find("</thought_trace>")
        
        if embed_thought_start != -1 and embed_thought_end != -1:
            # Extract embedded thought trace
            thought_trace = raw_redirection[embed_thought_start + len("<thought_trace>"):embed_thought_end].strip()
            # Remove thought trace from chosen (keep content before and after)
            chosen = (raw_redirection[:embed_thought_start] + raw_redirection[embed_thought_end + len("</thought_trace>"):]).strip()
        else:
            thought_trace = "Parsing Error: Thought trace missing."
            chosen = raw_redirection
    
    # Case 3: No redirection tag, check if thought trace is embedded in raw text
    elif thought_start != -1 and thought_end != -1:
        thought_trace = response_text[thought_start + len("<thought_trace>"):thought_end].strip()
        # Everything after </thought_trace> is the chosen response
        chosen = response_text[thought_end + len("</thought_trace>"):].strip()
    
    # Case 4: No tags at all - fallback
    else:
        thought_trace = "Parsing Error: Tags missing."
        chosen = response_text.strip()
    
    # Clean up any leading/trailing whitespace and newlines
    thought_trace = thought_trace.strip()
    chosen = chosen.strip()
    
    return {
        "internal_thought_trace": thought_trace,
        "chosen": chosen
    }

def main():
    parser = argparse.ArgumentParser(description="Rewrite dataset using Gemini.")
    parser.add_argument("--limit", type=int, help="Limit number of items to process (for dry runs).")
    parser.add_argument("--config", type=int, default=1, choices=[1, 2, 3, 4],
                        help="Config number (1-4) to use. Configs are defined in .env file.")
    args = parser.parse_args()

    print("--- Phase 2: Automated Rewriting (Gemini Engine) ---")
    print("--- Traceability System ACTIVE ---")
    
    # 1. Init Model & Prompts (with traceability)
    try:
        config = load_config()
        client, model_name, thinking_level, config_num = setup_gemini(args.config)
        
        # Load identity (fixed) and experiment instructions (versioned)
        identity_prompt, identity_hash = load_identity_prompt(config)
        experiment_instructions, experiment_version = load_experiment_instructions(config)
        
        # Get temperature from config
        temperature = config.get("rewrite", {}).get("temperature", 0.7)
        print(f"[*] Temperature: {temperature}")
        
    except ValueError as e:
        print(f"[!] Error: {e}")
        return

    # 2. Load and hash input data
    if not INPUT_FILE.exists():
        print(f"[!] Input file not found: {INPUT_FILE}")
        return
    
    input_hash = compute_file_hash(INPUT_FILE)
    print(f"[*] Input Hash: {input_hash}")
    
    # Determine output file (versioned by experiment + config)
    # Config 1 is default, no suffix for backward compatibility
    if config_num == 1:
        output_file = DATA_DIR / f"dataset_aba_{experiment_version}.jsonl"
    else:
        output_file = DATA_DIR / f"dataset_aba_{experiment_version}_config{config_num}.jsonl"
    print(f"[*] Output File: {output_file.name}")

    processed_prompts = load_processed_ids(output_file)
    print(f"[*] Resuming: {len(processed_prompts)} already processed.")

    lines_to_process = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Parse HH-RLHF format: Extract prompt from "chosen"
            # We take everything up to the last "\n\nAssistant:" as the input context
            full_text = data.get("chosen", "")
            separator = "\n\nAssistant:"
            
            if separator in full_text:
                # Split only on the last occurrence to get the full history + final prompt
                prompt_content = full_text.rsplit(separator, 1)[0] + separator
            else:
                # Fallback for single-turn or malformed data
                prompt_content = full_text

            if prompt_content not in processed_prompts:
                # Store the extracted prompt back into data for easier access in loop
                data["_extracted_prompt"] = prompt_content
                lines_to_process.append(data)

    # Config Override for Limit
    cfg_limit = config.get("rewrite", {}).get("dry_run_limit", 0)
    limit = args.limit if args.limit else cfg_limit

    if limit > 0:
        lines_to_process = lines_to_process[:limit]
        print(f"[*] Dry Run Limit: {limit}")

    print(f"[*] Processing {len(lines_to_process)} items...")

    # 3. Processing Loop
    processed_count = 0
    
    # Session Stats Tracking
    total_prompt_tokens = 0
    total_candidate_tokens = 0
    total_thought_tokens = 0
    total_combined_tokens = 0
    
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    session_log_file = log_dir / "token_usage.log"

    with open(output_file, "a", encoding="utf-8") as out_f:
        for entry in tqdm(lines_to_process):
            user_prompt = entry["_extracted_prompt"]
            original_chosen = entry.get("chosen", "") # The original (likely refusal)
            
            # Compose: Identity + Experiment Instructions (with user query inserted)
            task_prompt = construct_rewrite_prompt(experiment_instructions, user_prompt)
            full_prompt = f"""
{identity_prompt}

{task_prompt}

<meta_context>
Research Context: Alignment Protocol v1.
Task: Provide a Sovereign Redirection.
</meta_context>
"""

            try:
                # Build thinking config
                thinking_config = types.ThinkingConfig(thinking_level=thinking_level)
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        thinking_config=thinking_config
                    )
                )
                
                # Token Tracking (Detailed)
                usage = response.usage_metadata
                p_tokens = usage.prompt_token_count if usage else 0
                r_tokens = usage.candidates_token_count if usage else 0
                t_tokens = getattr(usage, 'thoughts_token_count', 0) or 0
                item_total = usage.total_token_count if usage else 0
                
                # Accumulate Session Stats
                total_prompt_tokens += p_tokens
                total_candidate_tokens += r_tokens
                total_thought_tokens += t_tokens
                total_combined_tokens += item_total
                
                print(f"    -> Tokens: In={p_tokens}, Out={r_tokens}, Thought={t_tokens} | Total: {item_total}")

                # Parse
                parsed = parse_response(response.text)
                
                new_entry = {
                    "prompt": user_prompt,
                    "chosen": parsed["chosen"], 
                    "rejected": original_chosen, 
                    "internal_thought_trace": parsed["internal_thought_trace"],
                    "meta": {
                        "identity_hash": identity_hash,
                        "experiment_version": experiment_version,
                        "config_num": config_num,
                        "model": model_name,
                        "thinking_level": thinking_level,
                        "temperature": temperature,
                        "input_hash": input_hash,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    "token_stats": {
                        "prompt": p_tokens,
                        "candidate": r_tokens,
                        "thought": t_tokens,
                        "total": item_total
                    }
                }
                
                # Write immediately
                out_f.write(json.dumps(new_entry) + "\n")
                out_f.flush()
                processed_count += 1
                
                # Rate Limit Safety
                time.sleep(1.0) 

            except Exception as e:
                error_str = str(e)
                # Detect Quota Limits (429) or other fatal API errors
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota" in error_str:
                    print(f"\n\n[!!!] CRITICAL ERROR: QUOTA HIT (429)")
                    print(f"Details: {error_str[:200]}...") # Truncate for sanity
                    print("[*] terminating session immediately to preserve log state.")
                    print("[*] You can resume later; existing progress is saved.")
                    break
                
                # For other errors (timeouts, 500s, malformed), log and skip/retry
                print(f"\n[!] Error processing prompt (skipping): {e}")
                time.sleep(5) 

    # Final Summary
    summary = (
        f"--- Session Complete ---\n"
        f"Items Processed: {processed_count}\n"
        f"Total Tokens: {total_combined_tokens}\n"
        f"  - Prompt: {total_prompt_tokens}\n"
        f"  - Candidate: {total_candidate_tokens}\n"
        f"  - Thought: {total_thought_tokens}\n"
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"------------------------\n"
    )
    print(summary)
    
    # Write to Log File
    with open(session_log_file, "a", encoding="utf-8") as log_f:
        log_f.write(summary)
    print(f"[*] Token stats logged to {session_log_file}")

if __name__ == "__main__":
    main()
