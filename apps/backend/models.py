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
    PUBLISHED = "published"

class ResourceType(enum.Enum):
    PDF = "pdf"
    VIDEO = "video"
    TOOL = "tool"
    EXTERNAL = "external"

class QuestionType(enum.Enum):
    MCQ = "mcq"
    OPEN_ENDED = "open-ended"

# Association tables for many-to-many relationships
lesson_tags = Table(
    'lesson_tags',
    Base.metadata,
    Column('lesson_id', Integer, ForeignKey('lesson_plans.lesson_id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'), primary_key=True)
)

class User(Base):
    """User accounts for the platform."""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EDUCATOR)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    educator_profile = relationship("EducatorProfile", back_populates="user", uselist=False)
    lesson_plans = relationship("LessonPlan", back_populates="author")
    feedback = relationship("Feedback", back_populates="user")

class EducatorProfile(Base):
    """Detailed profile information for educators."""
    __tablename__ = 'educator_profiles'
    
    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True)
    school_name = Column(String(255), nullable=True)
    subjects = Column(JSON, nullable=True)  # List of subjects taught
    grade_levels = Column(JSON, nullable=True)  # List of grade levels
    languages_spoken = Column(Text, nullable=True)  # Comma-separated languages
    
    # Relationships
    user = relationship("User", back_populates="educator_profile")

class LessonPlan(Base):
    """Lesson plans created by educators."""
    __tablename__ = 'lesson_plans'
    
    lesson_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    author_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    context_description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
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

class LessonSection(Base):
    """Individual sections within a lesson plan."""
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
    __tablename__ = 'curriculum_map'
    
    curriculum_id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(100), nullable=False, index=True)
    grade_level = Column(String(50), nullable=False, index=True)
    curriculum_standard = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    country = Column(String(100), nullable=True)  # For country-specific curricula
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_curriculum_subject_grade', 'subject', 'grade_level'),
    )

class LessonContext(Base):
    """Teacher-provided local context for lesson plans."""
    __tablename__ = 'lesson_context'
    
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