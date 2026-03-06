
import re

def clean_markdown(text):
    cleaned_text = text.strip()
    if cleaned_text.startswith("```"):
        # Remove opening backticks and optional language identifier
        cleaned_text = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned_text)
        # Remove closing backticks and optional whitespace
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        return cleaned_text
    return text

def test_cases():
    cases = [
        # Case 1: Standard with newline (Should pass)
        ("```json\n{\"foo\": \"bar\"}\n```", "{\"foo\": \"bar\"}"),
        
        # Case 2: No language tag (Should pass)
        ("```\n{\"foo\": \"bar\"}\n```", "{\"foo\": \"bar\"}"),
        
        # Case 3: Space instead of newline (Previously FAILED)
        ("```json {\"foo\": \"bar\"} ```", "{\"foo\": \"bar\"}"),
        
        # Case 4: No newline at end (Previously FAILED)
        ("```json\n{\"foo\": \"bar\"}```", "{\"foo\": \"bar\"}"),
        
        # Case 5: Weird spacing (Previously FAILED)
        ("``` json \n{\"foo\": \"bar\"}\n ```", "{\"foo\": \"bar\"}")
    ]
    
    print("Testing New Cleaning Logic:")
    all_pass = True
    for i, (input_text, expected) in enumerate(cases):
        result = clean_markdown(input_text)
        status = "✅ PASS" if result.strip() == expected else f"❌ FAIL (Got: {repr(result)})"
        print(f"Case {i+1}: {status}")
        if result.strip() != expected:
            all_pass = False
            
    if all_pass:
        print("\n🎉 All cases passed!")

if __name__ == "__main__":
    test_cases()
