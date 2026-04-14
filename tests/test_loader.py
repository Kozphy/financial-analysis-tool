from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.loader import (
    load_financial_statements,
    load_financial_statements_from_text,
)


class LoaderTests(unittest.TestCase):
    def test_load_financial_statements_reads_sample_data(self) -> None:
        records = load_financial_statements(PROJECT_ROOT / "data" / "financials.csv")

        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].period, "2024-Q1")
        self.assertEqual(records[-1].period, "2025-Q4")
        self.assertEqual(records[-1].current_assets, 1_205_000.0)

    def test_load_financial_statements_from_text_sorts_periods(self) -> None:
        csv_text = "\n".join(
            [
                "period,revenue,cost_of_revenue,operating_expenses,net_income,current_assets,current_liabilities,total_assets,total_liabilities",
                "2025-Q2,100,40,20,10,60,30,120,50",
                "2025-Q1,90,35,20,8,58,29,118,52",
            ]
        )

        records = load_financial_statements_from_text(csv_text)

        self.assertEqual([record.period for record in records], ["2025-Q1", "2025-Q2"])


if __name__ == "__main__":
    unittest.main()
