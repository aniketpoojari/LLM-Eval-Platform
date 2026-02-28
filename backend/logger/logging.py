import logging
import os
import sys


def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name):
    return logging.getLogger(name)
