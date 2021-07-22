import logging
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Collection, Iterable

from google.cloud import storage
from structlog import wrap_logger

import app.sftp_utilities as sftp
from app.encryption import pgp_encrypt_message
from app.manifest_file_builder import generate_manifest_file
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def process_complete_file(complete_partial_file: Path, pack_code, supplier, context_logger):
    context_logger.info("Going to encrypt file: ", file_name=str(complete_partial_file))

    encrypted_print_file, manifest_file = encrypt_file_and_write_manifest(complete_partial_file, pack_code, supplier,
                                                                          context_logger)
    temporary_files_paths = [encrypted_print_file, manifest_file]

    context_logger.info('Sending files to SFTP', file_paths=list(map(str, temporary_files_paths)))

    try:
        copy_files_to_sftp(temporary_files_paths, sftp.get_supplier_sftp_directory(supplier), context_logger)
    except Exception as ex:
        context_logger.error('Failed to send files to SFTP', file_paths=list(map(str, temporary_files_paths)))
        context_logger.warn('Deleting failed encrypted and manifest print files',
                            file_paths=list(map(str, temporary_files_paths)))
        delete_local_files(temporary_files_paths)
        raise ex

    context_logger.info('Successfully sent print files to SFTP', file_paths=list(map(str, temporary_files_paths)))
    context_logger.info('Deleting partial files', file_paths=list(map(str, [complete_partial_file])))
    delete_local_files([complete_partial_file])

    upload_files_to_bucket(manifest_file, encrypted_print_file, context_logger)

    context_logger.info('Deleting temporary files', file_paths=list(map(str, temporary_files_paths)))
    delete_local_files(temporary_files_paths)

    # Wait for a second so there is no chance of reusing the same file name
    sleep(1)


def encrypt_file_and_write_manifest(complete_partial_file: Path, pack_code, supplier, context_logger):
    context_logger.info('Encrypting print file')
    encrypted_print_file, filename = encrypt_print_file(complete_partial_file, pack_code, supplier)

    manifest_file = Config.ENCRYPTED_FILES_DIRECTORY.joinpath(f'{filename}.manifest')
    context_logger.info('Creating manifest for print file', manifest_file=manifest_file.name)

    row_count = get_metadata_from_partial_file_name(complete_partial_file.name)[3]
    generate_manifest_file(manifest_file, encrypted_print_file, pack_code, supplier, row_count)

    return encrypted_print_file, manifest_file


def encrypt_print_file(print_file, pack_code, supplier):
    encrypted_message = pgp_encrypt_message(print_file.read_text(), supplier)
    filename = f'{pack_code}_{datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")}'
    encrypted_print_file = Config.ENCRYPTED_FILES_DIRECTORY.joinpath(f'{filename}.csv.gpg')
    logger.info('Writing encrypted file', file_name=encrypted_print_file.name)
    encrypted_print_file.write_text(encrypted_message)
    return encrypted_print_file, filename


def delete_local_files(file_paths: Iterable[Path]):
    for file_path in file_paths:
        file_path.unlink()


def quarantine_partial_file(partial_file_path: Path):
    quarantine_destination = Config.QUARANTINED_FILES_DIRECTORY.joinpath(partial_file_path.name)
    partial_file_path.replace(quarantine_destination)
    logger.warn('Quarantined partial print file', quarantined_file_path=str(quarantine_destination))


def check_partial_files(partial_files_dir: Path):
    for partial_file in partial_files_dir.iterdir():
        supplier, pack_code, batch_id, batch_quantity = get_metadata_from_partial_file_name(partial_file.name)
        actual_number_of_lines = sum(1 for _ in partial_file.open())
        if batch_quantity == actual_number_of_lines:
            context_logger = logger.bind(supplier=supplier,
                                         pack_code=pack_code,
                                         batch_id=batch_id,
                                         batch_quantity=batch_quantity)

            if not check_partial_has_no_duplicates(partial_file, context_logger):
                context_logger.warn('Quarantining print file with duplicates')
                quarantine_partial_file(partial_file)
                return
            else:
                context_logger.info('File has no duplicates, beginning processing')
            process_complete_file(partial_file, pack_code, supplier, context_logger)


def get_metadata_from_partial_file_name(partial_file_name: str):
    supplier, pack_code, batch_id, batch_quantity = partial_file_name.split('.')
    return supplier, pack_code, batch_id, int(batch_quantity)


def start_file_sender(readiness_queue):
    logger.info('Testing connection to SFTP target directories')
    for supplier in Config.SUPPLIERS_CONFIG.keys():
        with sftp.SftpUtility(sftp_directory := sftp.get_supplier_sftp_directory(supplier)):
            logger.info('Successfully connected to supplier directory', supplier=supplier,
                        sftp_directory=sftp_directory)

    check_gcp_bucket_ready()

    readiness_queue.put(True)

    logger.info('Started file sender')
    while True:
        check_partial_files(Config.PARTIAL_FILES_DIRECTORY)
        sleep(Config.FILE_POLLING_DELAY_SECONDS)


def check_gcp_bucket_ready():
    if not Config.SENT_PRINT_FILE_BUCKET:
        logger.warn('SENT_PRINT_FILE_BUCKET set to empty, skipping uploading files to GCP')
        return

    logger.info('Testing connection to print file bucket', bucket_name=Config.SENT_PRINT_FILE_BUCKET)
    try:
        storage.Client().get_bucket(Config.SENT_PRINT_FILE_BUCKET)
    except Exception:
        logger.exception('Print file upload bucket cannot be accessed', bucket_name=Config.SENT_PRINT_FILE_BUCKET)
        return
    logger.info('Successfully got print file bucket', bucket_name=Config.SENT_PRINT_FILE_BUCKET)


def copy_files_to_sftp(file_paths: Collection[Path], remote_directory, context_logger):
    with sftp.SftpUtility(remote_directory) as sftp_client:
        context_logger.info('Copying files to SFTP remote', sftp_directory=sftp_client.sftp_directory)
        for file_path in file_paths:
            sftp_client.put_file(local_path=str(file_path), filename=file_path.name)

        context_logger.info(f'All {len(file_paths)} files successfully written to SFTP remote',
                            sftp_directory=sftp_client.sftp_directory,
                            file_names=[str(file_path.name) for file_path in file_paths])


def upload_files_to_bucket(manifest_file: Path, encrypted_print_file: Path, context_logger):
    if not Config.SENT_PRINT_FILE_BUCKET:
        context_logger.warn('SENT_PRINT_FILE_BUCKET set to empty, skipping uploading files to GCP')
        return

    context_logger.info('Copying files to GCP Bucket', sent_print_files_bucket=Config.SENT_PRINT_FILE_BUCKET,
                        file_name=encrypted_print_file.name)

    write_file_to_bucket(manifest_file)
    write_file_to_bucket(encrypted_print_file)


def write_file_to_bucket(file_path: Path):
    try:
        bucket = storage.Client().get_bucket(Config.SENT_PRINT_FILE_BUCKET)
        bucket.blob(file_path.name).upload_from_filename(filename=str(file_path))
    except Exception:
        logger.exception('File upload to GCS bucket failed', sent_print_files_bucket=Config.SENT_PRINT_FILE_BUCKET,
                         file_name=file_path.name)


def check_partial_has_no_duplicates(partial_file_path: Path, context_logger):
    context_logger.info('Checking complete file for duplicate rows')
    rows = set()
    with open(partial_file_path) as partial_file:
        for line_number, row in enumerate(partial_file, 1):
            if row in rows:
                context_logger.error('Duplicate row found in print file',
                                     line_number=line_number)
                return False
            rows.add(row)
    context_logger.info('Finished checking for duplicates')
    return True
