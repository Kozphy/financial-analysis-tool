"""Module entrypoint for ``python -m financial_analysis_tool``.

The module keeps package execution aligned with the console script by
delegating directly to the CLI ``main`` function.
"""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
