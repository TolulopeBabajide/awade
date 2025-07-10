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
Topic: {topic}
Learning Objectives: {objectives}
Duration: {duration} minutes
Language: {language}
Local Context: {local_context}

IMPORTANT: Structure your response in exactly these 6 sections:

1. LEARNING OBJECTIVES
   - Generate 3-5 clear, measurable learning objectives
   - Align with curriculum standards for the subject and grade
   - Use action verbs (understand, apply, analyze, etc.)

2. LOCAL CONTEXT
   - Integrate the provided local context information
   - Suggest activities using locally available resources
   - Teach concepts via real-life examples from the local environment
   - Use local case studies and scenarios
   - Suggest projects linked to local community needs

3. CORE CONTENT
   - Present the main concepts and knowledge
   - Break down complex topics into digestible parts
   - Include key definitions and explanations
   - Provide examples relevant to the local context

4. ACTIVITIES
   - Design 3-5 engaging activities
   - Include both individual and group work
   - Use locally available materials and resources
   - Provide clear step-by-step instructions
   - Include time allocations for each activity

5. QUIZ
   - Create 5-8 assessment questions
   - Mix different question types (multiple choice, short answer, practical)
   - Include questions that test understanding of local context
   - Provide answer key

6. RELATED PROJECTS (where applicable)
   - Suggest 2-3 project ideas
   - Link projects to local community needs
   - Include both short-term and long-term projects
   - Provide clear project guidelines and assessment criteria

Format the response as a structured lesson plan that teachers can immediately use.
Ensure all content is culturally appropriate and practically implementable.
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