"""Console, Markdown, and JSON reporting helpers for ESG analysis."""

from __future__ import annotations

import json
from pathlib import Path

from .esg_models import EsgAnalysisSummary


def build_esg_console_summary(summary: EsgAnalysisSummary) -> str:
    """Build a concise ESG summary for terminal output."""
    top_risk_company = summary.high_risk_companies[0]["company"] if summary.high_risk_companies else "n/a"
    lines = [
        "ESG Analysis Summary",
        "====================",
        f"Audience: {summary.audience_name}",
        f"Companies analyzed: {summary.company_count}",
        f"Rows analyzed: {summary.cleaned_row_count}",
        f"Years covered: {summary.years[0]}-{summary.years[-1]}",
        f"Average ESG score: {summary.average_esg_score:.2f}",
        f"Average carbon intensity: {summary.average_carbon_intensity:.2f}",
        f"Top latest-year risk signal: {top_risk_company}",
    ]
    return "\n".join(lines)


def build_esg_markdown_report(summary: EsgAnalysisSummary) -> str:
    """Build a business-facing Markdown report suitable for finance stakeholders."""
    lines = [
        f"# ESG Portfolio Review for {summary.audience_name}",
        "",
        "## Scope",
        "",
        f"- Companies analyzed: `{summary.company_count}`",
        f"- Cleaned rows: `{summary.cleaned_row_count}`",
        f"- Year range: `{summary.years[0]}-{summary.years[-1]}`",
        "",
        "## Data Quality",
        "",
        f"- Original rows: `{summary.cleaning_summary.get('original_rows', 'n/a')}`",
        f"- Duplicates removed: `{summary.cleaning_summary.get('duplicates_removed', 'n/a')}`",
        f"- Missing numeric values before cleaning: `{summary.cleaning_summary.get('initial_missing_values', 'n/a')}`",
        f"- Missing numeric values after cleaning: `{summary.cleaning_summary.get('remaining_missing_values', 'n/a')}`",
        "",
        "## Key Insights",
        "",
    ]

    for insight in summary.insights:
        lines.extend(
            [
                f"### {insight.title}",
                "",
                f"- Finding: {insight.finding}",
                f"- Business implication: {insight.implication}",
                "",
            ]
        )

    lines.extend(
        [
            "## Latest-Year Risk Watchlist",
            "",
            "| Company | Sector | ESG Score | Carbon Intensity | Governance Score | Controversies | Risk Score | Bucket |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )

    for item in summary.high_risk_companies:
        lines.append(
            "| "
            f"{item['company']} | "
            f"{item['sector']} | "
            f"{item['esg_score']:.2f} | "
            f"{item['carbon_intensity']:.2f} | "
            f"{item['governance_score']:.2f} | "
            f"{item['controversy_count']:.2f} | "
            f"{item['risk_score']:.2f} | "
            f"{item['risk_bucket']} |"
        )

    lines.extend(
        [
            "",
            "## Sector Exposure Snapshot",
            "",
            "| Sector | Companies | Avg ESG Score | Avg Carbon Intensity | Avg Green Capex % |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )

    for item in summary.sector_summary:
        lines.append(
            "| "
            f"{item['sector']} | "
            f"{item['company_count']} | "
            f"{item['average_esg_score']:.2f} | "
            f"{item['average_carbon_intensity']:.2f} | "
            f"{item['average_green_capex_pct']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Suggested Follow-Up Actions",
            "",
            "1. Prioritize stewardship discussions with high-risk companies that combine high carbon intensity with weak governance.",
            "2. Use sector-level carbon intensity as an escalation trigger for deeper due diligence in credit, investment, or insurance reviews.",
            "3. Track green capex and renewable energy usage as forward-looking indicators of transition readiness.",
        ]
    )
    return "\n".join(lines)


def write_esg_summary_json(summary: EsgAnalysisSummary, output_path: str | Path) -> None:
    """Write the ESG summary to a JSON file."""
    path = _ensure_parent_directory(output_path)
    path.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")


def write_esg_markdown_report(summary: EsgAnalysisSummary, output_path: str | Path) -> None:
    """Write the ESG business report to a Markdown file."""
    path = _ensure_parent_directory(output_path)
    path.write_text(build_esg_markdown_report(summary), encoding="utf-8")


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for an ESG output file when needed."""
    resolved_path = Path(path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path
