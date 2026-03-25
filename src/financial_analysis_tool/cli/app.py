from __future__ import annotations

from financial_analysis_tool.core.logging import configure_logging

from .parser import build_parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level)
    return args.handler(args)
