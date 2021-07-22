from pathlib import Path
from time import sleep

import pytest

from config import TestConfig
from test.integration_tests.utilities import build_test_messages, send_test_messages

QUARANTINED_FILES_DIRECTORY = Path(__file__).parents[2].joinpath('working_files',
                                                                 'quarantined_files')
supplier = list(TestConfig.SUPPLIERS_CONFIG)[0]
pack_code = 'EXAMPLE_LETTER'


def test_file_with_duplicate_rows_is_quarantined():
    # Given
    quantity = 3
    messages, batch_id = build_test_messages(quantity, supplier, pack_code)

    # Overwrite one of the test messages to be a duplicate
    messages[2] = messages[0]

    expected_quarantined_file = '\n'.join(message['row'] for message in messages) + '\n'

    # When
    send_test_messages(messages)

    # Then
    actual_quarantined_file = QUARANTINED_FILES_DIRECTORY.joinpath(f'{supplier}.{pack_code}.{batch_id}.{quantity}')
    wait_for_quarantined_file(actual_quarantined_file)
    assert actual_quarantined_file.read_text() == expected_quarantined_file


def wait_for_quarantined_file(expected_quarantined_file, max_attempts=10):
    for _attempt in range(max_attempts):
        if expected_quarantined_file.exists():
            break
        sleep(1)
    else:
        pytest.fail('Reached max attempts before file was quarantined created')
