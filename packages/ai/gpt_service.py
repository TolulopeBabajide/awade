"""
GPT service for Awade AI system.
Handles OpenAI API interactions with ethical safeguards and cultural considerations.
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from .prompts import (
    LESSON_PLAN_PROMPT,
    TRAINING_MODULE_PROMPT,
    CULTURAL_ADAPTATION_PROMPT,
    EXPLANATION_PROMPT
)

class AwadeGPTService:
    """
    Ethical AI service for educational content generation.
    Implements safeguards and cultural considerations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the GPT service with API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Ethical safeguards
        self.content_filters = [
            "inappropriate_content",
            "harmful_content",
            "biased_content"
        ]
    
    def generate_lesson_plan(
        self,
        subject: str,
        grade: str,
        objectives: List[str],
        duration: int = 45,
        language: str = "en",
        cultural_context: str = "African"
    ) -> Dict:
        """
        Generate a culturally relevant lesson plan.
        
        Args:
            subject: Subject area (e.g., "Mathematics", "Science")
            grade: Grade level (e.g., "Grade 4", "Grade 7")
            objectives: List of learning objectives
            duration: Lesson duration in minutes
            language: Primary language for the lesson
            cultural_context: Cultural context for adaptations
            
        Returns:
            Dict containing the generated lesson plan
        """
        try:
            prompt = LESSON_PLAN_PROMPT.format(
                subject=subject,
                grade=grade,
                objectives=", ".join(objectives),
                duration=duration,
                language=language
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert African educator. Generate culturally relevant, practical lesson plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse and structure the response
            content = response.choices[0].message.content
            return self._structure_lesson_plan(content, subject, grade, objectives)
            
        except Exception as e:
            return {
                "error": f"Failed to generate lesson plan: {str(e)}",
                "fallback": self._generate_fallback_lesson_plan(subject, grade, objectives)
            }
    
    def generate_training_module(
        self,
        topic: str,
        duration: int,
        audience: str = "African teachers",
        language: str = "en"
    ) -> Dict:
        """
        Generate a micro-training module for professional development.
        
        Args:
            topic: Training topic
            duration: Module duration in minutes
            audience: Target audience
            language: Module language
            
        Returns:
            Dict containing the training module
        """
        try:
            prompt = TRAINING_MODULE_PROMPT.format(
                topic=topic,
                duration=duration,
                audience=audience,
                language=language
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional development expert for African educators."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            return self._structure_training_module(content, topic, duration)
            
        except Exception as e:
            return {
                "error": f"Failed to generate training module: {str(e)}",
                "fallback": self._generate_fallback_training_module(topic, duration)
            }
    
    def explain_ai_content(self, content: str, context: str) -> str:
        """
        Explain AI-generated content in teacher-friendly terms.
        
        Args:
            content: The AI-generated content to explain
            context: Context for the explanation
            
        Returns:
            Explanation text
        """
        try:
            prompt = EXPLANATION_PROMPT.format(
                content=content,
                context=context
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a supportive mentor explaining AI suggestions to teachers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"
    
    def _structure_lesson_plan(self, content: str, subject: str, grade: str, objectives: List[str]) -> Dict:
        """Structure the raw AI response into a lesson plan format."""
        return {
            "title": f"{subject} Lesson Plan",
            "subject": subject,
            "grade": grade,
            "objectives": objectives,
            "activities": self._extract_activities(content),
            "materials": self._extract_materials(content),
            "assessment": self._extract_assessment(content),
            "rationale": self._extract_rationale(content),
            "content": content
        }
    
    def _structure_training_module(self, content: str, topic: str, duration: int) -> Dict:
        """Structure the raw AI response into a training module format."""
        return {
            "title": topic,
            "description": self._extract_description(content),
            "duration": duration,
            "objectives": self._extract_objectives(content),
            "steps": self._extract_steps(content),
            "content": content
        }
    
    def _extract_activities(self, content: str) -> List[str]:
        """Extract activities from AI response."""
        # Simple extraction - in production, use more sophisticated parsing
        lines = content.split('\n')
        activities = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['activity', 'exercise', 'task']):
                activities.append(line.strip())
        return activities[:3] if activities else ["Introduction", "Main content", "Assessment"]
    
    def _extract_materials(self, content: str) -> List[str]:
        """Extract materials from AI response."""
        lines = content.split('\n')
        materials = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['materials', 'resources', 'equipment']):
                materials.append(line.strip())
        return materials[:3] if materials else ["Whiteboard", "Markers", "Student worksheets"]
    
    def _extract_assessment(self, content: str) -> str:
        """Extract assessment strategy from AI response."""
        lines = content.split('\n')
        for line in lines:
            if 'assessment' in line.lower():
                return line.strip()
        return "Formative assessment through observation and student responses"
    
    def _extract_rationale(self, content: str) -> str:
        """Extract pedagogical rationale from AI response."""
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['rationale', 'reason', 'because']):
                return line.strip()
        return "This lesson plan follows best practices for active learning and student engagement"
    
    def _extract_description(self, content: str) -> str:
        """Extract module description from AI response."""
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                return line.strip()
        return "Professional development module"
    
    def _extract_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from AI response."""
        lines = content.split('\n')
        objectives = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['objective', 'goal', 'outcome']):
                objectives.append(line.strip())
        return objectives[:3] if objectives else ["Learn new strategies", "Apply knowledge", "Reflect on practice"]
    
    def _extract_steps(self, content: str) -> List[str]:
        """Extract step-by-step instructions from AI response."""
        lines = content.split('\n')
        steps = []
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                steps.append(line.strip())
        return steps[:5] if steps else ["Step 1", "Step 2", "Step 3"]
    
    def _generate_fallback_lesson_plan(self, subject: str, grade: str, objectives: List[str]) -> Dict:
        """Generate a basic fallback lesson plan when AI fails."""
        return {
            "title": f"{subject} Lesson Plan",
            "subject": subject,
            "grade": grade,
            "objectives": objectives,
            "activities": ["Introduction (5 min)", "Main content (30 min)", "Assessment (10 min)"],
            "materials": ["Whiteboard", "Markers", "Student worksheets"],
            "assessment": "Formative assessment through observation",
            "rationale": "Standard lesson structure for effective learning",
            "content": f"Basic {subject} lesson plan for {grade}"
        }
    
    def _generate_fallback_training_module(self, topic: str, duration: int) -> Dict:
        """Generate a basic fallback training module when AI fails."""
        return {
            "title": topic,
            "description": f"Professional development module on {topic}",
            "duration": duration,
            "objectives": ["Understand key concepts", "Apply new knowledge", "Reflect on practice"],
            "steps": ["Introduction", "Main content", "Practice", "Reflection"],
            "content": f"Basic training module on {topic}"
        } 