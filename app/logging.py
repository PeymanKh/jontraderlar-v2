"""Logging setup. JSON in production, human-readable in development."""
from __future__ import annotations

import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from app.config import settings


def setup_logging() -> None:
    """Configure the root logger once at process startup."""
    root = logging.getLogger()

    # Clear any handlers attached by basicConfig or library imports.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_json:
        handler.setFormatter(
            JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s",
                rename_fields={"asctime": "time", "levelname": "level"},
            )
        )
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root.addHandler(handler)
    root.setLevel(settings.log_level.value)

    # Quiet down some noisy libraries.
    for noisy in ("aiogram.event", "httpx", "httpcore", "pymongo", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
