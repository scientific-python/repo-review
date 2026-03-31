from __future__ import annotations

__lazy_modules__ = ["time"]

import time
from contextlib import contextmanager

TYPE_CHECKING = False
if TYPE_CHECKING:
    import logging
    from collections.abc import Generator


__all__ = ["log_timer"]


def __dir__() -> list[str]:
    return __all__


@contextmanager
def log_timer(
    logger: logging.Logger, msg: str, *args: object
) -> Generator[None, None, None]:
    """
    Context manager to log the time taken by a block of code.

    :param logger: The logger to use for logging the message.
    :param msg: The message to log, which can include format placeholders.
    :param args: Additional arguments to format into the message.

    Usage:
        with log_timer(logger, "Processing data for %s", dataset_name):
            process_data()
    """
    start_time = time.perf_counter()
    logger.debug(f"{msg} (started)", *args)  # noqa: G004
    try:
        yield
    finally:
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.info(f"{msg} (%.3f seconds)", *args, elapsed_time)  # noqa: G004
