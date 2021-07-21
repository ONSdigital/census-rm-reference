import hashlib
import json
from queue import Queue
from unittest.mock import Mock, patch

from app.message_listener import print_message_callback, \
    start_message_listener


def test_valid_message_is_acked(cleanup_test_files):
    # Given
    json_body = json.dumps({
        "printSupplier": "SUPPLIER_A",
        "batchId": "1",
        "batchQuantity": 3,
        "row": "test|example",
        "packCode": "EXAMPLE_LETTER"
    }).encode()

    # When
    mock_channel = Mock()
    mock_method = Mock()
    print_message_callback(mock_channel, mock_method, Mock(), json_body, cleanup_test_files.partial_files)

    # Then
    mock_channel.basic_ack.assert_called_with(delivery_tag=mock_method.delivery_tag)


def test_invalid_suppliers_are_nacked(cleanup_test_files, init_logger, caplog):
    # Given
    json_body = json.dumps({
        "supplier": "NOT_A_VALID_SUPPLIER",
        "batchId": "1",
        "batchQuantity": 3,
        "row": "test|example",
        "packCode": "EXAMPLE_LETTER"
    }).encode()
    actual_hash = hashlib.sha256(json_body).hexdigest()
    mock_channel = Mock()
    mock_method = Mock()
    mock_properties = Mock()
    mock_properties.message_id = 'mock_message_id'

    # When
    print_message_callback(mock_channel, mock_method, mock_properties, json_body, cleanup_test_files.partial_files)

    # Then
    mock_channel.basic_nack.assert_called_with(delivery_tag=mock_method.delivery_tag, requeue=False)
    mock_channel.basic_ack.assert_not_called()
    assert 'Could not process message' in caplog.text
    assert f'"message_hash": "{actual_hash}"' in caplog.text
    assert 'MalformedMessageError' in caplog.text


@patch('app.message_listener.RabbitContext')
def test_start_message_listener_queues_ready(_patch_rabbit):
    # Given
    readiness_queue = Queue()

    # When
    start_message_listener(readiness_queue)

    # Then
    assert readiness_queue.get(timeout=1)


def test_invalid_json_messages_are_nacked(cleanup_test_files, init_logger, caplog):
    # Given
    invalid_json_body = b"not_valid_json"
    actual_hash = hashlib.sha256(invalid_json_body).hexdigest()
    mock_channel = Mock()
    mock_method = Mock()
    mock_properties = Mock()
    mock_properties.message_id = 'mock_message_id'

    # When
    print_message_callback(mock_channel, mock_method, mock_properties, invalid_json_body,
                           cleanup_test_files.partial_files)

    # Then
    mock_channel.basic_nack.assert_called_with(delivery_tag=mock_method.delivery_tag, requeue=False)
    mock_channel.basic_ack.assert_not_called()
    assert 'Could not process message' in caplog.text
    assert f'"message_hash": "{actual_hash}"' in caplog.text
    assert 'JSONDecodeError' in caplog.text
