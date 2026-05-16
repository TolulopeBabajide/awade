"""
Curriculum Service for Awade

This module provides service methods for managing curriculum data, topics, learning objectives, and content areas in the Awade platform. It supports CRUD operations, search, and statistics for curriculum mapping and educational content.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from apps.backend.models import (
    Curriculum, Topic, CurriculumStructure, Country, GradeLevel, Subject, LearningObjective, TopicContent
)
from apps.backend.schemas.curriculum import (
    CurriculumCreate, CurriculumResponse, TopicCreate, TopicResponse, LearningObjectiveCreate, ContentCreate
)

class CurriculumService:
    """Service class for curriculum operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the CurriculumService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    # Curriculum CRUD operations (normalized)
    def create_curriculum(self, curriculum_data: CurriculumCreate) -> Curriculum:
        """
        Create a new curriculum.

        Args:
            curriculum_data (CurriculumCreate): The curriculum data to create.

        Returns:
            Curriculum: The created curriculum ORM object.
        """
        curriculum = Curriculum(**curriculum_data.model_dump())
        self.db.add(curriculum)
        self.db.commit()
        self.db.refresh(curriculum)
        return curriculum
    
    def get_curriculum(self, curricula_id: int) -> Optional[Curriculum]:
        """
        Get a curriculum by its ID.

        Args:
            curricula_id (int): The curriculum ID.

        Returns:
            Optional[Curriculum]: The curriculum ORM object or None if not found.
        """
        return self.db.query(Curriculum).filter(Curriculum.curricula_id == curricula_id).first()
    
    def get_curriculums(self, skip: int = 0, limit: int = 100, country_id: Optional[int] = None) -> List[Curriculum]:
        """
        Get a list of curriculums with optional filtering by country.

        Args:
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to return.
            country_id (Optional[int]): Filter by country ID.

        Returns:
            List[Curriculum]: List of curriculum ORM objects.
        """
        query = self.db.query(Curriculum)
        
        # Apply filters
        if country_id:
            query = query.filter(Curriculum.country_id == country_id)
        
        return query.offset(skip).limit(limit).all()
    
    def update_curriculum(self, curricula_id: int, curriculum_data: CurriculumCreate) -> Optional[Curriculum]:
        """
        Update a curriculum by its ID.

        Args:
            curricula_id (int): The curriculum ID.
            curriculum_data (CurriculumCreate): The updated curriculum data.

        Returns:
            Optional[Curriculum]: The updated curriculum ORM object or None if not found.
        """
        curriculum = self.get_curriculum(curricula_id)
        if not curriculum:
            return None
        
        update_data = curriculum_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(curriculum, field, value)
        
        curriculum.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(curriculum)
        return curriculum
    
    def delete_curriculum(self, curricula_id: int) -> bool:
        """
        Delete a curriculum and all related data by its ID.

        Args:
            curricula_id (int): The curriculum ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        curriculum = self.get_curriculum(curricula_id)
        if not curriculum:
            return False
        
        self.db.delete(curriculum)
        self.db.commit()
        return True
    
    # Topic CRUD operations (normalized)
    def create_topic(self, topic_data: TopicCreate) -> Topic:
        """
        Create a new topic.

        Args:
            topic_data (TopicCreate): The topic data to create.

        Returns:
            Topic: The created topic ORM object.
        """
        topic = Topic(**topic_data.model_dump())
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic
    
    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """
        Get a topic by its ID.

        Args:
            topic_id (int): The topic ID.

        Returns:
            Optional[Topic]: The topic ORM object or None if not found.
        """
        return self.db.query(Topic).filter(Topic.topic_id == topic_id).first()
    
    def get_topics(self, skip: int = 0, limit: int = 100, curriculum_structure_id: Optional[int] = None) -> List[Topic]:
        """
        Get a list of topics with optional filtering by curriculum structure.

        Args:
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to return.
            curriculum_structure_id (Optional[int]): Filter by curriculum structure ID.

        Returns:
            List[Topic]: List of topic ORM objects.
        """
        query = self.db.query(Topic)
        
        # Apply filters
        if curriculum_structure_id:
            query = query.filter(Topic.curriculum_structure_id == curriculum_structure_id)
        
        return query.offset(skip).limit(limit).all()
    
    def update_topic(self, topic_id: int, topic_data: TopicCreate) -> Optional[Topic]:
        """
        Update a topic by its ID.

        Args:
            topic_id (int): The topic ID.
            topic_data (TopicCreate): The updated topic data.

        Returns:
            Optional[Topic]: The updated topic ORM object or None if not found.
        """
        topic = self.get_topic(topic_id)
        if not topic:
            return None
        
        update_data = topic_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)
        
        topic.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(topic)
        return topic
    
    def delete_topic(self, topic_id: int) -> bool:
        """Delete a topic and all related data."""
        topic = self.get_topic(topic_id)
        if not topic:
            return False
        
        self.db.delete(topic)
        self.db.commit()
        return True
    
    # Learning Objective operations
    def create_learning_objective(self, objective_data: LearningObjectiveCreate) -> LearningObjective:
        """Create a new learning objective."""
        objective = LearningObjective(**objective_data.model_dump())
        self.db.add(objective)
        self.db.commit()
        self.db.refresh(objective)
        return objective
    
    def get_learning_objectives(self, topic_id: int) -> List[LearningObjective]:
        """Get all learning objectives for a topic."""
        return self.db.query(LearningObjective).filter(LearningObjective.topic_id == topic_id).all()
    
    def update_learning_objective(self, objective_id: int, objective_data: str) -> Optional[LearningObjective]:
        """Update a learning objective."""
        objective = self.db.query(LearningObjective).filter(LearningObjective.learning_objective_id == objective_id).first()
        if not objective:
            return None
        
        objective.objective = objective_data
        self.db.commit()
        self.db.refresh(objective)
        return objective
    
    def delete_learning_objective(self, objective_id: int) -> bool:
        """Delete a learning objective."""
        objective = self.db.query(LearningObjective).filter(LearningObjective.learning_objective_id == objective_id).first()
        if not objective:
            return False
        
        self.db.delete(objective)
        self.db.commit()
        return True
    
    # Content operations
    def create_content(self, content_data: ContentCreate) -> TopicContent:
        """Create a new content area."""
        content = TopicContent(**content_data.model_dump())
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content
    
    def get_contents(self, topic_id: int) -> List[TopicContent]:
        """Get all content areas for a topic."""
        return self.db.query(TopicContent).filter(TopicContent.topic_id == topic_id).all()
    
    def update_content(self, content_id: int, content_data: str) -> Optional[TopicContent]:
        """Update a content area."""
        content = self.db.query(TopicContent).filter(TopicContent.topic_contents_id == content_id).first()
        if not content:
            return None
        
        content.content_area = content_data
        self.db.commit()
        self.db.refresh(content)
        return content
    
    def delete_content(self, content_id: int) -> bool:
        """Delete a content area."""
        content = self.db.query(TopicContent).filter(TopicContent.topic_contents_id == content_id).first()
        if not content:
            return False
        
        self.db.delete(content)
        self.db.commit()
        return True

    # Search and utility methods
    def search_curriculums(self, search_term: str) -> List[Curriculum]:
        """Search curricula by country name, subject name, or curriculum title.

        AWD-M-164: The original implementation called .ilike() on ORM
        relationship attributes (Curriculum.country, Curriculum.subject) which
        raises AttributeError.  Fix: join Country for country_name lookup;
        outerjoin CurriculumStructure → Subject for subject name lookup;
        also search Curriculum.curricula_title.  distinct() prevents duplicate
        rows when a curriculum has multiple structures.

        AWD-M-166: Guard against empty or whitespace-only search_term.
        Passing "" would make ilike("%%") match every row — returning the full
        unfiltered result set with expensive joins.  Return [] early instead.
        """
        if not search_term or not search_term.strip():
            return []
        return (
            self.db.query(Curriculum)
            .join(Country, Curriculum.country_id == Country.country_id)
            .outerjoin(
                CurriculumStructure,
                CurriculumStructure.curricula_id == Curriculum.curricula_id,
            )
            .outerjoin(
                Subject,
                Subject.subject_id == CurriculumStructure.subject_id,
            )
            .filter(
                or_(
                    Curriculum.curricula_title.ilike(f"%{search_term}%"),
                    Country.country_name.ilike(f"%{search_term}%"),
                    Subject.name.ilike(f"%{search_term}%"),
                )
            )
            .distinct()
            .all()
        )

    def search_topics(self, search_term: str) -> List[Topic]:
        """Search topics by title.

        AWD-M-166: Guard against empty or whitespace-only search_term.
        Passing "" would make ilike("%%") match every row.  Return [] early.
        """
        if not search_term or not search_term.strip():
            return []
        return self.db.query(Topic).filter(
            or_(
                Topic.topic_title.ilike(f"%{search_term}%"),
            )
        ).all()
    
    def get_curriculum_statistics(self, curriculum_id: int) -> Dict[str, Any]:
        """Get statistics for a curriculum.

        Counts all topics, learning objectives, and content areas across every
        CurriculumStructure that belongs to the given curriculum.

        Args:
            curriculum_id: Primary key of the Curriculum record (curricula_id).

        Returns:
            Dict with total_topics, total_learning_objectives, total_contents,
            or an empty dict if the curriculum does not exist.
        """
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return {}

        # Collect all CurriculumStructure IDs that belong to this curriculum,
        # then fetch every Topic that references one of those structures.
        # (get_topics() filters by a single curriculum_structure_id, so we query
        # topics directly here to cover all structures under the curriculum.)
        structure_ids = [
            cs.curriculum_structure_id
            for cs in self.db.query(CurriculumStructure).filter(
                CurriculumStructure.curricula_id == curriculum_id
            ).all()
        ]
        topics = (
            self.db.query(Topic)
            .filter(Topic.curriculum_structure_id.in_(structure_ids))
            .all()
        ) if structure_ids else []

        total_topics = len(topics)

        total_objectives = 0
        total_contents = 0

        for topic in topics:
            # Topic primary key is topic_id, not id
            total_objectives += len(self.get_learning_objectives(topic.topic_id))
            total_contents += len(self.get_contents(topic.topic_id))

        return {
            "curriculum_id": curriculum_id,
            "total_topics": total_topics,
            "total_learning_objectives": total_objectives,
            "total_contents": total_contents,
        } 