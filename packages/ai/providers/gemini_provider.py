import os
import re
import logging
from typing import Optional
from .base import LLMProvider

# Configure logging
logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-genai package not installed.")

class GeminiProvider(LLMProvider):
    """
    Google Gemini implementation of LLMProvider.
    Uses 'gemini-flash-latest' for both basic and standard tiers by default.
    """

    # Default request timeout in seconds — prevents FastAPI workers from hanging
    # indefinitely under network degradation (OWASP LLM10 / Model DoS mitigation).
    # Override via GEMINI_TIMEOUT_SECONDS env var.
    DEFAULT_TIMEOUT = 60.0

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.is_configured = False
        self.timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", str(self.DEFAULT_TIMEOUT)))

        if GEMINI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options=genai_types.HttpOptions(timeout=self.timeout),
                )
                self.is_configured = True
                logger.info("GeminiProvider initialized (timeout=%.1fs)", self.timeout)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
    
    def _get_model_name(self, tier: str) -> str:
        """Map generic tiers to specific Gemini models."""
        # Available models as of Jan 2026: gemini-2.0-flash, gemini-flash-latest
        if tier == "basic":
            return os.getenv("GEMINI_MODEL_BASIC", "gemini-flash-latest")
        return os.getenv("GEMINI_MODEL_STANDARD", "gemini-flash-latest")

    def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        model_tier: str = "standard",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: str = "text"
    ) -> str:
        if not self.is_configured:
            raise RuntimeError("Gemini client not initialized")
            
        model_name = self._get_model_name(model_tier)
        
        safety_settings = [
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]

        generation_config = genai_types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction,
            safety_settings=safety_settings,
            **({"response_mime_type": "application/json"} if response_format == "json" else {}),
        )

        try:
            logger.info(f"Generating content with Gemini (Model: {model_name})")

            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=generation_config,
            )
            
            text = response.text
            
            if text:
                # Clean up potential markdown formatting (```json ... ```)
                cleaned_text = text.strip()
                if cleaned_text.startswith("```"):
                    # Remove opening backticks and optional language identifier
                    # Matches ``` followed by optional whitespace, optional language, and optional whitespace/newline
                    cleaned_text = re.sub(r"^```\s*[a-zA-Z]*\s*", "", cleaned_text)
                    # Remove closing backticks and optional whitespace
                    cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
                    return cleaned_text
                return text
            return ""
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    def health_check(self) -> bool:
        return self.is_configured
