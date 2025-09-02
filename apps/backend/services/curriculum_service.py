"""
Curriculum Service for Awade

This module provides service methods for managing curriculum data, topics, learning objectives, and content areas in the Awade platform. It supports CRUD operations, search, and statistics for curriculum mapping and educational content.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime

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
        curriculum = Curriculum(**curriculum_data.dict())
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
        
        update_data = curriculum_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(curriculum, field, value)
        
        curriculum.updated_at = datetime.utcnow()
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
        topic = Topic(**topic_data.dict())
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
        
        update_data = topic_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)
        
        topic.updated_at = datetime.utcnow()
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
        objective = LearningObjective(**objective_data.dict())
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
        content = TopicContent(**content_data.dict())
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
    
    # Teacher Activity operations
    # def create_teacher_activity(self, activity_data: TeacherActivityCreate) -> TeacherActivity:
    #     """Create a new teacher activity."""
    #     activity = TeacherActivity(**activity_data.dict())
    #     self.db.add(activity)
    #     self.db.commit()
    #     self.db.refresh(activity)
    #     return activity
    
    # def get_teacher_activities(self, topic_id: int) -> List[TeacherActivity]:
    #     """Get all teacher activities for a topic."""
    #     return self.db.query(TeacherActivity).filter(TeacherActivity.topic_id == topic_id).all()
    
    # def update_teacher_activity(self, activity_id: int, activity_data: str) -> Optional[TeacherActivity]:
    #     """Update a teacher activity."""
    #     activity = self.db.query(TeacherActivity).filter(TeacherActivity.id == activity_id).first()
    #     if not activity:
    #         return None
        
    #     activity.activity = activity_data
    #     self.db.commit()
    #     self.db.refresh(activity)
    #     return activity
    
    # def delete_teacher_activity(self, activity_id: int) -> bool:
    #     """Delete a teacher activity."""
    #     activity = self.db.query(TeacherActivity).filter(TeacherActivity.id == activity_id).first()
    #     if not activity:
    #         return False
        
    #     self.db.delete(activity)
    #     self.db.commit()
    #     return True
    
    # Student Activity operations
    # def create_student_activity(self, activity_data: StudentActivityCreate) -> StudentActivity:
    #     """Create a new student activity."""
    #     activity = StudentActivity(**activity_data.dict())
    #     self.db.add(activity)
    #     self.db.commit()
    #     self.db.refresh(activity)
    #     return activity
    
    # def get_student_activities(self, topic_id: int) -> List[StudentActivity]:
    #     """Get all student activities for a topic."""
    #     return self.db.query(StudentActivity).filter(StudentActivity.topic_id == topic_id).all()
    
    # def update_student_activity(self, activity_id: int, activity_data: str) -> Optional[StudentActivity]:
    #     """Update a student activity."""
    #     activity = self.db.query(StudentActivity).filter(StudentActivity.id == activity_id).first()
    #     if not activity:
    #         return None
        
    #     activity.activity = activity_data
    #     self.db.commit()
    #     self.db.refresh(activity)
    #     return activity
    
    # def delete_student_activity(self, activity_id: int) -> bool:
    #     """Delete a student activity."""
    #     activity = self.db.query(StudentActivity).filter(StudentActivity.id == activity_id).first()
    #     if not activity:
    #         return False
        
    #     self.db.delete(activity)
    #     self.db.commit()
    #     return True
    
    # Teaching Material operations
    # def create_teaching_material(self, material_data: TeachingMaterialCreate) -> TeachingMaterial:
    #     """Create a new teaching material."""
    #     material = TeachingMaterial(**material_data.dict())
    #     self.db.add(material)
    #     self.db.commit()
    #     self.db.refresh(material)
    #     return material
    
    # def get_teaching_materials(self, topic_id: int) -> List[TeachingMaterial]:
    #     """Get all teaching materials for a topic."""
    #     return self.db.query(TeachingMaterial).filter(TeachingMaterial.topic_id == topic_id).all()
    
    # def update_teaching_material(self, material_id: int, material_data: str) -> Optional[TeachingMaterial]:
    #     """Update a teaching material."""
    #     material = self.db.query(TeachingMaterial).filter(TeachingMaterial.id == material_id).first()
    #     if not material:
    #         return None
        
    #     material.material = material_data
    #     self.db.commit()
    #     self.db.refresh(material)
    #     return material
    
    # def delete_teaching_material(self, material_id: int) -> bool:
    #     """Delete a teaching material."""
    #     material = self.db.query(TeachingMaterial).filter(TeachingMaterial.id == material_id).first()
    #     if not material:
    #         return False
        
    #     self.db.delete(material)
    #     self.db.commit()
    #     return True
    
    # Evaluation Guide operations
    # def create_evaluation_guide(self, guide_data: EvaluationGuideCreate) -> EvaluationGuide:
    #     """Create a new evaluation guide."""
    #     guide = EvaluationGuide(**guide_data.dict())
    #     self.db.add(guide)
    #     self.db.commit()
    #     self.db.refresh(guide)
    #     return guide
    
    # def get_evaluation_guides(self, topic_id: int) -> List[EvaluationGuide]:
    #     """Get all evaluation guides for a topic."""
    #     return self.db.query(EvaluationGuide).filter(EvaluationGuide.topic_id == topic_id).all()
    
    # def update_evaluation_guide(self, guide_id: int, guide_data: str) -> Optional[EvaluationGuide]:
    #     """Update an evaluation guide."""
    #     guide = self.db.query(EvaluationGuide).filter(EvaluationGuide.id == guide_id).first()
    #     if not guide:
    #         return None
        
    #     guide.guide = guide_data
    #     self.db.commit()
    #     self.db.refresh(guide)
    #     return guide
    
    # def delete_evaluation_guide(self, guide_id: int) -> bool:
    #     """Delete an evaluation guide."""
    #     guide = self.db.query(EvaluationGuide).filter(EvaluationGuide.id == guide_id).first()
    #     if not guide:
    #         return False
        
    #     self.db.delete(guide)
    #     self.db.commit()
    #     return True
    

    
    # Search and utility methods
    def search_curriculums(self, search_term: str) -> List[Curriculum]:
        """Search curricula by country, subject, or theme."""
        return self.db.query(Curriculum).filter(
            or_(
                Curriculum.country.ilike(f"%{search_term}%"),
                Curriculum.subject.ilike(f"%{search_term}%"),            )
        ).all()
    
    def search_topics(self, search_term: str) -> List[Topic]:
        """Search topics by title or description."""
        return self.db.query(Topic).filter(
            or_(
                Topic.topic_title.ilike(f"%{search_term}%"),            )
        ).all()
    
    def get_curriculum_statistics(self, curriculum_id: int) -> Dict[str, Any]:
        """Get statistics for a curriculum."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return {}
        
        topics = self.get_topics(curriculum_id=curriculum_id)
        total_topics = len(topics)
        
        total_objectives = 0
        total_contents = 0
        # total_teacher_activities = 0
        # total_student_activities = 0
        # total_materials = 0
        # total_guides = 0
        
        for topic in topics:
            total_objectives += len(self.get_learning_objectives(topic.id))
            total_contents += len(self.get_contents(topic.id))
            # total_teacher_activities += len(self.get_teacher_activities(topic.id))
            # total_student_activities += len(self.get_student_activities(topic.id))
            # total_materials += len(self.get_teaching_materials(topic.id))
            # total_guides += len(self.get_evaluation_guides(topic.id))
        
        return {
            "curriculum_id": curriculum_id,
            "total_topics": total_topics,
            "total_learning_objectives": total_objectives,
            "total_contents": total_contents,
            # "total_teacher_activities": total_teacher_activities,
            # "total_student_activities": total_student_activities,
            # "total_teaching_materials": total_materials,
            # "total_evaluation_guides": total_guides
        } 