from pathlib import Path

import pytest

from app.encryption import pgp_encrypt_message
from test.utilities import decrypt_message

DUMMY_KEYS_PATH = Path(__file__).parents[3].joinpath('dummy_keys')


@pytest.mark.parametrize("supplier, supplier_key_path, supplier_passphrase",
                         [('SUPPLIER_A', DUMMY_KEYS_PATH.joinpath('dummy-key-supplier-a-private.asc'), 'test'),
                          ('SUPPLIER_B', DUMMY_KEYS_PATH.joinpath('dummy-key-supplier-b-private.asc'), 'test')])
def test_pgp_encrypt_message(supplier, supplier_key_path, supplier_passphrase):
    # Given
    message = 'test_message'

    # When
    encrypted_message = pgp_encrypt_message(message, supplier)

    # Then
    supplier_decrypted_message = decrypt_message(encrypted_message,
                                                 supplier_key_path,
                                                 supplier_passphrase)

    rm_decrypted_message = decrypt_message(encrypted_message,
                                           DUMMY_KEYS_PATH.joinpath('dummy-key-ssdc-rm-private.asc'),
                                           'test')

    assert supplier_decrypted_message == message, 'Supplier key should be able to decrypt the message'
    assert rm_decrypted_message == message, 'RM key should be able to decrypt the message'
