"""Logging utilities shared by the RAG submodule."""

import logging


DEFAULT_LOGGER_NAME = "disaster_response.models.rag"


def _ensure_basic_logging() -> None:
    """Keep standalone scripts usable when backend logging is not configured."""
    root = logging.getLogger()
    if root.handlers:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str = DEFAULT_LOGGER_NAME) -> logging.Logger:
    _ensure_basic_logging()
    return logging.getLogger(name)


class Logger:
    """Backward-compatible wrapper for legacy submodule scripts."""

    def __init__(self, name: str = DEFAULT_LOGGER_NAME) -> None:
        self.logger = get_logger(name)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str, **kwargs: object) -> None:
        self.logger.error(message, **kwargs)

    def critical(self, message: str) -> None:
        self.logger.critical(message)
