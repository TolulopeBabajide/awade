"""
Optimized Database Service for Awade

This module provides optimized database operations with caching, query optimization,
and performance monitoring for the Awade platform.

Author: Tolulope Babajide
"""

from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import json
import re

from .data_structures import DataStructureManager, CacheStrategy


class OptimizedDatabaseService:
    """Optimized database service with caching and performance monitoring."""
    
    def __init__(self, cache_capacity: int = 1000, queue_capacity: int = 1000, cache_ttl: int = 300):
        """
        Initialize optimized database service.
        
        Args:
            cache_capacity (int): Cache capacity
            queue_capacity (int): Queue capacity
            cache_ttl (int): Cache TTL in seconds
        """
        self.ds_manager = DataStructureManager(cache_capacity, queue_capacity)
        self.cache_ttl = cache_ttl
        
        # Query patterns for optimization
        self.query_patterns = {
            'user_by_email': {
                'cache_strategy': CacheStrategy.LRU,
                'ttl': 300,
                'complexity': 5
            },
            'lesson_plans_by_subject': {
                'cache_strategy': CacheStrategy.LFU,
                'ttl': 600,
                'complexity': 15
            },
            'curriculum_structure': {
                'cache_strategy': CacheStrategy.LRU,
                'ttl': 1800,
                'complexity': 10
            },
            'search_results': {
                'cache_strategy': CacheStrategy.LFU,
                'ttl': 300,
                'complexity': 20
            }
        }
    
    def _generate_cache_key(self, pattern: str, **kwargs) -> str:
        """
        Generate cache key for query pattern.
        
        Args:
            pattern (str): Query pattern name
            **kwargs: Query parameters
            
        Returns:
            str: Generated cache key
        """
        import hashlib
        import json
        
        # Sanitize and validate inputs
        safe_pattern = re.sub(r'[^a-zA-Z0-9_]', '', pattern)
        safe_params = {k: str(v) for k, v in kwargs.items() if isinstance(v, (str, int, float))}
        
        # Create secure hash
        content = json.dumps({"pattern": safe_pattern, "params": safe_params}, sort_keys=True)
        return f"{safe_pattern}:{hashlib.sha256(content.encode()).hexdigest()[:32]}"
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[Any]:
        """
        Get user by email with caching.
        
        Args:
            db (Session): Database session
            email (str): User email
            
        Returns:
            Optional[Any]: User object or None
        """
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        cache_key = self._generate_cache_key('user_by_email', email=email)
        
        # Try cache first
        cached_user = self.ds_manager.cache_get(cache_key, CacheStrategy.LRU)
        if cached_user:
            return cached_user
        
        # Query database
        from ..models import User
        user = db.query(User).filter(User.email == email).first()
        
        # Cache result
        if user:
            self.ds_manager.cache_set(cache_key, user, CacheStrategy.LRU)
        
        return user
    
    def get_lesson_plans_by_subject(self, db: Session, subject: str, grade_level: str = None, limit: int = 50) -> List[Any]:
        """
        Get lesson plans by subject with caching.
        
        Args:
            db (Session): Database session
            subject (str): Subject name
            grade_level (str, optional): Grade level filter
            limit (int): Maximum results
            
        Returns:
            List[Any]: List of lesson plans
        """
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Subject must be a non-empty string")
        
        if grade_level is not None and (not isinstance(grade_level, str) or not grade_level.strip()):
            raise ValueError("Grade level must be a non-empty string")
        
        if not isinstance(limit, int) or limit <= 0 or limit > 1000:
            raise ValueError("Limit must be a positive integer <= 1000")
        
        cache_key = self._generate_cache_key(
            'lesson_plans_by_subject', 
            subject=subject, 
            grade_level=grade_level or 'all',
            limit=limit
        )
        
        # Try cache first
        cached_plans = self.ds_manager.cache_get(cache_key, CacheStrategy.LFU)
        if cached_plans:
            return cached_plans
        
        # Query database
        from ..models import LessonPlan, Topic, CurriculumStructure, Subject, GradeLevel
        
        query = db.query(LessonPlan).join(Topic).join(CurriculumStructure).join(Subject)
        
        if grade_level:
            query = query.join(GradeLevel).filter(GradeLevel.name == grade_level)
        
        query = query.filter(Subject.name == subject).limit(limit)
        lesson_plans = query.all()
        
        # Cache result
        self.ds_manager.cache_set(cache_key, lesson_plans, CacheStrategy.LFU)
        
        return lesson_plans
    
    def get_curriculum_structure(self, db: Session, country_id: int = None, subject_id: int = None, grade_level_id: int = None) -> List[Any]:
        """
        Get curriculum structure with caching.
        
        Args:
            db (Session): Database session
            country_id (int, optional): Country filter
            subject_id (int, optional): Subject filter
            grade_level_id (int, optional): Grade level filter
            
        Returns:
            List[Any]: List of curriculum structures
        """
        # Validate input parameters
        if country_id is not None and (not isinstance(country_id, int) or country_id <= 0):
            raise ValueError("Country ID must be a positive integer")
        
        if subject_id is not None and (not isinstance(subject_id, int) or subject_id <= 0):
            raise ValueError("Subject ID must be a positive integer")
        
        if grade_level_id is not None and (not isinstance(grade_level_id, int) or grade_level_id <= 0):
            raise ValueError("Grade level ID must be a positive integer")
        
        cache_key = self._generate_cache_key(
            'curriculum_structure',
            country_id=country_id or 'all',
            subject_id=subject_id or 'all',
            grade_level_id=grade_level_id or 'all'
        )
        
        # Try cache first
        cached_structures = self.ds_manager.cache_get(cache_key, CacheStrategy.LRU)
        if cached_structures:
            return cached_structures
        
        # Query database
        from ..models import CurriculumStructure
        
        query = db.query(CurriculumStructure)
        
        if country_id:
            query = query.filter(CurriculumStructure.curricula_id == country_id)
        if subject_id:
            query = query.filter(CurriculumStructure.subject_id == subject_id)
        if grade_level_id:
            query = query.filter(CurriculumStructure.grade_level_id == grade_level_id)
        
        structures = query.all()
        
        # Cache result
        self.ds_manager.cache_set(cache_key, structures, CacheStrategy.LRU)
        
        return structures
    
    def search_lesson_plans(self, db: Session, query_text: str, subject: str = None, limit: int = 20) -> List[Any]:
        """
        Search lesson plans with full-text search and caching.
        
        Args:
            db (Session): Database session
            query_text (str): Search query
            subject (str, optional): Subject filter
            limit (int): Maximum results
            
        Returns:
            List[Any]: List of matching lesson plans
        """
        if not isinstance(query_text, str) or not query_text.strip():
            raise ValueError("Query text must be a non-empty string")
        
        if subject is not None and (not isinstance(subject, str) or not subject.strip()):
            raise ValueError("Subject must be a non-empty string")
        
        if not isinstance(limit, int) or limit <= 0 or limit > 100:
            raise ValueError("Limit must be a positive integer <= 100")
        
        # Sanitize query text
        sanitized_query = re.sub(r'[^\w\s]', ' ', query_text.strip())
        if not sanitized_query:
            return []
        
        cache_key = self._generate_cache_key(
            'search_results',
            query=sanitized_query,
            subject=subject or 'all',
            limit=limit
        )
        
        # Try cache first
        cached_results = self.ds_manager.cache_get(cache_key, CacheStrategy.LFU)
        if cached_results:
            return cached_results
        
        # Use search index
        search_results = self.ds_manager.search_documents(sanitized_query, limit)
        
        if not search_results:
            return []
        
        # Get lesson plans by IDs
        from ..models import LessonPlan
        lesson_plan_ids = [doc_id for doc_id, _ in search_results]
        
        query = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id.in_(lesson_plan_ids))
        
        if subject:
            from ..models import Topic, CurriculumStructure, Subject
            query = query.join(Topic).join(CurriculumStructure).join(Subject).filter(Subject.name == subject)
        
        lesson_plans = query.all()
        
        # Cache result
        self.ds_manager.cache_set(cache_key, lesson_plans, CacheStrategy.LFU)
        
        return lesson_plans
    
    def add_lesson_plan_to_search(self, lesson_plan_id: int, title: str, content: str) -> None:
        """
        Add lesson plan to search index.
        
        Args:
            lesson_plan_id (int): Lesson plan ID
            title (str): Lesson plan title
            content (str): Lesson plan content
        """
        if not isinstance(lesson_plan_id, int) or lesson_plan_id <= 0:
            raise ValueError("Lesson plan ID must be a positive integer")
        
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title must be a non-empty string")
        
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Content must be a non-empty string")
        
        # Sanitize inputs
        sanitized_title = re.sub(r'[^\w\s]', ' ', title.strip())
        sanitized_content = re.sub(r'[^\w\s]', ' ', content.strip())
        
        search_text = f"{sanitized_title} {sanitized_content}"
        self.ds_manager.add_search_document(lesson_plan_id, search_text)
    
    def optimize_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize database query.
        
        Args:
            query (str): SQL query
            params (Dict[str, Any]): Query parameters
            
        Returns:
            Dict[str, Any]: Optimized query plan
        """
        return self.ds_manager.optimize_query(query, params)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        return self.ds_manager.get_metrics()
    
    def clear_cache(self, strategy: CacheStrategy = None) -> None:
        """
        Clear cache.
        
        Args:
            strategy (CacheStrategy, optional): Specific cache strategy to clear
        """
        if strategy is None or strategy == CacheStrategy.LRU:
            self.ds_manager.lru_cache.clear()
        if strategy is None or strategy == CacheStrategy.LFU:
            self.ds_manager.lfu_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        return {
            'lru_cache_size': self.ds_manager.lru_cache.size(),
            'lru_cache_capacity': self.ds_manager.lru_cache.capacity,
            'lfu_cache_size': self.ds_manager.lfu_cache.size(),
            'lfu_cache_capacity': self.ds_manager.lfu_cache.capacity,
            'search_index_docs': self.ds_manager.search_index.doc_count,
            'queue_stats': self.ds_manager.request_queue.get_queue_stats()
        }
