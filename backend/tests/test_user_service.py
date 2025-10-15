"""Tests for user service."""
import uuid

import pytest

from app.services.user import UserService


class TestUserService:
    """Test user service functionality."""

    def test_user_service_initialization(self):
        """Test user service can be initialized."""
        service = UserService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_service_methods_exist(self):
        """Test all expected methods exist."""
        service = UserService()

        # Check methods exist
        assert hasattr(service, "get_or_create_user")
        assert callable(service.get_or_create_user)

        assert hasattr(service, "add_auth_factor")
        assert callable(service.add_auth_factor)

        assert hasattr(service, "get_user_auth_factors")
        assert callable(service.get_user_auth_factors)
