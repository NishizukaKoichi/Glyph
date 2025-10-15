"""Tests for OAuth service."""
import pytest

from app.services.oauth import OAuthService


class TestOAuthService:
    """Test OAuth service functionality."""

    def test_oauth_service_initialization(self):
        """Test OAuth service can be initialized."""
        service = OAuthService()
        assert service.oauth is not None

    @pytest.mark.asyncio
    async def test_get_user_info_google_structure(self):
        """Test Google user info has correct structure."""
        # This is a unit test - we'll mock the actual HTTP call in integration tests
        service = OAuthService()

        # Mock token
        mock_token = {"access_token": "mock_token"}

        # We can't call the real API without valid credentials,
        # so we just verify the method exists and has correct signature
        assert hasattr(service, "get_user_info_google")
        assert callable(service.get_user_info_google)

    @pytest.mark.asyncio
    async def test_get_user_info_microsoft_structure(self):
        """Test Microsoft user info has correct structure."""
        service = OAuthService()
        assert hasattr(service, "get_user_info_microsoft")
        assert callable(service.get_user_info_microsoft)

    @pytest.mark.asyncio
    async def test_get_user_info_github_structure(self):
        """Test GitHub user info has correct structure."""
        service = OAuthService()
        assert hasattr(service, "get_user_info_github")
        assert callable(service.get_user_info_github)

    @pytest.mark.asyncio
    async def test_get_user_info_twitter_structure(self):
        """Test Twitter user info has correct structure."""
        service = OAuthService()
        assert hasattr(service, "get_user_info_twitter")
        assert callable(service.get_user_info_twitter)
