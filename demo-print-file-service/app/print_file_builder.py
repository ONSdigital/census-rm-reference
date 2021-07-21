import json
import logging
from pathlib import Path
from typing import Dict

from structlog import wrap_logger

from app.exceptions import MalformedMessageError

logger = wrap_logger(logging.getLogger(__name__))


def generate_print_row(json_body: str, partial_files_directory: Path, suppliers_config: Dict):
    print_message = json.loads(json_body)
    supplier, pack_code, batch_id, batch_quantity, row = read_print_message(print_message)
    validate_supplier(supplier, suppliers_config)
    logger.debug('Appending print file line from message', supplier=supplier, pack_code=pack_code,
                 batch_quantity=batch_quantity, batch_id=batch_id)
    partial_print_file = partial_files_directory.joinpath(build_filename(supplier, pack_code, batch_id, batch_quantity))
    append_print_row(print_message, partial_print_file)


def build_filename(supplier, pack_code, batch_id, batch_quantity):
    return '.'.join((supplier, pack_code, batch_id, str(batch_quantity)))


def append_print_row(print_message, partial_print_file: Path):
    with open(partial_print_file, 'a') as print_file_append:
        print_file_append.write(print_message['row'] + '\n')


def read_print_message(print_message):
    try:
        supplier = print_message['printSupplier']
        pack_code = print_message['packCode']
        batch_id = print_message['batchId']
        batch_quantity = int(print_message['batchQuantity'])
        row = print_message['row']
    except (ValueError, KeyError) as e:
        raise MalformedMessageError(e)
    return supplier, pack_code, batch_id, batch_quantity, row


def validate_supplier(supplier, suppliers_config: Dict):
    if supplier not in suppliers_config.keys():
        raise MalformedMessageError(f'Received invalid supplier: {supplier}')
