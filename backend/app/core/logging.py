"""Structured logging configuration for JobWise."""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.typing import FilteringBoundLogger

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer() if not settings.DEBUG 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=FilteringBoundLogger,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> FilteringBoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request(
    logger: FilteringBoundLogger,
    method: str,
    url: str,
    status_code: int,
    process_time: float,
    **kwargs: Any,
) -> None:
    """Log HTTP request details."""
    logger.info(
        "http_request",
        method=method,
        url=url,
        status_code=status_code,
        process_time=process_time,
        **kwargs,
    )


def log_ai_generation(
    logger: FilteringBoundLogger,
    generation_id: str,
    stage: str,
    tokens_used: int,
    execution_time: float,
    status: str,
    **kwargs: Any,
) -> None:
    """Log AI generation stage details."""
    logger.info(
        "ai_generation_stage",
        generation_id=generation_id,
        stage=stage,
        tokens_used=tokens_used,
        execution_time=execution_time,
        status=status,
        **kwargs,
    )


def log_database_operation(
    logger: FilteringBoundLogger,
    operation: str,
    table: str,
    execution_time: float,
    **kwargs: Any,
) -> None:
    """Log database operation details."""
    logger.info(
        "database_operation",
        operation=operation,
        table=table,
        execution_time=execution_time,
        **kwargs,
    )


def log_external_service_call(
    logger: FilteringBoundLogger,
    service: str,
    endpoint: str,
    status_code: int,
    response_time: float,
    **kwargs: Any,
) -> None:
    """Log external service call details."""
    logger.info(
        "external_service_call",
        service=service,
        endpoint=endpoint,
        status_code=status_code,
        response_time=response_time,
        **kwargs,
    )