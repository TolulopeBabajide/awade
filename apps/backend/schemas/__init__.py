"""
Pydantic schemas package.

This package contains all the Pydantic models used for API request/response validation
and data serialization in the Awade backend application.

Modules:
    - curriculum: Curriculum-related schemas
    - lesson_plans: Lesson plan schemas
    - users: User management schemas
    - country: Country management schemas
    - subject: Subject management schemas
    - grade_level: Grade level management schemas
"""

# Schemas package
from . import country, subject, grade_level 