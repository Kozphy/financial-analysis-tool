"""Audit log tests for decision recommendation history."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.decision_audit import write_decision_audit_record


class DecisionAuditTests(unittest.TestCase):
    """Validate append-only JSONL audit logging for decisions."""

    def test_write_decision_audit_record_creates_jsonl_entry(self) -> None:
        """Verify the audit writer creates parent directories and appends JSON."""
        decision = {
            "company": "Harbor Cement",
            "decision": "REDUCE_EXPOSURE",
            "highest_severity": "HIGH",
            "signal_count": 4,
            "key_drivers": ["HIGH_CARBON_INTENSITY: High emissions intensity."],
            "rationale": "Multiple high-severity signals indicate concentrated downside risk.",
        }
        timestamp = datetime(2026, 4, 28, 12, 0, tzinfo=timezone.utc)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "logs" / "decision_history.jsonl"

            record = write_decision_audit_record(
                decision,
                output_path=output_path,
                timestamp=timestamp,
            )

            self.assertTrue(output_path.exists())
            lines = output_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            payload = json.loads(lines[0])
            self.assertEqual(payload, record)
            self.assertEqual(payload["timestamp"], "2026-04-28T12:00:00+00:00")
            self.assertEqual(payload["company"], "Harbor Cement")
            self.assertEqual(payload["decision"], "REDUCE_EXPOSURE")


if __name__ == "__main__":
    unittest.main()
