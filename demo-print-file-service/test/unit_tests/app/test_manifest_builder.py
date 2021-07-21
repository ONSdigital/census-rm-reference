from datetime import datetime
from unittest.mock import patch

from app.manifest_file_builder import create_manifest
from test.unit_tests import RESOURCE_FILE_PATH


@patch('app.manifest_file_builder.datetime')
def test_create_manifest(patch_datetime):
    # Given
    dummy_print_file = RESOURCE_FILE_PATH.joinpath("dummy_print_file.txt")
    row_count = 100
    pack_code = 'EXAMPLE_LETTER'
    supplier = 'SUPPLIER_A'
    patched_date = datetime.utcnow()
    patch_datetime.utcnow.return_value = patched_date
    expected_manifest = {
        'packCode': pack_code,
        'supplier': supplier,
        'manifestCreated': patched_date.isoformat(timespec='milliseconds') + 'Z',
        'sourceName': 'ONS_RM',
        'files': [
            {
                'name': dummy_print_file.name,
                'relativePath': './',
                'sizeBytes': '19',  # Calculated size of the dummy print file
                'md5sum': '79cad6cda5ebe6b9bdbdbb6a56587e28',  # Calculated md5 of the dummy print file
                'rows': row_count
            }
        ]
    }

    # When
    actual_manifest = create_manifest(dummy_print_file, pack_code, supplier, row_count)

    # Then
    assert expected_manifest == actual_manifest
