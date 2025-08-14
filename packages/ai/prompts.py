"""
AI Prompts for Awade Lesson Planning

This module contains prompt templates for AI-powered lesson plan generation,
curriculum alignment, and educational content creation.

Author: Tolulope Babajide
"""

# Comprehensive lesson resource prompt with JSON structure
COMPREHENSIVE_LESSON_RESOURCE_PROMPT = """
Create a comprehensive, locally contextual lesson resource for {topic} in {subject} for {grade_level} students in {country}.

Learning objectives: {learning_objectives}
Content areas: {contents}
Local context: {local_context}

Generate a detailed JSON response with this structure:
{{
  "title_header": {{
    "topic": "{topic}",
    "subject": "{subject}",
    "grade_level": "{grade_level}",
    "country": "{country}",
    "local_context": "{local_context}"
  }},
  "learning_objectives": [
    "Specific, measurable objective 1",
    "Specific, measurable objective 2", 
    "Specific, measurable objective 3"
  ],
  "lesson_content": {{
    "introduction": "Engaging introduction that connects to students' daily lives and local environment",
    "main_concepts": [
      "Detailed explanation of concept 1 with local relevance",
      "Detailed explanation of concept 2 with practical applications",
      "Detailed explanation of concept 3 with real-world connections"
    ],
    "examples": [
      "Real-life example 1: Specific local scenario or application that students can relate to",
      "Real-life example 2: Practical demonstration using local resources or situations",
      "Real-life example 3: Community-based example that shows the concept in action"
    ],
    "step_by_step_instructions": [
      "Step 1: Clear, actionable instruction with local context",
      "Step 2: Progressive instruction building on previous step",
      "Step 3: Final instruction that reinforces learning"
    ]
  }},
  "assessment": [
    "Critical thinking assessment: Question or activity that requires analysis and reasoning",
    "Practical application assessment: Task that demonstrates real-world understanding",
    "Creative assessment: Project that encourages innovative thinking and local problem-solving"
  ],
  "key_takeaways": [
    "Real-life application 1: How this concept applies to daily life in the local context",
    "Real-life application 2: Practical skills gained and their community relevance",
    "Real-life application 3: Long-term benefits and future applications in local context"
  ],
  "related_projects_or_activities": [
    "Hands-on project 1: Specific activity using local materials/resources that demonstrates the concept",
    "Community project 2: Group activity that applies learning to local community needs",
    "Practical skill activity 3: Individual or small group task that builds practical competencies"
  ],
  "references": [
    "Local curriculum reference: {subject} {grade_level} curriculum",
    "Local resource: Available textbook or material",
    "Community resource: Local expert, facility, or organization that can support learning"
  ]
}}

IMPORTANT REQUIREMENTS:
1. MAIN CONCEPTS: Provide detailed, comprehensive explanations for each curriculum content area listed in {contents}. Each concept should be thoroughly explained with local relevance.

2. EXAMPLES: Include specific, real-life scenarios and applications that students can see, touch, or experience in their local environment. Use local landmarks, businesses, cultural practices, or daily activities.

3. ASSESSMENT: Create assessments that encourage critical thinking, problem-solving, and real-world application. Include questions that require analysis, evaluation, and creative thinking.

4. KEY TAKEAWAYS: Focus on practical, real-life applications and relevance. Explain how the concepts apply to students' daily lives, future careers, or community development.

5. PROJECTS/ACTIVITIES: Design hands-on, practical activities using local materials and resources. Include community-based projects that apply learning to real local needs.

6. LOCAL CONTEXT: All content must be tailored to {local_context} and {country}. Use local examples, cultural references, available resources, and community-specific applications.

Make the content engaging, practical, and immediately relevant to students' lives and local environment.
"""

