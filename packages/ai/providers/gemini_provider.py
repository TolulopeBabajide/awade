import os
import logging
from typing import Optional
from .base import LLMProvider

# Configure logging
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai package not installed.")

class GeminiProvider(LLMProvider):
    """
    Google Gemini implementation of LLMProvider.
    Uses 'gemini-1.5-pro' for standard tier and 'gemini-1.5-flash' for basic tier.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.is_configured = False
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.is_configured = True
                logger.info("GeminiProvider initialized")
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
        
        # Gemini configuration
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        # Enable JSON mode if requested
        if response_format == "json":
            generation_config["response_mime_type"] = "application/json"
        
        # Basic safety settings (can be fine-tuned)
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        try:
            logger.info(f"Generating content with Gemini (Model: {model_name})")
            
            # Pass system_instruction if available
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            text = response.text
            
            if text:
                # Clean up potential markdown formatting (```json ... ```)
                cleaned_text = text.strip()
                if cleaned_text.startswith("```"):
                    import re
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
