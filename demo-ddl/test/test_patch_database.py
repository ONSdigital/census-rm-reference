from pathlib import Path
from unittest.mock import Mock

import pytest

from patch_database import patch_database


def test_patch_database():
    # Given
    mock_db_connection = Mock()
    mock_db_cursor = Mock()
    patches_directory = Path(__file__).parent.joinpath('patches')
    target_version = "test_2"

    # return '1' when from the mock as the max applied patch number
    mock_db_cursor.fetchone.return_value = (1,)

    # When
    patch_database(patches_directory, target_version, mock_db_cursor, mock_db_connection)

    # Then
    cursor_execute_calls = mock_db_cursor.execute.call_args_list
    insert_patch_number_sql_template = ('INSERT INTO ddl_version.patches (patch_number, applied_timestamp)'
                                        ' VALUES (%(patch_number)s, %(applied_timestamp)s)')
    assert cursor_execute_calls[0][0][0] == 'SELECT MAX(patch_number) FROM ddl_version.patches'

    # The last applied patch number is 1 so it should start on the patch "2_test.sql"
    assert cursor_execute_calls[1][0][0] == 'THIS SHOULD BE THE FIRST PATCH APPLIED'
    assert cursor_execute_calls[2][0][0] == insert_patch_number_sql_template
    assert cursor_execute_calls[2][0][1]['patch_number'] == 2
    assert cursor_execute_calls[3][0][0] == 'THIS SHOULD BE THE SECOND PATCH APPLIED'
    assert cursor_execute_calls[4][0][0] == insert_patch_number_sql_template
    assert cursor_execute_calls[4][0][1]['patch_number'] == 3
    assert cursor_execute_calls[5][0][0] == ("INSERT INTO ddl_version.version (version_tag, updated_timestamp)"
                                             " VALUES (%(version)s, %(updated_timestamp)s)")
    assert cursor_execute_calls[5][0][1]['version'] == target_version
    assert len(cursor_execute_calls) == 6
    mock_db_connection.commit.assert_called_once()


def test_patch_database_fails_gracefully():
    # Given
    mock_db_connection = Mock()
    mock_db_cursor = Mock()
    patches_directory = Path(__file__).parent.joinpath('patches')
    target_version = "test_2"
    mock_db_cursor.fetchone.return_value = (1,)

    execute_call_count = 0
    test_exception_message = 'exception raised by test side effect'

    def run_once_then_raise(*_1, **_2):
        nonlocal execute_call_count
        if execute_call_count >= 1:
            raise Exception(test_exception_message)
        execute_call_count += 1

    # Raise an exception on the second call to execute
    mock_db_cursor.execute.side_effect = run_once_then_raise

    # When
    with pytest.raises(Exception) as ex:
        patch_database(patches_directory, target_version, mock_db_cursor, mock_db_connection)

    # Then
    # First call is to check the patch number, it should raise the exception on the second
    cursor_execute_calls = mock_db_cursor.execute.call_args_list
    assert len(cursor_execute_calls) == 2

    assert ex.value.args[0] == test_exception_message
    mock_db_connection.commit.assert_not_called()
    mock_db_connection.rollback.assert_called_once()


def test_patch_database_no_changes_to_apply():
    # Given
    mock_db_connection = Mock()
    mock_db_cursor = Mock()
    patches_directory = Path(__file__).parent.joinpath('patches')
    target_version = "test_2"

    # return 3 as the last applied patch number so there are no newer patches to apply
    mock_db_cursor.fetchone.return_value = (3,)

    # When
    patch_database(patches_directory, target_version, mock_db_cursor, mock_db_connection)

    # Then
    mock_db_cursor.execute.assert_called_once_with('SELECT MAX(patch_number) FROM ddl_version.patches')
    mock_db_connection.commit.assert_not_called()
