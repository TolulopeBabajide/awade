
import os
import sys
import google.generativeai as genai

# Add root path to find packages if needed, though this is a standalone check
sys.path.append(os.getcwd())

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables.")
        return

    try:
        genai.configure(api_key=api_key)
        print("✅ Authenticated with Gemini API.")
        
        print("\nSearching for models supported by 'generateContent'...")
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                found = True
        
        if not found:
            print("⚠️ No models found that support 'generateContent'.")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_models()
