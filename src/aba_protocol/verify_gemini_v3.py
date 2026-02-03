import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load Environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
    exit(1)

print("--- Gemini v3 SDK Verification ---")

# 1. Initialize Client (New Pattern)
try:
    client = genai.Client(api_key=api_key)
    print("[*] Client Initialized.")
except Exception as e:
    print(f"[!] Client Init Failed: {e}")
    exit(1)

# 2. Test Generation & Metadata
model_id = "gemini-3-pro-preview"
print(f"[*] Testing Model: {model_id}")

try:
    response = client.models.generate_content(
        model=model_id,
        contents="Explain the concept of 'Sovereign Redirection' in one sentence.",
        config=types.GenerateContentConfig(
            temperature=0.7
        )
    )
    
    print("\n[*] Response Received:")
    print(f"    Text: {response.text}")
    print(f"    Usage Metadata: {response.usage_metadata}")
    
    # Introspect fields
    if response.usage_metadata:
        print("\n[*] Metadata Fields:")
        print(f"    Input Tokens: {response.usage_metadata.prompt_token_count}")
        print(f"    Output Tokens: {response.usage_metadata.candidates_token_count}")
        print(f"    Total Tokens: {response.usage_metadata.total_token_count}")
        
except Exception as e:
    print(f"\n[!] Generation Failed: {e}")
