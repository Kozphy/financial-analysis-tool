"""Portfolio ranking tests for severity and signal-count ordering."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.api import services
from financial_analysis_tool.risk_signals import RiskSignal


class PortfolioRankingTests(unittest.TestCase):
    """Validate portfolio ranking service behavior independent of FastAPI."""

    def test_portfolio_ranking_orders_by_severity_then_signal_count(self) -> None:
        """Verify HIGH ranks before MEDIUM before LOW with signal-count tie breaks."""
        signal_map = {
            "Low Co": [],
            "Medium Co": [
                RiskSignal("Medium Co", 2025, "HIGH_CARBON_INTENSITY", "MEDIUM", "Medium risk.", 1.0, "Review.")
            ],
            "High One Signal Co": [
                RiskSignal("High One Signal Co", 2025, "WEAK_GOVERNANCE", "HIGH", "High risk.", 1.0, "Review.")
            ],
            "High Two Signals Co": [
                RiskSignal("High Two Signals Co", 2025, "WEAK_GOVERNANCE", "HIGH", "High risk.", 1.0, "Review."),
                RiskSignal(
                    "High Two Signals Co",
                    2025,
                    "ELEVATED_CONTROVERSY_RISK",
                    "HIGH",
                    "High risk.",
                    2.0,
                    "Escalate.",
                ),
            ],
        }

        with patch.object(services, "list_companies", return_value=list(signal_map)):
            with patch.object(services, "_build_signals", side_effect=lambda company: signal_map[company]):
                ranking = services.get_portfolio_ranking()

        companies = ranking["companies"]
        self.assertEqual(
            [item["company"] for item in companies],
            ["High Two Signals Co", "High One Signal Co", "Medium Co", "Low Co"],
        )
        self.assertEqual([item["rank"] for item in companies], [1, 2, 3, 4])
        self.assertEqual(companies[0]["highest_severity"], "HIGH")
        self.assertEqual(companies[0]["signal_count"], 2)
        self.assertEqual(companies[0]["alert_level"], "CRITICAL")
        self.assertEqual(companies[-1]["alert_level"], "NORMAL")


if __name__ == "__main__":
    unittest.main()
