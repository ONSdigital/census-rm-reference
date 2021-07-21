import pgpy

from app.exceptions import EncryptionFailedException
from config import Config


def pgp_encrypt_message(message, supplier):
    # A key can be loaded from a file, like so:
    our_key, _ = pgpy.PGPKey.from_file(Config.OUR_PUBLIC_KEY_PATH)
    supplier_key, _ = pgpy.PGPKey.from_file(get_encryption_key_path(supplier))

    # this creates a standard message from text
    # it will also be compressed, by default with ZIP DEFLATE, unless otherwise specified
    text_message = pgpy.PGPMessage.new(message)

    cipher = pgpy.constants.SymmetricKeyAlgorithm.AES256
    sessionkey = cipher.gen_key()

    # encrypt the message to multiple recipients
    encrypted_message_v1 = our_key.encrypt(text_message, cipher=cipher, sessionkey=sessionkey)
    encrypted_message_v2 = supplier_key.encrypt(encrypted_message_v1, cipher=cipher, sessionkey=sessionkey)

    # do at least this as soon as possible after encrypting to the final recipient
    del sessionkey

    if encrypted_message_v2.is_encrypted:
        return str(encrypted_message_v2)
    raise EncryptionFailedException


def get_encryption_key_path(supplier):
    return Config.SUPPLIER_KEY_DIRECTORY.joinpath(Config.SUPPLIERS_CONFIG[supplier]['encryptionKeyFilename'])
