from datetime import datetime

import paramiko
import pgpy

from config import Config


class SftpUtility:
    def __init__(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_client.connect(hostname=Config.SFTP_HOST,
                                port=int(Config.SFTP_PORT),
                                username=Config.SFTP_USERNAME,
                                key_filename=Config.SFTP_KEY_FILENAME,
                                passphrase=Config.SFTP_PASSPHRASE,
                                look_for_keys=False,
                                timeout=120)

    def __enter__(self):
        self._sftp_client = self.ssh_client.open_sftp()
        return self

    def __exit__(self, *_):
        self.ssh_client.close()

    def get_all_files_after_time(self, period_start_time, prefix, supplier, suffix=""):
        files = self._sftp_client.listdir_attr(supplier)
        period = period_start_time.strftime('%Y-%m-%d')

        return [
            _file for _file in files
            if f'{prefix}_{period}' in _file.filename
               and _file.filename.startswith(prefix)
               and _file.filename.endswith(suffix)
               and period_start_time <= datetime.fromtimestamp(_file.st_mtime)
        ]

    def get_files_content_as_list(self, files, prefix, supplier):
        actual_content = []

        for _file in files:
            file_path = f'{supplier}{_file.filename}'
            content_list = self._get_file_lines_as_list(file_path)
            actual_content.extend(content_list)

        return actual_content

    def _get_file_lines_as_list(self, file_path):
        with self._sftp_client.open(file_path) as sftp_file:
            content = sftp_file.read().decode('utf-8')
            decrypted_content = self.decrypt_message(content)
            return decrypted_content.rstrip().split('\n')

    def decrypt_message(self, message):
        our_key, _ = pgpy.PGPKey.from_file('dummy-key-ssdc-rm-private.asc')
        with our_key.unlock('test'):
            encrypted_text_message = pgpy.PGPMessage.from_blob(message)
            message_text = our_key.decrypt(encrypted_text_message)

            return message_text.message
