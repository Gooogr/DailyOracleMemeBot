import sys
from typing import Literal

from loguru import logger


def setup_logger(
    service_name: Literal["sync_worker", "telegram_bot"],
    log_path: str = "/app/logs/{service_name}.log",
) -> None:
    resolved_path = log_path.format(service_name=service_name)

    logger.remove()

    logger.add(sink=sys.stderr, level="INFO", backtrace=True, enqueue=True, diagnose=False, catch=True)

    logger.add(
        resolved_path,
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        backtrace=True,
        enqueue=True,
        diagnose=False,
        catch=True,
    )
