"""
SQLAlchemy models for Awade database schema.
Simplified and clean implementation based on the new schema.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    Enum, Table, MetaData, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class UserRole(enum.Enum):
    """Enumeration of user roles in the Awade platform."""
    EDUCATOR = "EDUCATOR"
    ADMIN = "ADMIN"

class LessonStatus(enum.Enum):
    """Enumeration of lesson plan statuses."""
    DRAFT = "draft"
    EDITED = "edited"
    REVIEWED = "reviewed"
    EXPORTED = "exported"  

class ResourceType(enum.Enum):
    """Enumeration of resource types for lesson exports."""
    PDF = "pdf"
    DOCX = "docx"

# Association tables for many-to-many relationships
lesson_tags = Table(
    'lesson_tags',
    Base.metadata,
    Column('lesson_plan_id', Integer, ForeignKey('lesson_plans.lesson_plan_id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'), primary_key=True)
)

class Country(Base):
    """Countries table for curriculum organization."""
    __tablename__ = 'countries'
    
    country_id = Column(Integer, primary_key=True, autoincrement=True)
    country_name = Column(String(100), unique=True, nullable=False)
    iso_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    
    # Relationships
    curricula = relationship("Curriculum", back_populates="country")

class Curriculum(Base):
    """Curricula table - main curriculum records."""
    __tablename__ = 'curricula'
    
    curricula_id = Column(Integer, primary_key=True, autoincrement=True)
    curricula_title = Column(String(255), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.country_id'), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    country = relationship("Country", back_populates="curricula")
    curriculum_structures = relationship("CurriculumStructure", back_populates="curriculum", cascade="all, delete-orphan")

class GradeLevel(Base):
    """
    Grade levels table for educational curriculum organization.
    
    This table stores the different grade levels supported by the platform,
    from primary to secondary education. Each grade level can be associated
    with multiple curriculum structures and subjects.
    
    Attributes:
        grade_level_id: Primary key for the grade level
        name: Human-readable grade level name (e.g., "Grade 5", "JSS 1")
        
    Relationships:
        curriculum_structures: One-to-many relationship with curriculum structures
    """
    __tablename__ = 'grade_levels'
    
    grade_level_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    
    # Relationships
    curriculum_structures = relationship("CurriculumStructure", back_populates="grade_level")

class Subject(Base):
    """
    Subjects table for educational curriculum organization.
    
    This table stores the different academic subjects supported by the platform,
    such as Mathematics, Science, English, etc. Each subject can be taught
    across multiple grade levels and curriculum structures.
    
    Attributes:
        subject_id: Primary key for the subject
        name: Human-readable subject name (e.g., "Mathematics", "Science")
        
    Relationships:
        curriculum_structures: One-to-many relationship with curriculum structures
    """
    __tablename__ = 'subjects'
    
    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    
    # Relationships
    curriculum_structures = relationship("CurriculumStructure", back_populates="subject")

class CurriculumStructure(Base):
    """Curriculum structures linking curricula, grade levels, and subjects."""
    __tablename__ = 'curriculum_structures'
    
    curriculum_structure_id = Column(Integer, primary_key=True, autoincrement=True)
    curricula_id = Column(Integer, ForeignKey('curricula.curricula_id', ondelete='CASCADE'), nullable=False)
    grade_level_id = Column(Integer, ForeignKey('grade_levels.grade_level_id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'), nullable=False)
    
    # Relationships
    curriculum = relationship("Curriculum", back_populates="curriculum_structures")
    grade_level = relationship("GradeLevel", back_populates="curriculum_structures")
    subject = relationship("Subject", back_populates="curriculum_structures")
    topics = relationship("Topic", back_populates="curriculum_structure", cascade="all, delete-orphan")
    
    # Unique constraint to prevent duplicate structures
    __table_args__ = (
        Index('idx_curriculum_structure_unique', 'curricula_id', 'grade_level_id', 'subject_id', unique=True),
    )

class Topic(Base):
    """Topics within curriculum structures."""
    __tablename__ = 'topics'
    
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_structure_id = Column(Integer, ForeignKey('curriculum_structures.curriculum_structure_id', ondelete='CASCADE'), nullable=False)
    topic_title = Column(Text, nullable=False)
    
    # Relationships
    curriculum_structure = relationship("CurriculumStructure", back_populates="topics")
    learning_objectives = relationship("LearningObjective", back_populates="topic", cascade="all, delete-orphan")
    topic_contents = relationship("TopicContent", back_populates="topic", cascade="all, delete-orphan")
    lesson_plans = relationship("LessonPlan", back_populates="topic", cascade="all, delete-orphan")

class LearningObjective(Base):
    """Learning objectives for each topic."""
    __tablename__ = 'learning_objectives'
    
    learning_objective_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    objective = Column(Text, nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="learning_objectives")

class TopicContent(Base):
    """Topic contents for each topic."""
    __tablename__ = 'topic_contents'
    
    topic_contents_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    content_area = Column(Text, nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="topic_contents")

class User(Base):
    """User accounts for the platform."""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EDUCATOR, nullable=False)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    school_name = Column(String(200), nullable=True)
    subjects = Column(Text, nullable=True)  # JSON string or comma-separated
    grade_levels = Column(Text, nullable=True)  # JSON string or comma-separated
    languages_spoken = Column(Text, nullable=True)  # JSON string or comma-separated
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    lesson_resources = relationship("LessonResource", back_populates="user")
    lesson_plans = relationship("LessonPlan", back_populates="user", cascade="all, delete-orphan")

class LessonPlan(Base):
    """Lesson plans created by educators."""
    __tablename__ = 'lesson_plans'
    
    lesson_plan_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="lesson_plans")
    user = relationship("User", back_populates="lesson_plans")
    lesson_resources = relationship("LessonResource", back_populates="lesson_plan", cascade="all, delete-orphan")
    contexts = relationship("Context", back_populates="lesson_plan", cascade="all, delete-orphan")

class Context(Base):
    """Context information for lesson plans to improve AI generation."""
    __tablename__ = 'contexts'
    
    context_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_plan_id = Column(Integer, ForeignKey('lesson_plans.lesson_plan_id', ondelete='CASCADE'), nullable=False)
    context_text = Column(Text, nullable=False)
    context_type = Column(String(50), nullable=True)  # e.g., 'cultural', 'resources', 'student_background'
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="contexts")

class LessonResource(Base):
    """Lesson resources with AI-generated content."""
    __tablename__ = 'lesson_resources'
    
    lesson_resources_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_plan_id = Column(Integer, ForeignKey('lesson_plans.lesson_plan_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    context_input = Column(Text, nullable=True)
    ai_generated_content = Column(Text, nullable=True)
    user_edited_content = Column(Text, nullable=True)
    export_format = Column(String(10), nullable=True)
    status = Column(String(20), default='draft', nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    lesson_plan = relationship("LessonPlan", back_populates="lesson_resources")
    user = relationship("User", back_populates="lesson_resources")

# Additional tables for enhanced functionality (keeping some useful ones)
class Tag(Base):
    """Tags for categorizing lesson plans."""
    __tablename__ = 'tags'
    
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    lesson_plans = relationship("LessonPlan", secondary=lesson_tags, back_populates="tags")

# Add tags relationship to LessonPlan
LessonPlan.tags = relationship("Tag", secondary=lesson_tags, back_populates="lesson_plans") 