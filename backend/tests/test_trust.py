"""Tests for trust signals calculation."""
from datetime import UTC, datetime, timedelta

import pytest

from app.services.trust import TrustCalculator


class TestTrustCalculator:
    """Test trust risk score calculation."""

    def test_empty_signals(self):
        """Test with no trust signals."""
        calc = TrustCalculator()
        score, band = calc.calculate_risk_score([])
        assert score == 0
        assert band == "low"

    def test_no_consented_signals(self, mock_trust_signals):
        """Test with signals but no consent."""
        calc = TrustCalculator()

        signal = mock_trust_signals(
            id="test-1",
            user_id="user-1",
            issuer="https://example.com",
            kind="block",
            count=1,
            weight=1.0,
            independence_factor=1.0,
            credibility=1.0,
            consent_granted=False,
            since=datetime.now(UTC),
        )

        score, band = calc.calculate_risk_score([signal])
        assert score == 0
        assert band == "low"

    def test_single_block_signal(self, mock_trust_signals):
        """Test with single block signal."""
        calc = TrustCalculator()

        signal = mock_trust_signals(
            id="test-1",
            user_id="user-1",
            issuer="https://example.com",
            kind="block",
            count=1,
            weight=1.0,
            independence_factor=1.0,
            credibility=1.0,
            consent_granted=True,
            since=datetime.now(UTC),
        )

        score, band = calc.calculate_risk_score([signal])
        assert score >= 10  # Base weight * 10 scale factor
        assert band in ["low", "medium", "high"]

    def test_multiple_signals(self, mock_trust_signals):
        """Test with multiple trust signals."""
        calc = TrustCalculator()

        signals = [
            mock_trust_signals(
                id="test-1",
                user_id="user-1",
                issuer="https://example.com",
                kind="block",
                count=3,
                weight=1.0,
                independence_factor=1.0,
                credibility=1.0,
                consent_granted=True,
                since=datetime.now(UTC),
            ),
            mock_trust_signals(
                id="test-2",
                user_id="user-1",
                issuer="https://another.com",
                kind="mute",
                count=2,
                weight=1.0,
                independence_factor=1.0,
                credibility=1.0,
                consent_granted=True,
                since=datetime.now(UTC),
            ),
        ]

        score, band = calc.calculate_risk_score(signals)
        assert score > 0
        assert band in ["low", "medium", "high"]

    def test_freshness_decay(self, mock_trust_signals):
        """Test that old signals have less impact."""
        calc = TrustCalculator()

        # Recent signal
        recent = mock_trust_signals(
            id="test-1",
            user_id="user-1",
            issuer="https://example.com",
            kind="block",
            count=1,
            weight=1.0,
            independence_factor=1.0,
            credibility=1.0,
            consent_granted=True,
            since=datetime.now(UTC),
        )

        # Old signal
        old = mock_trust_signals(
            id="test-2",
            user_id="user-1",
            issuer="https://example.com",
            kind="block",
            count=1,
            weight=1.0,
            independence_factor=1.0,
            credibility=1.0,
            consent_granted=True,
            since=datetime.now(UTC) - timedelta(days=200),
        )

        recent_score, _ = calc.calculate_risk_score([recent])
        old_score, _ = calc.calculate_risk_score([old])

        assert recent_score > old_score

    def test_consent_filtering(self, mock_trust_signals):
        """Test consent-based filtering."""
        calc = TrustCalculator()

        signals = [
            mock_trust_signals(
                id="test-1",
                user_id="user-1",
                issuer="https://example.com",
                kind="block",
                count=1,
                weight=1.0,
                independence_factor=1.0,
                credibility=1.0,
                consent_granted=True,
                consent_scope={"block": {"share": True, "issuers": ["https://example.com"]}},
                since=datetime.now(UTC),
            ),
            mock_trust_signals(
                id="test-2",
                user_id="user-1",
                issuer="https://other.com",
                kind="block",
                count=1,
                weight=1.0,
                independence_factor=1.0,
                credibility=1.0,
                consent_granted=True,
                consent_scope={"block": {"share": False}},
                since=datetime.now(UTC),
            ),
        ]

        filtered = calc.filter_by_consent(signals, issuer="https://example.com")
        assert len(filtered) == 1
        assert filtered[0].issuer == "https://example.com"
