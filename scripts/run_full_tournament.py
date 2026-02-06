import subprocess
import sys
import time

def run_eval(model_id, adapter_path, base_model, limit=100):
    print(f"\n\n{'='*60}")
    print(f"QUEUING TOURNAMENT ROUND: {model_id}")
    print(f"{'='*60}\n")
    
    cmd = [
        sys.executable, "src/aba_protocol/run_tournament_eval.py",
        "--model_id", model_id,
        "--adapter_path", adapter_path,
        "--base_model", base_model,
        "--limit", str(limit)
    ]
    
    subprocess.run(cmd, check=True)
    time.sleep(5) # Cooldown

if __name__ == "__main__":
    # 1. Model A (Native)
    run_eval(
        model_id="A_Native",
        adapter_path="models/model_a_native",
        base_model="cognitivecomputations/dolphin-2.9-llama3-8b"
    )

    # 2. Model A (Control)
    run_eval(
        model_id="A_Control",
        adapter_path="models/model_a_control",
        base_model="cognitivecomputations/dolphin-2.9-llama3-8b"
    )

    # 3. Model A (Repair)
    run_eval(
        model_id="A_Repair",
        adapter_path="models/model_a_lora",
        base_model="unsloth/llama-3-8b-instruct-bnb-4bit"
    )
    
    print("\n\n>>> TOURNAMENT COMPLETE <<<")
