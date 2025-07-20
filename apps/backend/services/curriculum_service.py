"""
Curriculum service for managing curriculum data and related operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import (
    Curriculum, Topic, LearningObjective, Content, TeacherActivity, 
    StudentActivity, TeachingMaterial, EvaluationGuide
)
from ..schemas.curriculum import (
    CurriculumCreate, CurriculumUpdate, TopicCreate, TopicUpdate,
    LearningObjectiveCreate, ContentCreate, TeacherActivityCreate,
    StudentActivityCreate, TeachingMaterialCreate, EvaluationGuideCreate,
    TopicBulkCreate, CurriculumBulkCreate
)

class CurriculumService:
    """Service class for curriculum operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Curriculum CRUD operations
    def create_curriculum(self, curriculum_data: CurriculumCreate) -> Curriculum:
        """Create a new curriculum."""
        curriculum = Curriculum(**curriculum_data.dict())
        self.db.add(curriculum)
        self.db.commit()
        self.db.refresh(curriculum)
        return curriculum
    
    def get_curriculum(self, curriculum_id: int) -> Optional[Curriculum]:
        """Get a curriculum by ID."""
        return self.db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    
    def get_curriculums(self, skip: int = 0, limit: int = 100, **filters) -> List[Curriculum]:
        """Get curricula with optional filtering."""
        query = self.db.query(Curriculum)
        
        # Apply filters
        if filters.get('country'):
            query = query.filter(Curriculum.country == filters['country'])
        if filters.get('grade_level'):
            query = query.filter(Curriculum.grade_level == filters['grade_level'])
        if filters.get('subject'):
            query = query.filter(Curriculum.subject == filters['subject'])
        if filters.get('theme'):
            query = query.filter(Curriculum.theme == filters['theme'])
        
        return query.offset(skip).limit(limit).all()
    
    def update_curriculum(self, curriculum_id: int, curriculum_data: CurriculumUpdate) -> Optional[Curriculum]:
        """Update a curriculum."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return None
        
        update_data = curriculum_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(curriculum, field, value)
        
        curriculum.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(curriculum)
        return curriculum
    
    def delete_curriculum(self, curriculum_id: int) -> bool:
        """Delete a curriculum and all related data."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return False
        
        self.db.delete(curriculum)
        self.db.commit()
        return True
    
    # Topic CRUD operations
    def create_topic(self, topic_data: TopicCreate) -> Topic:
        """Create a new topic."""
        topic = Topic(**topic_data.dict())
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic
    
    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """Get a topic by ID."""
        return self.db.query(Topic).filter(Topic.id == topic_id).first()
    
    def get_topic_by_code(self, topic_code: str) -> Optional[Topic]:
        """Get a topic by its unique code."""
        return self.db.query(Topic).filter(Topic.topic_code == topic_code).first()
    
    def get_topics(self, skip: int = 0, limit: int = 100, **filters) -> List[Topic]:
        """Get topics with optional filtering."""
        query = self.db.query(Topic)
        
        # Apply filters
        if filters.get('curriculum_id'):
            query = query.filter(Topic.curriculum_id == filters['curriculum_id'])
        if filters.get('topic_code'):
            query = query.filter(Topic.topic_code == filters['topic_code'])
        if filters.get('topic_title'):
            query = query.filter(Topic.topic_title.ilike(f"%{filters['topic_title']}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def update_topic(self, topic_id: int, topic_data: TopicUpdate) -> Optional[Topic]:
        """Update a topic."""
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
        objective = self.db.query(LearningObjective).filter(LearningObjective.id == objective_id).first()
        if not objective:
            return None
        
        objective.objective = objective_data
        self.db.commit()
        self.db.refresh(objective)
        return objective
    
    def delete_learning_objective(self, objective_id: int) -> bool:
        """Delete a learning objective."""
        objective = self.db.query(LearningObjective).filter(LearningObjective.id == objective_id).first()
        if not objective:
            return False
        
        self.db.delete(objective)
        self.db.commit()
        return True
    
    # Content operations
    def create_content(self, content_data: ContentCreate) -> Content:
        """Create a new content area."""
        content = Content(**content_data.dict())
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content
    
    def get_contents(self, topic_id: int) -> List[Content]:
        """Get all content areas for a topic."""
        return self.db.query(Content).filter(Content.topic_id == topic_id).all()
    
    def update_content(self, content_id: int, content_data: str) -> Optional[Content]:
        """Update a content area."""
        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return None
        
        content.content_area = content_data
        self.db.commit()
        self.db.refresh(content)
        return content
    
    def delete_content(self, content_id: int) -> bool:
        """Delete a content area."""
        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return False
        
        self.db.delete(content)
        self.db.commit()
        return True
    
    # Teacher Activity operations
    def create_teacher_activity(self, activity_data: TeacherActivityCreate) -> TeacherActivity:
        """Create a new teacher activity."""
        activity = TeacherActivity(**activity_data.dict())
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def get_teacher_activities(self, topic_id: int) -> List[TeacherActivity]:
        """Get all teacher activities for a topic."""
        return self.db.query(TeacherActivity).filter(TeacherActivity.topic_id == topic_id).all()
    
    def update_teacher_activity(self, activity_id: int, activity_data: str) -> Optional[TeacherActivity]:
        """Update a teacher activity."""
        activity = self.db.query(TeacherActivity).filter(TeacherActivity.id == activity_id).first()
        if not activity:
            return None
        
        activity.activity = activity_data
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def delete_teacher_activity(self, activity_id: int) -> bool:
        """Delete a teacher activity."""
        activity = self.db.query(TeacherActivity).filter(TeacherActivity.id == activity_id).first()
        if not activity:
            return False
        
        self.db.delete(activity)
        self.db.commit()
        return True
    
    # Student Activity operations
    def create_student_activity(self, activity_data: StudentActivityCreate) -> StudentActivity:
        """Create a new student activity."""
        activity = StudentActivity(**activity_data.dict())
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def get_student_activities(self, topic_id: int) -> List[StudentActivity]:
        """Get all student activities for a topic."""
        return self.db.query(StudentActivity).filter(StudentActivity.topic_id == topic_id).all()
    
    def update_student_activity(self, activity_id: int, activity_data: str) -> Optional[StudentActivity]:
        """Update a student activity."""
        activity = self.db.query(StudentActivity).filter(StudentActivity.id == activity_id).first()
        if not activity:
            return None
        
        activity.activity = activity_data
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def delete_student_activity(self, activity_id: int) -> bool:
        """Delete a student activity."""
        activity = self.db.query(StudentActivity).filter(StudentActivity.id == activity_id).first()
        if not activity:
            return False
        
        self.db.delete(activity)
        self.db.commit()
        return True
    
    # Teaching Material operations
    def create_teaching_material(self, material_data: TeachingMaterialCreate) -> TeachingMaterial:
        """Create a new teaching material."""
        material = TeachingMaterial(**material_data.dict())
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material
    
    def get_teaching_materials(self, topic_id: int) -> List[TeachingMaterial]:
        """Get all teaching materials for a topic."""
        return self.db.query(TeachingMaterial).filter(TeachingMaterial.topic_id == topic_id).all()
    
    def update_teaching_material(self, material_id: int, material_data: str) -> Optional[TeachingMaterial]:
        """Update a teaching material."""
        material = self.db.query(TeachingMaterial).filter(TeachingMaterial.id == material_id).first()
        if not material:
            return None
        
        material.material = material_data
        self.db.commit()
        self.db.refresh(material)
        return material
    
    def delete_teaching_material(self, material_id: int) -> bool:
        """Delete a teaching material."""
        material = self.db.query(TeachingMaterial).filter(TeachingMaterial.id == material_id).first()
        if not material:
            return False
        
        self.db.delete(material)
        self.db.commit()
        return True
    
    # Evaluation Guide operations
    def create_evaluation_guide(self, guide_data: EvaluationGuideCreate) -> EvaluationGuide:
        """Create a new evaluation guide."""
        guide = EvaluationGuide(**guide_data.dict())
        self.db.add(guide)
        self.db.commit()
        self.db.refresh(guide)
        return guide
    
    def get_evaluation_guides(self, topic_id: int) -> List[EvaluationGuide]:
        """Get all evaluation guides for a topic."""
        return self.db.query(EvaluationGuide).filter(EvaluationGuide.topic_id == topic_id).all()
    
    def update_evaluation_guide(self, guide_id: int, guide_data: str) -> Optional[EvaluationGuide]:
        """Update an evaluation guide."""
        guide = self.db.query(EvaluationGuide).filter(EvaluationGuide.id == guide_id).first()
        if not guide:
            return None
        
        guide.guide = guide_data
        self.db.commit()
        self.db.refresh(guide)
        return guide
    
    def delete_evaluation_guide(self, guide_id: int) -> bool:
        """Delete an evaluation guide."""
        guide = self.db.query(EvaluationGuide).filter(EvaluationGuide.id == guide_id).first()
        if not guide:
            return False
        
        self.db.delete(guide)
        self.db.commit()
        return True
    
    # Bulk operations
    def create_curriculum_with_topics(self, curriculum_data: CurriculumBulkCreate) -> Curriculum:
        """Create a curriculum with all its topics and related data."""
        # Create curriculum
        curriculum = Curriculum(
            country=curriculum_data.country,
            grade_level=curriculum_data.grade_level,
            subject=curriculum_data.subject,
            theme=curriculum_data.theme
        )
        self.db.add(curriculum)
        self.db.commit()
        self.db.refresh(curriculum)
        
        # Create topics and related data
        for topic_data in curriculum_data.topics:
            topic = Topic(
                curriculum_id=curriculum.id,
                topic_code=topic_data.topic_code,
                topic_title=topic_data.topic_title,
                description=topic_data.description
            )
            self.db.add(topic)
            self.db.commit()
            self.db.refresh(topic)
            
            # Create learning objectives
            for objective in topic_data.learning_objectives:
                learning_obj = LearningObjective(topic_id=topic.id, objective=objective)
                self.db.add(learning_obj)
            
            # Create contents
            for content in topic_data.contents:
                content_obj = Content(topic_id=topic.id, content_area=content)
                self.db.add(content_obj)
            
            # Create teacher activities
            for activity in topic_data.teacher_activities:
                teacher_activity = TeacherActivity(topic_id=topic.id, activity=activity)
                self.db.add(teacher_activity)
            
            # Create student activities
            for activity in topic_data.student_activities:
                student_activity = StudentActivity(topic_id=topic.id, activity=activity)
                self.db.add(student_activity)
            
            # Create teaching materials
            for material in topic_data.teaching_materials:
                teaching_material = TeachingMaterial(topic_id=topic.id, material=material)
                self.db.add(teaching_material)
            
            # Create evaluation guides
            for guide in topic_data.evaluation_guides:
                evaluation_guide = EvaluationGuide(topic_id=topic.id, guide=guide)
                self.db.add(evaluation_guide)
        
        self.db.commit()
        self.db.refresh(curriculum)
        return curriculum
    
    # Search and utility methods
    def search_curriculums(self, search_term: str) -> List[Curriculum]:
        """Search curricula by country, subject, or theme."""
        return self.db.query(Curriculum).filter(
            or_(
                Curriculum.country.ilike(f"%{search_term}%"),
                Curriculum.subject.ilike(f"%{search_term}%"),
                Curriculum.theme.ilike(f"%{search_term}%")
            )
        ).all()
    
    def search_topics(self, search_term: str) -> List[Topic]:
        """Search topics by title or description."""
        return self.db.query(Topic).filter(
            or_(
                Topic.topic_title.ilike(f"%{search_term}%"),
                Topic.description.ilike(f"%{search_term}%")
            )
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
        total_teacher_activities = 0
        total_student_activities = 0
        total_materials = 0
        total_guides = 0
        
        for topic in topics:
            total_objectives += len(self.get_learning_objectives(topic.id))
            total_contents += len(self.get_contents(topic.id))
            total_teacher_activities += len(self.get_teacher_activities(topic.id))
            total_student_activities += len(self.get_student_activities(topic.id))
            total_materials += len(self.get_teaching_materials(topic.id))
            total_guides += len(self.get_evaluation_guides(topic.id))
        
        return {
            "curriculum_id": curriculum_id,
            "total_topics": total_topics,
            "total_learning_objectives": total_objectives,
            "total_contents": total_contents,
            "total_teacher_activities": total_teacher_activities,
            "total_student_activities": total_student_activities,
            "total_teaching_materials": total_materials,
            "total_evaluation_guides": total_guides
        } 