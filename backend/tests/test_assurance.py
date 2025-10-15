"""Tests for assurance score calculation."""
from datetime import UTC, datetime, timedelta

import pytest

from app.services.assurance import AssuranceCalculator


class TestAssuranceCalculator:
    """Test assurance score calculation."""

    def test_empty_factors(self):
        """Test with no authentication factors."""
        calc = AssuranceCalculator()
        score, level = calc.calculate_score([])
        assert score == 0
        assert level == "alpha"

    def test_single_webauthn_factor(self, mock_auth_factors):
        """Test with single WebAuthn factor."""
        calc = AssuranceCalculator()

        factor = mock_auth_factors(
            id="test-1",
            user_id="user-1",
            factor_type="webauthn",
            base_weight=35,
            independence_factor=1.0,
            last_used_at=datetime.now(UTC),
        )

        score, level = calc.calculate_score([factor])
        assert score >= 35
        assert level in ["alpha", "beta", "gamma"]

    def test_multiple_factors(self, mock_auth_factors):
        """Test with multiple authentication factors."""
        calc = AssuranceCalculator()

        factors = [
            mock_auth_factors(
                id="test-1",
                user_id="user-1",
                factor_type="webauthn",
                base_weight=35,
                independence_factor=1.0,
                last_used_at=datetime.now(UTC),
            ),
            mock_auth_factors(
                id="test-2",
                user_id="user-1",
                factor_type="google",
                base_weight=25,
                independence_factor=1.0,
                last_used_at=datetime.now(UTC) - timedelta(days=5),
            ),
        ]

        score, level = calc.calculate_score(factors)
        assert score >= 55  # 35 + 25 * 0.95 (freshness)
        assert level in ["alpha", "beta"]  # Should be alpha (< 70) or beta if score reaches 70

    def test_freshness_decay(self, mock_auth_factors):
        """Test that freshness affects score."""
        calc = AssuranceCalculator()

        # Recent factor
        recent = mock_auth_factors(
            id="test-1",
            user_id="user-1",
            factor_type="google",
            base_weight=25,
            independence_factor=1.0,
            last_used_at=datetime.now(UTC),
        )

        # Old factor
        old = mock_auth_factors(
            id="test-2",
            user_id="user-1",
            factor_type="google",
            base_weight=25,
            independence_factor=1.0,
            last_used_at=datetime.now(UTC) - timedelta(days=100),
        )

        recent_score, _ = calc.calculate_score([recent])
        old_score, _ = calc.calculate_score([old])

        assert recent_score > old_score

    def test_gamma_level_requirements(self, mock_auth_factors):
        """Test gamma level requires recent WebAuthn."""
        calc = AssuranceCalculator()

        # High score but no WebAuthn
        factors_no_webauthn = [
            mock_auth_factors(
                id="test-1",
                user_id="user-1",
                factor_type="google",
                base_weight=25,
                independence_factor=1.0,
                last_used_at=datetime.now(UTC),
            ),
            mock_auth_factors(
                id="test-2",
                user_id="user-1",
                factor_type="microsoft",
                base_weight=25,
                independence_factor=1.0,
                last_used_at=datetime.now(UTC),
            ),
            mock_auth_factors(
                id="test-3",
                user_id="user-1",
                factor_type="kyc",
                base_weight=40,
                independence_factor=1.0,
                last_used_at=datetime.now(UTC),
            ),
        ]

        score, level = calc.calculate_score(factors_no_webauthn)
        assert score >= 85
        assert level != "gamma"  # Should be beta, not gamma

        # High score with recent WebAuthn
        factors_with_webauthn = factors_no_webauthn + [
            mock_auth_factors(
                id="test-4",
                user_id="user-1",
                factor_type="webauthn",
                base_weight=35,
                independence_factor=1.0,
                last_used_at=datetime.now(UTC),
            )
        ]

        score, level = calc.calculate_score(factors_with_webauthn)
        assert score >= 85
        assert level == "gamma"
