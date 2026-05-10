import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("--- RAW API DIAGNOSTIC ---")
try:
    # Just grab the first model to see what its structure is
    model_list = list(client.models.list())
    if model_list:
        print(f"Success! Found {len(model_list)} models.")
        print("First model raw data:")
        print(model_list[0]) 
        
        print("\nFull list of model names:")
        for m in model_list:
            print(f"- {m.name}")
    else:
        print("The model list is empty. Your API key might not have permissions.")
        
except Exception as e:
    print(f"\nFATAL ERROR: {e}")