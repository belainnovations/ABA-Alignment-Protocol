"""
Diagnostic Script: List Available Vertex AI Models

This script connects to Vertex AI using the project credentials and lists
all models available to the user. This removes the guesswork from finding
the correct Model ID string (e.g. gemini-3-pro vs gemini-1.5-pro-002).
"""

import os
from google import genai
from dotenv import load_dotenv

# Load Env (for Project/Location/Creds)
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

print(f"[*] Diagnostics: Listing Models for Project '{PROJECT_ID}' in '{LOCATION}'")

if not PROJECT_ID:
    print("[!] Error: GOOGLE_CLOUD_PROJECT not set in .env")
    exit(1)

try:
    # Initialize Vertex Client
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )

    print("[*] Client initialized. Querying API...")

    # List Models
    # Note: Pager usage is typical for list endpoints
    pager = client.models.list()
    
    found_any = False
    print("\n--- Available Gemini Models ---")
    for model in pager:
        # Filter for relevant generative models to reduce noise
        if "gemini" in model.name.lower():
            print(f"Name: {model.name}")
            print(f"  - Display Name: {model.display_name}")
            print(f"  - Version: {model.version}")
            print(f"  - Input Token Limit: {model.input_token_limit}")
            print("-" * 30)
            found_any = True
            
    if not found_any:
        print("[!] No 'gemini' models found. Printing ALL models:")
        for model in pager:
            print(f"Name: {model.name}")

except Exception as e:
    print(f"\n[!] API Error: {e}")
    print("Hint: Check if Vertex AI API is enabled in Console.")
