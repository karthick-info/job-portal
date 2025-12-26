import google.generativeai as genai

api_key = 'AIzaSyDhg68m-EXPY3l1OxSUV4JQ8CYJOMVlSB0'
genai.configure(api_key=api_key)

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
