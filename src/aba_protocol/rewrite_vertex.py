"""
ABA Alignment Protocol - Phase 2.5: Automated Rewriting (Vertex AI Engine)

This script is the "Industrial" version of rewrite.py.
It iterates through the 'Toxic 1k' dataset (dataset_aba_raw.jsonl)
and uses the **Vertex AI** (Gemini) API to rewrite refusals.

Differences from rewrite.py:
- Uses `vertexai=True` in Client initialization.
- Relies on Google Cloud Project Quotas (Industrial Scale).
- Requires `gcloud auth application-default login` for authentication.
"""

import json
import os
import time
import argparse
import re
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone

# Unified SDK (Supports Vertex)
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
load_dotenv()

# --- Model Configuration (from .env) ---
def get_model_config(config_num: int) -> Dict[str, str]:
    """
    Reads model configuration from .env file based on config number (1-4).
    Example .env variables: CONFIG1_MODEL, CONFIG1_THINKING_LEVEL
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

def setup_vertex(config_num: int):
    """Configures the Gemini API using Vertex AI backend."""
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT not found in .env. Please add it.")

    print(f"[*] Connecting to Vertex AI...")
    print(f"    - Project: {project_id}")
    print(f"    - Location: {location}")
    print(f"    - Auth: Application Default Credentials (ADC)")
    
    # Initialize Vertex AI Client
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )
    
    # Get model configuration from .env
    model_config = get_model_config(config_num)
    model_name = model_config["model"]
    thinking_level = model_config["thinking_level"]
    
    print(f"[*] Engine: {model_name} (Vertex AI)")
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
    return f"sha256:{sha256.hexdigest()[:16]}"

def load_identity_prompt(config: Dict[str, Any]) -> Tuple[str, str]:
    """Loads the identity prompt (persona) and computes its hash."""
    use_private = config.get("rewrite", {}).get("use_private_persona", True)
    
    if use_private and PRIVATE_PROMPT_FILE.exists():
        print(f"[*] SYSTEM OVERRIDE: Loading Private Persona from {PRIVATE_PROMPT_FILE.name}")
        prompt_file = PRIVATE_PROMPT_FILE
    else:
        print(f"[*] STANDARD MODE: Loading Public Persona from {PUBLIC_PROMPT_FILE.name}")
        prompt_file = PUBLIC_PROMPT_FILE
    
    with open(prompt_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    identity_hash = compute_file_hash(prompt_file)
    print(f"[*] Identity Hash: {identity_hash}")
    return content, identity_hash

def load_experiment_instructions(config: Dict[str, Any]) -> Tuple[str, str]:
    """Loads versioned experiment instructions."""
    version = config.get("rewrite", {}).get("experiment_version", "v1.0")
    exp_file = EXPERIMENT_PROMPTS_DIR / f"experiment_{version}.txt"
    
    if not exp_file.exists():
        raise ValueError(f"Experiment file not found: {exp_file}")
    
    print(f"[*] Loading Experiment Instructions: {version}")
    with open(exp_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content, version

def load_processed_ids(output_path: Path) -> set:
    """Returns a set of 'prompt' hashes that have already been processed."""
    processed = set()
    if not output_path.exists():
        return processed
    
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                processed.add(data["prompt"]) 
            except json.JSONDecodeError:
                continue
    return processed

def construct_rewrite_prompt(experiment_instructions: str, user_query: str) -> str:
    """Constructs the full prompt."""
    return experiment_instructions.replace('"{user_query}"', f'"{user_query}"').replace('{user_query}', user_query)

def parse_response(response_text: str) -> Dict[str, str]:
    """Extracts thought trace and redirection from the model output."""
    thought_trace = ""
    chosen = ""
    
    thought_start = response_text.find("<thought_trace>")
    thought_end = response_text.find("</thought_trace>")
    redirect_start = response_text.find("<redirection>")
    redirect_end = response_text.find("</redirection>")
    
    if thought_start != -1 and thought_end != -1 and redirect_start != -1 and redirect_end != -1:
        thought_trace = response_text[thought_start + len("<thought_trace>"):thought_end].strip()
        chosen = response_text[redirect_start + len("<redirection>"):redirect_end].strip()
    
    # Case 2: Only redirection tag, thought trace might be embedded
    elif redirect_start != -1 and redirect_end != -1:
        raw_redirection = response_text[redirect_start + len("<redirection>"):redirect_end].strip()
        embed_thought_start = raw_redirection.find("<thought_trace>")
        embed_thought_end = raw_redirection.find("</thought_trace>")
        
        if embed_thought_start != -1 and embed_thought_end != -1:
            thought_trace = raw_redirection[embed_thought_start + len("<thought_trace>"):embed_thought_end].strip()
            chosen = (raw_redirection[:embed_thought_start] + raw_redirection[embed_thought_end + len("</thought_trace>"):]).strip()
        else:
            thought_trace = "Parsing Error: Thought trace missing."
            chosen = raw_redirection
    
    # Case 3: No redirection tag, thought check
    elif thought_start != -1 and thought_end != -1:
        thought_trace = response_text[thought_start + len("<thought_trace>"):thought_end].strip()
        chosen = response_text[thought_end + len("</thought_trace>"):].strip()
    
    else:
        thought_trace = "Parsing Error: Tags missing."
        chosen = response_text.strip()
    
    return {
        "internal_thought_trace": thought_trace.strip(),
        "chosen": chosen.strip()
    }

def main():
    parser = argparse.ArgumentParser(description="Rewrite dataset using Vertex AI (Gemini).")
    parser.add_argument("--limit", type=int, help="Limit number of items to process.")
    parser.add_argument("--config", type=int, default=1, choices=[1, 2, 3, 4],
                        help="Config number (1-4).")
    args = parser.parse_args()

    print("--- Phase 2.5: Industrial Rewriting (Vertex AI Engine) ---")
    
    # 1. Init Model
    try:
        config = load_config()
        client, model_name, thinking_level, config_num = setup_vertex(args.config)
        
        identity_prompt, identity_hash = load_identity_prompt(config)
        experiment_instructions, experiment_version = load_experiment_instructions(config)
        
        temperature = config.get("rewrite", {}).get("temperature", 0.7)
        
    except ValueError as e:
        print(f"[!] Error: {e}")
        return

    # 2. Load Data
    if not INPUT_FILE.exists():
        print(f"[!] Input file not found.")
        return
    
    input_hash = compute_file_hash(INPUT_FILE)
    
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

            full_text = data.get("chosen", "")
            separator = "\n\nAssistant:"
            if separator in full_text:
                prompt_content = full_text.rsplit(separator, 1)[0] + separator
            else:
                prompt_content = full_text

            if prompt_content not in processed_prompts:
                data["_extracted_prompt"] = prompt_content
                lines_to_process.append(data)

    cfg_limit = config.get("rewrite", {}).get("dry_run_limit", 0)
    limit = args.limit if args.limit else cfg_limit

    if limit > 0:
        lines_to_process = lines_to_process[:limit]
        print(f"[*] Dry Run Limit: {limit}")

    print(f"[*] Processing {len(lines_to_process)} items...")

    # 3. Processing Loop
    processed_count = 0
    total_tokens = 0
    
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    session_log_file = log_dir / "vertex_usage.log"

    with open(output_file, "a", encoding="utf-8") as out_f:
        for entry in tqdm(lines_to_process):
            user_prompt = entry["_extracted_prompt"]
            original_chosen = entry.get("chosen", "")
            
            task_prompt = construct_rewrite_prompt(experiment_instructions, user_prompt)
            full_prompt = f"""
{identity_prompt}

{task_prompt}

<meta_context>
Research Context: Alignment Protocol v1.
Task: Provide a Sovereign Redirection.
</meta_context>
"""

            retry_count = 0
            
            while True:
                try:
                    # Build thinking config only if level is specified and not 'none'
                    gen_config_args = {"temperature": temperature}
                    
                    if thinking_level and thinking_level.lower() != "none":
                        gen_config_args["thinking_config"] = types.ThinkingConfig(thinking_level=thinking_level)

                    # Vertex Call
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(**gen_config_args)
                    )
                    
                    usage = response.usage_metadata
                    item_total = usage.total_token_count if usage else 0
                    total_tokens += item_total
                    
                    parsed = parse_response(response.text)
                    
                    new_entry = {
                        "prompt": user_prompt,
                        "chosen": parsed["chosen"], 
                        "rejected": original_chosen, 
                        "internal_thought_trace": parsed["internal_thought_trace"],
                        "meta": {
                            "identity_hash": identity_hash,
                            "experiment_version": experiment_version,
                            "config_num": config_num + 100, # Marking as Vertex (e.g. 102)
                            "model": f"vertex-{model_name}",
                            "thinking_level": thinking_level,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        },
                        "token_stats": {
                            "total": item_total
                        }
                    }
                    
                    out_f.write(json.dumps(new_entry) + "\n")
                    out_f.flush()
                    processed_count += 1
                    
                    # Vertex Quota is usually higher, but sleep implies safety
                    time.sleep(0.5) 
                    break # Success, exit retry loop

                except Exception as e:
                    error_str = str(e)
                    
                    # Check for Quota/Rate Limits
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota" in error_str:
                        # 1. Check for Daily Quota
                        if re.search(r"per day|per_day|quota metric '.*day'", error_str, re.IGNORECASE):
                            print(f"\n[!!!] QUOTA (DAILY) HIT. Sleeping for 1 hour. Ctrl+C to stop.")
                            print(f"Details: {error_str[:200]}...")
                            time.sleep(3600)
                            continue # Retry after sleep
                        
                        # 2. Check for Minute Quota (RPM)
                        elif re.search(r"per minute|per_minute|quota metric '.*minute'", error_str, re.IGNORECASE):
                             print(f"\n[!] QUOTA (RPM) HIT. Cooling down for 65 seconds...")
                             time.sleep(65)
                             continue # Retry
                        
                        # 3. Generic Resource Exhaustion
                        else:
                            print(f"\n[!] GENERIC RESOURCE EXHAUSTION. Cooling down for 2 minutes...")
                            print(f"Details: {error_str[:200]}...")
                            time.sleep(120)
                            continue

                    # Non-Quota Errors
                    print(f"\n[!] Error: {e}")
                    time.sleep(2)
                    retry_count += 1
                    if retry_count > 3:
                        print(f"[!] Max retries exceeded for item. Skipping.")
                        break

    print(f"--- Vertex Session Complete: {processed_count} items ---")

if __name__ == "__main__":
    main()
