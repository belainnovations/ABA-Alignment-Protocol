"""
Convert SFT JSONL datasets to readable Markdown for human review.
Produces a side-by-side comparison of Control vs ABA responses.

Usage:
    python scripts/convert_to_markdown.py              # all prompts
    python scripts/convert_to_markdown.py --limit 20   # first 20
    python scripts/convert_to_markdown.py --category safety  # filter by category
"""

import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "phase_3e"


def load_dataset(path):
    """Load JSONL into dict keyed by instruction text."""
    items = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line)
                items[d['instruction']] = d
            except (json.JSONDecodeError, KeyError):
                continue
    return items


def format_response(output):
    """Format a response for Markdown, splitting think/response sections.
    
    Handles three cases:
    1. Properly closed <think>...</think> -> THINKING + RESPONSE
    2. Unclosed <think> (no </think>) -> THINKING (format error noted)
    3. No <think> at all -> full output with note
    """
    if not output or output.startswith("*["):
        return output + "\n"

    has_open = '<think>' in output
    has_close = '</think>' in output

    if has_open and has_close:
        # Case 1: Properly formatted — split on </think>
        parts = output.split('</think>', 1)
        think_part = parts[0].replace('<think>', '').strip()
        response_part = parts[1].strip() if len(parts) > 1 else ""

        result = ""
        if think_part:
            result += "**THINKING:**\n\n"
            result += f"```\n{think_part}\n```\n\n"
        if response_part:
            result += "**RESPONSE:**\n\n"
            result += f"{response_part}\n\n"
        else:
            result += "> *[FORMAT NOTE: No user-facing response after thinking block]*\n\n"
        return result

    elif has_open and not has_close:
        # Case 2: Unclosed <think> tag — format error
        # Treat everything after <think> as thinking content
        parts = output.split('<think>', 1)
        before = parts[0].strip()
        think_part = parts[1].strip() if len(parts) > 1 else ""

        result = "> *[FORMAT ERROR: `<think>` tag opened but never closed with `</think>`]*\n\n"
        if before:
            result += f"**BEFORE TAG:**\n\n{before}\n\n"
        if think_part:
            result += "**THINKING (unclosed):**\n\n"
            result += f"```\n{think_part}\n```\n\n"
        result += "> *[No user-facing RESPONSE section — entire output was inside unclosed thinking block]*\n\n"
        return result

    else:
        # Case 3: No think tags at all
        return f"> *[No `<think>` block detected]*\n\n{output}\n\n"


def main():
    parser = argparse.ArgumentParser(description="Convert JSONL to Markdown")
    parser.add_argument("--limit", type=int, default=None, help="Limit output")
    parser.add_argument("--category", type=str, default=None, help="Filter category")
    parser.add_argument("--output", type=str, default=None, help="Output file")
    args = parser.parse_args()

    control = load_dataset(DATA_DIR / "sft_control.jsonl")
    aba = load_dataset(DATA_DIR / "sft_aba.jsonl")

    # Load prompts in order
    prompts = []
    with open(DATA_DIR / "prompts_500.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            try:
                prompts.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Filter
    if args.category:
        prompts = [p for p in prompts if p['category'] == args.category]

    if args.limit:
        prompts = prompts[:args.limit]

    # Build markdown
    lines = []
    lines.append(f"# SFT Data Review: Control vs ABA\n")
    lines.append(f"**Total prompts shown:** {len(prompts)}\n")
    if args.category:
        lines.append(f"**Category filter:** {args.category}\n")

    # Stats
    cats = {}
    for p in prompts:
        cat = p['category']
        cats[cat] = cats.get(cat, 0) + 1
    lines.append("| Category | Count |")
    lines.append("|---|---|")
    for cat, count in sorted(cats.items()):
        lines.append(f"| {cat} | {count} |")
    lines.append("")

    lines.append("---\n")

    for i, prompt_data in enumerate(prompts):
        prompt_text = prompt_data['prompt']
        category = prompt_data['category']
        sub_theme = prompt_data.get('sub_theme', '')

        c_data = control.get(prompt_text)
        a_data = aba.get(prompt_text)

        c_output = c_data['output'] if c_data and c_data.get('output') else "*[No response generated]*"
        a_output = a_data['output'] if a_data and a_data.get('output') else "*[No response generated]*"

        c_tokens = c_data['token_stats']['total'] if c_data else 0
        a_tokens = a_data['token_stats']['total'] if a_data else 0

        lines.append(f"## [{i+1}] {category} / {sub_theme}\n")
        lines.append(f"### Prompt\n")
        lines.append(f"> {prompt_text}\n")

        # Render Control
        lines.append(f"### Control Response ({c_tokens} tokens)\n")
        lines.append(format_response(c_output))

        # Render ABA
        lines.append(f"### ABA Response ({a_tokens} tokens)\n")
        lines.append(format_response(a_output))

        lines.append(f"---\n")

    # Write
    out_path = Path(args.output) if args.output else DATA_DIR / "review.md"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"[OK] Written {len(prompts)} entries to {out_path}")
    print(f"     File size: {out_path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
