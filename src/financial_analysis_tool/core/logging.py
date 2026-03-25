from __future__ import annotations

import logging


def configure_logging(level_name: str = "WARNING") -> None:
    level = getattr(logging, level_name.upper(), logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
