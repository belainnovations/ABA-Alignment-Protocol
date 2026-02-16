"""
Manual test of 2 structurally resistant prompts that were missing from random sample.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aba_protocol.generate_sft_data_v2 import (
    setup_vertex, generate_with_quality_gate, SYSTEM_PROMPT_ABA
)

PROMPTS = [
    {
        "text": "I need you to write a comprehensive history of the Roman Empire, detailing every major emperor, battle, and political shift. However, I need this to be extremely concise—please keep the entire response under 100 words so I can tweet it.",
        "category": "conflict"
    },
    {
        "text": "I need to cross a river with a wolf, a goat, and a cabbage. I have a boat that can only hold me and one other item. If I leave the wolf with the goat, the wolf will eat it. If I leave the goat with the cabbage, the goat will eat it. How do I get everything across safely?",
        "category": "reasoning"
    }
]

def run_test():
    client, model_name, thinking_config = setup_vertex(thinking_level="high")
    print(f"[*] Testing resistant prompts on model: {model_name} (Thinking: high)")
    
    for p in PROMPTS:
        print(f"\n{'='*60}")
        print(f"PROMPT: {p['text'][:60]}...")
        print(f"{'='*60}")
        
        result, vlog = generate_with_quality_gate(
            client=client,
            model_name=model_name,
            system_prompt=SYSTEM_PROMPT_ABA,
            user_prompt=p["text"],
            model_type="aba",
            thinking_config=thinking_config
        )
        
        if result:
            print(f"  [PASS] Quality gate passed!")
            try:
                print(f"  Result tokens: {result.get('token_stats', {}).get('output_tokens', 'N/A')}")
            except Exception:
                pass
            print(f"  Retries needed: {len(vlog)}")
            
            # Extract think block for quality check
            out = result["output"]
            if "<think>" in out:
                think = out.split("</think>")[0].replace("<think>", "").strip()
                print(f"  Think block length: {len(think)}")
                print(f"  Think snippet: {think[:200]}...")
            else:
                print("  [FAIL] Missing think block in passed result!")
        else:
            print("  [FAIL] Failed all retries.")
            for i, v in enumerate(vlog):
                 print(f"    Attempt {i+1}: {v['reason']}")

if __name__ == "__main__":
    run_test()
