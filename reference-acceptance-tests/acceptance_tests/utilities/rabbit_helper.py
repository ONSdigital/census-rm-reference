import functools
import logging

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def start_listening_to_rabbit_queue(queue, on_message_callback, timeout=60):
    rabbit = RabbitContext(queue_name=queue)
    connection = rabbit.open_connection()

    connection.call_later(
        delay=timeout,
        callback=functools.partial(_timeout_callback, rabbit))

    rabbit.channel.basic_consume(
        queue=queue,
        on_message_callback=on_message_callback)
    rabbit.channel.start_consuming()


def _timeout_callback(rabbit):
    logger.error('Timed out waiting for messages')
    rabbit.close_connection()
    test_helper.fail("Didn't find the expected number of messages")
