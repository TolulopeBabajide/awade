# Awade AI Service - GPT-5 Integration

This package provides AI-powered services for lesson plan generation and educational content creation using OpenAI's GPT-5 model.

## Features

### GPT-5 Model Support
- **Model**: `gpt-5` (default), `gpt-5-mini`, `gpt-5-nano`
- **Reasoning Effort**: Control the quality and speed of responses
- **Verbosity**: Control the length and detail of responses
- **Responses API**: Enhanced performance with chain-of-thought support

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
OPENAI_MODEL=gpt-5
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# GPT-5 Specific Configuration
OPENAI_REASONING_EFFORT=medium  # minimal, low, medium, high
OPENAI_VERBOSITY=medium          # low, medium, high
```

### Reasoning Effort Levels

| Level | Description | Best For |
|-------|-------------|----------|
| `minimal` | Fastest response, fewest reasoning tokens | Simple tasks, code generation |
| `low` | Balanced speed and quality | General use, instruction following |
| `medium` | Default setting, good reasoning | Most educational tasks |
| `high` | Highest quality, thorough reasoning | Complex analysis, detailed explanations |

### Verbosity Levels

| Level | Description | Best For |
|-------|-------------|----------|
| `low` | Concise responses | Code generation, simple answers |
| `medium` | Balanced detail | General explanations, lesson plans |
| `high` | Detailed responses | Comprehensive documentation, analysis |

## Usage

### Basic Usage

```python
from packages.ai.gpt_service import AwadeGPTService

# Initialize service
service = AwadeGPTService()

# Generate lesson resource
result = service.generate_comprehensive_lesson_resource(
    subject="Mathematics",
    grade="Grade 5",
    topic="Fractions",
    learning_objectives=["Understand parts of whole", "Compare fractions"],
    contents=["Fraction concepts", "Visual representation"]
)
```

### GPT-5 Specific Usage

```python
# Use the new Responses API for better performance
result = service.generate_lesson_resource_gpt5_responses_api(
    subject="Science",
    grade="Grade 6",
    topic="Ecosystems",
    learning_objectives=["Understand food chains", "Learn about habitats"],
    contents=["Food webs", "Environmental factors"],
    previous_response_id="prev_response_id"  # For chain-of-thought continuity
)

# Check GPT-5 capabilities
capabilities = service.get_gpt5_capabilities()
print(f"Supports Responses API: {capabilities['supports_responses_api']}")
```

### Configuration Examples

```python
# High-quality, detailed responses
service.reasoning_effort = "high"
service.verbosity = "high"

# Fast, concise responses
service.reasoning_effort = "minimal"
service.verbosity = "low"

# Balanced approach (default)
service.reasoning_effort = "medium"
service.verbosity = "medium"
```

## API Methods

### Core Methods

- `generate_comprehensive_lesson_resource()` - Standard lesson resource generation
- `generate_lesson_resource_gpt5_responses_api()` - GPT-5 optimized method
- `_make_api_call()` - Low-level API call method

### Utility Methods

- `test_openai_connection()` - Test API connectivity
- `get_gpt5_capabilities()` - Get GPT-5 feature information
- `check_health()` - Check service health status

## Migration from Previous Models

### From GPT-4
- GPT-5 provides better reasoning and instruction following
- Use `reasoning_effort="medium"` for similar quality
- Use `verbosity="medium"` for similar response length

### From o3 Models
- GPT-5 with `reasoning_effort="high"` provides superior reasoning
- Better performance on complex educational tasks
- Improved chain-of-thought capabilities

## Best Practices

### For Educational Content
- Use `reasoning_effort="medium"` or `"high"` for lesson planning
- Use `verbosity="medium"` for comprehensive lesson resources
- Leverage chain-of-thought with `previous_response_id`

### For Code Generation
- Use `reasoning_effort="minimal"` for simple code tasks
- Use `verbosity="low"` for concise code output
- Combine with clear, specific prompts

### For Performance
- Use `reasoning_effort="minimal"` for fastest responses
- Use the Responses API method for multi-turn conversations
- Cache response IDs for chain-of-thought continuity

## Testing

Run the test script to verify GPT-5 features:

```bash
python packages/ai/test_gpt5_features.py
```

This will test:
- Configuration loading
- GPT-5 capabilities detection
- Different reasoning and verbosity settings
- Responses API method functionality

## Error Handling

The service includes comprehensive error handling:
- Automatic fallback to mock responses
- Graceful degradation when API is unavailable
- Detailed logging for debugging
- Schema validation for responses

## Dependencies

- `openai` - OpenAI Python client
- `jsonschema` - JSON schema validation (optional)
- Standard Python libraries

## Support

For issues or questions:
1. Check the logs for detailed error information
2. Verify environment variable configuration
3. Test API connectivity with `test_openai_connection()`
4. Review GPT-5 capabilities with `get_gpt5_capabilities()`
