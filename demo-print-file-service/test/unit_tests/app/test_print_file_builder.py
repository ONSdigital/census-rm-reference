import json

import pytest

from app.exceptions import MalformedMessageError
from app.print_file_builder import generate_print_row
from config import TestConfig

pack_code = 'EXAMPLE_LETTER'
supplier = list(TestConfig.SUPPLIERS_CONFIG.keys())[0]


def test_generate_print_row(cleanup_test_files):
    # Given
    row = 'test|data|example'
    json_body = json.dumps({
        "packCode": pack_code,
        "printSupplier": supplier,
        "batchId": "1",
        "batchQuantity": 1,
        "row": row
    })

    # When
    generate_print_row(json_body, cleanup_test_files.partial_files, TestConfig.SUPPLIERS_CONFIG)

    # Then
    generated_print_file = cleanup_test_files.partial_files.joinpath(f'{supplier}.{pack_code}.1.1')
    assert generated_print_file.read_text() == (row + '\n')


def test_generate_print_row_invalid_supplier(cleanup_test_files):
    # Given
    json_body = json.dumps({
        "packCode": pack_code,
        "supplier": "NOT_A_VALID_SUPPLIER",
        "batchId": "1",
        "batchQuantity": 3,
        "row": "test|example",
    })

    # When/Then
    with pytest.raises(MalformedMessageError):
        generate_print_row(json_body, cleanup_test_files.partial_files, TestConfig.SUPPLIERS_CONFIG)
