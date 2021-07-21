import logging

from structlog import wrap_logger

from app.message_error_handler import handle_message_error
from app.print_file_builder import generate_print_row
from app.rabbit_context import RabbitContext
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def start_message_listener(readiness_queue):
    logger.info('Starting print message listener')
    with RabbitContext() as rabbit:
        rabbit.channel.basic_consume(
            queue=rabbit.queue_name,
            on_message_callback=print_message_callback)
        readiness_queue.put(True)
        logger.info('Started print message listener')
        rabbit.channel.start_consuming()


def print_message_callback(ch, method, properties, body, partial_files_directory=Config.PARTIAL_FILES_DIRECTORY,
                           suppliers_config=Config.SUPPLIERS_CONFIG):
    try:
        generate_print_row(body, partial_files_directory, suppliers_config)
    except Exception as e:
        handle_message_error(body, e, ch, method.delivery_tag, properties)
        return
    ch.basic_ack(delivery_tag=method.delivery_tag)
