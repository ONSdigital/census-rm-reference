import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, call, patch

import paramiko
import pytest
from google.cloud import exceptions

from app.file_sender import check_gcp_bucket_ready, check_partial_files, check_partial_has_no_duplicates, \
    copy_files_to_sftp, \
    process_complete_file, quarantine_partial_file, upload_files_to_bucket, write_file_to_bucket
from app.manifest_file_builder import generate_manifest_file
from config import TestConfig
from test.unit_tests import RESOURCE_FILE_PATH


def test_copy_files_to_sftp():
    # Given
    test_files = [Path('test1'), Path('test2'), Path('test3')]
    os.environ['SFTP_DIRECTORY'] = 'test_path'
    mock_storage_client = Mock()
    context_logger = Mock()

    # When
    with patch('app.file_sender.sftp.paramiko.SSHClient') as client:
        client.return_value.open_sftp.return_value = mock_storage_client  # mock the sftp client connection
        mock_storage_client.stat.return_value.st_mode = paramiko.sftp_client.stat.S_IFDIR  # mock directory exists
        copy_files_to_sftp(test_files, 'testdir', context_logger)

    mock_put_file = mock_storage_client.put

    # Then
    mock_put_file.assert_has_calls(
        [call(str(file_path), file_path.name) for file_path in test_files])


def test_processing_complete_file_uploads_correct_files(cleanup_test_files):
    complete_file_path = Path(shutil.copyfile(RESOURCE_FILE_PATH.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.1'),
                                              TestConfig.PARTIAL_FILES_DIRECTORY.joinpath(
                                                  'SUPPLIER_A.EXAMPLE_LETTER.1.1')))
    context_logger = Mock()
    with patch('app.file_sender.sftp.SftpUtility') as patched_sftp, patch('app.file_sender.datetime') as patch_datetime:
        mock_time = datetime(2019, 1, 1, 7, 6, 5)
        patch_datetime.utcnow.return_value = mock_time
        process_complete_file(complete_file_path, 'EXAMPLE_LETTER', 'SUPPLIER_A', context_logger)

    put_sftp_call_kwargs = [kwargs for _, kwargs in
                            patched_sftp.return_value.__enter__.return_value.put_file.call_args_list]

    iso_mocked = mock_time.strftime("%Y-%m-%dT%H-%M-%S")

    assert put_sftp_call_kwargs[0]['local_path'] == str(
        cleanup_test_files.encrypted_files.joinpath(f'EXAMPLE_LETTER_{iso_mocked}.csv.gpg'))
    assert put_sftp_call_kwargs[0]['filename'] == f'EXAMPLE_LETTER_{iso_mocked}.csv.gpg'
    assert put_sftp_call_kwargs[1]['local_path'] == str(
        cleanup_test_files.encrypted_files.joinpath(f'EXAMPLE_LETTER_{iso_mocked}.manifest'))
    assert put_sftp_call_kwargs[1]['filename'] == f'EXAMPLE_LETTER_{iso_mocked}.manifest'


def test_local_files_are_deleted_after_upload(cleanup_test_files):
    complete_file_path = Path(shutil.copyfile(RESOURCE_FILE_PATH.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.1'),
                                              TestConfig.PARTIAL_FILES_DIRECTORY.joinpath(
                                                  'SUPPLIER_A.EXAMPLE_LETTER.1.1')))
    context_logger = Mock()
    with patch('app.file_sender.sftp.SftpUtility'):
        process_complete_file(complete_file_path, 'EXAMPLE_LETTER', 'SUPPLIER_A', context_logger)

    with pytest.raises(StopIteration):
        next(TestConfig.PARTIAL_FILES_DIRECTORY.iterdir())
    with pytest.raises(StopIteration):
        next(TestConfig.ENCRYPTED_FILES_DIRECTORY.iterdir())


def test_generating_manifest_file(cleanup_test_files):
    manifest_file = cleanup_test_files.encrypted_files.joinpath('EXAMPLE_LETTER_2019-07-05T08-15-41.manifest')
    print_file = RESOURCE_FILE_PATH.joinpath('EXAMPLE_LETTER_2021-06-01T08-15-41.csv.gpg')
    generate_manifest_file(manifest_file, print_file, 'EXAMPLE_LETTER', 'SUPPLIER_A', row_count=10)

    manifest_json = json.loads(manifest_file.read_text())

    assert manifest_json['sourceName'] == 'ONS_RM'
    assert manifest_json['packCode'] == 'EXAMPLE_LETTER'
    assert manifest_json['supplier'] == 'SUPPLIER_A'
    assert manifest_json['files'][0]['rows'] == 10


def test_check_partial_has_no_duplicates_with_duplicates(cleanup_test_files):
    # Given
    partial_duplicate_path = RESOURCE_FILE_PATH.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.2.duplicate_row')
    mock_logger = Mock()

    # When
    result = check_partial_has_no_duplicates(partial_duplicate_path, mock_logger)

    # Then
    assert not result, 'Check should return False for file with duplicates'
    mock_logger.error.assert_called_once_with('Duplicate row found in print file', line_number=2)


def test_check_partial_has_no_duplicates_without_duplicates(cleanup_test_files):
    # Given
    partial_duplicate_path = RESOURCE_FILE_PATH.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.2')

    # When
    result = check_partial_has_no_duplicates(partial_duplicate_path, Mock())

    # Then
    assert result


def test_quarantine_partial_file(cleanup_test_files):
    # Given
    partial_print_file = Path(
        shutil.copyfile(RESOURCE_FILE_PATH.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.2.duplicate_row'),
                        TestConfig.PARTIAL_FILES_DIRECTORY.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.2')))
    partial_print_file_text = partial_print_file.read_text()
    expected_destination = Path(TestConfig.QUARANTINED_FILES_DIRECTORY.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.2'))

    # When
    quarantine_partial_file(partial_print_file)

    # Then
    assert not partial_print_file.exists()
    assert expected_destination.exists()
    assert expected_destination.read_text() == partial_print_file_text


def test_failed_encrypted_files_and_manifests_are_deleted(cleanup_test_files):
    # Given
    complete_file_path = Path(shutil.copyfile(RESOURCE_FILE_PATH.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.1'),
                                              TestConfig.PARTIAL_FILES_DIRECTORY.joinpath(
                                                  'SUPPLIER_A.EXAMPLE_LETTER.1.1')))
    context_logger = Mock()
    sftp_failure_exception_message = 'Simulate SFTP transfer failure'

    def simulate_sftp_failure(*_args, **_kwargs):
        raise Exception(sftp_failure_exception_message)

    with patch('app.file_sender.sftp.paramiko.SSHClient') as client, \
            pytest.raises(Exception) as raised_exception:
        client.return_value.open_sftp.side_effect = simulate_sftp_failure

        # When
        process_complete_file(complete_file_path, 'EXAMPLE_LETTER', 'SUPPLIER_A', context_logger)

    if not str(raised_exception.value) == sftp_failure_exception_message:
        raise raised_exception.value

    # Then
    # Check encrypted_files_directory is empty
    assert not any(cleanup_test_files.encrypted_files.iterdir())

    # Check complete partial file is still there
    assert complete_file_path.exists()

    # Check original exception is re-raised
    assert str(raised_exception.value) == sftp_failure_exception_message


def test_check_partial_files_processes_complete_file(cleanup_test_files):
    # Given
    partial_file_path = Path(cleanup_test_files.partial_files.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.1'))
    partial_file_path.touch()

    mock_storage_client = Mock()

    # When
    with patch('app.file_sender.sftp.paramiko.SSHClient') as client:
        client.return_value.open_sftp.return_value = mock_storage_client  # mock the sftp client connection
        mock_storage_client.stat.return_value.st_mode = paramiko.sftp_client.stat.S_IFDIR  # mock directory exists

        check_partial_files(cleanup_test_files.partial_files)
        client.assert_not_called()

        Path(shutil.copyfile(RESOURCE_FILE_PATH.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.1'),
                             cleanup_test_files.partial_files.joinpath('SUPPLIER_A.EXAMPLE_LETTER.1.1')))
        check_partial_files(cleanup_test_files.partial_files)

    # Then
    client.assert_called_once()


def test_failing_write_to_gcp_bucket_is_handled():
    # When
    with patch('app.file_sender.storage.Client') as bucket_client:
        # Simulate an error from the GCS storage client
        bucket_client.side_effect = exceptions.GoogleCloudError("bucket doesn't exist")

        try:
            write_file_to_bucket(RESOURCE_FILE_PATH.joinpath('dummy_print_file.txt'))
        except Exception:
            assert False, "Exception msgs from writing to GCP bucket should be handled"


def test_write_to_gcp_bucket():
    # Given
    test_printfile = Path('test1')
    test_manifest_file = Path('test2')
    mock_storage_client = Mock()
    mock_bucket = Mock()
    context_logger = Mock()

    # When
    with patch('app.file_sender.storage') as google_storage, \
            patch('app.file_sender.Config') as config:
        config.SENT_PRINT_FILE_BUCKET = 'test'
        google_storage.Client.return_value = mock_storage_client  # mock the cloud client
        mock_storage_client.get_bucket.return_value = mock_bucket

        upload_files_to_bucket(test_printfile, test_manifest_file, context_logger)

    mock_write_file = mock_bucket.blob

    # Then
    mock_write_file.assert_has_calls(
        [call('test1'), call().upload_from_filename(filename='test1'), call('test2'),
         call().upload_from_filename(filename='test2')])


def test_gcp_bucket_ready_value_not_set():
    with patch('app.file_sender.storage') as google_storage:
        check_gcp_bucket_ready()

    google_storage.assert_not_called()


def test_gcp_bucket_ready_successful():
    mock_storage_client = Mock()
    mock_bucket = Mock()

    with patch('app.file_sender.storage') as google_storage, \
            patch('app.file_sender.Config') as config:
        config.SENT_PRINT_FILE_BUCKET = 'test'
        google_storage.Client.return_value = mock_storage_client  # mock the cloud client
        mock_storage_client.get_bucket.return_value = mock_bucket
        check_gcp_bucket_ready()

    mock_storage_client.get_bucket.assert_called_once()


def test_failing_check_of_gcp_bucket_is_handled():
    # When
    with patch('app.file_sender.storage.Client') as bucket_client:
        bucket_client.side_effect = exceptions.GoogleCloudError("bucket doesn't exist")

        try:
            check_gcp_bucket_ready()
        except Exception:
            assert False, "Exception msgs when checking GCP bucket should be handled"
