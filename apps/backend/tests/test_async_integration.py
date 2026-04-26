
import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock, call
from datetime import datetime, timezone
from apps.backend.worker import generate_lesson_resource_task
from apps.backend.models import LessonResource, User, LessonPlan, Topic, CurriculumStructure, Subject, GradeLevel, Context, Curriculum
from apps.backend.services.lesson_plan_service import LessonPlanService

# ---------------------------------------------------------------------------
# Minimal valid AI-output JSON that satisfies LessonResourceAIContent schema
# ---------------------------------------------------------------------------
VALID_AI_CONTENT = json.dumps({
    "title_header": {
        "topic": "Fractions",
        "subject": "Mathematics",
        "grade_level": "JSS 1",
        "country": "Nigeria",
        "local_context": "Standard classroom"
    },
    "learning_objectives": [
        "Understand basic fraction concepts",
        "Apply fractions to real-world problems"
    ],
    "lesson_content": {
        "introduction": "Today we explore fractions.",
        "main_concepts": ["Numerator and denominator", "Equivalent fractions"],
        "examples": ["1/2 of an orange", "2/4 = 1/2"],
        "step_by_step_instructions": ["Step 1: Define fraction", "Step 2: Practise"]
    },
    "assessment": ["Solve 3/4 + 1/4"],
    "key_takeaways": ["Fractions represent parts of a whole"],
    "related_projects_or_activities": ["Fraction pizza activity"],
    "references": ["Nigerian Mathematics Curriculum JSS 1"]
})

# Fixture to mock DB session for worker
@pytest.fixture
def mock_db_session():
    session = MagicMock()
    return session

@pytest.mark.asyncio
async def test_worker_task_execution(mock_db_session):
    """
    Test that the worker task correctly fetches data, calls AI service, and updates status.
    """
    resource_id = 1
    
    # Mock Database Objects
    mock_resource = MagicMock(spec=LessonResource)
    mock_resource.lesson_resources_id = resource_id
    mock_resource.context_input = "Extra context"
    mock_resource.lesson_plan = MagicMock()
    mock_resource.lesson_plan.topic = MagicMock()
    mock_resource.lesson_plan.topic.learning_objectives = []
    mock_resource.lesson_plan.topic.topic_contents = []
    
    # Setup mock returns.
    # The worker makes 5 .first() calls in order:
    #   1. LessonResource  2. CurriculumStructure  3. Subject  4. GradeLevel  5. LessonTemplate
    # All five must be present; a short list raises StopIteration, which is caught by the
    # worker's except-block, preventing the AI call from ever being reached.
    mock_lesson_template = MagicMock(name="LessonTemplate")
    mock_lesson_template.schema_json = None
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_resource,                           # 1st query: LessonResource
        MagicMock(name="CurriculumStructure"),   # 2nd query: CurriculumStructure
        MagicMock(name="Subject"),               # 3rd query: Subject
        MagicMock(name="GradeLevel"),            # 4th query: GradeLevel
        mock_lesson_template,                    # 5th query: LessonTemplate
    ]
    mock_db_session.query.return_value.filter.return_value.all.return_value = [] # Contexts

    # Mock AI Service.
    # generate_lesson_resource returns tuple[str, bool]; the worker unpacks it as
    # `ai_content, is_safe = ...` so return_value must be a 2-tuple, not a bare string.
    # The returned JSON must satisfy LessonResourceAIContent schema (AWD-M-48).
    with patch("apps.backend.worker.AwadeGPTService") as MockAI:
        mock_ai_instance = MockAI.return_value
        mock_ai_instance.generate_lesson_resource.return_value = (VALID_AI_CONTENT, True)

        ctx = {'db_session_maker': lambda: mock_db_session}

        await generate_lesson_resource_task(ctx, resource_id)

        # Assertions
        mock_ai_instance.generate_lesson_resource.assert_called_once()
        assert mock_resource.ai_generated_content == VALID_AI_CONTENT
        assert mock_resource.status == "generated"
        mock_db_session.commit.assert_called()


@pytest.mark.asyncio
async def test_worker_schema_validation_failure_flags_resource(mock_db_session):
    """
    AWD-M-48: When AI returns malformed JSON that fails LessonResourceAIContent
    validation, the worker must set status='failed', create a ResourceModeration
    flagged entry, and NOT persist the malformed content.
    """
    resource_id = 42

    mock_resource = MagicMock(spec=LessonResource)
    mock_resource.lesson_resources_id = resource_id
    mock_resource.context_input = None
    mock_resource.lesson_plan = MagicMock()
    mock_resource.lesson_plan.topic = MagicMock()
    mock_resource.lesson_plan.topic.learning_objectives = []
    mock_resource.lesson_plan.topic.topic_contents = []

    mock_lesson_template = MagicMock(name="LessonTemplate")
    mock_lesson_template.schema_json = None
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_resource,
        MagicMock(name="CurriculumStructure"),
        MagicMock(name="Subject"),
        MagicMock(name="GradeLevel"),
        mock_lesson_template,
    ]
    mock_db_session.query.return_value.filter.return_value.all.return_value = []

    # AI returns JSON that is missing required 'lesson_content' field — invalid per schema
    malformed_content = json.dumps({"title_header": {"topic": "X", "subject": "Y", "grade_level": "Z"}, "learning_objectives": []})

    with patch("apps.backend.worker.AwadeGPTService") as MockAI:
        mock_ai_instance = MockAI.return_value
        mock_ai_instance.generate_lesson_resource.return_value = (malformed_content, True)

        ctx = {'db_session_maker': lambda: mock_db_session}

        await generate_lesson_resource_task(ctx, resource_id)

        # Content must NOT have been written to the resource
        assert not hasattr(mock_resource, 'ai_generated_content') or \
               mock_resource.ai_generated_content != malformed_content
        # Status must be 'failed'
        assert mock_resource.status == "failed"
        # A ResourceModeration entry must have been added
        mock_db_session.add.assert_called_once()
        moderation_arg = mock_db_session.add.call_args[0][0]
        assert moderation_arg.status == "flagged"
        assert "schema validation" in moderation_arg.notes.lower()
        # DB must have been committed
        mock_db_session.commit.assert_called()


@pytest.mark.asyncio
async def test_worker_unsafe_content_still_persisted_with_moderation(mock_db_session):
    """
    AWD-M-48: When AI returns structurally valid JSON but is_safe=False, the worker
    should persist the content (same pre-existing behaviour) AND create a moderation entry.
    The schema validation path must not interfere with the safety-flag flow.
    """
    resource_id = 7

    mock_resource = MagicMock(spec=LessonResource)
    mock_resource.lesson_resources_id = resource_id
    mock_resource.context_input = None
    mock_resource.lesson_plan = MagicMock()
    mock_resource.lesson_plan.topic = MagicMock()
    mock_resource.lesson_plan.topic.learning_objectives = []
    mock_resource.lesson_plan.topic.topic_contents = []

    mock_lesson_template = MagicMock(name="LessonTemplate")
    mock_lesson_template.schema_json = None
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_resource,
        MagicMock(name="CurriculumStructure"),
        MagicMock(name="Subject"),
        MagicMock(name="GradeLevel"),
        mock_lesson_template,
    ]
    mock_db_session.query.return_value.filter.return_value.all.return_value = []

    with patch("apps.backend.worker.AwadeGPTService") as MockAI:
        mock_ai_instance = MockAI.return_value
        # Valid schema but is_safe=False (content-safety concern)
        mock_ai_instance.generate_lesson_resource.return_value = (VALID_AI_CONTENT, False)

        ctx = {'db_session_maker': lambda: mock_db_session}

        await generate_lesson_resource_task(ctx, resource_id)

        # Content should still be persisted (the safety flag only adds a moderation entry)
        assert mock_resource.ai_generated_content == VALID_AI_CONTENT
        assert mock_resource.status == "generated"
        # A ResourceModeration entry should have been added for the safety flag
        mock_db_session.add.assert_called_once()
        moderation_arg = mock_db_session.add.call_args[0][0]
        assert moderation_arg.status == "flagged"
        mock_db_session.commit.assert_called()

@pytest.mark.asyncio
async def test_service_enqueues_job():
    """
    Test that the service enqueues a job when Redis is available.
    """
    mock_db = MagicMock()
    mock_redis = AsyncMock()
    
    service = LessonPlanService(mock_db, mock_redis)
    
    # Mock refresh side effect to simulate ID generation
    def refresh_side_effect(obj):
        obj.lesson_resources_id = 123
        obj.created_at = datetime.now(timezone.utc)
    
    mock_db.refresh.side_effect = refresh_side_effect
    
    # Mock Data
    request_data = MagicMock()
    request_data.context_input = "test"
    request_data.export_format = "pdf"
    
    current_user = MagicMock()
    current_user.user_id = 1
    
    # Mock DB queries
    mock_lesson = MagicMock()
    mock_lesson.user_id = 1
    
    mock_topic = MagicMock()
    mock_topic.learning_objectives = []
    mock_topic.topic_contents = []
    mock_topic.curriculum_structure_id = 1
    
    mock_structure = MagicMock()
    mock_structure.subject_id = 1
    mock_structure.grade_level_id = 1
    
    mock_subject = MagicMock()
    mock_subject.name = "Math"
    
    mock_grade = MagicMock()
    mock_grade.name = "Grade 1"
    
    # Configure side_effect for multiple queries
    # 1. LessonPlan
    # 2. Topic
    # 3. CurriculumStructure
    # 4. Subject
    # 5. GradeLevel
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_lesson,
        mock_topic,
        mock_structure,
        mock_subject,
        mock_grade
    ]
    
    mock_db.query.return_value.filter.return_value.all.return_value = [] # Contexts
    
    # Call method
    result = await service.generate_lesson_resource(lesson_id=1, data=request_data, current_user=current_user)
    
    # Verify Enqueue
    mock_redis.enqueue_job.assert_called_once_with('generate_lesson_resource_task', resource_id=result.lesson_resources_id)
    assert result.status == 'processing'
