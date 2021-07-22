import logging
import multiprocessing
import queue
from time import sleep

from structlog import wrap_logger
from tenacity import retry, wait_exponential

from app.exceptions import DaemonStartupError
from app.file_sender import start_file_sender
from app.readiness import Readiness
from app.message_listener import start_message_listener
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def run_daemons():
    process_manager = multiprocessing.Manager()
    daemons = [
        {'name': 'message-listener', 'target': start_message_listener, 'process': None},
        {'name': 'file-sender', 'target': start_file_sender, 'process': None}
    ]
    for daemon in daemons:
        daemon['process'] = run_in_daemon(daemon['target'], daemon['name'], process_manager)

    with Readiness(readiness_file=Config.READINESS_FILE_PATH) as readiness:
        logger.info('Started print service')
        while True:
            for daemon in daemons:
                if not daemon['process'].is_alive():
                    logger.error('Daemon died, attempting to restart', daemon=daemon['name'])
                    readiness.show_unready()
                    daemon['process'] = retry_run_daemon(daemon['target'], daemon['name'], process_manager)
                    readiness.show_ready()
            sleep(1)


def run_in_daemon(target, name, process_manager, timeout=20) -> multiprocessing.Process:
    readiness_queue = process_manager.Queue()
    daemon = multiprocessing.Process(target=target, args=(readiness_queue,), daemon=True, name=name)
    daemon.start()
    try:
        if readiness_queue.get(block=True, timeout=timeout):
            return daemon
    except queue.Empty as err:
        raise DaemonStartupError(f'Error starting daemon: [{name}]') from err


@retry(wait=wait_exponential(multiplier=1, min=1, max=10))
def retry_run_daemon(target, name, process_manager, timeout=20) -> multiprocessing.Process:
    return run_in_daemon(target, name, process_manager, timeout=timeout)
