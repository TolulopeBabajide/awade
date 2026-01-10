"""
GPT Service for Awade Lesson Planning

This module provides AI-powered services for lesson plan generation,
curriculum alignment, and educational content creation using OpenAI's GPT models.

Author: Tolulope Babajide
"""

import os
import json
import logging
import re
from typing import List, Dict, Any, Optional

# Import OpenAI if available, otherwise use mock
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available. Using mock responses.")

from .prompts import COMPREHENSIVE_LESSON_RESOURCE_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the GPT service.
        
        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, will try to get from environment.
            model (Optional[str]): OpenAI model to use. If not provided, will use environment variable.
        """
        # Get configuration from environment variables
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # Initialize OpenAI client
        if OPENAI_AVAILABLE and self.api_key:
            try:
                openai.api_key = self.api_key
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized successfully with model: {self.model}")
            except Exception as e:
                self.client = None
        else:
            self.client = None
            if not OPENAI_AVAILABLE:
                pass
            elif not self.api_key:
                pass
    
    def _make_api_call(self, prompt: str, temperature: Optional[float] = None, topic: str = "General Topic", subject: str = "Mathematics", grade: str = "Grade 4") -> str:
        """
        Make an API call to OpenAI or return mock response.
        
        Args:
            prompt (str): The prompt to send to the AI
            temperature (Optional[float]): Creativity level (0.0 to 1.0). If not provided, uses configured default.
            topic (str): The topic being taught (for mock responses)
            subject (str): The subject area (for mock responses)
            grade (str): The grade level (for mock responses)
            
        Returns:
            str: AI response or mock response
        """
        if not self.client:
            logger.info("Using mock response (OpenAI client not available)")
            return self._generate_mock_response(prompt, topic, subject, grade)
        
        # Use configured temperature if not provided
        temp = temperature if temperature is not None else self.temperature
        
        try:
            logger.info(f"Making OpenAI API call with model: {self.model}, temperature: {temp}")
            
            # Prepare API parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert educational content creator specializing in African curriculum development. You create comprehensive, locally contextual lesson resources that are age-appropriate, culturally relevant, and practical for teachers to implement."},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Add token limit parameter
            api_params["max_tokens"] = self.max_tokens
            
            # Add temperature parameter
            api_params["temperature"] = temp
            
            response = self.client.chat.completions.create(**api_params)
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI API call successful. Response length: {len(content)} characters")
            
            # Check if response is empty or just whitespace
            if not content or not content.strip():
                return self._generate_mock_lesson_resource(topic, subject, grade)
            
            return content
            
        except openai.AuthenticationError as e:
            logger.warning(f"OpenAI authentication failed: {e}")
            return self._generate_mock_lesson_resource(topic, subject, grade)
        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {e}")
            return self._generate_mock_lesson_resource(topic, subject, grade)
        except openai.APIError as e:
            logger.warning(f"OpenAI API error: {e}")
            return self._generate_mock_lesson_resource(topic, subject, grade)
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI API call: {e}")
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

    def _validate_output(self, content: str) -> bool:
        """
        Validate the AI output for safety and structure.
        """
        try:
            data = json.loads(content)
            
            # Check for minimum required fields
            required_fields = ["title_header", "learning_objectives", "lesson_content"]
            for field in required_fields:
                if field not in data:
                    logger.warning(f"AI output missing required field: {field}")
                    return False
            
            # Simple check for harmful patterns in text (placeholder)
            # In production, use a dedicated safety API or model
            harmful_patterns = [r"badword1", r"badword2"] # Example
            str_content = str(data).lower()
            for pattern in harmful_patterns:
                if re.search(pattern, str_content):
                    logger.warning("Harmful pattern detected in AI output")
                    return False
                    
            return True
        except json.JSONDecodeError:
            return False
    
    def check_health(self) -> bool:
        """
        Check if the AI service is healthy and ready to use.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            return bool(self.client)
        except Exception as e:
            return False
    
    def _generate_mock_response(self, prompt: str, topic: str = "General Topic", subject: str = "Mathematics", grade: str = "Grade 4") -> str:
        """
        Generate a mock response for testing purposes.
        
        Args:
            prompt (str): The original prompt
            topic (str): The topic being taught
            subject (str): The subject area
            grade (str): The grade level
            
        Returns:
            str: Mock response
        """
        if "comprehensive lesson resource" in prompt.lower():
            return self._generate_mock_lesson_resource(topic, subject, grade)
        else:
            return f"Mock response: This is a placeholder response for {topic} in {subject} for {grade} students."
    
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
        context: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive lesson resource using the prompt template.
        
        Args:
            subject (str): Subject area (e.g., Mathematics, Science)
            grade (str): Grade level (e.g., Grade 4, JSS1)
            topic (str): Specific topic to teach
            objectives (List[str]): Learning objectives from curriculum
            duration (int): Lesson duration in minutes
            context (Optional[str]): Local context and available resources
            
        Returns:
            str: Generated lesson resource content in JSON format
        """
        try:
            logger.info(f"Generating lesson resource for {subject} {grade} - {topic}")
            logger.info(f"Learning Objectives: {objectives}")
            logger.info(f"Contents: {contents}")
            logger.info(f"Context: {context}")
            
            # Format objectives as string
            objectives_str = ", ".join(objectives) if objectives else "To be determined"
            
            # Get country from context or use default
            country = "Nigeria"  # Default country
            if context and "nigeria" in context.lower():
                country = "Nigeria"
            elif context and "ghana" in context.lower():
                country = "Ghana"
            elif context and "kenya" in context.lower():
                country = "Kenya"
            
            # Prepare prompt parameters according to the template
            prompt_params = {
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "country": country,
                "local_context": context or "Standard classroom with basic resources",
                "learning_objectives": objectives_str,
                "contents": ", ".join(contents) if contents else "Comprehensive lesson content including introduction, main concepts, examples, and activities"
            }
            
            # Generate prompt using the template
            prompt = COMPREHENSIVE_LESSON_RESOURCE_PROMPT.format(**prompt_params)
            
            # Sanitize input
            prompt = self._sanitize_input(prompt)
            logger.info(f"Generated sanitized prompt for {country} context")
            
            # Make API call with topic, subject, and grade for proper mock responses
            response = self._make_api_call(prompt, topic=topic, subject=subject, grade=grade)
            
            # Validate output safety and structure
            if not self._validate_output(response):
                logger.warning("AI output failed validation. Falling back to mock/safe response.")
                return self._generate_mock_lesson_resource(topic, subject, grade)
                
            logger.info(f"Received validated response from OpenAI API (length: {len(response)} characters)")
            
            # Try to parse as JSON, fallback to plain text if needed
            try:
                # Check if response is valid JSON
                parsed_json = json.loads(response)
                logger.info("Successfully parsed AI response as JSON")
                return response
            except json.JSONDecodeError as e:
                # If not valid JSON, return as plain text
                return response
                
        except Exception as e:
            logger.error(f"Error generating lesson resource: {e}")
            return self._generate_mock_lesson_resource(topic, subject, grade)