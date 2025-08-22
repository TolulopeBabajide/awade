# Awade AI Service - GPT Integration

This package provides AI-powered services for lesson plan generation and educational content creation using OpenAI's GPT models.

## Features

### GPT Model Support
- **Model**: `gpt-4` (default), `gpt-3.5-turbo`, or any other OpenAI model
- **Fallback System**: Mock responses when API is unavailable
- **Local Context Integration**: Tailored for African education

### Key Capabilities
- Comprehensive lesson resource generation
- Curriculum-aligned content creation
- Local context integration for African education
- Fallback to mock responses when API is unavailable

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Model Configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7
```

## Usage

### Basic Usage

```python
from packages.ai.gpt_service import AwadeGPTService

# Initialize service
service = AwadeGPTService()

# Generate lesson resource
result = service.generate_lesson_resource(
    subject="Mathematics",
    grade="Grade 4",
    topic="Fractions",
    objectives=["Understand basic fractions", "Apply fractions to real-world problems"],
    contents=["Introduction to fractions", "Fraction operations", "Practical applications"],
    context="Nigerian classroom with basic resources"
)

# Check service health
is_healthy = service.check_health()
```

### Available Methods

- `generate_lesson_resource()` - Generate comprehensive lesson resources
- `check_health()` - Check service health status

## API Endpoints

The service is integrated with the following backend endpoints:

- **`POST /api/lesson-plans/{lesson_id}/resources/generate`** - Generate lesson resources
- **`GET /api/lesson-plans/ai/health`** - Check AI service health

## Mock Responses

When the OpenAI API is unavailable, the service automatically falls back to generating mock responses that include:

- Structured lesson content with local context
- Learning objectives and assessment criteria
- Practical examples and activities
- Cultural relevance to African communities

## Error Handling

The service gracefully handles:
- API authentication failures
- Rate limiting
- Network errors
- Invalid responses

All errors result in fallback to mock responses, ensuring the application remains functional.
