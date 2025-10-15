"""Tests for WebAuthn service."""

import pytest

from app.services.webauthn import WebAuthnService


class TestWebAuthnService:
    """Test WebAuthn service functionality."""

    def test_webauthn_service_initialization(self):
        """Test WebAuthn service can be initialized."""
        service = WebAuthnService()
        assert service is not None
        assert service.rp_id == "localhost"
        assert service.rp_name == "Glyph"
        assert service.origin == "http://localhost:8000"

    def test_generate_registration_options(self):
        """Test generating registration options."""
        service = WebAuthnService()
        options = service.generate_registration_options(
            user_id="test-user-id", username="testuser", display_name="Test User"
        )

        assert "challenge" in options
        assert "rp" in options
        assert "user" in options
        assert "pubKeyCredParams" in options
        assert "timeout" in options
        assert "authenticatorSelection" in options
        assert "attestation" in options

        # Verify RP details
        assert options["rp"]["id"] == "localhost"
        assert options["rp"]["name"] == "Glyph"

        # Verify user details
        assert options["user"]["name"] == "testuser"
        assert options["user"]["displayName"] == "Test User"

    def test_generate_authentication_options_empty_credentials(self):
        """Test generating authentication options with no credentials."""
        service = WebAuthnService()
        options = service.generate_authentication_options([])

        assert "challenge" in options
        assert "timeout" in options
        assert "rpId" in options
        assert "allowCredentials" in options
        assert "userVerification" in options

        # Should have empty allow credentials
        assert options["allowCredentials"] == []
        assert options["rpId"] == "localhost"

    def test_generate_authentication_options_with_credentials(self):
        """Test generating authentication options with credentials."""
        service = WebAuthnService()
        credentials = [
            {"credential_id": "dGVzdC1jcmVkZW50aWFsLTEtaWQ"},
            {"credential_id": "dGVzdC1jcmVkZW50aWFsLTItaWQ"},
        ]
        options = service.generate_authentication_options(credentials)

        assert "challenge" in options
        assert "allowCredentials" in options
        assert len(options["allowCredentials"]) == 2

        # Verify credential structure
        for cred in options["allowCredentials"]:
            assert "type" in cred
            assert "id" in cred
            assert "transports" in cred

    def test_generate_challenge(self):
        """Test challenge generation."""
        challenge1 = WebAuthnService.generate_challenge()
        challenge2 = WebAuthnService.generate_challenge()

        # Challenges should be strings
        assert isinstance(challenge1, str)
        assert isinstance(challenge2, str)

        # Challenges should be different
        assert challenge1 != challenge2

        # Challenges should be non-empty
        assert len(challenge1) > 0
        assert len(challenge2) > 0

    @pytest.mark.asyncio
    async def test_service_methods_exist(self):
        """Test all expected methods exist."""
        service = WebAuthnService()

        # Check registration methods exist
        assert hasattr(service, "generate_registration_options")
        assert callable(service.generate_registration_options)

        assert hasattr(service, "verify_registration_response")
        assert callable(service.verify_registration_response)

        # Check authentication methods exist
        assert hasattr(service, "generate_authentication_options")
        assert callable(service.generate_authentication_options)

        assert hasattr(service, "verify_authentication_response")
        assert callable(service.verify_authentication_response)

        # Check challenge generation
        assert hasattr(service, "generate_challenge")
        assert callable(service.generate_challenge)
