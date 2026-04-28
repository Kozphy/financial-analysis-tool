"""Decision engine tests for mapping signals to portfolio actions."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.decision_engine import map_signals_to_decision
from financial_analysis_tool.risk_signals import RiskSignal


class DecisionEngineTests(unittest.TestCase):
    """Validate deterministic portfolio decision mapping behavior."""

    def test_high_governance_signal_maps_to_enhanced_due_diligence(self) -> None:
        """Verify high governance risk escalates to enhanced due diligence."""
        signals = [
            RiskSignal(
                company="Test Co",
                year=2025,
                signal_type="WEAK_GOVERNANCE",
                severity="HIGH",
                reason="Governance score is below threshold.",
                metric_value=48.0,
                recommendation="Escalate governance review.",
            )
        ]

        decision = map_signals_to_decision("Test Co", signals)

        self.assertEqual(decision.decision, "ENHANCED_DUE_DILIGENCE")
        self.assertEqual(decision.highest_severity, "HIGH")
        self.assertEqual(decision.signal_count, 1)
        self.assertTrue(decision.key_drivers)

    def test_multiple_high_signals_map_to_reduce_exposure(self) -> None:
        """Verify clustered high-severity signals map to reduced exposure."""
        signals = [
            RiskSignal("Test Co", 2025, "HIGH_CARBON_INTENSITY", "HIGH", "High carbon.", 0.8, "Engage."),
            RiskSignal("Test Co", 2025, "WEAK_GOVERNANCE", "HIGH", "Weak governance.", 48.0, "Review."),
            RiskSignal("Test Co", 2025, "ELEVATED_CONTROVERSY_RISK", "HIGH", "Many controversies.", 4.0, "Escalate."),
        ]

        decision = map_signals_to_decision("Test Co", signals)

        self.assertEqual(decision.decision, "REDUCE_EXPOSURE")
        self.assertEqual(decision.highest_severity, "HIGH")
        self.assertEqual(decision.signal_count, 3)

    def test_no_signals_maps_to_hold(self) -> None:
        """Verify a company with no breached thresholds remains a hold."""
        decision = map_signals_to_decision("Test Co", [])

        self.assertEqual(decision.decision, "HOLD")
        self.assertEqual(decision.highest_severity, "LOW")
        self.assertEqual(decision.signal_count, 0)


if __name__ == "__main__":
    unittest.main()
