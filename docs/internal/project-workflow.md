# Awade Project Workflow

## Overview

This document outlines the complete user workflow for the Awade platform, from initial signup through lesson plan generation, editing, and offline classroom use.

## 🎯 Complete User Journey

### Flowchart View
```mermaid
flowchart LR
    Start([Start])
    Signup[Sign Up / Log In]
    Dashboard[Teacher Dashboard]
    SelectCurr[Select Subject, Grade & Topic]
    InputContext[Input Local Context]
    Generate[Generate Lesson Plan]
    Edit[Edit Lesson Plan]
    Export[Export (PDF/DOC)]
    End([Offline Use in Class])

    Start --> Signup
    Signup --> Dashboard
    Dashboard --> SelectCurr
    SelectCurr --> InputContext
    InputContext --> Generate
    Generate --> Edit
    Edit --> Export
    Export --> End
```

### State Diagram View
```mermaid
stateDiagram-v2
    [*] --> SignUp
    SignUp --> Dashboard
    Dashboard --> SelectCurriculum
    SelectCurriculum --> InputContext
    InputContext --> GenerateLesson
    GenerateLesson --> ReviewLesson
    ReviewLesson --> EditLesson
    EditLesson --> ExportLesson
    ExportLesson --> [*]

    state ReviewLesson {
        [*] --> AutoReview
        AutoReview --> ManualReview
        ManualReview --> [*]
    }
```

### 🧠 Description of Activities:
- **SignUp**: Teacher creates or logs into an account.
- **Dashboard**: Entry point to start creating lessons.
- **SelectCurriculum**: Choose subject, grade, and topic.
- **InputContext**: Enter culturally/local-relevant teaching context.
- **GenerateLesson**: AI creates initial draft of the lesson.
- **ReviewLesson**: User sees a preview before proceeding.
- **EditLesson**: Modify, personalize, and enhance the AI-generated lesson.
- **ExportLesson**: Download as offline PDF/DOC for classroom use.

### 🔄 State Transitions & Review Process

#### ReviewLesson State Details:
- **AutoReview**: System automatically validates lesson plan against curriculum standards and completeness
- **ManualReview**: Teacher manually reviews the generated content for accuracy and relevance
- **Transition Logic**: AutoReview → ManualReview → Continue to EditLesson

#### Key State Transitions:
- **SignUp → Dashboard**: Successful authentication grants access to main interface
- **Dashboard → SelectCurriculum**: Teacher initiates lesson creation process
- **SelectCurriculum → InputContext**: Curriculum selection enables context input
- **InputContext → GenerateLesson**: Context data triggers AI generation
- **GenerateLesson → ReviewLesson**: Generated content enters review pipeline
- **ReviewLesson → EditLesson**: Approved content moves to editing phase
- **EditLesson → ExportLesson**: Finalized lesson plan ready for export
- **ExportLesson → [*]**: Process completion, lesson plan ready for classroom use

## 📋 Workflow Steps

### 1. **Authentication & Onboarding**
- **Start**: Teacher discovers Awade platform
- **Sign Up / Log In**: 
  - New users create account with email/password
  - Existing users authenticate
  - Profile setup (name, school, region, language preferences)

### 2. **Dashboard Access**
- **Teacher Dashboard**: 
  - Overview of existing lesson plans
  - Quick access to lesson plan generation
  - Curriculum mapping tools
  - Training modules
  - Recent activity and favorites

### 3. **Curriculum Selection**
- **Select Subject**: Choose from available subjects (Mathematics, Science, English, etc.)
- **Select Grade Level**: Specify target grade level (Grade 1-12)
- **Select Topic**: Choose specific curriculum topic or standard to cover

### 4. **Local Context Input**
- **Input Local Context**: Provide relevant local information:
  - Available classroom resources
  - Cultural context and community examples
  - Language preferences (English, French, Swahili, Yoruba, Igbo, Hausa)
  - Regional considerations
  - Student background and needs

### 5. **AI-Powered Generation**
- **Generate Lesson Plan**: System creates comprehensive lesson plan with:
  - Learning Objectives (aligned with curriculum standards)
  - Local Context Integration
  - Core Content (main concepts and knowledge)
  - Activities (3-5 engaging, resource-appropriate activities)
  - Quiz (5-8 assessment questions with answer key)
  - Related Projects (2-3 community-linked projects)

### 6. **Review & Customization**
- **Edit Lesson Plan**: Teachers can:
  - Modify generated content
  - Adjust activities for their specific context
  - Add or remove sections
  - Customize language and examples
  - Verify curriculum alignment

### 7. **Export & Distribution**
- **Export (PDF/DOC)**: Download lesson plan in:
  - Professional PDF format
  - Editable DOC format
  - Includes curriculum standards alignment
  - Ready for printing and sharing

### 8. **Classroom Implementation**
- **Offline Use in Class**: Teachers can:
  - Use lesson plans without internet connection
  - Print materials for classroom use
  - Share with colleagues
  - Implement in actual teaching

## 🔄 Iterative Process

The workflow supports iterative improvement:
- Teachers can return to edit lesson plans
- Generate variations for different contexts
- Build upon previous lesson plans
- Share and collaborate with other teachers

## 🎯 Key Features at Each Stage

### Authentication Stage
- Secure user registration and login
- Profile management
- Language preference settings
- Regional customization

### Dashboard Stage
- Lesson plan library
- Quick generation tools
- Curriculum mapping interface
- Training module access
- Progress tracking

### Selection Stage
- Comprehensive subject coverage
- Grade-appropriate content
- Curriculum standards alignment
- Topic-specific resources

### Context Stage
- Local resource integration
- Cultural adaptation
- Community relevance
- Accessibility considerations

### Generation Stage
- AI-powered content creation
- Standards-aligned objectives
- Resource-appropriate activities
- Local context integration
- Assessment tools

### Editing Stage
- Full content customization
- Standards verification
- Resource adjustment
- Language modification
- Activity adaptation

### Export Stage
- Multiple format support
- Professional formatting
- Curriculum alignment documentation
- Print-ready materials

### Implementation Stage
- Offline accessibility
- Classroom-ready materials
- Sharing capabilities
- Feedback collection

## 📊 Success Metrics

### User Engagement
- Time from signup to first lesson plan generation
- Frequency of lesson plan creation
- User retention rates
- Feature adoption rates

### Content Quality
- Curriculum alignment accuracy
- Local context integration effectiveness
- Teacher satisfaction scores
- Student learning outcomes

### Platform Performance
- Generation speed and reliability
- Export quality and consistency
- Offline functionality
- Cross-platform compatibility

## 🔗 Integration Points

### AI Service Integration
- GPT-powered content generation
- Curriculum standards alignment
- Local context adaptation
- Language translation support

### Database Integration
- User profile management
- Lesson plan storage and retrieval
- Curriculum mapping data
- Usage analytics

### Export Service Integration
- PDF generation with WeasyPrint
- DOC format support
- Professional formatting
- Standards documentation

### Offline Support
- Local storage capabilities
- Synchronization when online
- Print-friendly formatting
- Resource optimization

---

**Last Updated:** 2025-01-27  
**Next Review:** 2025-02-27  
**Document Owner:** Product Team  
**Status:** Active 