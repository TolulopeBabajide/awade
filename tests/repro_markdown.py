
import re

def clean_markdown(text):
    if text.strip().startswith("```"):
        # Current implementation
        text = re.sub(r"^```[a-zA-Z]*\n", "", text.strip())
        text = re.sub(r"\n```$", "", text.strip())
    return text

def test_cases():
    cases = [
        # Case 1: Standard with newline (Should pass)
        ("```json\n{\"foo\": \"bar\"}\n```", "{\"foo\": \"bar\"}"),
        
        # Case 2: No language tag (Should pass)
        ("```\n{\"foo\": \"bar\"}\n```", "{\"foo\": \"bar\"}"),
        
        # Case 3: Space instead of newline (Likely FAIL)
        ("```json {\"foo\": \"bar\"} ```", "{\"foo\": \"bar\"}"),
        
        # Case 4: No newline at end (Likely FAIL)
        ("```json\n{\"foo\": \"bar\"}```", "{\"foo\": \"bar\"}"),
        
        # Case 5: Weird spacing
        ("``` json \n{\"foo\": \"bar\"}\n ```", "{\"foo\": \"bar\"}")
    ]
    
    print("Testing Cleaning Logic:")
    for i, (input_text, expected) in enumerate(cases):
        result = clean_markdown(input_text)
        status = "✅ PASS" if result.strip() == expected else f"❌ FAIL (Got: {repr(result)})"
        print(f"Case {i+1}: {status}")

if __name__ == "__main__":
    test_cases()
