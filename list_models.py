import google.generativeai as genai

import os

api_key = os.environ.get('GEMINI_API_KEY', 'your-api-key-here')
genai.configure(api_key=api_key)

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
