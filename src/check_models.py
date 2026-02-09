import os
from google import genai

# PASTE YOUR API KEY HERE
API_KEY = "AIzaSyDTiTcTmrh_1BG-o5dtGSuu-ynR5ACksOM"

client = genai.Client(api_key=API_KEY)

print("--- Querying Google for available models ---")

try:
    pager = client.models.list()

    print("\n✅ AVAILABLE MODELS (Exact IDs):")
    for model in pager:
        # Just print the name and display name
        print(f" - ID: {model.name}")
        # Some models might have a display_name, let's try printing it safely
        if hasattr(model, 'display_name'):
             print(f"   Name: {model.display_name}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n------------------------------------------")
