
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone
from apps.backend.worker import generate_lesson_resource_task
from apps.backend.models import LessonResource, User, LessonPlan, Topic, CurriculumStructure, Subject, GradeLevel, Context, Curriculum
from apps.backend.services.lesson_plan_service import LessonPlanService

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
    
    # Setup mock returns
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_resource, # First query: resource
        MagicMock(name="CurriculumStructure"), # Second query: structure
        MagicMock(name="Subject"), # Third query: subject
        MagicMock(name="GradeLevel") # Fourth query: grade
    ]
    mock_db_session.query.return_value.filter.return_value.all.return_value = [] # Contexts
    
    # Mock AI Service
    with patch("apps.backend.worker.AwadeGPTService") as MockAI:
        mock_ai_instance = MockAI.return_value
        mock_ai_instance.generate_lesson_resource.return_value = "Generated Content"
        
        ctx = {'db_session_maker': lambda: mock_db_session}
        
        await generate_lesson_resource_task(ctx, resource_id)
        
        # Assertions
        mock_ai_instance.generate_lesson_resource.assert_called_once()
        assert mock_resource.ai_generated_content == "Generated Content"
        assert mock_resource.status == "generated"
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
