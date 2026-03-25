from __future__ import annotations

from pathlib import Path

from .helpers import load_csv_price_records


class CSVPriceSource:
    def __init__(self, csv_path: str | Path) -> None:
        self._path = Path(csv_path)

    def load_records(self):
        return load_csv_price_records(self._path)
