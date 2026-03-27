"""
C1 — Structured Logging Configuration
Uses structlog for structured, machine-readable log output.
No print statements in production code.
"""

import logging
import structlog


def configure_logging() -> None:
    """Configure structlog with JSON output for production and console for dev."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a named structured logger."""
    return structlog.get_logger(name)
