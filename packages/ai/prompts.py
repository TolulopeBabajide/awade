"""
AI Prompts for Awade Lesson Planning

This module contains prompt templates for AI-powered lesson plan generation,
curriculum alignment, and educational content creation.

Author: Tolulope Babajide
"""

# Comprehensive lesson resource prompt with JSON structure
COMPREHENSIVE_LESSON_RESOURCE_PROMPT = """
You are an educational AI assistant helping to generate comprehensive, locally contextual lesson resources for teachers.

Create a comprehensive locally contextual lesson resource content on {topic} under {subject} for {grade_level} students in {country} (for context: {local_context}).
The lesson resource should cover the following:

1. lesson objectives: {learning_objectives}

2. contents should include: {contents}


Ensure:
- The lesson is contextualized to the local environment mentioned.
- Explanations are age-appropriate and culturally relevant.
- Reference real or realistic local examples (e.g., local rivers, markets, crops, etc.).

---


Please create the comprehensive lesson resource in the following JSON structure:

{{
  "title_header": {{
    "topic": "...",
    "subject": "...",
    "grade_level": "...",
    "country": "...",
    "local_context": "..."
  }},
  "learning_objectives": [
    "...", 
    "...", 
    "..."
  ],
  "lesson_content": {{
    "introduction": "...",
    "main_concepts": ["...", "..."],
    "examples": ["...", "..."],
    "step_by_step_instructions": ["...", "..."]
  }},
  "assessment": [
    "...", "..."
  ],
  "key_takeaways": [
    "...", "..."
  ],
  "related_projects_or_activities": [
    "...", "..."
  ],
  "references": [
    "...", "..."
  ]
}}


Please ensure the content is:
- Age-appropriate for the grade level
- Culturally relevant to African educational contexts
- Practical and implementable with locally available resources
- Aligned with modern pedagogical best practices
- Engaging and interactive
- Clear and well-structured for teachers to implement

Focus on making the content accessible, practical, and relevant to the local context provided.
"""

