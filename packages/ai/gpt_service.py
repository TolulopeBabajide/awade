"""
GPT Service for Awade Lesson Planning

This module provides AI-powered services for lesson plan generation,
curriculum alignment, and educational content creation using OpenAI's GPT models.

Author: Tolulope Babajide
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import OpenAI if available, otherwise use mock
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI package not available. Using mock responses.")

from .prompts import COMPREHENSIVE_LESSON_RESOURCE_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            self.client = None
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI package not available. Using mock responses.")
            elif not self.api_key:
                logger.warning("OpenAI API key not configured. Using mock responses.")
    
    def _make_api_call(self, prompt: str, temperature: Optional[float] = None) -> str:
        """
        Make an API call to OpenAI or return mock response.
        
        Args:
            prompt (str): The prompt to send to the AI
            temperature (Optional[float]): Creativity level (0.0 to 1.0). If not provided, uses configured default.
            
        Returns:
            str: AI response or mock response
        """
        if not self.client:
            logger.info("Using mock response (OpenAI client not available)")
            return self._generate_mock_response(prompt)
        
        # Use configured temperature if not provided
        temp = temperature if temperature is not None else self.temperature
        
        try:
            logger.info(f"Making OpenAI API call with model: {self.model}, temperature: {temp}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator specializing in African curriculum development. You create comprehensive, locally contextual lesson resources that are age-appropriate, culturally relevant, and practical for teachers to implement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI API call successful. Response length: {len(content)} characters")
            return content
            
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication failed: {str(e)}")
            return self._generate_mock_response(prompt)
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            return self._generate_mock_response(prompt)
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_mock_response(prompt)
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI API call: {str(e)}")
            return self._generate_mock_response(prompt)
    
    def test_openai_connection(self) -> Dict[str, Any]:
        """
        Test the OpenAI API connection and return status information.
        
        Returns:
            Dict[str, Any]: Connection status and configuration details
        """
        status = {
            "openai_available": OPENAI_AVAILABLE,
            "api_key_configured": bool(self.api_key),
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "client_initialized": bool(self.client),
            "connection_test": False,
            "error": None
        }
        
        if not self.client:
            status["error"] = "OpenAI client not initialized"
            return status
        
        try:
            # Make a simple test call
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                max_tokens=10
            )
            status["connection_test"] = True
            status["test_response"] = test_response.choices[0].message.content
            logger.info("OpenAI connection test successful")
        except Exception as e:
            status["error"] = str(e)
            logger.error(f"OpenAI connection test failed: {str(e)}")
        
        return status
    
    def check_health(self) -> bool:
        """
        Check if the AI service is healthy and ready to use.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            status = self.test_openai_connection()
            return status.get("connection_test", False) or bool(self.client)
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def _generate_mock_response(self, prompt: str) -> str:
        """
        Generate a mock response for testing purposes.
        
        Args:
            prompt (str): The original prompt
            
        Returns:
            str: Mock response
        """
        if "comprehensive lesson resource" in prompt.lower():
            return self._generate_mock_lesson_resource()
        else:
            return "Mock response: This is a placeholder response for testing purposes."
    
    def _generate_mock_lesson_resource(self) -> str:
        """Generate a mock comprehensive lesson resource."""
        return json.dumps({
            "title_header": {
                "topic": "Fractions",
                "subject": "Mathematics",
                "grade_level": "Grade 4",
                "country": "Nigeria",
                "local_context": "Nigerian classroom with basic resources"
            },
            "learning_objectives": [
                "Understand basic fraction concepts using local examples",
                "Identify fractions in everyday objects from the community",
                "Compare simple fractions using local materials"
            ],
            "lesson_content": {
                "introduction": "Today we will learn about fractions using objects from our community.",
                "main_concepts": [
                    "Fractions represent parts of a whole",
                    "Fractions can be written as numbers",
                    "We can compare fractions using different methods"
                ],
                "examples": [
                    "Using local fruits to demonstrate fractions",
                    "Using classroom objects to show parts of a whole"
                ],
                "step_by_step_instructions": [
                    "Step 1: Introduce the concept using familiar objects",
                    "Step 2: Demonstrate fractions with visual aids",
                    "Step 3: Practice with hands-on activities"
                ]
            },
            "assessment": [
                "Multiple choice questions about fractions",
                "Short answer questions with real-world examples",
                "Practical application problems"
            ],
            "key_takeaways": [
                "Fractions represent parts of a whole",
                "Fractions can be found in everyday objects",
                "We can compare fractions using different methods"
            ],
            "related_projects_or_activities": [
                "Community fraction hunt project",
                "Local market fraction activity",
                "Classroom fraction display"
            ],
            "references": [
                "Nigerian National Curriculum - Mathematics Grade 4",
                "Local mathematics textbook",
                "Community resources for hands-on learning"
            ]
        }, indent=2)
    
    def generate_lesson_resource(
        self,
        subject: str,
        grade: str,
        topic: str,
        objectives: List[str],
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
            logger.info(f"Objectives: {objectives}")
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
                "contents": "Comprehensive lesson content including introduction, main concepts, examples, and activities"
            }
            
            # Generate prompt using the template
            prompt = COMPREHENSIVE_LESSON_RESOURCE_PROMPT.format(**prompt_params)
            logger.info(f"Generated prompt for {country} context")
            
            # Make API call
            response = self._make_api_call(prompt)
            logger.info(f"Received response from OpenAI API (length: {len(response)} characters)")
            
            # Try to parse as JSON, fallback to plain text if needed
            try:
                # Check if response is valid JSON
                parsed_json = json.loads(response)
                logger.info("Successfully parsed AI response as JSON")
                return response
            except json.JSONDecodeError as e:
                # If not valid JSON, return as plain text
                logger.warning(f"AI response is not valid JSON: {str(e)}")
                logger.warning(f"Response preview: {response[:200]}...")
                logger.warning(f"Response ends with: {response[-100:]}...")
                return response
                
        except Exception as e:
            logger.error(f"Error generating lesson resource: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._generate_mock_lesson_resource()
    
    def generate_comprehensive_lesson_resource(
        self,
        subject: str,
        grade: str,
        topic: str,
        learning_objectives: List[str],
        duration: int = 45,
        local_context: Optional[str] = None,
        curriculum_framework: str = "Nigerian National Curriculum"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive lesson resource with structured JSON output.
        
        Args:
            subject (str): Subject area (e.g., Mathematics, Science)
            grade (str): Grade level (e.g., Grade 4, JSS1)
            topic (str): Specific topic to teach
            learning_objectives (List[str]): Learning objectives
            duration (int): Lesson duration in minutes
            local_context (Optional[str]): Local context and available resources
            curriculum_framework (str): Curriculum framework name
            
        Returns:
            Dict[str, Any]: Generated lesson resource with status and content
        """
        try:
            # Generate the lesson resource using the main method
            lesson_resource_json = self.generate_lesson_resource(
                subject=subject,
                grade=grade,
                topic=topic,
                objectives=learning_objectives,
                duration=duration,
                context=local_context
            )
            
            # Try to parse as JSON, fallback to plain text if needed
            try:
                lesson_resource = json.loads(lesson_resource_json)
                return {
                    "status": "success",
                    "lesson_resource": lesson_resource,
                    "raw_response": lesson_resource_json
                }
            except json.JSONDecodeError:
                # If not valid JSON, return as plain text
                logger.warning("AI response is not valid JSON, returning as plain text")
                return {
                    "status": "partial_success",
                    "lesson_resource": {"raw_content": lesson_resource_json},
                    "raw_response": lesson_resource_json
                }
                
        except Exception as e:
            logger.error(f"Error generating comprehensive lesson resource: {str(e)}")
            fallback_resource = self._generate_fallback_comprehensive_resource(
                subject, grade, topic, learning_objectives
            )
            return {
                "status": "fallback",
                "lesson_resource": fallback_resource,
                "error": str(e)
            }
    
    def _generate_fallback_comprehensive_resource(
        self,
        subject: str,
        grade: str,
        topic: str,
        learning_objectives: List[str]
    ) -> Dict[str, Any]:
        """Generate a fallback comprehensive lesson resource."""
        return {
            "title_header": {
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "country": "Nigeria",
                "local_context": "Standard classroom with basic resources"
            },
            "learning_objectives": learning_objectives,
            "lesson_content": {
                "introduction": f"Introduction to {topic}",
                "main_concepts": [
                    f"Main concept 1 for {topic}",
                    f"Main concept 2 for {topic}",
                    f"Main concept 3 for {topic}"
                ],
                "examples": [
                    f"Example 1 for {topic}",
                    f"Example 2 for {topic}"
                ],
                "step_by_step_instructions": [
                    "Step 1: Introduction",
                    "Step 2: Main content",
                    "Step 3: Practice"
                ]
            },
            "assessment": [
                f"Assessment question 1 for {topic}",
                f"Assessment question 2 for {topic}",
                f"Assessment question 3 for {topic}"
            ],
            "key_takeaways": [
                f"Key takeaway 1 about {topic}",
                f"Key takeaway 2 about {topic}",
                f"Key takeaway 3 about {topic}"
            ],
            "related_projects_or_activities": [
                f"Project 1 for {topic}",
                f"Activity 1 for {topic}",
                f"Project 2 for {topic}"
            ],
            "references": [
                f"Reference 1 for {topic}",
                f"Reference 2 for {topic}",
                f"Reference 3 for {topic}"
            ]
        }
    
   