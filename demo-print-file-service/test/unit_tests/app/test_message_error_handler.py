import base64
import datetime
import hashlib
import json
from unittest.mock import Mock, patch

import pika
from pika import BasicProperties

from app.message_error_handler import handle_message_error
from config import TestConfig

EXCEPTION_MESSAGE = 'An exception during message processing'
MOCK_MESSAGE_ID = 'mock_message_id'
POST_METHOD_TO_PATCH = 'app.message_error_handler.requests.post'


def test_handle_error_reports_exception(init_logger, caplog):
    # Given
    mock_channel = Mock(pika.adapters.blocking_connection.BlockingChannel)
    mock_method = Mock()
    mock_properties = Mock()
    mock_properties.message_id = MOCK_MESSAGE_ID
    message = b'Iamamessage'
    message_hash = hashlib.sha256(message).hexdigest()
    processing_exception = Exception(EXCEPTION_MESSAGE)

    expected_exception_report = {
        'messageHash': message_hash,
        'service': TestConfig.NAME,
        'queue': TestConfig.RABBIT_QUEUE,
        'exceptionClass': type(processing_exception),
        'exceptionMessage': repr(processing_exception),
    }

    # When
    with patch(POST_METHOD_TO_PATCH) as patched_post:
        handle_message_error(message, processing_exception, mock_channel, mock_method.delivery_tag, mock_properties)

    # Then
    assert patched_post.called_once_with(TestConfig.EXCEPTION_MANAGER_URL, expected_exception_report)


def test_handle_error_falls_back_on_logging(init_logger, caplog):
    # Given
    mock_channel = Mock(pika.adapters.blocking_connection.BlockingChannel)
    mock_method = Mock()
    mock_properties = Mock()
    mock_properties.message_id = MOCK_MESSAGE_ID
    message = b'Iamamessage'
    message_hash = hashlib.sha256(message).hexdigest()
    processing_exception = Exception(EXCEPTION_MESSAGE)

    # When
    with patch(POST_METHOD_TO_PATCH) as patched_post:
        patched_post.side_effect = mock_reporting_failure
        handle_message_error(message, processing_exception, mock_channel, mock_method.delivery_tag, mock_properties)

    # Then
    assert 'Could not process message' in caplog.text
    assert EXCEPTION_MESSAGE in caplog.text
    assert f'"message_hash": "{message_hash}"' in caplog.text


def test_handle_error_log_it(init_logger, caplog):
    mock_channel = Mock(pika.adapters.blocking_connection.BlockingChannel)
    mock_method = Mock()
    mock_properties = Mock()
    mock_properties.message_id = MOCK_MESSAGE_ID
    message = b'Iamamessage'
    message_hash = hashlib.sha256(message).hexdigest()
    processing_exception = Exception(EXCEPTION_MESSAGE)
    mock_advice = {'logIt': True}

    # When
    with patch(POST_METHOD_TO_PATCH) as patched_post:
        patched_post.return_value.json.return_value = mock_advice
        handle_message_error(message, processing_exception, mock_channel, mock_method.delivery_tag, mock_properties)

    # Then
    assert 'Could not process message' in caplog.text
    assert EXCEPTION_MESSAGE in caplog.text
    assert f'"message_hash": "{message_hash}"' in caplog.text


def test_handle_error_no_log(init_logger, caplog):
    # Given
    mock_channel = Mock(pika.adapters.blocking_connection.BlockingChannel)
    mock_method = Mock()
    mock_properties = Mock()
    mock_properties.message_id = MOCK_MESSAGE_ID
    message = b'Iamamessage'
    processing_exception = Exception(EXCEPTION_MESSAGE)
    mock_advice = {'logIt': False}

    # When
    with patch(POST_METHOD_TO_PATCH) as patched_post:
        patched_post.return_value.json.return_value = mock_advice
        handle_message_error(message, processing_exception, mock_channel, mock_method.delivery_tag, mock_properties)

    assert not caplog.text


def test_handle_error_quarantine_message(init_logger, caplog):
    # Given
    mock_channel = Mock(pika.adapters.blocking_connection.BlockingChannel)
    mock_method = Mock()
    message = b'Iamamessage'
    message_hash = hashlib.sha256(message).hexdigest()
    processing_exception = Exception(EXCEPTION_MESSAGE)
    mock_advice = {'skipIt': True}

    expected_quarantine_message = json.dumps({
        'messageHash': message_hash,
        'messagePayload': base64.b64encode(message).decode(),
        'service': TestConfig.NAME,
        'queue': TestConfig.RABBIT_QUEUE,
        'exceptionClass': type(processing_exception).__name__,
        'contentType': 'application/json',
        'headers': {"time": "2019-11-18T10:59:42Z"},
    })
    properties = BasicProperties(content_type='application/json',
                                 headers={'time': datetime.datetime(2019, 11, 18, 10, 59, 42)})
    # When
    with patch(POST_METHOD_TO_PATCH) as patched_post:
        patched_post.return_value.json.return_value = mock_advice
        handle_message_error(message, processing_exception, mock_channel, mock_method.delivery_tag, properties)

    post_calls = patched_post.call_args_list

    assert len(post_calls) == 2
    assert post_calls[1][0][0] == f'{TestConfig.EXCEPTION_MANAGER_URL}/storeskippedmessage'
    assert post_calls[1][1]['data'] == expected_quarantine_message

    assert "Attempting to quarantine and skip bad message" in caplog.text
    assert "Successfully quarantined and skipped bad message" in caplog.text
    assert f'"queue": "{TestConfig.RABBIT_QUEUE}"' in caplog.text
    assert f'"message_hash": "{message_hash}"' in caplog.text
    assert "Could not process message" not in caplog.text


def test_handle_error_peek_message(init_logger, caplog):
    # Given
    mock_channel = Mock(pika.adapters.blocking_connection.BlockingChannel)
    mock_method = Mock()
    mock_properties = Mock()
    mock_properties.message_id = MOCK_MESSAGE_ID
    message = b'Iamamessage'
    message_hash = hashlib.sha256(message).hexdigest()
    processing_exception = Exception(EXCEPTION_MESSAGE)
    mock_advice = {'peek': True}
    expected_peek_message = {
        'messageHash': message_hash,
        'messagePayload': base64.b64encode(message).decode(),
    }

    # When
    with patch(POST_METHOD_TO_PATCH) as patched_post:
        patched_post.return_value.json.return_value = mock_advice
        handle_message_error(message, processing_exception, mock_channel, mock_method.delivery_tag, mock_properties)

    post_calls = patched_post.call_args_list

    assert len(post_calls) == 2
    assert post_calls[1][0][0] == f'{TestConfig.EXCEPTION_MANAGER_URL}/peekreply'
    assert post_calls[1][1]['json'] == expected_peek_message

    assert not caplog.text


def mock_reporting_failure():
    raise Exception('Mocked failure to report exception')
