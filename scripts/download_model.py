
"""
Script to explicitly download the target model for Phase 3b.
Isolates the download step from the training loop to prevent silent hangs.
"""
from unsloth import FastLanguageModel
import os

model_name = "cognitivecomputations/dolphin-2.9-llama3-8b"
print(f"Downloading {model_name}...")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    load_in_4bit=True,
    dtype=None,
)

print("Download complete.")
