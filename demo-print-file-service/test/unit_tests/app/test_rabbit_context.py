from unittest.mock import patch

from app.rabbit_context import RabbitContext


@patch('app.rabbit_context.pika')
def test_context_manager_opens_connection_and_channel(patch_pika):
    with RabbitContext():
        patch_pika.BlockingConnection.assert_called_once()
        patch_pika.BlockingConnection.return_value.channel.assert_called_once()


@patch('app.rabbit_context.pika')
def test_context_manager_closes_connection(patch_pika):
    with RabbitContext():
        pass
    patch_pika.BlockingConnection.return_value.close.assert_called_once()
