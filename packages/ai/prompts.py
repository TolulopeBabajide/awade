"""
Prompt templates for Awade AI system.
These templates are designed to generate curriculum-aligned, culturally relevant content.
"""

LESSON_PLAN_PROMPT = """
You are an expert African educator with deep knowledge of local curricula and cultural contexts. 
Generate a comprehensive lesson plan that is:

1. Curriculum-aligned for the specified subject and grade level
2. Culturally relevant and inclusive
3. Practical for classroom implementation
4. Engaging and student-centered

Subject: {subject}
Grade Level: {grade}
Learning Objectives: {objectives}
Duration: {duration} minutes
Language: {language}

Please provide:
- Clear learning activities with time allocations
- Required materials and resources
- Assessment strategies
- Rationale for pedagogical choices
- Cultural considerations and adaptations

Format the response as a structured lesson plan that teachers can immediately use.
"""

TRAINING_MODULE_PROMPT = """
You are a professional development expert specializing in African education contexts.
Create a micro-training module that is:

1. Practical and immediately applicable
2. Respectful of local teaching contexts
3. Accessible for teachers with varying tech skills
4. Focused on measurable outcomes

Topic: {topic}
Duration: {duration} minutes
Target Audience: {audience}
Language: {language}

Please provide:
- Clear learning objectives
- Step-by-step instructions
- Practical examples and scenarios
- Reflection questions
- Additional resources

Keep the content concise, actionable, and culturally sensitive.
"""

CULTURAL_ADAPTATION_PROMPT = """
Adapt the following educational content to be culturally relevant for {region} context:

Content: {content}
Original Language: {original_language}
Target Language: {target_language}

Consider:
- Local cultural practices and values
- Available resources and infrastructure
- Language nuances and expressions
- Community-specific examples
- Respectful representation of local knowledge

Provide the adapted content while maintaining educational effectiveness.
"""

EXPLANATION_PROMPT = """
Explain the following AI-generated educational content in simple, teacher-friendly terms:

Content: {content}
Context: {context}

Please explain:
1. Why this approach was chosen
2. How it aligns with best practices
3. What adaptations teachers might consider
4. How to implement it effectively
5. Potential challenges and solutions

Use clear, non-technical language that builds teacher confidence and understanding.
""" 