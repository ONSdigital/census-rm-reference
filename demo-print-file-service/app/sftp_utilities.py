import logging
from contextlib import suppress

import paramiko
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


class SftpUtility:

    def __init__(self, remote_directory):
        self.sftp_directory = remote_directory
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
        if not self.sftp_directory_exists:
            logger.info('Recursively creating new directory on SFTP remote', sftp_directory=self.sftp_directory)
            sftp_dirs = self.sftp_directory.split('/')
            parent = ''
            for sftp_dir in sftp_dirs:
                parent += '/' + sftp_dir
                with suppress(IOError):
                    self._sftp_client.mkdir(parent)
        self._sftp_client.chdir(self.sftp_directory)
        return self

    def __exit__(self, *_):
        self.ssh_client.close()

    def put_file(self, local_path, filename):
        self._sftp_client.put(local_path, filename)

    @property
    def sftp_directory_exists(self):
        try:
            return paramiko.sftp_client.stat.S_ISDIR(self._sftp_client.stat(self.sftp_directory).st_mode)
        except IOError:
            return False


def get_supplier_sftp_directory(supplier):
    return Config.SUPPLIERS_CONFIG[supplier]['sftpDirectory']
