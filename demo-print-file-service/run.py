import logging

from structlog import wrap_logger

from app.logger import logger_initial_config
from app.run_daemons import run_daemons
from config import Config


def run():
    Config.check_config()
    logger_initial_config()
    logger = wrap_logger(logging.getLogger(__name__))
    logger.info('Starting print file service', app_log_level=Config.LOG_LEVEL, pika_log_level=Config.LOG_LEVEL_PIKA,
                paramiko_log_level=Config.LOG_LEVEL_PARAMIKO, environment=Config.ENVIRONMENT)
    initialise_directories()
    run_daemons()


def initialise_directories():
    Config.PARTIAL_FILES_DIRECTORY.mkdir(exist_ok=True)
    Config.ENCRYPTED_FILES_DIRECTORY.mkdir(exist_ok=True)
    Config.QUARANTINED_FILES_DIRECTORY.mkdir(exist_ok=True)


if __name__ == '__main__':
    run()
