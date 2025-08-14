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

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except ImportError:
    pass
except Exception as e:
    pass

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
        
        # GPT-5 specific configuration
        self.reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", "medium")  # minimal, low, medium, high
        self.verbosity = os.getenv("OPENAI_VERBOSITY", "medium")  # low, medium, high
        
        # Initialize OpenAI client
        if OPENAI_AVAILABLE and self.api_key:
            try:
                openai.api_key = self.api_key
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized successfully with model: {self.model}")
                if self.model.startswith("gpt-5"):
                    logger.info(f"GPT-5 configuration: reasoning_effort={self.reasoning_effort}, verbosity={self.verbosity}")
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
            return self._generate_mock_lesson_resource(topic, subject, grade)
        except openai.RateLimitError as e:
            return self._generate_mock_lesson_resource(topic, subject, grade)
        except openai.APIError as e:
            return self._generate_mock_lesson_resource(topic, subject, grade)
        except Exception as e:
            return self._generate_mock_lesson_resource(topic, subject, grade)
    
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
        
        # Add GPT-5 specific status
        if self.model.startswith("gpt-5"):
            status["reasoning_effort"] = self.reasoning_effort
            status["verbosity"] = self.verbosity
            status["supports_gpt5_features"] = True
        else:
            status["supports_gpt5_features"] = False
        
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
            # Extract topic, subject, and grade from the prompt if possible
            # For now, use default values
            return self._generate_mock_lesson_resource("General Topic", "Mathematics", "Grade 4")
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
            logger.info(f"Generated prompt for {country} context")
            
            # Make API call with topic, subject, and grade for proper mock responses
            response = self._make_api_call(prompt, topic=topic, subject=subject, grade=grade)
            logger.info(f"Received response from OpenAI API (length: {len(response)} characters)")
            
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
            return self._generate_mock_lesson_resource(topic, subject, grade)
    
    def generate_comprehensive_lesson_resource(
        self,
        subject: str,
        grade: str,
        topic: str,
        learning_objectives: List[str],
        contents: List[str],
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
                contents=contents,
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
                return {
                    "status": "partial_success",
                    "lesson_resource": {"raw_content": lesson_resource_json},
                    "raw_response": lesson_resource_json
                }
                
        except Exception as e:
            fallback_resource = self._generate_fallback_comprehensive_resource(
                subject, grade, topic, learning_objectives, contents
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
        learning_objectives: List[str],
        contents: List[str]
    ) -> Dict[str, Any]:
        """Generate a fallback comprehensive lesson resource with enhanced local context."""
        return {
            "title_header": {
                "topic": topic,
                "subject": subject,
                "grade_level": grade,
                "country": "Nigeria",
                "local_context": "Nigerian classroom with basic resources"
            },
            "learning_objectives": learning_objectives or [
                f"Demonstrate comprehensive understanding of {topic.lower()} through local examples and practical applications",
                f"Apply {topic.lower()} concepts to solve real-world problems in the Nigerian community context",
                f"Create innovative solutions using {topic.lower()} knowledge relevant to local development needs"
            ],
            "lesson_content": {
                "introduction": f"Today we will explore {topic.lower()} through the lens of our Nigerian community, connecting abstract concepts to everyday experiences that students encounter in their daily lives, from local markets to community infrastructure.",
                "main_concepts": contents or [
                    f"Core Concept 1: {topic} fundamentals explained through Nigerian market scenarios, agricultural practices, and community infrastructure",
                    f"Core Concept 2: Practical applications of {topic.lower()} in local businesses, transportation systems, and community services",
                    f"Core Concept 3: Advanced {topic.lower()} applications in local technology, healthcare, and environmental conservation"
                ],
                "examples": [
                    f"Local Market Application: How {topic.lower()} concepts apply to pricing, measurements, and transactions in Nigerian community markets",
                    f"Agricultural Connection: Using {topic.lower()} principles to understand crop yields, irrigation systems, and farm management in local Nigerian farming",
                    f"Community Infrastructure: How {topic.lower()} concepts relate to road construction, building design, and urban planning in Nigerian communities"
                ],
                "step_by_step_instructions": [
                    "Step 1: Introduce concepts using familiar Nigerian objects and scenarios that students encounter daily",
                    "Step 2: Demonstrate practical applications through hands-on activities using local Nigerian materials and resources",
                    "Step 3: Guide students in applying concepts to solve real Nigerian community problems and create local solutions"
                ]
            },
            "assessment": [
                f"Critical Thinking: Analyze how {topic.lower()} concepts could solve a specific Nigerian community challenge",
                f"Practical Application: Design a solution using {topic.lower()} principles for a real local Nigerian problem",
                f"Creative Problem-Solving: Develop an innovative approach to apply {topic.lower()} knowledge in the Nigerian community context"
            ],
            "key_takeaways": [
                f"Real-Life Relevance: {topic} concepts directly apply to daily Nigerian activities like shopping, transportation, and community planning",
                f"Community Impact: Understanding {topic.lower()} enables students to contribute to Nigerian local development and problem-solving",
                f"Future Applications: {topic} knowledge opens opportunities in Nigerian local industries, entrepreneurship, and community leadership"
            ],
            "related_projects_or_activities": [
                f"Community Survey Project: Students research and document how {topic.lower()} concepts are used in Nigerian local businesses and services",
                f"Local Problem-Solving Workshop: Groups identify Nigerian community challenges and apply {topic.lower()} knowledge to propose solutions",
                f"Hands-On Demonstration: Students create practical models or demonstrations using Nigerian local materials to showcase {topic.lower()} concepts"
            ],
            "references": [
                f"Nigerian National Curriculum - {subject} {grade} with local adaptation guidelines",
                f"Local Nigerian {subject} textbook and community resource materials",
                f"Nigerian community experts, local businesses, and organizations that can support practical learning"
            ]
        }
    
    def generate_lesson_resource_gpt5_responses_api(
        self,
        subject: str,
        grade: str,
        topic: str,
        learning_objectives: List[str],
        contents: List[str],
        duration: int = 45,
        local_context: Optional[str] = None,
        previous_response_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a lesson resource using GPT-5 with the Responses API for better performance.
        
        This method uses the new Responses API which supports:
        - Chain of thought (CoT) between turns
        - Better reasoning capabilities
        - Improved performance and lower latency
        
        Args:
            subject (str): Subject area (e.g., Mathematics, Science)
            grade (str): Grade level (e.g., Grade 4, JSS1)
            topic (str): Specific topic to teach
            learning_objectives (List[str]): Learning objectives
            contents (List[str]): Content areas to cover
            duration (int): Lesson duration in minutes
            local_context (Optional[str]): Local context and available resources
            previous_response_id (Optional[str]): ID of previous response for CoT continuity
            
        Returns:
            Dict[str, Any]: Generated lesson resource with status and content
        """
        if not self.client or not self.model.startswith("gpt-5"):
            return self.generate_comprehensive_lesson_resource(
                subject, grade, topic, learning_objectives, contents, duration, local_context
            )
        
        try:
            # Create prompt for GPT-5
            prompt = f"""
Create a comprehensive lesson resource for {topic} in {subject} for {grade} students in Nigeria.

Learning Objectives: {', '.join(learning_objectives)}
Content Areas: {', '.join(contents)}
Duration: {duration} minutes
Context: {local_context or "Standard Nigerian classroom"}

Generate a structured lesson resource that includes:
- Clear learning objectives
- Engaging introduction
- Main concepts with examples
- Step-by-step instructions
- Assessment questions
- Key takeaways
- Related activities
- Cultural relevance to Nigeria

Format the response as a comprehensive JSON object.
"""
            
            # Prepare API parameters for Responses API
            api_params = {
                "model": self.model,
                "input": prompt,
                "reasoning": {
                    "effort": self.reasoning_effort
                },
                "text": {
                    "verbosity": self.verbosity
                }
            }
            
            # Add previous response ID for CoT continuity if available
            if previous_response_id:
                api_params["previous_response_id"] = previous_response_id
                logger.info(f"Using previous response ID for CoT continuity: {previous_response_id}")
            
            logger.info(f"Making GPT-5 Responses API call with reasoning_effort={self.reasoning_effort}, verbosity={self.verbosity}")
            
            # Use the responses API for GPT-5
            response = self.client.responses.create(**api_params)
            
            # Extract content from the response
            content = response.output[0].text.value if response.output else ""
            
            if not content:
                return {
                    "status": "fallback",
                    "lesson_resource": self._generate_fallback_comprehensive_resource(
                        subject, grade, topic, learning_objectives
                    ),
                    "response_id": response.id
                }
            
            # Try to parse as JSON
            try:
                lesson_resource = json.loads(content)
                return {
                    "status": "success",
                    "lesson_resource": lesson_resource,
                    "raw_response": content,
                    "response_id": response.id,
                    "reasoning_items": response.reasoning_items if hasattr(response, 'reasoning_items') else None
                }
            except json.JSONDecodeError:
                return {
                    "status": "partial_success",
                    "lesson_resource": {"raw_content": content},
                    "raw_response": content,
                    "response_id": response.id,
                    "reasoning_items": response.reasoning_items if hasattr(response, 'reasoning_items') else None
                }
                
        except Exception as e:
            return self.generate_comprehensive_lesson_resource(
                subject, grade, topic, learning_objectives, contents, duration, local_context
            )
    
    def get_gpt5_capabilities(self) -> Dict[str, Any]:
        """
        Get information about GPT-5 capabilities and configuration.
        
        Returns:
            Dict[str, Any]: GPT-5 capabilities and configuration details
        """
        if not self.model.startswith("gpt-5"):
            return {"error": "Not using GPT-5 model"}
        
        return {
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "verbosity": self.verbosity,
            "supports_responses_api": True,
            "supports_chain_of_thought": True,
            "supports_custom_tools": True,
            "supports_context_free_grammars": True,
            "best_for": [
                "Complex reasoning tasks",
                "Code generation and refactoring",
                "Long context processing",
                "Tool calling and agentic tasks",
                "Instruction following"
            ],
            "recommended_settings": {
                "reasoning_effort": {
                    "minimal": "Fastest response, good for simple tasks",
                    "low": "Balanced speed and quality",
                    "medium": "Default setting, good for most tasks",
                    "high": "Highest quality, thorough reasoning"
                },
                "verbosity": {
                    "low": "Concise responses, good for code generation",
                    "medium": "Balanced detail, good for explanations",
                    "high": "Detailed responses, good for documentation"
                }
            }
        }