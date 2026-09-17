import logging
import sys
from core.config import get_settings

def config_logging()->None:
    settings = get_settings()

    logging.basicConfig(level=settings.log_level, format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def redact(value: str | None, keep: int = 2)->str:
    if not value:
        return ""
    if value is None: