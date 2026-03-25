from __future__ import annotations

import logging
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode

from financial_analysis_tool.core.exceptions import InputDataError, MOPSAPIError
from financial_analysis_tool.core.http import request_text

from ..models import FinancialRecord


LOGGER = logging.getLogger(__name__)
MOPS_ENDPOINT_PATH = "/mops/web/ajax_t163sb04"
MOPS_HEADER_ALIASES = {
    "company_id": ("公司代號", "公司代碼", "代號"),
    "revenue": ("營業收入合計", "營業收入", "收入合計", "淨收益"),
    "cost_of_revenue": ("營業成本合計", "營業成本"),
    "gross_profit": ("營業毛利（毛損）", "營業毛利(毛損)", "營業毛利"),
    "operating_expenses": ("營業費用合計", "營業費用"),
    "operating_income": ("營業利益（損失）", "營業利益(損失)", "營業利益"),
    "net_income": (
        "本期淨利（淨損）",
        "本期淨利(淨損)",
        "本期稅後淨利（淨損）",
        "本期稅後淨利(淨損)",
        "本期淨利",
        "稅後淨利（淨損）",
        "稅後淨利",
        "歸屬於母公司業主之淨利（淨損）",
        "歸屬於母公司業主之淨利(淨損)",
        "歸屬於母公司業主淨利（淨損）",
        "歸屬於母公司業主淨利",
    ),
}
VALID_MOPS_MARKETS = {"sii", "otc", "rotc", "pub", "all"}


class MOPSFinancialSource:
    def __init__(
        self,
        *,
        company_id: str,
        start_year: int,
        end_year: int,
        seasons: tuple[int, ...] | list[int],
        base_url: str,
        market: str,
        timeout: int = 15,
        retries: int = 2,
        retry_backoff_seconds: float = 0.5,
        cache_dir: Path | None = None,
    ) -> None:
        self._company_id = company_id.strip()
        self._start_year = start_year
        self._end_year = end_year
        self._seasons = tuple(seasons)
        self._base_url = base_url
        self._market = market.strip().lower()
        self._timeout = timeout
        self._retries = retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self._cache_dir = cache_dir

    def load_records(self) -> list[FinancialRecord]:
        if self._company_id == "":
            raise InputDataError("MOPS source requires a company id.")
        if self._start_year > self._end_year:
            raise InputDataError("MOPS start year must be less than or equal to the end year.")
        if self._market not in VALID_MOPS_MARKETS:
            raise InputDataError("MOPS market must be one of: all, sii, otc, rotc, pub.")

        requested_seasons = sorted({int(season) for season in self._seasons})
        if not requested_seasons or any(season < 1 or season > 4 for season in requested_seasons):
            raise InputDataError("MOPS seasons must be a subset of 1, 2, 3, 4.")

        records: list[FinancialRecord] = []
        for year in range(self._start_year, self._end_year + 1):
            roc_year = _to_mops_year(year)
            period_year = _to_gregorian_year(year)
            for season in requested_seasons:
                LOGGER.info(
                    "fetch_mops company_id=%s year=%s season=%s market=%s",
                    self._company_id,
                    period_year,
                    season,
                    self._market,
                )
                html_payload = self._request_statement(roc_year=roc_year, season=season)
                record = _parse_mops_financial_record(
                    html_payload,
                    company_id=self._company_id,
                    period_year=period_year,
                    season=season,
                )
                if record is not None:
                    records.append(record)

        if not records:
            raise InputDataError(
                f"No MOPS financial records were found for company '{self._company_id}'."
            )

        return sorted(records, key=_financial_period_sort_key)

    def _request_statement(self, *, roc_year: int, season: int) -> str:
        url = f"{self._base_url.rstrip('/')}{MOPS_ENDPOINT_PATH}"
        payload = urlencode(
            {
                "encodeURIComponent": "1",
                "step": "1",
                "firstin": "1",
                "off": "1",
                "TYPEK": self._market,
                "year": str(roc_year),
                "season": f"{season:02d}",
            }
        ).encode("utf-8")
        return request_text(
            url,
            method="POST",
            data=payload,
            headers={
                "User-Agent": "financial-analysis-tool/0.1",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": self._base_url.rstrip("/"),
                "Referer": f"{self._base_url.rstrip('/')}/mops/web/t163sb04",
            },
            timeout=self._timeout,
            retries=self._retries,
            backoff_seconds=self._retry_backoff_seconds,
            cache_dir=self._cache_dir,
            cache_namespace="mops",
            error_cls=MOPSAPIError,
            source_label="MOPS",
        )


def _parse_mops_financial_record(
    html_payload: str,
    *,
    company_id: str,
    period_year: int,
    season: int,
) -> FinancialRecord | None:
    if "page cannot be accessed" in html_payload.lower():
        raise MOPSAPIError(
            "MOPS rejected the request. Try again later or switch the MOPS base URL if TWSE changes the endpoint."
        )
    if "查詢無資料" in html_payload:
        return None

    tables = _HTMLTableParser().parse_tables(html_payload)
    for table in tables:
        row_index = _find_company_row_index(table, company_id)
        if row_index is None:
            continue

        data_row = table[row_index]
        header_row = _find_header_row(table, row_index, len(data_row))
        if header_row is None:
            continue

        revenue = _find_metric_value(header_row, data_row, "revenue")
        gross_profit = _find_metric_value(header_row, data_row, "gross_profit")
        cost_of_revenue = _find_metric_value(header_row, data_row, "cost_of_revenue")
        operating_income = _find_metric_value(header_row, data_row, "operating_income")
        operating_expenses = _find_metric_value(header_row, data_row, "operating_expenses")
        net_income = _find_metric_value(header_row, data_row, "net_income")

        if revenue is None or net_income is None:
            continue
        if cost_of_revenue is None and gross_profit is not None:
            cost_of_revenue = revenue - gross_profit
        if operating_expenses is None and gross_profit is not None and operating_income is not None:
            operating_expenses = gross_profit - operating_income
        if cost_of_revenue is None or operating_expenses is None:
            continue

        return FinancialRecord(
            period=f"{period_year}-Q{season}",
            revenue=revenue,
            cost_of_revenue=cost_of_revenue,
            operating_expenses=operating_expenses,
            net_income=net_income,
        )

    return None


def _find_company_row_index(table: list[list[str]], company_id: str) -> int | None:
    for index, row in enumerate(table):
        for cell in row[:3]:
            normalized_cell = _normalize_cell_text(cell)
            if normalized_cell == company_id or normalized_cell.startswith(company_id):
                return index
    return None


def _find_header_row(
    table: list[list[str]],
    row_index: int,
    row_length: int,
) -> list[str] | None:
    for candidate_index in range(row_index - 1, -1, -1):
        candidate = table[candidate_index]
        if len(candidate) != row_length:
            continue
        if _header_score(candidate) > 0:
            return candidate

    for candidate_index in range(row_index - 1, -1, -1):
        candidate = table[candidate_index]
        if _header_score(candidate) > 0:
            return candidate

    return None


def _header_score(row: list[str]) -> int:
    score = 0
    for cell in row:
        normalized_cell = _normalize_label(cell)
        for aliases in MOPS_HEADER_ALIASES.values():
            if any(_normalize_label(alias) in normalized_cell for alias in aliases):
                score += 1
                break
    return score


def _find_metric_value(
    header_row: list[str],
    data_row: list[str],
    metric_name: str,
) -> float | None:
    target_aliases = tuple(_normalize_label(alias) for alias in MOPS_HEADER_ALIASES[metric_name])
    for index, header in enumerate(header_row):
        normalized_header = _normalize_label(header)
        if any(alias in normalized_header for alias in target_aliases):
            if index >= len(data_row):
                return None
            return _parse_mops_number(data_row[index])
    return None


def _financial_period_sort_key(record: FinancialRecord) -> tuple[int, int]:
    year_raw, quarter_raw = record.period.split("-Q", maxsplit=1)
    return int(year_raw), int(quarter_raw)


def _parse_mops_number(value: str | None) -> float | None:
    normalized_value = (value or "").strip()
    if normalized_value in {"", "--", "---", "N/A"}:
        return None

    normalized_value = normalized_value.replace(",", "").replace("%", "")
    normalized_value = normalized_value.replace("\u3000", "").strip()
    if normalized_value.startswith("(") and normalized_value.endswith(")"):
        normalized_value = f"-{normalized_value[1:-1]}"
    normalized_value = re.sub(r"[^0-9.\-]", "", normalized_value)
    if normalized_value in {"", "-", ".", "-."}:
        return None

    return float(normalized_value)


def _normalize_label(value: str) -> str:
    return re.sub(r"[\s\u3000]+", "", value or "")


def _normalize_cell_text(value: str) -> str:
    return _normalize_label(value).replace("：", ":")


def _to_mops_year(year: int) -> int:
    return year - 1911 if year >= 1911 else year


def _to_gregorian_year(year: int) -> int:
    return year + 1911 if year < 1911 else year


class _HTMLTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._tables: list[list[list[str]]] = []
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._cell_parts: list[str] | None = None
        self._table_depth = 0

    def parse_tables(self, html_payload: str) -> list[list[list[str]]]:
        self._tables = []
        self.feed(html_payload)
        self.close()
        return self._tables

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._current_table = []
            return
        if self._table_depth == 0:
            return
        if tag == "tr":
            self._current_row = []
            return
        if tag in {"td", "th"} and self._current_row is not None:
            self._cell_parts = []
            return
        if tag == "br" and self._cell_parts is not None:
            self._cell_parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            if self._table_depth == 1 and self._current_table:
                self._tables.append(self._current_table)
                self._current_table = None
            self._table_depth = max(self._table_depth - 1, 0)
            return
        if self._table_depth == 0:
            return
        if tag in {"td", "th"} and self._cell_parts is not None and self._current_row is not None:
            cell_value = re.sub(r"\s+", " ", "".join(self._cell_parts)).strip()
            self._current_row.append(cell_value)
            self._cell_parts = None
            return
        if tag == "tr" and self._current_row is not None and self._current_table is not None:
            if any(cell.strip() for cell in self._current_row):
                self._current_table.append(self._current_row)
            self._current_row = None

    def handle_data(self, data: str) -> None:
        if self._cell_parts is not None:
            self._cell_parts.append(data)
