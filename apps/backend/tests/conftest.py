"""
Pytest configuration and fixtures for Awade backend tests.

This module provides shared fixtures and configuration for all backend tests.

Author: Tolulope Babajide
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Add the parent directory and project root to the path
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
apps_dir = os.path.dirname(backend_dir)
root_dir = os.path.dirname(apps_dir)

sys.path.insert(0, backend_dir)
sys.path.insert(0, root_dir)

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.models import Base, User, Country, Curriculum, Subject, GradeLevel, CurriculumStructure, Topic, LessonPlan
from apps.backend.services.data_structures import DataStructureManager, CacheStrategy


@pytest.fixture(scope="session")
def test_db_url():
    """Create a test database URL."""
    return "sqlite:///./test_awade.db"


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create a test database engine."""
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_user(test_db):
    """Create a sample user for testing."""
    user = User(
        full_name="Test User",
        email="test@example.com",
        password_hash="hashed_password",
        role="EDUCATOR",
        country="Nigeria",
        region="Lagos"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_country(test_db):
    """Create a sample country for testing."""
    country = Country(
        country_name="Test Country",
        iso_code="TC",
        region="Test Region"
    )
    test_db.add(country)
    test_db.commit()
    test_db.refresh(country)
    return country


@pytest.fixture(scope="function")
def sample_curriculum(test_db, sample_country):
    """Create a sample curriculum for testing."""
    curriculum = Curriculum(
        curricula_title="Test Curriculum",
        country_id=sample_country.country_id
    )
    test_db.add(curriculum)
    test_db.commit()
    test_db.refresh(curriculum)
    return curriculum


@pytest.fixture(scope="function")
def sample_subject(test_db):
    """Create a sample subject for testing."""
    subject = Subject(name="Mathematics")
    test_db.add(subject)
    test_db.commit()
    test_db.refresh(subject)
    return subject


@pytest.fixture(scope="function")
def sample_grade_level(test_db):
    """Create a sample grade level for testing."""
    grade_level = GradeLevel(name="Grade 5")
    test_db.add(grade_level)
    test_db.commit()
    test_db.refresh(grade_level)
    return grade_level


@pytest.fixture(scope="function")
def sample_curriculum_structure(test_db, sample_curriculum, sample_subject, sample_grade_level):
    """Create a sample curriculum structure for testing."""
    structure = CurriculumStructure(
        curricula_id=sample_curriculum.curricula_id,
        subject_id=sample_subject.subject_id,
        grade_level_id=sample_grade_level.grade_level_id
    )
    test_db.add(structure)
    test_db.commit()
    test_db.refresh(structure)
    return structure


@pytest.fixture(scope="function")
def sample_topic(test_db, sample_curriculum_structure):
    """Create a sample topic for testing."""
    topic = Topic(
        curriculum_structure_id=sample_curriculum_structure.curriculum_structure_id,
        topic_title="Basic Algebra"
    )
    test_db.add(topic)
    test_db.commit()
    test_db.refresh(topic)
    return topic


@pytest.fixture(scope="function")
def sample_lesson_plan(test_db, sample_topic, sample_user):
    """Create a sample lesson plan for testing."""
    lesson_plan = LessonPlan(
        topic_id=sample_topic.topic_id,
        user_id=sample_user.user_id
    )
    test_db.add(lesson_plan)
    test_db.commit()
    test_db.refresh(lesson_plan)
    return lesson_plan


@pytest.fixture(scope="function")
def data_structure_manager():
    """Create a data structure manager for testing."""
    return DataStructureManager(cache_capacity=100, queue_capacity=50)


@pytest.fixture(scope="function")
def mock_openai():
    """Mock OpenAI API for testing."""
    with patch('packages.ai.gpt_service.openai') as mock:
        mock.OpenAI.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Mock AI response"))]
        )
        yield mock


@pytest.fixture(scope="function")
def mock_google_oauth():
    """Mock Google OAuth for testing."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "aud": "test_client_id",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ.update({
        "DATABASE_URL": "sqlite:///./test_awade.db",
        "SECRET_KEY": "test_secret_key",
        "JWT_SECRET_KEY": "test_jwt_secret",
        "OPENAI_API_KEY": "test_openai_key",
        "GOOGLE_CLIENT_ID": "test_google_client_id",
        "DEBUG": "True",
        "ENVIRONMENT": "testing"
    })


# Test markers
pytestmark = pytest.mark.database
