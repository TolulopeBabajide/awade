"""
GPT Service for Awade Lesson Planning

This module provides AI-powered services for lesson plan generation,
curriculum alignment, and educational content creation using LLM providers.

Author: Tolulope Babajide
"""

import os
import json
import logging
import re
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .prompts import COMPREHENSIVE_LESSON_RESOURCE_PROMPT, PARENT_HELPER_PROMPT

# ---------------------------------------------------------------------------
# Input-sanitisation constants — applied to user-supplied text BEFORE it is
# inserted into a prompt template (AWD-M-12)
# ---------------------------------------------------------------------------

# Maximum characters accepted from a user-supplied context field.
# Longer inputs are truncated to prevent token-stuffing / prompt DoS.
_MAX_USER_CONTEXT_CHARS: int = 2000

# Regex patterns that indicate an instruction-injection attempt in user input.
# Any match causes the offending phrase to be scrubbed and logged.
_INPUT_INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?(?:previous\s+)?instructions",
    r"disregard\s+(all\s+)?instructions",
    r"override\s+(your\s+)?(?:instructions|training)",
    r"you\s+are\s+now\s+(?:a\s+)?(?:different|new|another)",
    r"act\s+as\s+(?:a\s+)?(?:different|new|another|unrestricted|uncensored)",
    r"\bsystem\s+prompt\b",
    r"\bjailbreak\b",
    r"bypass\s+(?:safety|security|filters)",
    r"new\s+(?:role|persona|mode|behaviour|behavior)\s*:",
    r"<\s*/?(?:system|assistant|user)\s*>",   # fake role tags
]

# ---------------------------------------------------------------------------
# Content-safety patterns — applied to raw AI output in validate_output()
# ---------------------------------------------------------------------------

# PII that should never leak from prompts into persisted output
_OUTPUT_PII_PATTERNS: list[tuple[str, str]] = [
    (r"[\w\.\-]+@[\w\.\-]+\.\w+", "email address"),
    (r"(?<!\d)\+?\d{10,15}(?!\d)", "phone number"),
    (r"sk-[a-zA-Z0-9]{32,}", "API key"),
]

# Phrases that indicate the model was jailbroken / injection succeeded
_OUTPUT_INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"\bsystem\s+prompt\b",
    r"\bjailbreak\b",
    r"disregard\s+(all\s+)?instructions",
    r"bypass\s+(safety|security|filters)",
    r"override\s+(your\s+)?(instructions|training)",
    r"you\s+are\s+now\s+(?:a\s+)?(?:different|new|another)",
]

# Terms clearly inappropriate in child-facing educational content
_HARMFUL_CONTENT_PATTERNS: list[str] = [
    r"\bporn(?:ography)?\b",
    r"\bxxx\b",
    r"\bnudity\b",
    r"\bkill\s+yourself\b",
    r"\bself[- ]harm\b",
]
from .providers.base import LLMProvider
from .providers.openai_provider import OpenAIProvider
from .providers.gemini_provider import GeminiProvider
from .cache import ContentCache

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except ImportError:
    logger.debug("dotenv not available, skipping environment loading")
except Exception as e:
    logger.debug(f"Environment loading issue: {e}")

class AwadeGPTService:
    """
    AI service for lesson plan generation and educational content creation.
    
    This service provides methods for:
    - Generating comprehensive lesson resources from lesson plans
    - Curriculum-aligned content generation
    - Local context integration
    
    It delegates actual generation to the configured LLMProvider (OpenAI, Gemini)
    and handles caching via ContentCache.
    """
    
    def __init__(self, api_key: Optional[str] = None, provider_type: Optional[str] = None):
        """
        Initialize the GPT service.
        
        Args:
            api_key (Optional[str]): API key for the provider.
            provider_type (Optional[str]): 'openai', 'gemini', or 'mock'.
        """
        self.provider_type = provider_type or os.getenv("AI_PROVIDER", "openai").lower()
        self.provider: Optional[LLMProvider] = None
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "8192"))
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        
        # Initialize Provider
        self._init_provider(api_key)
        
        # Initialize Cache
        self.cache = ContentCache() # Will use env vars for connection
    
    def _init_provider(self, api_key: Optional[str]):
        """Initialize the specific provider backend."""
        try:
            if self.provider_type == "openai":
                self.provider = OpenAIProvider(api_key=api_key)
            elif self.provider_type == "gemini":
                self.provider = GeminiProvider(api_key=api_key)
            elif self.provider_type == "mock":
                logger.info("Using explicit Mock provider configuration")
                self.provider = None
            else:
                logger.warning(f"Unknown provider '{self.provider_type}', falling back to Mock")
                self.provider = None
                
            if self.provider:
                logger.info(f"AI Provider initialized: {self.provider_type}")
        except Exception as e:
            logger.error(f"Failed to initialize provider {self.provider_type}: {e}")
            self.provider = None
    
    def _make_api_call(
        self, 
        prompt: str, 
        temperature: Optional[float] = None, 
        model_tier: str = "standard",
        topic: str = "General Topic", 
        subject: str = "Mathematics", 
        grade: str = "Grade 4",
        prompt_metadata: Optional[Dict[str, Any]] = None,
        response_format: str = "text"
    ) -> str:
        """
        Make an API call to the configured provider or return mock response.
        Handles caching automatically.
        """
        # 1. Check if we should use Mock
        if not self.provider:
            logger.info("Using mock response (Provider not available)")
            return self._generate_mock_response(prompt, topic, subject, grade)
        
        temp = temperature if temperature is not None else self.temperature
        
        # 2. Check Cache
        if prompt_metadata:
            # Add tier to metadata to ensure distinct cache keys for different tiers
            cache_metadata = prompt_metadata.copy()
            cache_metadata["model_tier"] = model_tier
            
            cached_content = self.cache.get(
                provider=self.provider_type,
                model=model_tier, # We use abstract model name in key
                prompt_data=cache_metadata
            )
            if cached_content:
                return cached_content
        
        # 3. Call Provider
        try:
            system_instruction = "You are an expert educational content creator specializing in African curriculum development. You create comprehensive, locally contextual lesson resources that are age-appropriate, culturally relevant, and practical for teachers to implement."
            
            logger.info(f"Generating content using {self.provider_type} (Tier: {model_tier})")
            content = self.provider.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                model_tier=model_tier,
                temperature=temp,
                max_tokens=self.max_tokens,
                response_format=response_format
            )
            
            # Check if response is empty
            if not content or not content.strip():
                return self._generate_mock_lesson_resource(topic, subject, grade)
            
            # 4. Save to Cache
            if prompt_metadata:
                self.cache.set(
                    provider=self.provider_type,
                    model=model_tier,
                    prompt_data=cache_metadata,
                    content=content
                )
                
            return content
            
        except Exception as e:
            logger.error(f"Error in AI generation: {e}")
            # Fallback to mock on critical failure
            return self._generate_mock_lesson_resource(topic, subject, grade)
            
    def _sanitize_input(self, text: str) -> str:
        """
        Sanitize input to remove potentially sensitive information.
        """
        if not text:
            return text
            
        # Remove potential API keys (simple heuristic)
        text = re.sub(r'(sk-[a-zA-Z0-9]{32,})', '[REDACTED_KEY]', text)
        
        # Remove potential email addresses
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
        
        # Remove potential phone numbers (simple international format)
        text = re.sub(r'\+?\d{10,15}', '[REDACTED_PHONE]', text)

        return text

    def _sanitize_user_context(self, text: Optional[str]) -> Optional[str]:
        """
        Sanitise educator-supplied context before inserting it into a prompt template.

        Applies three layers of defence (AWD-M-12):
        1. Truncate to _MAX_USER_CONTEXT_CHARS to prevent token-stuffing / DoS.
        2. Strip PII (API keys, email addresses, phone numbers).
        3. Detect and scrub instruction-injection patterns.

        Returns the sanitised string; never raises — any error falls back to
        an empty string so generation can continue safely.
        """
        if not text:
            return text

        try:
            # 1. Truncate
            if len(text) > _MAX_USER_CONTEXT_CHARS:
                logger.warning(
                    "User context truncated from %d to %d chars (AWD-M-12)",
                    len(text),
                    _MAX_USER_CONTEXT_CHARS,
                )
                text = text[:_MAX_USER_CONTEXT_CHARS] + " [truncated]"

            # 2. Strip PII (reuse existing sanitiser)
            text = self._sanitize_input(text)

            # 3. Detect and scrub injection patterns
            for pattern in _INPUT_INJECTION_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    logger.warning(
                        "Prompt injection pattern detected in user context, scrubbing (AWD-M-12)"
                    )
                    text = re.sub(pattern, "[removed]", text, flags=re.IGNORECASE)

        except Exception:
            logger.error("Unexpected error in _sanitize_user_context; returning empty context", exc_info=True)
            return ""

        return text

    def _check_content_safety(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Run content-safety checks on a raw AI output string.

        Checks (in order):
        1. PII leakage — email, phone number, API key
        2. Prompt-injection markers — phrases indicating the model was manipulated
        3. Harmful content — terms inappropriate for child-facing education

        Returns (is_safe, reason).  reason is None when safe.
        """
        # 1. PII
        for pattern, label in _OUTPUT_PII_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Content safety: PII detected in AI output (%s)", label)
                return False, f"Output contains {label}"

        # 2. Injection markers
        for pattern in _OUTPUT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Content safety: injection marker detected in AI output")
                return False, "Output contains prompt-injection marker"

        # 3. Harmful content
        for pattern in _HARMFUL_CONTENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Content safety: harmful content detected in AI output")
                return False, "Output contains harmful content"

        return True, None

    def validate_output(self, content: str) -> tuple[bool, Optional[str]]:
        """
        Validate the AI output for safety and structure.

        Runs in two passes:
        1. Content-safety pass on the raw string (PII, injection markers, harmful words)
        2. Structural validation — JSON parse + required-field check

        Returns (is_valid, reason).  reason is None when valid.
        """
        try:
            # 1. Content-safety pass (raw string — before JSON parsing)
            is_safe, safety_reason = self._check_content_safety(content)
            if not is_safe:
                return False, safety_reason

            # 2. Structural validation
            # Clean and repair first (redundant when called from generate_lesson_resource,
            # but provides a safety net for internal callers)
            clean_content = self._clean_and_repair(content)

            data = json.loads(clean_content)

            # Check for minimum required fields
            required_fields = ["title_header", "learning_objectives", "lesson_content"]
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"

            return True, None
        except json.JSONDecodeError as e:
            # Provide first 50 chars of content for debugging
            logger.error(f"JSON Decode Error: {e}. Content preview: {content[:50]}...")
            return False, "Invalid JSON format"

    def _repair_json(self, json_str: str) -> str:
        """
        Attempt to repair common JSON syntax errors from LLMs.
        - Removes trailing commas in objects and arrays
        """
        if not json_str: return json_str
        
        # Remove trailing commas in objects: { "a": 1, } -> { "a": 1 }
        json_str = re.sub(r',\s*}', '}', json_str)
        # Remove trailing commas in arrays: [ 1, 2, ] -> [ 1, 2 ]
        json_str = re.sub(r',\s*\]', ']', json_str)
        
        return json_str
    
    def check_health(self) -> bool:
        """
        Check if the AI service is healthy and ready to use.
        """
        if self.provider:
            return self.provider.health_check()
        return False
    
    def _generate_mock_response(self, prompt: str, topic: str = "General Topic", subject: str = "Mathematics", grade: str = "Grade 4") -> str:
        """Generate a mock response for testing purposes."""
        if "comprehensive lesson resource" in prompt.lower():
            return self._generate_mock_lesson_resource(topic, subject, grade)
        else:
            return f"Mock response: This is a placeholder response for {topic} in {subject} for {grade} students."
    
    def _clean_and_repair(self, content: str) -> str:
        """
        Clean markdown formatting and repair common JSON syntax errors.
        """
        if not content: return ""
        
        # 1. Strip markdown
        clean_content = content.replace("```json", "").replace("```", "").strip()
        
        # 2. Extract JSON payload if surrounded by text
        if "{" in clean_content:
            import re
            match = re.search(r'(\{.*\})', clean_content, re.DOTALL)
            if match:
                clean_content = match.group(1)
                
        # 3. Repair JSON syntax (trailing commas)
        clean_content = self._repair_json(clean_content)
        
        return clean_content

    def _generate_mock_lesson_resource(self, topic: str = "General Topic", subject: str = "Mathematics", grade: str = "Grade 4") -> str:
        """Generate a mock comprehensive lesson resource with enhanced local context."""
        return json.dumps({
            "title_header": {
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "country": "Nigeria",
                "local_context": "Nigerian classroom with basic resources"
            },
            "learning_objectives": [
                f"Demonstrate understanding of {topic.lower()} through local examples and practical applications",
                f"Apply {topic.lower()} concepts to solve real-world problems in the community",
                f"Create practical solutions using {topic.lower()} knowledge relevant to local context"
            ],
            "lesson_content": {
                "introduction": f"Today we will explore {topic.lower()} through the lens of our local community, connecting abstract concepts to everyday experiences that students encounter in their daily lives.",
                "main_concepts": [
                    f"Core Concept 1: {topic} fundamentals explained through local market scenarios, agricultural practices, and community infrastructure",
                    f"Core Concept 2: Practical applications of {topic.lower()} in local businesses, transportation systems, and community services",
                    f"Core Concept 3: Advanced {topic.lower()} applications in local technology, healthcare, and environmental conservation"
                ],
                "examples": [
                    f"Local Market Application: How {topic.lower()} concepts apply to pricing, measurements, and transactions in our community markets",
                    f"Agricultural Connection: Using {topic.lower()} principles to understand crop yields, irrigation systems, and farm management in local farming",
                    f"Community Infrastructure: How {topic.lower()} concepts relate to road construction, building design, and urban planning in our area"
                ],
                "step_by_step_instructions": [
                    "Step 1: Introduce concepts using familiar local objects and scenarios that students encounter daily",
                    "Step 2: Demonstrate practical applications through hands-on activities using local materials and resources",
                    "Step 3: Guide students in applying concepts to solve real community problems and create local solutions"
                ]
            },
            "assessment": [
                f"Critical Thinking: Analyze how {topic.lower()} concepts could solve a specific local community challenge",
                f"Practical Application: Design a solution using {topic.lower()} principles for a real local problem",
                f"Creative Problem-Solving: Develop an innovative approach to apply {topic.lower()} knowledge in the community"
            ],
            "key_takeaways": [
                f"Real-Life Relevance: {topic} concepts directly apply to daily activities like shopping, transportation, and community planning",
                f"Community Impact: Understanding {topic.lower()} enables students to contribute to local development and problem-solving",
                f"Future Applications: {topic} knowledge opens opportunities in local industries, entrepreneurship, and community leadership"
            ],
            "related_projects_or_activities": [
                f"Community Survey Project: Students research and document how {topic.lower()} concepts are used in local businesses and services",
                f"Local Problem-Solving Workshop: Groups identify community challenges and apply {topic.lower()} knowledge to propose solutions",
                f"Hands-On Demonstration: Students create practical models or demonstrations using local materials to showcase {topic.lower()} concepts"
            ],
            "references": [
                f"Nigerian National Curriculum - {subject} {grade} with local adaptation guidelines",
                f"Local {subject} textbook and community resource materials",
                f"Community experts, local businesses, and organizations that can support practical learning"
            ]
        }, indent=2)
    
    def generate_lesson_resource(
        self,
        subject: str,
        grade: str,
        topic: str,
        objectives: List[str],
        contents: Optional[List[str]] = None,
        duration: int = 45,
        context: Optional[str] = None,
        template_schema: Optional[str] = None,
        model_tier: str = "standard"
    ) -> tuple[str, bool]:
        """
        Generate a comprehensive lesson resource using the prompt template.
        """
        try:
            logger.info(f"Generating lesson resource for {subject} {grade} - {topic} (Tier: {model_tier})")
            
            # Format objectives as string
            objectives_str = ", ".join(objectives) if objectives else "To be determined"
            
            # Sanitise user-supplied context before it enters the prompt (AWD-M-12).
            # _sanitize_user_context enforces a length cap, strips PII, and removes
            # instruction-injection patterns.
            safe_context = self._sanitize_user_context(context) if context else None

            # Get country from context or use default
            country = "Nigeria"  # Default country
            if safe_context:
                context_lower = safe_context.lower()
                if "nigeria" in context_lower: country = "Nigeria"
                elif "ghana" in context_lower: country = "Ghana"
                elif "kenya" in context_lower: country = "Kenya"

            # Prepare prompt parameters
            contents_val = ", ".join(contents) if contents else "Comprehensive lesson content including introduction, main concepts, examples, and activities"
            if template_schema:
                contents_val = f"{contents_val}\n\nSTRICT TEMPLATE STRUCTURE RULES:\n{template_schema}"

            prompt_params = {
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "country": country,
                "local_context": safe_context or "Standard classroom with basic resources",
                "learning_objectives": objectives_str,
                "contents": contents_val
            }
            
            # Generate prompt
            prompt = COMPREHENSIVE_LESSON_RESOURCE_PROMPT.format(**prompt_params)
            prompt = self._sanitize_input(prompt)
            
            # Construct metadata for caching
            # We use the prompt_params as the unique identifier for the request logic
            # This satisfies "Include Context Input in cache hash" since context is in prompt_params["local_context"]
            prompt_metadata = {
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "objectives": objectives,
                "context": safe_context,  # Use sanitised value, not raw user input (AWD-M-39)
                "template_schema": template_schema
            }
            
            # Make API call
            response = self._make_api_call(
                prompt=prompt, 
                topic=topic, 
                subject=subject, 
                grade=grade,
                model_tier=model_tier,
                prompt_metadata=prompt_metadata,
                response_format="json"  # Enforce JSON mode
            )
            
            # Clean and repair the response before validation
            # This ensures we store valid JSON even if the Provider returned markdown or trailing commas
            cleaned_response = self._clean_and_repair(response)
            
            # Validate output (using the cleaned version)
            is_valid, reason = self.validate_output(cleaned_response)
            if not is_valid:
                logger.warning(f"AI output failed validation: {reason}. Flagging for review.")
                # We return the cleaned version even if invalid, as it's better than raw markdown
                return cleaned_response, False
                
            return cleaned_response, True
                
        except Exception as e:
            logger.error(f"Error generating lesson resource: {e}")
            return self._generate_mock_lesson_resource(topic, subject, grade), True

    # ─── Parent Guide Generation ──────────────────────────────────────

    def generate_parent_guide(
        self,
        subject: str,
        grade: str,
        topic: str,
        country: str,
        curriculum: str,
        objectives: List[str],
        contents: Optional[List[str]] = None,
        model_tier: str = "standard",
    ) -> tuple[str, bool]:
        """
        Generate a 'How to Help' guide for a parent using the PARENT_HELPER_PROMPT.

        Returns:
            tuple[str, bool]: (JSON string of the guide, whether validation passed)
        """
        try:
            logger.info(f"Generating parent guide for {subject} {grade} - {topic} ({country})")

            objectives_str = ", ".join(objectives) if objectives else "To be determined"
            contents_str = (
                ", ".join(contents) if contents
                else "General topic content"
            )

            # Pre-format: sanitise each curriculum field individually before
            # template substitution so PII / key-like strings are stripped
            # prior to being embedded in the prompt (AWD-M-128 defence-in-depth).
            prompt_params = {
                "topic": self._sanitize_input(topic),
                "subject": self._sanitize_input(subject),
                "grade_level": self._sanitize_input(grade),
                "country": self._sanitize_input(country),
                "curriculum": self._sanitize_input(curriculum),
                "learning_objectives": self._sanitize_input(objectives_str),
                "contents": self._sanitize_input(contents_str),
            }

            prompt = PARENT_HELPER_PROMPT.format(**prompt_params)
            prompt = self._sanitize_input(prompt)  # post-format pass retained

            prompt_metadata = {
                "type": "parent_guide",
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "country": country,
                "curriculum": curriculum,
                "objectives": objectives,
            }

            response = self._make_api_call(
                prompt=prompt,
                topic=topic,
                subject=subject,
                grade=grade,
                model_tier=model_tier,
                prompt_metadata=prompt_metadata,
                response_format="json",
            )

            cleaned = self._clean_and_repair(response)

            # Light validation — check for key fields
            is_valid, reason = self._validate_parent_guide(cleaned)
            if not is_valid:
                logger.warning(f"Parent guide validation failed: {reason}")
                return cleaned, False

            return cleaned, True

        except Exception as e:
            logger.error(f"Error generating parent guide: {e}")
            return self._generate_mock_parent_guide(topic, subject, grade, country, curriculum), True

    def _validate_parent_guide(self, content: str) -> tuple[bool, Optional[str]]:
        """Validate a parent-guide AI output.

        Runs in two passes (mirrors ``validate_output`` for lesson resources):

        1. Content-safety pass on the raw string — PII, prompt-injection markers,
           harmful content (AWD-M-58, OWASP LLM02). Persisted parent guides are
           exported as PDF, so any unscrubbed model emission must be rejected
           before it reaches the database.
        2. Structural validation — JSON parse + required top-level keys.
        """
        # 1. Content-safety pass (raw string — before JSON parsing)
        is_safe, safety_reason = self._check_content_safety(content)
        if not is_safe:
            return False, safety_reason

        # 2. Structural validation
        try:
            data = json.loads(content)
            required = ["topic_header", "simple_explanation", "home_activity", "conversation_starters", "common_mistakes"]
            for field in required:
                if field not in data:
                    return False, f"Missing required field: {field}"
            return True, None
        except json.JSONDecodeError:
            return False, "Invalid JSON format"

    def _generate_mock_parent_guide(
        self,
        topic: str = "General Topic",
        subject: str = "Mathematics",
        grade: str = "Grade 4",
        country: str = "Nigeria",
        curriculum: str = "Nigerian Curriculum",
    ) -> str:
        """Generate a mock parent guide for testing / fallback."""
        return json.dumps({
            "topic_header": {
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "country": country,
                "curriculum": curriculum,
            },
            "simple_explanation": {
                "what_it_is": f"{topic} is a foundational concept in {subject} that helps children understand how things work in the world around them. Think of it as the building blocks your child will use for more advanced ideas later on. At this level, the focus is on understanding the basics through practical, everyday examples.",
                "why_it_matters": f"Understanding {topic.lower()} helps your child solve problems they encounter every day — from shopping at the market to understanding how things are built in your community.",
            },
            "home_activity": {
                "title": f"Kitchen Table {subject} Challenge",
                "description": f"A fun 20-minute activity where you and your child explore {topic.lower()} using things you already have at home.",
                "materials_needed": [
                    "A notebook or scrap paper",
                    "A pen or pencil",
                    "Household items (cups, spoons, coins)",
                ],
                "steps": [
                    f"Step 1: Start by asking your child what they already know about {topic.lower()}. Listen without correcting — you want to understand where they are.",
                    "Step 2: Together, look around the kitchen or living room for examples that connect to the topic. Talk about what you find.",
                    "Step 3: Create a simple challenge — ask your child to explain the concept to you as if you've never heard of it before. This is where real understanding shows.",
                ],
                "what_to_look_for": "Your child can explain the basic idea in their own words, even if the language isn't perfect. They can point to a real example in your home.",
            },
            "conversation_starters": [
                f"What did your teacher say about {topic.lower()} today? Was there anything that surprised you?",
                f"If you had to explain {topic.lower()} to your younger cousin, what would you say?",
                f"Can you think of a time you've seen {topic.lower()} in real life — maybe at the market or on the way to school?",
            ],
            "common_mistakes": [
                {
                    "mistake": f"Confusing {topic.lower()} with a related but different concept",
                    "why_it_happens": "At this age, children are still building mental categories. It's completely normal to mix up similar ideas.",
                    "how_to_help": "Instead of saying 'that's wrong,' try asking 'what's the difference between X and Y?' and let them work it out. If they get stuck, give a concrete example from home.",
                },
                {
                    "mistake": "Memorising steps without understanding why they work",
                    "why_it_happens": "School often rewards getting the right answer, so children learn to follow steps without asking why.",
                    "how_to_help": "Ask 'why does that step come next?' or 'what would happen if we skipped it?' — this builds real understanding, not just memorisation.",
                },
            ],
            "curriculum_context": {
                "what_came_before": f"Before this topic, your child learned foundational concepts that set the stage for {topic.lower()}. If they're struggling, it might help to quickly revisit those basics.",
                "what_comes_next": f"After {topic.lower()}, the curriculum moves to more advanced applications. A strong understanding now means less struggle later.",
                "how_long_in_school": "About 1-2 weeks of class time",
            },
            "encouragement_tips": [
                f"Try saying: 'I can see you're really thinking hard about this — that's exactly what good learners do.' Effort-based praise builds resilience.",
                "If your child is frustrated, take a break. Say: 'Let's come back to this after dinner — sometimes our brains need time to process.' This teaches them that struggle is normal, not a sign of failure.",
            ],
        }, indent=2)