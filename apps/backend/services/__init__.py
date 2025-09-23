"""
Services package for Awade backend.

This package contains service classes that handle business logic,
separating concerns from the router layer.
"""

import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
if parent_dir not in sys.path:
    sys.path.extend([parent_dir, root_dir])

from .curriculum_service import CurriculumService
from .file_upload_service import FileUploadService
# from .pdf_service import PDFService  # Temporarily disabled due to WeasyPrint dependencies
from .lesson_plan_service import LessonPlanService
from .auth_service import AuthService
from .user_service import UserService
from .context_service import ContextService
from .country_service import CountryService
from .subject_service import SubjectService
from .grade_level_service import GradeLevelService
from .data_structures import DataStructureManager, CacheStrategy, LRUCache, LFUCache, SearchIndex, RequestQueue, QueryOptimizer
from .optimized_database_service import OptimizedDatabaseService

__all__ = [
    "CurriculumService",
    "FileUploadService", 
    # "PDFService",  # Temporarily disabled due to WeasyPrint dependencies
    "LessonPlanService",
    "AuthService",
    "UserService",
    "ContextService",
    "CountryService",
    "SubjectService",
    "GradeLevelService",
    "DataStructureManager",
    "CacheStrategy",
    "LRUCache",
    "LFUCache", 
    "SearchIndex",
    "RequestQueue",
    "QueryOptimizer",
    "OptimizedDatabaseService"
] 