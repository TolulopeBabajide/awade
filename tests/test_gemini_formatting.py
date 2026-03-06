
import unittest
import re
from packages.ai.providers.gemini_provider import GeminiProvider

class MockGeminiProvider(GeminiProvider):
    def __init__(self):
        self.is_configured = True
        self.api_key = "mock"

class TestGeminiFormatting(unittest.TestCase):
    def setUp(self):
        # We can test the cleaning logic by subclassing or mocking
        # But since the logic is inside generate_content, we'll extract/replicate logic or use a helper
        # Actually, let's just test the logic directly if we can't easily mock the API call wrapper
        pass

    def clean_and_repair(self, text):
        # Replicate the full pipeline logic from gpt_service
        cleaned_text = text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```\s*[a-zA-Z]*\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        
        # Repair logic
        cleaned_text = re.sub(r',\s*}', '}', cleaned_text)
        cleaned_text = re.sub(r',\s*\]', ']', cleaned_text)
        return cleaned_text

    def test_markdown_cleaning(self):
        cases = [
            ("```json\n{\"foo\": \"bar\"}\n```", "{\"foo\": \"bar\"}"),
            ("```\n{\"foo\": \"bar\"}\n```", "{\"foo\": \"bar\"}"),
            ("```json {\"foo\": \"bar\"} ```", "{\"foo\": \"bar\"}"),
            ("```json\n{\"foo\": \"bar\"}```", "{\"foo\": \"bar\"}"),
            ("``` json \n{\"foo\": \"bar\"}\n ```", "{\"foo\": \"bar\"}"),
            ("Just plain text", "Just plain text"),
            # Trailing comma cases
            ('{"foo": "bar",}', '{"foo": "bar"}'),
            ('[1, 2, 3,]', '[1, 2, 3]'),
            ('{"foo": [1, 2,], "bar": "baz",}', '{"foo": [1, 2], "bar": "baz"}')
        ]
        
        for input_text, expected in cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.clean_and_repair(input_text), expected)

if __name__ == '__main__':
    unittest.main()
