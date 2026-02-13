"""Measure system prompt and instruction token sizes."""
import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

def est_tokens(text):
    """Rough estimate: ~4 chars per token for English."""
    return len(text) // 4

with open('src/aba_protocol/generate_sft_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract system prompts using triple-quote markers
ctrl_match = re.search(r'SYSTEM_PROMPT_CONTROL\s*=\s*"""(.*?)"""', content, re.DOTALL)
aba_match = re.search(r'SYSTEM_PROMPT_ABA\s*=\s*"""(.*?)"""', content, re.DOTALL)

if ctrl_match:
    c_text = ctrl_match.group(1)
    print(f'CONTROL system prompt:')
    print(f'  Characters: {len(c_text)}')
    print(f'  Est. tokens: {est_tokens(c_text)}')
    print()

if aba_match:
    a_text = aba_match.group(1)
    print(f'ABA system prompt:')
    print(f'  Characters: {len(a_text)}')
    print(f'  Est. tokens: {est_tokens(a_text)}')
    print()

# Check instruction lengths
instructions = []
with open('data/phase_3e/prompts_500.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        instructions.append(len(d['prompt']))

avg_chars = sum(instructions) / len(instructions)
max_chars = max(instructions)
min_chars = min(instructions)
print(f'User instructions (prompts_500.jsonl):')
print(f'  Count: {len(instructions)}')
print(f'  Avg chars: {avg_chars:.0f} (~{avg_chars/4:.0f} tokens)')
print(f'  Max chars: {max_chars} (~{max_chars/4:.0f} tokens)')
print(f'  Min chars: {min_chars} (~{min_chars/4:.0f} tokens)')
