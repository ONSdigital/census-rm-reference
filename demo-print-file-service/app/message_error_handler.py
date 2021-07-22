import base64
import hashlib
import json
import logging

import requests
from structlog import wrap_logger

from app.json_helper import CustomJSONEncoder
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def _report_exception_for_advice(message_hash, service, queue, exception_class, exception_trace):
    exception_report_payload = {
        'messageHash': message_hash,
        'service': service,
        'queue': queue,
        'exceptionClass': exception_class,
        'exceptionMessage': exception_trace,
    }

    response = requests.post(f'{Config.EXCEPTION_MANAGER_URL}/reportexception', json=exception_report_payload)
    response.raise_for_status()
    return response.json()


def _quarantine_message(body: bytes, message_hash, exception_class, properties):
    _quarantine_message_in_exception_manager(body, message_hash, exception_class, properties.headers)


def _quarantine_message_in_exception_manager(body: bytes, message_hash, exception_class, headers):
    quarantine_payload = {
        'messageHash': message_hash,
        'messagePayload': base64.b64encode(body).decode(),
        'service': Config.NAME,
        'queue': Config.RABBIT_QUEUE,
        'exceptionClass': exception_class,
        'contentType': 'application/json',
        'headers': headers,
    }

    response = requests.post(f'{Config.EXCEPTION_MANAGER_URL}/storeskippedmessage', data=json.dumps(
        quarantine_payload, cls=CustomJSONEncoder), headers={'Content-Type': 'application/json'})
    response.raise_for_status()


def _peek_message(message_hash, body: bytes):
    peek_payload = {
        'messageHash': message_hash,
        'messagePayload': base64.b64encode(body).decode(),
    }

    response = requests.post(f'{Config.EXCEPTION_MANAGER_URL}/peekreply', json=peek_payload)
    response.raise_for_status()


def handle_message_error(message_body: bytes, exception: Exception, channel, delivery_tag, properties):
    message_hash = hashlib.sha256(message_body).hexdigest()
    exception_class = type(exception).__name__

    try:
        advice = _report_exception_for_advice(message_hash, Config.NAME, Config.RABBIT_QUEUE, exception_class,
                                              repr(exception))

        if advice.get('skipIt'):
            logger.warn('Attempting to quarantine and skip bad message', message_hash=message_hash,
                        queue=Config.RABBIT_QUEUE)
            _quarantine_message(message_body, message_hash, exception_class, properties)
            channel.basic_ack(delivery_tag=delivery_tag)
            logger.warn('Successfully quarantined and skipped bad message', message_hash=message_hash,
                        queue=Config.RABBIT_QUEUE)
            return

        elif advice.get('peek'):
            _peek_message(message_hash, message_body)
            channel.basic_nack(delivery_tag=delivery_tag, requeue=False)
            return

        elif not advice.get('logIt', True):
            channel.basic_nack(delivery_tag=delivery_tag, requeue=False)
            return

    except Exception as e:
        # Suppress exceptions here so that if any of the error advice process fails for any reasons,
        # we fallback to default behaviour
        logger.error('Exception handling advice failed', error_message=repr(e))

    # Default/fallback behaviour is to log the error and nack the message
    logger.error('Could not process message', message_hash=message_hash, exception=exception)
    channel.basic_nack(delivery_tag=delivery_tag, requeue=False)
