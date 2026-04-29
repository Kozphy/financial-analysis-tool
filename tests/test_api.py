"""API contract tests for the FastAPI delivery layer.

These tests verify that the HTTP surface exposes healthy service metadata,
company discovery, explainable risk signals, and expected error handling.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

HAS_API_STACK = all(
    importlib.util.find_spec(module_name) is not None
    for module_name in ("fastapi", "httpx", "pandas", "numpy")
)

if HAS_API_STACK:
    from fastapi.testclient import TestClient

    from financial_analysis_tool.api import services
    from financial_analysis_tool.api.app import app


@unittest.skipUnless(HAS_API_STACK, "API dependencies are not installed in this environment.")
class ApiTests(unittest.TestCase):
    """Validate API endpoints without starting an external web server."""

    def setUp(self) -> None:
        """Create a FastAPI test client for each API test."""
        self.client = TestClient(app)

    def test_health_returns_ok(self) -> None:
        """Verify the health endpoint returns service metadata and OK status."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "OK")
        self.assertEqual(payload["service"], "Financial ESG Risk Intelligence API")

    def test_companies_returns_non_empty_list(self) -> None:
        """Verify the companies endpoint exposes the sample coverage universe."""
        response = self.client.get("/companies")

        self.assertEqual(response.status_code, 200)
        companies = response.json()["companies"]
        self.assertGreater(len(companies), 0)
        self.assertIn("Harbor Cement", companies)

    def test_unknown_company_returns_404(self) -> None:
        """Verify unknown companies are mapped to an HTTP 404 response."""
        response = self.client.get("/signals/Unknown%20Company")

        self.assertEqual(response.status_code, 404)

    def test_signals_returns_explainable_signals(self) -> None:
        """Verify signal responses include reasons, recommendations, and severity."""
        response = self.client.get("/signals/Harbor%20Cement")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["company"], "Harbor Cement")
        self.assertGreater(len(payload["signals"]), 0)
        first_signal = payload["signals"][0]
        self.assertIn("reason", first_signal)
        self.assertIn("recommendation", first_signal)
        self.assertIn(first_signal["severity"], {"LOW", "MEDIUM", "HIGH"})

    def test_invalid_pipeline_mode_returns_400(self) -> None:
        """Verify invalid pipeline modes are rejected with an HTTP 400 response."""
        response = self.client.post("/pipeline/run", json={"mode": "invalid"})

        self.assertEqual(response.status_code, 400)

    def test_decision_endpoint_writes_audit_log_record(self) -> None:
        """Verify decision requests append one JSONL audit record."""
        original_path = services.DECISION_HISTORY_PATH

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_path = Path(temp_dir) / "logs" / "decision_history.jsonl"
            services.DECISION_HISTORY_PATH = audit_path
            try:
                response = self.client.get("/decisions/Harbor%20Cement")
            finally:
                services.DECISION_HISTORY_PATH = original_path

            self.assertEqual(response.status_code, 200)
            decision = response.json()
            lines = audit_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            audit_record = json.loads(lines[0])
            self.assertIn("timestamp", audit_record)
            self.assertEqual(audit_record["company"], decision["company"])
            self.assertEqual(audit_record["decision"], decision["decision"])
            self.assertEqual(audit_record["highest_severity"], decision["highest_severity"])
            self.assertEqual(audit_record["signal_count"], decision["signal_count"])
            self.assertEqual(audit_record["key_drivers"], decision["key_drivers"])
            self.assertEqual(audit_record["rationale"], decision["rationale"])

    def test_portfolio_ranking_returns_expected_schema(self) -> None:
        """Verify portfolio ranking exposes dashboard-ready fields."""
        response = self.client.get("/portfolio/ranking")

        self.assertEqual(response.status_code, 200)
        companies = response.json()["companies"]
        self.assertGreater(len(companies), 0)
        first_item = companies[0]
        self.assertEqual(
            set(first_item),
            {
                "rank",
                "company",
                "decision",
                "highest_severity",
                "signal_count",
                "top_drivers",
                "alert_level",
            },
        )
        self.assertIsInstance(first_item["rank"], int)
        self.assertIsInstance(first_item["top_drivers"], list)
        self.assertIn(first_item["highest_severity"], {"LOW", "MEDIUM", "HIGH"})


if __name__ == "__main__":
    unittest.main()
