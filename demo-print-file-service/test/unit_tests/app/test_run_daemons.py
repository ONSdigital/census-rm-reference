import queue
from unittest.mock import patch, ANY

import pytest

from app.run_daemons import run_daemons
from app.exceptions import DaemonStartupError


@patch('app.run_daemons.multiprocessing.Process')
@patch('app.run_daemons.multiprocessing.Manager')
def test_sftp_failure_blocks_app_startup(patched_manager, _patched_process):
    # Given
    # Message listener starts first so fail on the second start
    call_count = 0

    def first_true_then_raise_queue_empty(*_args, **_kwargs):
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            return True
        else:
            raise queue.Empty

    patched_manager.return_value.Queue.return_value.get.side_effect = first_true_then_raise_queue_empty

    # When
    with pytest.raises(DaemonStartupError) as err:
        run_daemons()

    # Then
    assert str(err.value) == 'Error starting daemon: [file-sender]'


@patch('app.run_daemons.multiprocessing.Process')
@patch('app.run_daemons.multiprocessing.Manager')
def test_rabbit_connection_failure_blocks_app_startup(patched_manager, _patched_process):
    # Given
    patched_manager.return_value.Queue.return_value.get.side_effect = raise_queue_empty

    # When
    with pytest.raises(DaemonStartupError) as err:
        run_daemons()

    # Then
    assert str(err.value) == 'Error starting daemon: [message-listener]'


@patch('app.run_daemons.multiprocessing.Manager')
@patch('app.run_daemons.multiprocessing.Process')
@patch('app.run_daemons.retry_run_daemon')
def test_message_listener_restarts_on_error(patched_retry_run_daemon, patched_process, patched_manager):
    # Given
    patched_manager.return_value.Queue.return_value.get.return_value = True
    patched_process.return_value.is_alive.return_value = False

    # Raise an exception to break out of the infinite loop
    patched_retry_run_daemon.side_effect = raise_exception

    # When
    with pytest.raises(Exception):
        run_daemons()

    # Then
    patched_retry_run_daemon.assert_called_once_with(ANY, 'message-listener', ANY)


@patch('app.run_daemons.multiprocessing.Manager')
@patch('app.run_daemons.multiprocessing.Process')
@patch('app.run_daemons.retry_run_daemon')
def test_file_sender_restarts_on_error(patched_retry_run_daemon, patched_process, patched_manager):
    # Given
    patched_manager.return_value.Queue.return_value.get.return_value = True

    # is_alive is called for the message listener first, so return False on the second call
    patched_process.return_value.is_alive.side_effect = (True, False)

    # Raise an exception to break out of the infinite loop
    patched_retry_run_daemon.side_effect = raise_exception

    # When
    with pytest.raises(Exception):
        run_daemons()

    # Then
    patched_retry_run_daemon.assert_called_once_with(ANY, 'file-sender', ANY)


def raise_exception(*_, **_kwargs):
    raise Exception('An error happened')


def raise_queue_empty(*_args, **_kwargs):
    raise queue.Empty
