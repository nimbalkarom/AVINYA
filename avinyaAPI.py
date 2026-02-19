import google.generativeai as genai
import os

# 🔑 PASTE YOUR GEMINI API KEY HERE
GEMINI_API_KEY = "AIzaSyBm8PLJFkXlKTr4icAEdeSfShgVlnHUwgo"

def test_api():
    print(f"Testing API Key: {GEMINI_API_KEY[:10]}...")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        print("Listing available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        # Test with gemini-2.0-flash
        print("\nAttempting to send message with 'gemini-2.0-flash'...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello")
        
        print("\n[SUCCESS] Response received:")
        print(response.text)
        
    except Exception as e:
        print("\n[ERROR] Details:")
        print(e)


if __name__ == "__main__":
    test_api()

