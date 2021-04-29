import functools
import json
import logging

import requests

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper

from structlog import wrap_logger

from config import Config

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


def purge_queues():
    all_queues = _get_all_queues()
    with RabbitContext() as rabbit:
        for queue in all_queues:
            rabbit.channel.queue_purge(queue=queue)


def _timeout_callback(rabbit):
    logger.error('Timed out waiting for messages')
    rabbit.close_connection()
    test_helper.fail("Didn't find the expected number of messages")


def _get_all_queues():
    uri = f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/%2f/'
    response = requests.get(uri, auth=(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))
    response.raise_for_status()
    response_data = json.loads(response.content)

    return [queue['name'] for queue in response_data]
