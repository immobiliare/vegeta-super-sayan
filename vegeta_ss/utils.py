import logging
from pathlib import Path

from rich.logging import RichHandler

ROOT_PATH = Path(__file__).parent.parent
LOG_LOCATION = "./var/log/app.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s]" " %(message)s [%(pathname)s:%(lineno)d]"


class RelativePathFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.pathname = str(Path(record.pathname).relative_to(ROOT_PATH))
        except ValueError:
            pass
        return super().format(record)


def format_time(time_in_ns: int) -> str:
    """Format time in nanoseconds to a human-readable string.

    Args:
        time_in_ns (int): Time in nanoseconds.

    Returns:
        str: Formatted time string.
    """
    units = [("s", 1e9, float), ("ms", 1e6, int), ("μs", 1e3, int), ("ns", 1, int)]

    for unit, factor, num_type in units:
        if time_in_ns >= factor:
            quotient = time_in_ns / factor
            return f"{num_type(round(quotient, 3))}{unit}"
    return f"{time_in_ns}ns"  # Fallback


def get_logger(__name__):
    def _get_custom_handler(handler, format, filter=None):
        handler.setFormatter(RelativePathFormatter(format))
        if filter:
            handler.addFilter(filter)
        return handler

    log_dir = Path(LOG_LOCATION).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    _logger = logging.getLogger(__name__)
    _logger.setLevel(LOG_LEVEL)

    file_handler = logging.FileHandler(LOG_LOCATION)
    custom_file_handler = _get_custom_handler(file_handler, LOG_FORMAT)
    _logger.addHandler(custom_file_handler)

    console_handler = _get_custom_handler(
        RichHandler(show_time=False, show_path=False), LOG_FORMAT
    )
    _logger.addHandler(console_handler)

    return _logger


logger = get_logger(__name__)
