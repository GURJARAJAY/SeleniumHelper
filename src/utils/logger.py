import logging
import sys


def get_logger() -> logging.Logger:
    logger = logging.getLogger("web-automation")

    if len(logger.handlers) == 0:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)-15s %(name)s %(levelname)-8s  "
            "%(funcName)20s() %(lineno)s] %(message)s"
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger