"""CLI entrypoints."""

from .app import main
from .parser import build_parser

__all__ = ["build_parser", "main"]
