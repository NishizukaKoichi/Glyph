"""Pytest configuration and fixtures."""
import pytest


@pytest.fixture
def mock_auth_factors():
    """Provide mock auth factors for testing without database."""
    from datetime import UTC, datetime

    class MockAuthFactor:
        def __init__(self, **kwargs):
            self.id = kwargs.get("id", "test-1")
            self.user_id = kwargs.get("user_id", "user-1")
            self.factor_type = kwargs.get("factor_type", "webauthn")
            self.provider = kwargs.get("provider")
            self.provider_user_id = kwargs.get("provider_user_id")
            self.base_weight = kwargs.get("base_weight", 0)
            self.independence_factor = kwargs.get("independence_factor", 1.0)
            self.extra_data = kwargs.get("extra_data", {})
            self.last_used_at = kwargs.get("last_used_at")
            self.created_at = kwargs.get("created_at", datetime.now(UTC))
            self.updated_at = kwargs.get("updated_at", datetime.now(UTC))

    return MockAuthFactor


@pytest.fixture
def mock_trust_signals():
    """Provide mock trust signals for testing without database."""
    from datetime import UTC, datetime

    class MockTrustSignal:
        def __init__(self, **kwargs):
            self.id = kwargs.get("id", "test-1")
            self.user_id = kwargs.get("user_id", "user-1")
            self.issuer = kwargs.get("issuer", "https://example.com")
            self.kind = kwargs.get("kind", "block")
            self.count = kwargs.get("count", 1)
            self.weight = kwargs.get("weight", 1.0)
            self.independence_factor = kwargs.get("independence_factor", 1.0)
            self.credibility = kwargs.get("credibility", 1.0)
            self.jws = kwargs.get("jws")
            self.consent_granted = kwargs.get("consent_granted", False)
            self.consent_scope = kwargs.get("consent_scope", {})
            self.extra_data = kwargs.get("extra_data", {})
            self.since = kwargs.get("since", datetime.now(UTC))
            self.expires_at = kwargs.get("expires_at")
            self.created_at = kwargs.get("created_at", datetime.now(UTC))
            self.updated_at = kwargs.get("updated_at", datetime.now(UTC))

    return MockTrustSignal
