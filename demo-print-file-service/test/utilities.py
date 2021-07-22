import pgpy


def decrypt_message(message, key_file_path, key_passphrase):
    key, _ = pgpy.PGPKey.from_file(key_file_path)
    with key.unlock(key_passphrase):
        encrypted_text_message = pgpy.PGPMessage.from_blob(message)
        message_text = key.decrypt(encrypted_text_message)
        return message_text.message
