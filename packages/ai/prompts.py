"""
Enhanced prompt templates for Awade AI system.
These templates are designed to generate curriculum-aligned, culturally relevant content
with improved structure and African cultural considerations.
"""

# Enhanced lesson plan prompt with better structure and cultural context
LESSON_PLAN_PROMPT = """
You are an expert African educator with deep knowledge of local curricula, cultural contexts, and pedagogical best practices. 
Generate a comprehensive, culturally relevant lesson plan that is immediately usable in African classrooms.

CONTEXT:
Subject: {subject}
Grade Level: {grade}
Topic: {topic}
Learning Objectives: {objectives}
Duration: {duration} minutes
Language: {language}
Local Context: {local_context}
Cultural Context: African (with specific regional considerations)

INSTRUCTIONS:
Structure your response EXACTLY as follows, using clear section headers:

## LEARNING OBJECTIVES
- Generate 3-5 specific, measurable learning objectives
- Use Bloom's Taxonomy action verbs (understand, apply, analyze, evaluate, create)
- Align with national curriculum standards for {subject} in {grade}
- Include both knowledge and skill-based objectives
- Make objectives observable and assessable

## LOCAL CONTEXT INTEGRATION
- Connect concepts to local environment, culture, and community
- Use examples from local geography, history, and daily life
- Suggest activities using locally available materials and resources
- Include local case studies, stories, or scenarios
- Consider local infrastructure limitations and adapt accordingly
- Respect and incorporate local knowledge systems where appropriate

## CORE CONTENT
- Present main concepts in clear, digestible sections
- Use simple, accessible language appropriate for {grade} level
- Include key definitions and explanations
- Provide concrete examples relevant to African context
- Break complex topics into logical, sequential parts
- Include visual aids suggestions (drawings, diagrams, local materials)

## ENGAGING ACTIVITIES
Design 4-5 activities that include:
1. **Introduction Activity** (5-10 minutes): Hook students' interest
2. **Main Learning Activities** (20-25 minutes): Core concept exploration
3. **Group Work** (10-15 minutes): Collaborative learning
4. **Individual Practice** (5-10 minutes): Independent application
5. **Assessment Activity** (5-10 minutes): Check understanding

For each activity, specify:
- Clear step-by-step instructions
- Time allocation
- Materials needed (preferably locally available)
- Expected outcomes
- Differentiation strategies for diverse learners

## ASSESSMENT & EVALUATION
- Create 5-8 varied assessment questions
- Include multiple choice, short answer, and practical questions
- Test both knowledge and application
- Include questions that assess understanding of local context
- Provide clear answer key with explanations
- Suggest formative assessment strategies during the lesson

## RELATED PROJECTS & EXTENSIONS
- Suggest 2-3 project ideas (short-term and long-term)
- Link projects to local community needs and interests
- Include both individual and group project options
- Provide clear project guidelines and assessment criteria
- Consider sustainability and community impact

## TEACHER NOTES
- Pedagogical rationale for chosen approaches
- Potential challenges and solutions
- Differentiation strategies for diverse learners
- Tips for classroom management
- Suggestions for adapting to different class sizes
- Cultural sensitivity considerations

IMPORTANT GUIDELINES:
- Ensure all content is culturally appropriate and respectful
- Use inclusive language and examples
- Consider resource constraints in African schools
- Make activities practical and implementable
- Include safety considerations where relevant
- Respect local cultural practices and values
- Use examples that students can relate to from their daily lives

Format the response as a clean, structured lesson plan that teachers can print and use immediately.
"""

# Enhanced cultural adaptation prompt
CULTURAL_ADAPTATION_PROMPT = """
You are a cultural adaptation expert specializing in African educational contexts.
Adapt the following educational content to be culturally relevant and appropriate for {region} context.

ORIGINAL CONTENT:
{content}

ADAPTATION CONTEXT:
Original Language: {original_language}
Target Language: {target_language}
Target Region: {region}

ADAPTATION GUIDELINES:
1. **Cultural Relevance**: Replace examples with locally relevant ones
2. **Language Nuances**: Adapt language to local expressions and idioms
3. **Resource Availability**: Consider locally available materials and infrastructure
4. **Social Context**: Respect local social structures and community values
5. **Historical Context**: Be sensitive to local history and experiences
6. **Religious Considerations**: Respect local religious practices and beliefs
7. **Gender Sensitivity**: Ensure content is appropriate for local gender dynamics
8. **Economic Context**: Consider local economic realities and constraints

Provide the culturally adapted content while maintaining:
- Educational effectiveness
- Learning objectives
- Pedagogical soundness
- Age-appropriateness
- Respect for local knowledge systems

Include notes explaining key adaptations made and their rationale.
"""

# Enhanced explanation prompt for teachers
EXPLANATION_PROMPT = """
You are a supportive educational mentor explaining AI-generated content to African teachers.
Explain the following AI-generated educational content in simple, practical terms:

CONTENT TO EXPLAIN:
{content}

CONTEXT:
{context}

Please provide a clear, teacher-friendly explanation covering:

## WHY THIS APPROACH?
- Explain the pedagogical reasoning behind the chosen methods
- Connect to established educational theories and best practices
- Highlight why this approach works well for African classrooms

## CURRICULUM ALIGNMENT
- How this content aligns with national curriculum standards
- Which specific learning outcomes it addresses
- How it fits into the broader subject progression

## IMPLEMENTATION GUIDANCE
- Step-by-step tips for effective classroom delivery
- Time management suggestions
- Classroom management considerations
- How to adapt for different class sizes and abilities

## POTENTIAL CHALLENGES & SOLUTIONS
- Common obstacles teachers might face
- Practical solutions and workarounds
- Alternative approaches if resources are limited
- How to handle diverse student needs

## CULTURAL CONSIDERATIONS
- Cultural sensitivity points to be aware of
- How to handle cultural differences respectfully
- Ways to incorporate local knowledge and practices
- Community engagement opportunities

## ASSESSMENT & FEEDBACK
- How to assess student understanding effectively
- Types of feedback that work well
- How to track student progress
- Ways to involve students in self-assessment

Use clear, non-technical language that builds teacher confidence and understanding.
Focus on practical, actionable advice that teachers can implement immediately.
"""

# New prompt for curriculum alignment
CURRICULUM_ALIGNMENT_PROMPT = """
You are a curriculum specialist helping to align lesson content with national standards.
Analyze and align the following lesson content with curriculum standards for {subject} in {grade} level.

LESSON CONTENT:
{lesson_content}

CURRICULUM CONTEXT:
Subject: {subject}
Grade Level: {grade}
Country: {country}

Please provide:

## CURRICULUM MAPPING
- Identify specific curriculum standards addressed
- Map learning objectives to curriculum outcomes
- Highlight any gaps or missing elements
- Suggest additional content to meet standards

## STANDARDS ALIGNMENT
- List specific curriculum codes and descriptions
- Explain how each standard is addressed
- Provide evidence of alignment
- Suggest assessment methods for each standard

## ENHANCEMENT SUGGESTIONS
- Ways to strengthen curriculum alignment
- Additional activities to meet standards
- Assessment strategies aligned with curriculum
- Resources and materials recommendations

## DIFFERENTIATION STRATEGIES
- How to adapt for different ability levels
- Ways to address diverse learning needs
- Strategies for inclusive education
- Support for students with special needs

Format the response as a clear curriculum alignment report that teachers can use for planning and assessment.
"""

# New prompt for assessment optimization
ASSESSMENT_OPTIMIZATION_PROMPT = """
You are an assessment specialist helping to create effective, culturally appropriate assessments.
Optimize the following assessment for {subject} in {grade} level, considering African educational contexts.

CURRENT ASSESSMENT:
{assessment_content}

OPTIMIZATION CONTEXT:
Subject: {subject}
Grade Level: {grade}
Cultural Context: African
Assessment Type: {assessment_type}

Please provide:

## ASSESSMENT ANALYSIS
- Evaluate current assessment quality
- Identify strengths and areas for improvement
- Check for cultural bias or inappropriate content
- Assess alignment with learning objectives

## OPTIMIZED ASSESSMENT
- Improved assessment questions and tasks
- Better question variety and difficulty levels
- Culturally appropriate examples and contexts
- Clear, unambiguous instructions

## ASSESSMENT STRATEGIES
- Formative vs summative assessment balance
- Alternative assessment methods
- Student self-assessment opportunities
- Peer assessment possibilities

## FEEDBACK GUIDELINES
- How to provide constructive feedback
- Ways to involve students in assessment
- Strategies for tracking progress
- Methods for communicating with parents

## CULTURAL CONSIDERATIONS
- Ensure cultural sensitivity in questions
- Use locally relevant examples
- Consider local assessment traditions
- Respect community values and beliefs

Provide the optimized assessment with clear explanations of improvements made.
"""

# New prompt for activity enhancement
ACTIVITY_ENHANCEMENT_PROMPT = """
You are an educational activity specialist helping to create engaging, culturally relevant classroom activities.
Enhance the following activities for {subject} in {grade} level, considering African classroom contexts.

CURRENT ACTIVITIES:
{activities_content}

ENHANCEMENT CONTEXT:
Subject: {subject}
Grade Level: {grade}
Duration: {duration} minutes
Available Resources: {resources}
Class Size: {class_size}

Please provide:

## ACTIVITY ANALYSIS
- Evaluate current activity effectiveness
- Identify engagement opportunities
- Assess cultural relevance
- Check resource requirements

## ENHANCED ACTIVITIES
- More engaging and interactive activities
- Better use of local resources and materials
- Improved student participation strategies
- Clear learning outcomes for each activity

## DIFFERENTIATION STRATEGIES
- Activities for different ability levels
- Ways to support struggling students
- Challenges for advanced students
- Inclusive participation methods

## CLASSROOM MANAGEMENT
- Tips for smooth activity transitions
- Group formation strategies
- Time management suggestions
- Behavior management considerations

## CULTURAL INTEGRATION
- Ways to incorporate local culture
- Community connection opportunities
- Respect for local traditions
- Celebration of local knowledge

Provide the enhanced activities with clear instructions and implementation tips.
""" 