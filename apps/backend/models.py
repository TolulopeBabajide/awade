"""
SQLAlchemy models for Awade database schema.
Based on the MVP requirements for African educator support platform.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, 
    Enum, JSON, Float, Table, MetaData, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class UserRole(enum.Enum):
    EDUCATOR = "educator"
    ADMIN = "admin"

class LessonStatus(enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    EDITED = "edited"
    REVIEWED = "reviewed"
    EXPORTED = "exported"
    USED_OFFLINE = "used_offline"
    ARCHIVED = "archived"

class ResourceType(enum.Enum):
    PDF = "pdf"
    VIDEO = "video"
    TOOL = "tool"
    EXTERNAL = "external"

class QuestionType(enum.Enum):
    MCQ = "mcq"
    OPEN_ENDED = "open-ended"

class CurriculumFrameworkType(enum.Enum):
    NATIONAL = "national"
    STATE = "state"
    INTERNATIONAL = "international"
    SCHOOL_DISTRICT = "school_district"

class StandardLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningOutcomeType(enum.Enum):
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    ATTITUDE = "attitude"
    COMPETENCY = "competency"

# Association tables for many-to-many relationships
lesson_tags = Table(
    'lesson_tags',
    Base.metadata,
    Column('lesson_id', Integer, ForeignKey('lesson_plans.lesson_id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'), primary_key=True)
)

class User(Base):
    """User accounts for the platform with consolidated profile information."""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EDUCATOR)
    country = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True)
    school_name = Column(String(255), nullable=True)
    subjects = Column(JSON, nullable=True)  # List of subjects taught
    grade_levels = Column(JSON, nullable=True)  # List of grade levels
    languages_spoken = Column(Text, nullable=True)  # Comma-separated languages
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    lesson_plans = relationship("LessonPlan", back_populates="author")
    feedback = relationship("Feedback", back_populates="user")

class LessonPlan(Base):
    """Lesson plans created by educators with 6-section structure."""
    __tablename__ = 'lesson_plans'
    
    lesson_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    topic = Column(String(255), nullable=True)
    author_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # 6-Section AI-generated content
    learning_objectives = Column(Text, nullable=True)
    local_context_section = Column(Text, nullable=True)
    core_content = Column(Text, nullable=True)
    activities = Column(Text, nullable=True)
    quiz = Column(Text, nullable=True)
    related_projects = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    status = Column(Enum(LessonStatus), default=LessonStatus.DRAFT, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="lesson_plans")
    sections = relationship("LessonSection", back_populates="lesson_plan", order_by="LessonSection.order_number")
    resource_links = relationship("ResourceLink", back_populates="lesson_plan")
    quizzes = relationship("Quiz", back_populates="lesson_plan")
    feedback = relationship("Feedback", back_populates="lesson_plan")
    tags = relationship("Tag", secondary=lesson_tags, back_populates="lesson_plans")
    contexts = relationship("LessonContext", back_populates="lesson_plan")
    curriculum_maps = relationship("CurriculumMap", back_populates="lesson_plan")
    standard_mappings = relationship("StandardMapping", back_populates="lesson_plan")

class LessonSection(Base):
    """Individual sections within a lesson plan (for additional content)."""
    __tablename__ = 'lesson_sections'
    
    section_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lesson_plans.lesson_id'), nullable=False)
    section_title = Column(String(255), nullable=False)
    content_text = Column(Text, nullable=False)
    media_link = Column(String(500), nullable=True)
    order_number = Column(Integer, nullable=False)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="sections")

class Tag(Base):
    """Tags for categorizing lesson plans."""
    __tablename__ = 'tags'
    
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    lesson_plans = relationship("LessonPlan", secondary=lesson_tags, back_populates="tags")

class ResourceLink(Base):
    """External resources linked to lesson plans."""
    __tablename__ = 'resource_links'
    
    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lesson_plans.lesson_id'), nullable=False)
    link_url = Column(String(500), nullable=False)
    type = Column(Enum(ResourceType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="resource_links")

class Quiz(Base):
    """Quizzes associated with lesson plans."""
    __tablename__ = 'quizzes'
    
    quiz_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lesson_plans.lesson_id'), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", order_by="Question.question_id")

class Question(Base):
    """Questions within quizzes."""
    __tablename__ = 'questions'
    
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.quiz_id'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

class Answer(Base):
    """Answer options for quiz questions."""
    __tablename__ = 'answers'
    
    answer_id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.question_id'), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="answers")

class Feedback(Base):
    """Feedback and ratings for lesson plans."""
    __tablename__ = 'feedback'
    
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lesson_plans.lesson_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Integer, nullable=False)  # Scale 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="feedback")
    user = relationship("User", back_populates="feedback")

class CurriculumMap(Base):
    """Curriculum standards mapping for different subjects and grades."""
    __tablename__ = 'curriculum_maps'
    
    curriculum_id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(100), nullable=False, index=True)
    grade_level = Column(String(50), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    standard_code = Column(String(255), nullable=False)
    standard_description = Column(Text, nullable=False)
    country = Column(String(100), nullable=True)  # For country-specific curricula
    lesson_plan_id = Column(Integer, ForeignKey('lesson_plans.lesson_id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="curriculum_maps")
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_curriculum_subject_grade', 'subject', 'grade_level'),
    )

class CurriculumFramework(Base):
    """Curriculum frameworks and standards bodies."""
    __tablename__ = 'curriculum_frameworks'
    
    framework_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    framework_type = Column(Enum(CurriculumFrameworkType), nullable=False)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    version = Column(String(50), nullable=True)
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    standards = relationship("CurriculumStandard", back_populates="framework")
    
    # Indexes
    __table_args__ = (
        Index('idx_framework_country_type', 'country', 'framework_type'),
        Index('idx_framework_active', 'is_active'),
    )

class CurriculumStandard(Base):
    """Individual curriculum standards within frameworks."""
    __tablename__ = 'curriculum_standards'
    
    standard_id = Column(Integer, primary_key=True, autoincrement=True)
    framework_id = Column(Integer, ForeignKey('curriculum_frameworks.framework_id'), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    grade_level = Column(String(50), nullable=False, index=True)
    standard_code = Column(String(255), nullable=False)
    standard_title = Column(String(500), nullable=False)
    standard_description = Column(Text, nullable=False)
    level = Column(Enum(StandardLevel), nullable=True)
    strand = Column(String(255), nullable=True)  # e.g., "Number and Operations"
    sub_strand = Column(String(255), nullable=True)  # e.g., "Fractions"
    content_area = Column(String(255), nullable=True)  # e.g., "Algebra", "Geometry"
    is_core = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    framework = relationship("CurriculumFramework", back_populates="standards")
    learning_outcomes = relationship("LearningOutcome", back_populates="standard")
    standard_mappings = relationship("StandardMapping", back_populates="standard")
    
    # Indexes
    __table_args__ = (
        Index('idx_standard_subject_grade', 'subject', 'grade_level'),
        Index('idx_standard_code', 'standard_code'),
        Index('idx_standard_strand', 'strand', 'sub_strand'),
    )

class LearningOutcome(Base):
    """Specific learning outcomes for curriculum standards."""
    __tablename__ = 'learning_outcomes'
    
    outcome_id = Column(Integer, primary_key=True, autoincrement=True)
    standard_id = Column(Integer, ForeignKey('curriculum_standards.standard_id'), nullable=False)
    outcome_type = Column(Enum(LearningOutcomeType), nullable=False)
    outcome_code = Column(String(255), nullable=True)
    outcome_title = Column(String(500), nullable=False)
    outcome_description = Column(Text, nullable=False)
    success_criteria = Column(Text, nullable=True)  # How to measure achievement
    assessment_methods = Column(JSON, nullable=True)  # Array of assessment types
    prerequisites = Column(Text, nullable=True)  # Prerequisite knowledge/skills
    order_sequence = Column(Integer, nullable=True)  # For ordering outcomes
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    standard = relationship("CurriculumStandard", back_populates="learning_outcomes")
    
    # Indexes
    __table_args__ = (
        Index('idx_outcome_type', 'outcome_type'),
        Index('idx_outcome_sequence', 'standard_id', 'order_sequence'),
    )

class StandardMapping(Base):
    """Mapping between curriculum standards and lesson plans."""
    __tablename__ = 'standard_mappings'
    
    mapping_id = Column(Integer, primary_key=True, autoincrement=True)
    standard_id = Column(Integer, ForeignKey('curriculum_standards.standard_id'), nullable=False)
    lesson_plan_id = Column(Integer, ForeignKey('lesson_plans.lesson_id'), nullable=False)
    mapping_type = Column(String(50), nullable=False, default='primary')  # primary, secondary, supplementary
    coverage_percentage = Column(Float, nullable=True)  # How much of the standard is covered (0-100)
    alignment_notes = Column(Text, nullable=True)  # Notes about how the lesson aligns
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    standard = relationship("CurriculumStandard", back_populates="standard_mappings")
    lesson_plan = relationship("LessonPlan", back_populates="standard_mappings")
    creator = relationship("User")
    
    # Unique constraint to prevent duplicate mappings
    __table_args__ = (
        Index('idx_mapping_lesson_standard', 'lesson_plan_id', 'standard_id'),
        Index('idx_mapping_type', 'mapping_type'),
    )

class CurriculumTopic(Base):
    """Topics within curriculum standards for better organization."""
    __tablename__ = 'curriculum_topics'
    
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(100), nullable=False, index=True)
    grade_level = Column(String(50), nullable=False, index=True)
    topic_name = Column(String(255), nullable=False)
    topic_description = Column(Text, nullable=True)
    parent_topic_id = Column(Integer, ForeignKey('curriculum_topics.topic_id'), nullable=True)
    difficulty_level = Column(Enum(StandardLevel), nullable=True)
    estimated_hours = Column(Float, nullable=True)  # Estimated teaching hours
    is_core = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Self-referential relationship for topic hierarchy
    parent_topic = relationship("CurriculumTopic", remote_side=[topic_id])
    child_topics = relationship("CurriculumTopic")
    
    # Indexes
    __table_args__ = (
        Index('idx_topic_subject_grade', 'subject', 'grade_level'),
        Index('idx_topic_parent', 'parent_topic_id'),
    )

class LessonContext(Base):
    """Teacher-provided local context for lesson plans."""
    __tablename__ = 'lesson_contexts'
    
    context_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lesson_plans.lesson_id'), nullable=False)
    context_key = Column(String(100), nullable=False)  # e.g., 'local_resources', 'student_background'
    context_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="contexts")
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_context_lesson_key', 'lesson_id', 'context_key'),
    )

# New Curriculum Models
class Curriculum(Base):
    """Main curriculum records for different countries, grades, and subjects."""
    __tablename__ = 'curricula'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), nullable=False, index=True)
    grade_level = Column(String(10), nullable=False, index=True)
    subject = Column(String(100), nullable=False, index=True)
    theme = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    topics = relationship("Topic", back_populates="curriculum", cascade="all, delete-orphan")
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_curriculum_country_grade_subject', 'country', 'grade_level', 'subject'),
    )

class Topic(Base):
    """Topics within a curriculum."""
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_id = Column(Integer, ForeignKey('curricula.id', ondelete='CASCADE'), nullable=False)
    topic_code = Column(String(50), unique=True, nullable=False, index=True)
    topic_title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    curriculum = relationship("Curriculum", back_populates="topics")
    learning_objectives = relationship("LearningObjective", back_populates="topic", cascade="all, delete-orphan")
    contents = relationship("Content", back_populates="topic", cascade="all, delete-orphan")
    teacher_activities = relationship("TeacherActivity", back_populates="topic", cascade="all, delete-orphan")
    student_activities = relationship("StudentActivity", back_populates="topic", cascade="all, delete-orphan")
    teaching_materials = relationship("TeachingMaterial", back_populates="topic", cascade="all, delete-orphan")
    evaluation_guides = relationship("EvaluationGuide", back_populates="topic", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_topic_curriculum', 'curriculum_id'),
        Index('idx_topic_code', 'topic_code'),
    )

class LearningObjective(Base):
    """Learning objectives for each topic."""
    __tablename__ = 'learning_objectives'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    objective = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="learning_objectives")

class Content(Base):
    """Content areas for each topic."""
    __tablename__ = 'contents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    content_area = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="contents")

class TeacherActivity(Base):
    """Teacher activities for each topic."""
    __tablename__ = 'teacher_activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    activity = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="teacher_activities")

class StudentActivity(Base):
    """Student activities for each topic."""
    __tablename__ = 'student_activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    activity = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="student_activities")

class TeachingMaterial(Base):
    """Teaching materials for each topic."""
    __tablename__ = 'teaching_materials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    material = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="teaching_materials")

class EvaluationGuide(Base):
    """Evaluation guides for each topic."""
    __tablename__ = 'evaluation_guides'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    guide = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="evaluation_guides") 