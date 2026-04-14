"""Static SVG chart generation for profitability and balance-sheet trend visuals."""

from __future__ import annotations

import html
from pathlib import Path

from .models import PeriodMetrics


def generate_profitability_chart(
    period_metrics: list[PeriodMetrics],
    output_path: str | Path,
    *,
    company_name: str,
) -> None:
    """Generate the profitability trend chart used in reports and GitHub screenshots."""
    if not period_metrics:
        raise ValueError("At least one period metric is required for chart generation.")

    periods = [period.period for period in period_metrics]
    parts = [
        _svg_header(
            title=f"{company_name} Profitability Trends",
            subtitle="Revenue growth and profitability margins across reporting periods.",
            width=1120,
            height=760,
        )
    ]
    parts.extend(
        _build_panel(
            x=50,
            y=120,
            width=1020,
            height=270,
            title="Revenue and Net Income",
            periods=periods,
            series=[
                ("Revenue", [period.revenue for period in period_metrics], "#0f766e"),
                ("Net Income", [period.net_income for period in period_metrics], "#b45309"),
            ],
            y_formatter=lambda value: f"${value / 1_000_000:.1f}M",
        )
    )
    parts.extend(
        _build_panel(
            x=50,
            y=430,
            width=1020,
            height=270,
            title="Margin Trend",
            periods=periods,
            series=[
                ("Gross Margin", [_percent_value(period.gross_margin) for period in period_metrics], "#1d4ed8"),
                ("Operating Margin", [_percent_value(period.operating_margin) for period in period_metrics], "#7c3aed"),
                ("Net Margin", [_percent_value(period.net_margin) for period in period_metrics], "#be123c"),
            ],
            y_formatter=lambda value: f"{value:.0f}%",
        )
    )
    parts.append("</svg>")
    _ensure_parent_directory(output_path).write_text("\n".join(parts), encoding="utf-8")


def generate_financial_position_chart(
    period_metrics: list[PeriodMetrics],
    output_path: str | Path,
    *,
    company_name: str,
) -> None:
    """Generate the liquidity and leverage chart used in portfolio outputs."""
    if not period_metrics:
        raise ValueError("At least one period metric is required for chart generation.")

    periods = [period.period for period in period_metrics]
    parts = [
        _svg_header(
            title=f"{company_name} Financial Position",
            subtitle="Liquidity and leverage trends for balance-sheet review.",
            width=1120,
            height=760,
        )
    ]
    parts.extend(
        _build_panel(
            x=50,
            y=120,
            width=1020,
            height=270,
            title="Current Assets vs Current Liabilities",
            periods=periods,
            series=[
                ("Current Assets", [period.current_assets for period in period_metrics], "#0f766e"),
                ("Current Liabilities", [period.current_liabilities for period in period_metrics], "#b91c1c"),
            ],
            y_formatter=lambda value: f"${value / 1_000_000:.1f}M",
        )
    )
    parts.extend(
        _build_panel(
            x=50,
            y=430,
            width=1020,
            height=270,
            title="Liquidity and Leverage Ratios",
            periods=periods,
            series=[
                ("Current Ratio", [_ratio_value(period.current_ratio) for period in period_metrics], "#1d4ed8"),
                ("Debt Ratio", [_percent_value(period.debt_ratio) for period in period_metrics], "#b45309"),
            ],
            y_formatter=lambda value: f"{value:.1f}",
        )
    )
    parts.append("</svg>")
    _ensure_parent_directory(output_path).write_text("\n".join(parts), encoding="utf-8")


def _svg_header(*, title: str, subtitle: str, width: int, height: int) -> str:
    """Build the shared SVG document header and title block."""
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            "<style>",
            "text { font-family: Segoe UI, Arial, sans-serif; fill: #102a43; }",
            ".title { font-size: 30px; font-weight: bold; }",
            ".subtitle { font-size: 14px; fill: #486581; }",
            ".panel-title { font-size: 18px; font-weight: bold; }",
            ".axis-label { font-size: 12px; fill: #627d98; }",
            ".legend { font-size: 12px; }",
            "</style>",
            '<rect width="100%" height="100%" fill="#f8fbff" />',
            f'<text class="title" x="60" y="60">{html.escape(title)}</text>',
            f'<text class="subtitle" x="60" y="88">{html.escape(subtitle)}</text>',
        ]
    )


def _build_panel(
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    periods: list[str],
    series: list[tuple[str, list[float], str]],
    y_formatter,
) -> list[str]:
    """Render one multi-series chart panel inside the SVG document."""
    margin_top = 42
    margin_right = 35
    margin_bottom = 48
    margin_left = 80

    plot_left = x + margin_left
    plot_top = y + margin_top
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    plot_bottom = plot_top + plot_height
    plot_right = plot_left + plot_width

    values = [value for _, data, _ in series for value in data]
    value_min = min(0.0, min(values))
    value_max = max(values)
    if value_max == value_min:
        value_max += 1.0

    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="#ffffff" stroke="#d9e2ec" />',
        f'<text class="panel-title" x="{x + 24}" y="{y + 28}">{html.escape(title)}</text>',
    ]

    for tick in range(5):
        ratio = tick / 4
        tick_value = value_max - ((value_max - value_min) * ratio)
        tick_y = plot_top + (plot_height * ratio)
        parts.append(
            f'<line x1="{plot_left}" y1="{tick_y:.2f}" x2="{plot_right}" y2="{tick_y:.2f}" stroke="#e4edf5" />'
        )
        parts.append(
            f'<text class="axis-label" x="{plot_left - 12}" y="{tick_y + 4:.2f}" text-anchor="end">{html.escape(y_formatter(tick_value))}</text>'
        )

    point_count = len(periods)
    if point_count == 1:
        x_positions = [plot_left + (plot_width / 2)]
    else:
        x_positions = [
            plot_left + (plot_width * index / (point_count - 1)) for index in range(point_count)
        ]

    for label, position in zip(periods, x_positions):
        parts.append(
            f'<text class="axis-label" x="{position:.2f}" y="{plot_bottom + 24}" text-anchor="middle">{html.escape(label)}</text>'
        )

    for index, (label, _, color) in enumerate(series):
        legend_x = x + 24 + (index * 190)
        legend_y = y + height - 16
        parts.append(
            f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 26}" y2="{legend_y}" stroke="{color}" stroke-width="3" />'
        )
        parts.append(
            f'<text class="legend" x="{legend_x + 34}" y="{legend_y + 4}">{html.escape(label)}</text>'
        )

    for _, data, color in series:
        points = []
        for index, value in enumerate(data):
            point_x = x_positions[index]
            point_y = _scale_value(
                value=value,
                min_value=value_min,
                max_value=value_max,
                plot_top=plot_top,
                plot_height=plot_height,
            )
            points.append((point_x, point_y))

        point_string = " ".join(f"{point_x:.2f},{point_y:.2f}" for point_x, point_y in points)
        parts.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="3.5" points="{point_string}" />'
        )

        for point_x, point_y in points:
            parts.append(
                f'<circle cx="{point_x:.2f}" cy="{point_y:.2f}" r="4.5" fill="{color}" stroke="#ffffff" stroke-width="2" />'
            )

    return parts


def _scale_value(
    *,
    value: float,
    min_value: float,
    max_value: float,
    plot_top: int,
    plot_height: int,
) -> float:
    """Scale a numeric value into the SVG plot coordinate system."""
    ratio = (value - min_value) / (max_value - min_value)
    return plot_top + plot_height - (ratio * plot_height)


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for a chart output path when needed."""
    resolved_path = Path(path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def _percent_value(value: float | None) -> float:
    """Convert a decimal ratio into a percentage number for plotting."""
    return 0.0 if value is None else value * 100


def _ratio_value(value: float | None) -> float:
    """Normalize optional ratio values for plotting."""
    return 0.0 if value is None else value
