"""Structured JSON logging for AutonomyLoops.

Uses structlog for machine-parseable, context-rich log output
suitable for log aggregation systems (ELK, Datadog, CloudWatch).
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def configure_logging(level: str = "info", json_output: bool = True) -> None:
    """Configure structured logging for the application.

    Args:
        level: Log level (debug, info, warning, error).
        json_output: If True, output JSON. If False, output human-readable.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a named structured logger.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Structured logger instance.
    """
    return structlog.get_logger(name)


# Configure with defaults on import
configure_logging()
