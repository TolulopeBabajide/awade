"""
SQLAlchemy models for Awade database schema.
Simplified and clean implementation based on the new schema.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Enum, Table, MetaData, Index, Boolean
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class UserRole(enum.Enum):
    """Enumeration of user roles in the Awade platform."""
    EDUCATOR = "EDUCATOR"
    PARENT = "PARENT"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

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
    curriculum_title = Column(String(255), nullable=False)
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
    themes = relationship("Theme", back_populates="curriculum_structure", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="curriculum_structure", cascade="all, delete-orphan")

    # Unique constraint to prevent duplicate structures
    __table_args__ = (
        Index('idx_curriculum_structure_unique', 'curricula_id', 'grade_level_id', 'subject_id', unique=True),
    )

class Theme(Base):
    """Themes group topics within a curriculum structure (NERDC e-curriculum).

    Each theme belongs to exactly one curriculum structure and carries the
    source theme number plus its human-readable title. Topics optionally link
    to a theme via ``Topic.theme_id`` (nullable so legacy topics imported
    before themes existed remain valid).
    """
    __tablename__ = 'themes'

    theme_id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_structure_id = Column(Integer, ForeignKey('curriculum_structures.curriculum_structure_id', ondelete='CASCADE'), nullable=False)
    theme_number = Column(Integer, nullable=True)
    theme_title = Column(Text, nullable=False)

    # Relationships
    curriculum_structure = relationship("CurriculumStructure", back_populates="themes")
    topics = relationship("Topic", back_populates="theme")

    __table_args__ = (
        Index('idx_theme_structure_number', 'curriculum_structure_id', 'theme_number', unique=True),
    )

class Topic(Base):
    """Topics within curriculum structures."""
    __tablename__ = 'topics'
    
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_structure_id = Column(Integer, ForeignKey('curriculum_structures.curriculum_structure_id', ondelete='CASCADE'), nullable=False)
    theme_id = Column(Integer, ForeignKey('themes.theme_id', ondelete='SET NULL'), nullable=True)
    topic_title = Column(Text, nullable=False)

    # Relationships
    curriculum_structure = relationship("CurriculumStructure", back_populates="topics")
    theme = relationship("Theme", back_populates="topics")
    learning_objectives = relationship("LearningObjective", back_populates="topic", cascade="all, delete-orphan")
    topic_contents = relationship("TopicContent", back_populates="topic", cascade="all, delete-orphan")
    teacher_activities = relationship("TeacherActivity", back_populates="topic", cascade="all, delete-orphan")
    student_activities = relationship("StudentActivity", back_populates="topic", cascade="all, delete-orphan")
    teaching_learning_materials = relationship("TeachingLearningMaterial", back_populates="topic", cascade="all, delete-orphan")
    evaluation_guides = relationship("EvaluationGuide", back_populates="topic", cascade="all, delete-orphan")
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

class TeacherActivity(Base):
    """Teacher activities for each topic (NERDC ``teachers_activities``)."""
    __tablename__ = 'teacher_activities'

    teacher_activity_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    activity = Column(Text, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="teacher_activities")

class StudentActivity(Base):
    """Student activities for each topic (NERDC ``students_activities``)."""
    __tablename__ = 'student_activities'

    student_activity_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    activity = Column(Text, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="student_activities")

class TeachingLearningMaterial(Base):
    """Teaching/learning materials for each topic (NERDC ``teaching_learning_materials``)."""
    __tablename__ = 'teaching_learning_materials'

    material_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    material = Column(Text, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="teaching_learning_materials")

class EvaluationGuide(Base):
    """Evaluation-guide items for each topic (NERDC ``evaluation_guide``)."""
    __tablename__ = 'evaluation_guides'

    evaluation_guide_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    guide_item = Column(Text, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="evaluation_guides")

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
    profile_image_url = Column(String(500), nullable=True)  # URL to profile image (for backward compatibility)
    profile_image_data = Column(Text, nullable=True)  # Base64 encoded image data
    profile_image_type = Column(String(50), nullable=True)  # MIME type of the image
    phone = Column(String(20), nullable=True)  # Phone number
    bio = Column(Text, nullable=True)  # User bio/description
    last_login = Column(DateTime, nullable=True)
    is_suspended = Column(Integer, default=0, nullable=False) # 0 = active, 1 = suspended
    password_reset_token = Column(String(64), nullable=True)  # SHA-256 hex digest of raw reset token
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)  # UTC expiry for the reset token (1hr window)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    lesson_resources = relationship("LessonResource", back_populates="user")
    lesson_plans = relationship("LessonPlan", back_populates="user", cascade="all, delete-orphan")
    children = relationship("ChildProfile", back_populates="parent", cascade="all, delete-orphan")

class ChildProfile(Base):
    """Child profiles managed by parent users."""
    __tablename__ = 'child_profiles'

    child_id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    school_name = Column(String(200), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.country_id'), nullable=True)
    curricula_id = Column(Integer, ForeignKey('curricula.curricula_id'), nullable=True)
    grade_level_id = Column(Integer, ForeignKey('grade_levels.grade_level_id'), nullable=True)
    subjects = Column(Text, nullable=True)  # JSON array of subject IDs the child needs help with
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    parent = relationship("User", back_populates="children")
    country = relationship("Country")
    curriculum = relationship("Curriculum")
    grade_level = relationship("GradeLevel")
    parent_guides = relationship("ParentGuide", back_populates="child", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_child_parent', 'parent_id'),
    )


class ParentGuide(Base):
    """AI-generated 'How to Help' guides for parent users."""
    __tablename__ = 'parent_guides'

    guide_id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(Integer, ForeignKey('child_profiles.child_id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    ai_generated_content = Column(Text, nullable=True)
    user_edited_content = Column(Text, nullable=True)
    is_bookmarked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    child = relationship("ChildProfile", back_populates="parent_guides")
    topic = relationship("Topic")

    __table_args__ = (
        Index('idx_guide_child_topic', 'child_id', 'topic_id'),
    )


class ParentalConsent(Base):
    """COPPA-required parental consent record for child profile creation.

    One row per parent. Records the datetime and consent-text version at the
    moment the parent explicitly agreed to the data collection disclosure.
    The unique constraint on parent_id ensures idempotency — re-POSTing to
    /api/consent is safe and updates the timestamp.
    """
    __tablename__ = 'parental_consents'

    consent_id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )
    consented_at = Column(DateTime, default=func.now(), nullable=False)
    # ip_address stores the originating IP for audit purposes (IPv6-safe length).
    ip_address = Column(String(45), nullable=True)
    # Version of the consent text shown to the user — bump when the disclosure changes.
    consent_version = Column(String(20), default='1.0', nullable=False)

    # Relationship back to the parent user
    parent = relationship("User", foreign_keys=[parent_id])


class LessonPlan(Base):
    """Lesson plans created by educators."""
    __tablename__ = 'lesson_plans'
    
    lesson_plan_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

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

# Admin and Moderation Tables
class AdminAuditLog(Base):
    """Audit logs for administrative actions."""
    __tablename__ = 'admin_audit_logs'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., 'suspend_user', 'change_role', 'delete_resource'
    target_type = Column(String(50), nullable=False)  # e.g., 'user', 'lesson_resource', 'curriculum'
    target_id = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)  # Detailed info about the change (JSON string)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    # actor may be NULL when the admin user account has been deleted (ondelete='SET NULL')
    actor = relationship("User")

class ResourceModeration(Base):
    """Moderation status and notes for lesson resources."""
    __tablename__ = 'resource_moderation'
    
    moderation_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_resource_id = Column(Integer, ForeignKey('lesson_resources.lesson_resources_id', ondelete='CASCADE'), unique=True, nullable=False)
    status = Column(String(20), default='pending', nullable=False)  # pending, safe, flagged, removed
    notes = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    lesson_resource = relationship("LessonResource", backref="moderation")
    reviewer = relationship("User")

class LessonTemplate(Base):
    """Templates for AI-generated lesson plans."""
    __tablename__ = 'lesson_templates'
    
    template_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    schema_json = Column(Text, nullable=False)  # JSON schema for the template structure
    is_active = Column(Integer, default=1, nullable=False)  # Using Integer as pseudo-boolean for consistency
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

# Add tags relationship to LessonPlan
LessonPlan.tags = relationship("Tag", secondary=lesson_tags, back_populates="lesson_plans")