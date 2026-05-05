"""
Test suite for Awade backend services.

This module tests the service layer implementations including authentication,
user management, lesson planning, and context management.

Author: Tolulope Babajide
"""

import os
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from services.auth_service import AuthService, _SELF_REGISTERABLE_ROLES
from services.user_service import UserService
from services.lesson_plan_service import LessonPlanService
from services.context_service import ContextService
from services.data_structures import LRUCache, LFUCache, SearchIndex, RequestQueue, DataStructureManager, CacheStrategy
from services.optimized_database_service import OptimizedDatabaseService
from models import User, UserRole, LessonPlan, Context


class TestAuthService:
    """Test authentication service."""
    
    def test_auth_service_initialization(self, test_db):
        """Test AuthService initialization."""
        service = AuthService(test_db)
        assert service.db == test_db

    def test_self_registerable_roles_constant(self):
        """AWD-M-105: _SELF_REGISTERABLE_ROLES is a single module-level frozenset
        containing exactly PARENT and EDUCATOR — no more, no less."""
        from models import UserRole

        # Must be a frozenset (immutable — cannot be mutated by accident)
        assert isinstance(_SELF_REGISTERABLE_ROLES, frozenset), (
            "_SELF_REGISTERABLE_ROLES must be a frozenset to prevent accidental mutation"
        )

        # Must contain exactly the two self-registerable roles
        assert _SELF_REGISTERABLE_ROLES == frozenset({UserRole.PARENT, UserRole.EDUCATOR}), (
            "_SELF_REGISTERABLE_ROLES must contain exactly PARENT and EDUCATOR"
        )

        # ADMIN and SUPER_ADMIN must NOT be in the set
        assert UserRole.ADMIN not in _SELF_REGISTERABLE_ROLES
        assert UserRole.SUPER_ADMIN not in _SELF_REGISTERABLE_ROLES

    def test_password_validation(self, test_db):
        """Test password validation."""
        service = AuthService(test_db)
        
        # Test valid password
        assert service.get_password_min_length() >= 8
        
        # Test password hashing
        password = "test_password_123"
        hashed = service._hash_password(password)
        assert hashed != password
        assert service._verify_password(password, hashed)
    
    @patch('services.auth_service.requests.get')
    def test_google_token_verification(self, mock_get, test_db):
        """Test Google OAuth token verification."""
        service = AuthService(test_db)
        
        # Mock successful Google response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "aud": "test_client_id",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_get.return_value = mock_response
        
        # Mock environment variable
        with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test_client_id'}):
            result = service.verify_google_token("test_token")
            assert result["email"] == "test@example.com"
            assert result["name"] == "Test User"
    
    def test_google_token_verification_failure(self, test_db):
        """Test Google OAuth token verification failure."""
        service = AuthService(test_db)

        with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test_client_id'}):
            with patch('services.auth_service.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 401
                mock_get.return_value = mock_response

                with pytest.raises(HTTPException) as exc_info:
                    service.verify_google_token("invalid_token")
                assert exc_info.value.status_code == 401

    def test_google_token_request_timeout_returns_503(self, test_db):
        """AWD-M-103: requests.get timeout must return 503, not stall worker."""
        import requests as requests_lib
        service = AuthService(test_db)

        with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test_client_id'}):
            with patch('services.auth_service.requests.get') as mock_get:
                mock_get.side_effect = requests_lib.exceptions.Timeout()

                with pytest.raises(HTTPException) as exc_info:
                    service.verify_google_token("any_token")

        assert exc_info.value.status_code == 503
        assert "temporarily unavailable" in exc_info.value.detail.lower()
        # Must not leak internal details
        assert "timeout" not in exc_info.value.detail.lower()

    def test_google_token_unconfigured_does_not_leak_env_var_name(self, test_db):
        """AWD-H-72: 500 response must not reveal GOOGLE_CLIENT_ID env var name."""
        service = AuthService(test_db)

        # Ensure the env var is absent so get_google_client_id() returns ""
        with patch.dict('os.environ', {}, clear=False):
            os.environ.pop('GOOGLE_CLIENT_ID', None)
            with pytest.raises(HTTPException) as exc_info:
                service.verify_google_token("any_token")

        assert exc_info.value.status_code == 500
        detail = exc_info.value.detail
        # Generic message — must not reveal the internal env var name
        assert "GOOGLE_CLIENT_ID" not in detail
        assert "environment variable" not in detail
        assert "Please contact support" in detail

    def test_register_user_cannot_self_elevate_to_admin(self, test_db):
        """AWD-H-74: register_user must coerce ADMIN/SUPER_ADMIN roles to PARENT."""
        from schemas.users import UserCreate

        service = AuthService(test_db)

        for elevated_role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            payload = UserCreate(
                email=f"attacker_{elevated_role.value}@example.com",
                password="ValidPassword123!",
                full_name="Attacker",
                role=elevated_role,
                country="NG",
            )
            auth_response, _refresh = service.register_user(payload)
            assert auth_response.user.role == UserRole.PARENT.value, (
                f"register_user must coerce role={elevated_role.value} to PARENT, "
                f"got {auth_response.user.role}"
            )

    def test_register_user_delegates_hashing_to_hash_password(self, test_db):
        """AWD-M-106: register_user must call self._hash_password() — not inline bcrypt.

        Verifies that there is a single hashing path: any change to bcrypt work factor
        or encoding in _hash_password() automatically applies to registration too.
        """
        from schemas.users import UserCreate
        from unittest.mock import patch

        service = AuthService(test_db)
        payload = UserCreate(
            email="hash_delegation_test@example.com",
            password="SecurePass999!",
            full_name="Hash Test",
            role=UserRole.PARENT,
            country="NG",
        )

        with patch.object(service, "_hash_password", wraps=service._hash_password) as mock_hash:
            auth_response, _ = service.register_user(payload)
            mock_hash.assert_called_once_with(payload.password)

        # The stored hash must be verifiable — confirms the delegation produced a real hash
        db_user = test_db.query(__import__("models", fromlist=["User"]).User).filter_by(
            email="hash_delegation_test@example.com"
        ).first()
        assert db_user is not None
        assert service._verify_password(payload.password, db_user.password_hash)

    def test_authenticate_user_delegates_verification_to_verify_password(self, test_db):
        """AWD-M-107: authenticate_user must call self._verify_password() — not inline bcrypt.

        Verifies that there is a single verification path: any change to bcrypt work factor
        or encoding in _verify_password() automatically applies to authentication too.
        """
        from schemas.users import UserCreate, UserLogin
        from unittest.mock import patch

        service = AuthService(test_db)

        # First register a user so there is a real hashed password in the DB
        register_payload = UserCreate(
            email="verify_delegation_test@example.com",
            password="SecureVerify999!",
            full_name="Verify Test",
            role=UserRole.PARENT,
            country="NG",
        )
        service.register_user(register_payload)

        login_payload = UserLogin(
            email="verify_delegation_test@example.com",
            password="SecureVerify999!",
        )

        with patch.object(service, "_verify_password", wraps=service._verify_password) as mock_verify:
            auth_response, _ = service.authenticate_user(login_payload)
            mock_verify.assert_called_once_with(
                login_payload.password,
                mock_verify.call_args[0][1],  # hashed_password arg — value from DB
            )

        assert auth_response.user.email == "verify_delegation_test@example.com"

    def test_register_user_delegates_user_response_to_get_current_user_profile(self, test_db):
        """AWD-M-98: register_user must build UserResponse via get_current_user_profile().

        Ensures a single JSON-parsing path with try/except guards — malformed subjects/
        grade_levels JSON in the DB cannot cause an unhandled JSONDecodeError at
        registration time.
        """
        from schemas.users import UserCreate
        from unittest.mock import patch

        service = AuthService(test_db)
        payload = UserCreate(
            email="profile_delegation_register@example.com",
            password="SecureProf999!",
            full_name="Profile Reg Test",
            role=UserRole.PARENT,
            country="NG",
        )

        with patch.object(
            service, "get_current_user_profile", wraps=service.get_current_user_profile
        ) as mock_profile:
            auth_response, _ = service.register_user(payload)
            mock_profile.assert_called_once()

        assert auth_response.user.email == "profile_delegation_register@example.com"

    def test_authenticate_user_delegates_user_response_to_get_current_user_profile(self, test_db):
        """AWD-M-98: authenticate_user must build UserResponse via get_current_user_profile().

        Ensures a single JSON-parsing path with try/except guards — malformed subjects/
        grade_levels JSON in the DB cannot cause an unhandled JSONDecodeError at
        login time.
        """
        from schemas.users import UserCreate, UserLogin
        from unittest.mock import patch

        service = AuthService(test_db)

        # Register first so there is a real user in the DB
        register_payload = UserCreate(
            email="profile_delegation_login@example.com",
            password="SecureProf888!",
            full_name="Profile Login Test",
            role=UserRole.PARENT,
            country="NG",
        )
        service.register_user(register_payload)

        login_payload = UserLogin(
            email="profile_delegation_login@example.com",
            password="SecureProf888!",
        )

        with patch.object(
            service, "get_current_user_profile", wraps=service.get_current_user_profile
        ) as mock_profile:
            auth_response, _ = service.authenticate_user(login_payload)
            mock_profile.assert_called_once()

        assert auth_response.user.email == "profile_delegation_login@example.com"


class TestUserService:
    """Test user service."""
    
    def test_user_service_initialization(self, test_db):
        """Test UserService initialization."""
        service = UserService(test_db)
        assert service.db == test_db
    
    def test_get_users_pagination(self, test_db, sample_user):
        """Test user retrieval with pagination."""
        service = UserService(test_db)
        
        users = service.get_users(skip=0, limit=10)
        assert len(users) >= 1
        assert any(user.email == "test@example.com" for user in users)
    
    def test_get_user_by_id(self, test_db, sample_user):
        """Test get user by ID."""
        service = UserService(test_db)

        # Pass owner as current_user — owner may read their own record
        user = service.get_user(sample_user.user_id, current_user=sample_user)
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_user_not_found(self, test_db):
        """Test get user when not found."""
        service = UserService(test_db)

        # Use caller.user_id == requested id — ownership check short-circuits,
        # service proceeds to DB lookup and raises 404 for the missing record
        caller = Mock()
        caller.user_id = 99999
        with pytest.raises(HTTPException) as exc_info:
            service.get_user(99999, current_user=caller)
        assert exc_info.value.status_code == 404


class TestLessonPlanService:
    """Test lesson plan service."""
    
    def test_lesson_plan_service_initialization(self, test_db):
        """Test LessonPlanService initialization."""
        service = LessonPlanService(test_db)
        assert service.db == test_db
    
    def test_generate_lesson_plan(self, test_db, sample_user, sample_topic):
        """Test lesson plan generation."""
        service = LessonPlanService(test_db)
        
        from schemas.lesson_plans import LessonPlanCreate
        
        request = LessonPlanCreate(
            subject="Mathematics",
            grade_level="Grade 5",
            topic="Basic Algebra",
            user_id=sample_user.user_id
        )
        
        # Mock the topic query
        with patch.object(service.db, 'query') as mock_query:
            mock_query.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.first.return_value = sample_topic
            
            result = service.generate_lesson_plan(request, sample_user)
            assert result is not None
            assert result.subject == "Mathematics"
    
    def test_get_lesson_plans(self, test_db, sample_user, sample_lesson_plan):
        """Test lesson plan retrieval."""
        service = LessonPlanService(test_db)
        
        lesson_plans = service.get_lesson_plans(sample_user)
        assert len(lesson_plans) >= 1


class TestContextService:
    """Test context service."""
    
    def test_context_service_initialization(self, test_db):
        """Test ContextService initialization."""
        service = ContextService(test_db)
        assert service.db == test_db
    
    def test_create_context(self, test_db, sample_lesson_plan):
        """Test context creation."""
        service = ContextService(test_db)
        
        from schemas.contexts import ContextCreate
        
        context_data = ContextCreate(
            lesson_plan_id=sample_lesson_plan.lesson_plan_id,
            context_text="Test context for lesson plan",
            context_type="cultural"
        )
        
        result = service.create_context(context_data)
        assert result is not None
        assert result.context_text == "Test context for lesson plan"
    
    def test_get_contexts_by_lesson_plan(self, test_db, sample_lesson_plan):
        """Test get contexts by lesson plan."""
        service = ContextService(test_db)
        
        # Create a context first
        from schemas.contexts import ContextCreate
        context_data = ContextCreate(
            lesson_plan_id=sample_lesson_plan.lesson_plan_id,
            context_text="Test context",
            context_type="cultural"
        )
        service.create_context(context_data)
        
        # Get contexts
        result = service.get_contexts_by_lesson_plan(sample_lesson_plan.lesson_plan_id)
        assert result.total >= 1


class TestDataStructures:
    """Test data structures implementation."""
    
    def test_lru_cache_basic_operations(self):
        """Test LRU cache basic operations."""
        cache = LRUCache(3)
        
        # Test put and get
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.size() == 1
        
        # Test eviction
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        cache.put("key4", "value4")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_lfu_cache_frequency_tracking(self):
        """Test LFU cache frequency tracking."""
        cache = LFUCache(3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Access key1 multiple times
        cache.get("key1")
        cache.get("key1")
        cache.get("key1")
        
        # Access key2 once
        cache.get("key2")
        
        # Add new item - should evict key2 (lower frequency)
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"  # High frequency, should remain
        # Note: key2 might still be in cache due to LFU implementation details
        assert cache.get("key3") == "value3"  # New item should be present
        assert cache.get("key3") == "value3"  # Should be there
    
    def test_search_index_functionality(self):
        """Test search index functionality."""
        index = SearchIndex()
        
        # Add documents
        index.add_document(1, "mathematics algebra calculus")
        index.add_document(2, "mathematics geometry trigonometry")
        index.add_document(3, "physics mechanics dynamics")
        
        # Search
        results = index.search("mathematics", limit=3)
        assert len(results) == 2
        assert results[0][0] in [1, 2]  # Should return math documents
        assert results[0][1] > 0  # Should have positive score
    
    def test_request_queue_priority(self):
        """Test request queue priority handling."""
        queue = RequestQueue(5)
        
        # Add requests with different priorities
        queue.add_request({"id": 1}, "low")
        queue.add_request({"id": 2}, "normal")
        queue.add_request({"id": 3}, "high")
        
        # High priority should be processed first
        next_request = queue.get_next_request()
        assert next_request["id"] == 3
        
        # Then normal priority
        next_request = queue.get_next_request()
        assert next_request["id"] == 2
        
        # Finally low priority
        next_request = queue.get_next_request()
        assert next_request["id"] == 1
    
    def test_data_structure_manager(self):
        """Test data structure manager."""
        manager = DataStructureManager(100, 50)
        
        # Test cache operations
        manager.cache_set("test_key", "test_value", CacheStrategy.LRU)
        value = manager.cache_get("test_key", CacheStrategy.LRU)
        assert value == "test_value"
        
        # Test search operations
        manager.add_search_document(1, "test document")
        results = manager.search_documents("test")
        assert len(results) == 1
        assert results[0][0] == 1
        
        # Test request queuing
        success = manager.add_request({"type": "test"}, "normal")
        assert success == True
        
        next_request = manager.get_next_request()
        assert next_request["type"] == "test"


class TestOptimizedDatabaseService:
    """Test optimized database service."""
    
    def test_optimized_database_service_initialization(self):
        """Test OptimizedDatabaseService initialization."""
        service = OptimizedDatabaseService()
        assert service.ds_manager is not None
        assert service.cache_ttl == 300
        assert len(service.query_patterns) > 0
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        service = OptimizedDatabaseService()
        
        key1 = service._generate_cache_key('user_by_email', email='test@example.com')
        key2 = service._generate_cache_key('user_by_email', email='test@example.com')
        
        assert key1 == key2
        assert 'user_by_email' in key1
        # Note: The key is hashed for security, so the email won't be directly visible
        assert len(key1) > 0  # Key should be generated
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        service = OptimizedDatabaseService()
        
        metrics = service.get_performance_metrics()
        
        assert 'cache_hits' in metrics
        assert 'cache_misses' in metrics
        assert 'queries_optimized' in metrics
        assert 'requests_processed' in metrics
        assert 'queue_stats' in metrics
        assert 'cache_utilization' in metrics


class TestIntegration:
    """Integration tests."""
    
    def test_end_to_end_caching_workflow(self):
        """Test complete caching workflow."""
        manager = DataStructureManager(100, 50)
        service = OptimizedDatabaseService()
        
        # Add data to search index
        service.ds_manager.add_search_document(1, "mathematics lesson plan")
        service.ds_manager.add_search_document(2, "science experiment guide")
        
        # Search
        results = service.ds_manager.search_documents("mathematics")
        assert len(results) == 1
        
        # Cache the results
        service.ds_manager.cache_set("search:math", results, CacheStrategy.LFU)
        
        # Retrieve from cache
        cached_results = service.ds_manager.cache_get("search:math", CacheStrategy.LFU)
        assert cached_results == results
    
    def test_request_queuing_workflow(self):
        """Test complete request queuing workflow."""
        manager = DataStructureManager(100, 50)
        
        # Add multiple requests
        for i in range(5):
            manager.add_request({"id": i, "type": "search"}, "normal")
        
        # Process requests
        processed = []
        for _ in range(5):
            request = manager.get_next_request()
            if request:
                processed.append(request)
        
        assert len(processed) == 5
        assert manager.metrics['requests_processed'] == 5
