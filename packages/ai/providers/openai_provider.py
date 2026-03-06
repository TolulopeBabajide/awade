import os
import logging
from typing import Optional
from .base import LLMProvider

# Configure logging
logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class OpenAIProvider(LLMProvider):
    """
    OpenAI implementation of LLMProvider.
    Uses 'gpt-4o' for standard tier and 'gpt-4o-mini' for basic tier.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAIProvider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def _get_model_name(self, tier: str) -> str:
        """Map generic tiers to specific OpenAI models."""
        if tier == "basic":
            return os.getenv("OPENAI_MODEL_BASIC", "gpt-4o-mini")
        return os.getenv("OPENAI_MODEL_STANDARD", "gpt-4o")

    def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        model_tier: str = "standard",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: str = "text"
    ) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
            
        model = self._get_model_name(model_tier)
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare kwargs
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Enable JSON mode if requested
        if response_format == "json":
             kwargs["response_format"] = {"type": "json_object"}
        
        try:
            logging.info(f"Generating content with OpenAI (Model: {model})")
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    def health_check(self) -> bool:
        return bool(self.client)
