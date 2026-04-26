from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Defines the contract for content generation to ensure swapability.
    """
    
    @abstractmethod
    def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        model_tier: str = "standard",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: str = "text"
    ) -> str:
        """
        Generate content using the provider.
        
        Args:
            prompt (str): The user prompt
            system_instruction (Optional[str]): System prompt/context
            model_tier (str): "basic" (fast/cheap) or "standard" (quality/expensive)
            temperature (float): Creativity (0.0 - 1.0)
            max_tokens (int): Max response tokens
            
        Returns:
            str: Generated text content
        """
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is configured and reachable."""
        pass
