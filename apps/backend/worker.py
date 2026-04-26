
import asyncio
import logging
from arq.connections import RedisSettings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import sys
from datetime import datetime, timezone
from pydantic import ValidationError

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])

from apps.backend.database import get_db_url
from apps.backend.models import LessonResource, Topic, CurriculumStructure, Subject, GradeLevel, Context, User
from apps.backend.services.auth_service import AuthService
from apps.backend.schemas.lesson_plans import LessonResourceAIContent
from packages.ai.gpt_service import AwadeGPTService

logger = logging.getLogger(__name__)

# Configure database session for worker
engine = create_engine(get_db_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def startup(ctx):
    """
    Worker startup hook.
    """
    logger.info("Worker starting up...")
    ctx['db_session_maker'] = SessionLocal

async def shutdown(ctx):
    """
    Worker shutdown hook.
    """
    logger.info("Worker shutting down...")

async def generate_lesson_resource_task(ctx, resource_id: int):
    """
    Task to generate lesson resource content using AI.
    """
    logger.info("Processing lesson resource generation for ID: %s", resource_id)
    
    db = ctx['db_session_maker']()
    try:
        # Fetch resource
        resource = db.query(LessonResource).filter(LessonResource.lesson_resources_id == resource_id).first()
        if not resource:
            logger.warning("Resource %s not found", resource_id)
            return

        # Fetch dependency data (Topic, Subject, Grade)
        # Assuming resource follows standard hierarchy via LessonPlan -> Topic -> Curriculum
        # Note: LessonResource is linked to LessonPlan
        lesson_plan = resource.lesson_plan
        topic = lesson_plan.topic
        
        if not topic:
             logger.warning("Topic not found for resource %s", resource_id)
             resource.status = "failed"
             db.commit()
             return

        curriculum_structure = db.query(CurriculumStructure).filter(
            CurriculumStructure.curriculum_structure_id == topic.curriculum_structure_id
        ).first()
        
        subject = db.query(Subject).filter(Subject.subject_id == curriculum_structure.subject_id).first()
        grade_level = db.query(GradeLevel).filter(GradeLevel.grade_level_id == curriculum_structure.grade_level_id).first()
        
        # Gather context
        objectives = [obj.objective for obj in topic.learning_objectives] if topic.learning_objectives else []
        contents = [content.content_area for content in topic.topic_contents] if topic.topic_contents else []
        
        contexts = db.query(Context).filter(Context.lesson_plan_id == lesson_plan.lesson_plan_id).all()
        context_texts = [ctx.context_text for ctx in contexts]
        
        combined_context = ""
        if context_texts:
            combined_context += "Stored Context:\n" + "\n".join(context_texts) + "\n\n"
        if resource.context_input:
            combined_context += "Additional Context:\n" + resource.context_input
            
        # Generate AI content
        ai_service = AwadeGPTService()
        
        # This call might be blocking if not async, but arq runs in threadpool executor if function is not async
        # AwadeGPTService uses OpenAI client which is synchronous by default unless using AsyncOpenAI
        # For simplicity in this sprint, we assume it's acceptable or wrap in loop
        
        # Fetch active template
        from apps.backend.models import LessonTemplate
        active_template = db.query(LessonTemplate).filter(LessonTemplate.is_active == 1).first()
        template_schema = active_template.schema_json if active_template else None

        # Using run_in_executor to not block the event loop if the service is sync
        loop = asyncio.get_event_loop()
        ai_content, is_safe = await loop.run_in_executor(
            None, 
            lambda: ai_service.generate_lesson_resource(
                subject=subject.name if subject else "Mathematics",
                grade=grade_level.name if grade_level else "JSS 1",
                topic=topic.topic_title,
                objectives=objectives,
                contents=contents,
                context=combined_context,
                template_schema=template_schema
            )
        )
        
        from apps.backend.models import ResourceModeration

        # Validate AI output shape against Pydantic schema before persisting (AWD-M-48).
        # Malformed output from the AI service can cause downstream 503s in the PDF
        # export service; flagging it here keeps bad data out of the DB entirely.
        try:
            LessonResourceAIContent.model_validate_json(ai_content)
        except (ValidationError, ValueError) as exc:
            logger.error(
                "Lesson resource schema validation failed for resource %s: %s",
                resource_id,
                exc,
            )
            resource.status = "failed"
            moderation = ResourceModeration(
                lesson_resource_id=resource_id,
                status='flagged',
                notes="AI output failed Pydantic schema validation — content not persisted.",
            )
            db.add(moderation)
            db.commit()
            return

        # Update resource
        resource.ai_generated_content = ai_content
        resource.status = "generated"

        # If not safe, create a moderation entry for content-safety issues
        if not is_safe:
            moderation = ResourceModeration(
                lesson_resource_id=resource_id,
                status='flagged',
                notes="Automatically flagged by AI safety filter due to potential structural or content issues."
            )
            db.add(moderation)

        db.commit()
        logger.info("Successfully generated content for resource %s", resource_id)
        
    except Exception as e:
        logger.error("Error generating resource %s", resource_id, exc_info=True)
        resource.status = "failed"
        db.commit()
    finally:
        db.close()

# Arq Worker Settings
class WorkerSettings:
    functions = [generate_lesson_resource_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379))
    )
