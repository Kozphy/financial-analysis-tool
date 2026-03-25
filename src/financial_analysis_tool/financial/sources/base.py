from __future__ import annotations

from typing import Protocol

from ..models import FinancialRecord


class FinancialSource(Protocol):
    def load_records(self) -> list[FinancialRecord]:
        """Load canonical financial records from a specific data source."""
