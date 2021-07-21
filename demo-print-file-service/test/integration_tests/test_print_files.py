import fnmatch
import json
from pathlib import Path
from time import sleep

import paramiko
import pytest

from app.sftp_utilities import get_supplier_sftp_directory
from config import TestConfig
from test.integration_tests.utilities import build_test_messages, send_test_messages
from test.utilities import decrypt_message

supplier = list(TestConfig.SUPPLIERS_CONFIG)[0]
pack_code = 'EXAMPLE_LETTER'


def test_example_print_file(sftp_client):
    # Given
    test_messages, _ = build_test_messages(10, supplier, pack_code)
    send_test_messages(test_messages)

    # When
    matched_manifest_file, matched_print_file = get_print_and_manifest_filenames(sftp_client,
                                                                                 get_supplier_sftp_directory(supplier),
                                                                                 pack_code)

    # Then
    decrypted_print_file = get_and_check_print_file(
        sftp=sftp_client,
        remote_print_file_path=get_supplier_sftp_directory(supplier) + matched_print_file,
        decryption_key_path=Path(__file__).parents[2].joinpath('dummy_keys',
                                                               'dummy-key-supplier-a-private.asc'),
        decryption_key_passphrase='test',
        expected='\n'.join(message['row'] for message in test_messages) + '\n'
    )

    get_and_check_manifest_file(sftp=sftp_client,
                                remote_manifest_path=get_supplier_sftp_directory(supplier) + matched_manifest_file,
                                expected_values={
                                    'packCode': pack_code,
                                    'supplier': supplier,
                                },
                                decrypted_print_file=decrypted_print_file)


def test_our_decryption_key(sftp_client):
    # Given
    test_messages, _ = build_test_messages(1, supplier, pack_code)
    send_test_messages(test_messages)

    # When
    matched_manifest_file, matched_print_file = get_print_and_manifest_filenames(sftp_client,
                                                                                 get_supplier_sftp_directory(supplier),
                                                                                 pack_code)

    # Then
    get_and_check_print_file(
        sftp=sftp_client,
        remote_print_file_path=get_supplier_sftp_directory(supplier) + matched_print_file,
        decryption_key_path=Path(__file__).parents[2].joinpath('dummy_keys',
                                                               'dummy-key-ssdc-rm-private.asc'),
        decryption_key_passphrase='test',
        expected=test_messages[0]['row'] + '\n')


def get_print_and_manifest_filenames(sftp, remote_directory, pack_code, max_attempts=10):
    for _attempt in range(max_attempts):
        matched_print_files = [filename for filename in sftp.listdir(remote_directory)
                               if fnmatch.fnmatch(filename, f'{pack_code}_*.csv.gpg')]
        matched_manifest_files = [filename for filename in sftp.listdir(remote_directory)
                                  if fnmatch.fnmatch(filename, f'{pack_code}_*.manifest')]
        if len(matched_print_files) and len(matched_manifest_files):
            break
        sleep(1)
    else:
        pytest.fail('Reached max attempts before files were created')
    assert len(matched_manifest_files) == 1
    assert len(matched_print_files) == 1
    return matched_manifest_files[0], matched_print_files[0]


def get_and_check_manifest_file(sftp, remote_manifest_path, expected_values, decrypted_print_file):
    with sftp.open(remote_manifest_path) as actual_manifest_file:
        manifest_json = json.loads(actual_manifest_file.read())
    for key, value in expected_values.items():
        assert manifest_json[key] == value
    actual_row_count = len(decrypted_print_file.splitlines())

    assert actual_row_count == manifest_json['files'][0]['rows']
    assert manifest_json['files'][0]['relativePath'] == './'
    assert manifest_json['sourceName'] == 'ONS_RM'


def get_and_check_print_file(sftp, remote_print_file_path, decryption_key_path, decryption_key_passphrase, expected):
    with sftp.open(remote_print_file_path) as actual_print_file:
        decrypted_print_file = decrypt_message(actual_print_file.read(),
                                               decryption_key_path,
                                               decryption_key_passphrase)
    assert decrypted_print_file == expected
    return decrypted_print_file


@pytest.fixture(autouse=True)
def clear_down_sftp_folders():
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=TestConfig.SFTP_HOST,
                       port=int(TestConfig.SFTP_PORT),
                       username=TestConfig.SFTP_USERNAME,
                       key_filename=str(Path(__file__).parents[2].resolve().joinpath(TestConfig.SFTP_KEY_FILENAME)),
                       passphrase=TestConfig.SFTP_PASSPHRASE,
                       look_for_keys=False,
                       timeout=120)
    sftp = ssh_client.open_sftp()

    for supplier_to_clear in TestConfig.SUPPLIERS_CONFIG.keys():
        for file in sftp.listdir(get_supplier_sftp_directory(supplier_to_clear)):
            sftp.remove(get_supplier_sftp_directory(supplier_to_clear) + file)


@pytest.fixture()
def sftp_client():
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=TestConfig.SFTP_HOST,
                       port=int(TestConfig.SFTP_PORT),
                       username=TestConfig.SFTP_USERNAME,
                       key_filename=str(Path(__file__).parents[2].joinpath(TestConfig.SFTP_KEY_FILENAME)),
                       passphrase=TestConfig.SFTP_PASSPHRASE,
                       look_for_keys=False,
                       timeout=120)
    yield ssh_client.open_sftp()
    ssh_client.close()
