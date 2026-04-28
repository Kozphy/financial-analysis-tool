"""Risk signal tests for explainability and deterministic business rules."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.risk_signals import build_esg_risk_signals


class RiskSignalTests(unittest.TestCase):
    """Validate ESG signal generation independent of the API layer."""

    def test_build_esg_risk_signals_returns_explainable_signals(self) -> None:
        """Verify high-risk ESG rows produce reasoned, actionable signals."""
        rows = [
            {
                "company": "High Risk Co",
                "year": 2024,
                "carbon_intensity": 0.80,
                "governance_score": 48,
                "controversy_count": 4,
                "renewable_energy_pct": 12,
                "green_capex_pct": 4,
                "esg_score_change": 1.0,
            },
            {
                "company": "Peer Co",
                "year": 2024,
                "carbon_intensity": 0.20,
                "governance_score": 80,
                "controversy_count": 0,
                "renewable_energy_pct": 60,
                "green_capex_pct": 14,
                "esg_score_change": 2.0,
            },
        ]

        signals = build_esg_risk_signals("High Risk Co", rows)

        signal_types = {signal.signal_type for signal in signals}
        self.assertIn("HIGH_CARBON_INTENSITY", signal_types)
        self.assertIn("WEAK_GOVERNANCE", signal_types)
        self.assertIn("ELEVATED_CONTROVERSY_RISK", signal_types)
        self.assertIn("TRANSITION_RISK_WATCHLIST", signal_types)
        self.assertTrue(all(signal.reason for signal in signals))
        self.assertTrue(all(signal.recommendation for signal in signals))

    def test_build_esg_risk_signals_is_deterministic(self) -> None:
        """Verify repeated signal generation returns identical payloads."""
        rows = [
            {
                "company": "High Risk Co",
                "year": 2024,
                "carbon_intensity": 0.80,
                "governance_score": 48,
                "controversy_count": 4,
                "renewable_energy_pct": 12,
                "green_capex_pct": 4,
                "esg_score_change": 1.0,
            },
            {
                "company": "Peer Co",
                "year": 2024,
                "carbon_intensity": 0.20,
                "governance_score": 80,
                "controversy_count": 0,
                "renewable_energy_pct": 60,
                "green_capex_pct": 14,
                "esg_score_change": 2.0,
            },
        ]

        first = [signal.to_dict() for signal in build_esg_risk_signals("High Risk Co", rows)]
        second = [signal.to_dict() for signal in build_esg_risk_signals("High Risk Co", rows)]

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
