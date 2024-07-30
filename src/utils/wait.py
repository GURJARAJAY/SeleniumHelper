import time

from utils.logger import get_logger

LOG = get_logger()


class Utilities:
    @classmethod
    def wait(cls, duration_in_seconds, wait_message=""):
        LOG.info(f"Sleeping for {duration_in_seconds} seconds - {wait_message}")
        time.sleep(duration_in_seconds)