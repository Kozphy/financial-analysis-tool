from __future__ import annotations

from typing import Protocol

from ..models import PriceRecord


class PriceSource(Protocol):
    def load_records(self) -> list[PriceRecord]:
        """Load canonical price records from a specific data source."""
