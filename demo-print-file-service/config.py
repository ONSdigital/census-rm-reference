import inspect
import json
import os
from pathlib import Path


class ConfigError(Exception):
    pass


class Config:
    RABBIT_QUEUE = os.getenv('RABBIT_QUEUE', 'caseProcessor.printFileSvc.printBatchRow')
    RABBIT_HOST = os.getenv('RABBIT_HOST')
    RABBIT_PORT = os.getenv('RABBIT_PORT', 5672)
    RABBIT_VIRTUALHOST = os.getenv('RABBIT_VIRTUALHOST', '/')
    RABBIT_USERNAME = os.getenv('RABBIT_USERNAME')
    RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD')

    PARTIAL_FILES_DIRECTORY = Path(os.getenv('PARTIAL_FILES_DIRECTORY', 'partial_files/'))
    ENCRYPTED_FILES_DIRECTORY = Path(os.getenv('ENCRYPTED_FILES_DIRECTORY', 'encrypted_files/'))
    QUARANTINED_FILES_DIRECTORY = Path(os.getenv('QUARANTINED_FILES_DIRECTORY', 'quarantined_files/'))
    FILE_POLLING_DELAY_SECONDS = int(os.getenv('FILE_POLLING_DELAY_SECONDS', 10))

    READINESS_FILE_PATH = Path(os.getenv('READINESS_FILE_PATH', 'print-file-service-ready'))

    NAME = os.getenv('NAME', 'demo-print-file-service')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DATE_FORMAT = os.getenv('LOG_DATE_FORMAT', '%Y-%m-%dT%H:%M:%S.%f')
    LOG_LEVEL_PIKA = os.getenv('LOG_LEVEL_PIKA', 'ERROR')
    LOG_LEVEL_PARAMIKO = os.getenv('LOG_LEVEL_PARAMIKO', 'ERROR')

    EXCEPTIONMANAGER_CONNECTION_HOST = os.getenv('EXCEPTIONMANAGER_CONNECTION_HOST')
    EXCEPTIONMANAGER_CONNECTION_PORT = os.getenv('EXCEPTIONMANAGER_CONNECTION_PORT')
    EXCEPTION_MANAGER_URL = f'http://{EXCEPTIONMANAGER_CONNECTION_HOST}:{EXCEPTIONMANAGER_CONNECTION_PORT}'

    SFTP_HOST = os.getenv('SFTP_HOST')
    SFTP_PORT = os.getenv('SFTP_PORT')
    SFTP_USERNAME = os.getenv('SFTP_USERNAME')
    SFTP_KEY_FILENAME = os.getenv('SFTP_KEY_FILENAME')
    SFTP_PASSPHRASE = os.getenv('SFTP_PASSPHRASE')

    OUR_PUBLIC_KEY_PATH = Path(os.getenv('OUR_PUBLIC_KEY_PATH')) if os.getenv('OUR_PUBLIC_KEY_PATH') else None

    SUPPLIER_KEY_DIRECTORY = Path(os.getenv('SUPPLIER_KEY_DIRECTORY')) if os.getenv('SUPPLIER_KEY_DIRECTORY') else None
    SUPPLIER_CONFIG_JSON_PATH = Path(os.getenv('SUPPLIER_CONFIG_JSON_PATH')) if os.getenv(
        'SUPPLIER_CONFIG_JSON_PATH') else None
    SUPPLIERS_CONFIG = json.loads(
        SUPPLIER_CONFIG_JSON_PATH.read_text()) \
        if SUPPLIER_CONFIG_JSON_PATH and SUPPLIER_CONFIG_JSON_PATH.exists() else None

    ENVIRONMENT = os.getenv('ENVIRONMENT', 'PROD')
    SENT_PRINT_FILE_BUCKET = os.getenv('SENT_PRINT_FILE_BUCKET',
                                       '')  # Defaults to an empty string instead of none so that it can be left unset

    @classmethod
    def check_config(cls):
        missing_config_items = set()
        for config_key, config_value in (member for member in inspect.getmembers(cls) if
                                         not inspect.isbuiltin(member) and
                                         not inspect.isroutine(member) and
                                         not member[0].startswith('__') and
                                         not member[0].endswith('__')):
            if config_value is None:
                missing_config_items.add(config_key)
        if missing_config_items:
            raise ConfigError(f'Missing config items: {[item for item in missing_config_items]}')

        cls.check_supplier_config()

    @classmethod
    def check_supplier_config(cls):
        required_supplier_config = {'sftpDirectory', 'encryptionKeyFilename'}

        if not cls.SUPPLIERS_CONFIG:
            raise ConfigError('Supplier config is empty')

        for supplier in cls.SUPPLIERS_CONFIG.values():
            if set(supplier.keys()) != required_supplier_config:
                raise ConfigError('Invalid supplier config')

            encryption_key_file = cls.SUPPLIER_KEY_DIRECTORY.joinpath(supplier.get('encryptionKeyFilename'))
            if not encryption_key_file.exists():
                raise ConfigError(f'Supplier key not found in {encryption_key_file} from configured relative path ')


class DevConfig(Config):
    RABBIT_HOST = os.getenv('RABBIT_HOST', 'localhost')
    RABBIT_PORT = os.getenv('RABBIT_PORT', '6672')
    RABBIT_USERNAME = os.getenv('RABBIT_USERNAME', 'guest')
    RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD', 'guest')

    FILE_POLLING_DELAY_SECONDS = int(os.getenv('FILE_POLLING_DELAY_SECONDS', 1))

    EXCEPTIONMANAGER_CONNECTION_HOST = os.getenv('EXCEPTIONMANAGER_CONNECTION_HOST', 'localhost')
    EXCEPTIONMANAGER_CONNECTION_PORT = os.getenv('EXCEPTIONMANAGER_CONNECTION_PORT', '8666')
    EXCEPTION_MANAGER_URL = f'http://{EXCEPTIONMANAGER_CONNECTION_HOST}:{EXCEPTIONMANAGER_CONNECTION_PORT}'

    SFTP_HOST = os.getenv('SFTP_HOST', 'localhost')
    SFTP_PORT = os.getenv('SFTP_PORT', '122')
    SFTP_USERNAME = os.getenv('SFTP_USERNAME', 'centos')
    SFTP_KEY_FILENAME = os.getenv('SFTP_KEY_FILENAME', 'dummy_keys/dummy_rsa')
    SFTP_PASSPHRASE = os.getenv('SFTP_PASSPHRASE', 'dummy_secret')

    OUR_PUBLIC_KEY_PATH = Path(os.getenv('OUR_PUBLIC_KEY_PATH') or Path(__file__).parent.joinpath('dummy_keys')
                               .joinpath('dummy-key-ssdc-rm-public.asc'))

    SUPPLIER_KEY_DIRECTORY = Path(os.getenv('SUPPLIER_KEY_DIRECTORY') or Path(__file__).parent.joinpath('dummy_keys'))
    SUPPLIER_CONFIG_JSON_PATH = Path(
        os.getenv('SUPPLIER_CONFIG_JSON_PATH') or Path(__file__).parent.joinpath('dummy_supplier_config.json'))
    SUPPLIERS_CONFIG = json.loads(
        SUPPLIER_CONFIG_JSON_PATH.read_text())\
        if SUPPLIER_CONFIG_JSON_PATH and SUPPLIER_CONFIG_JSON_PATH.exists() else None


class TestConfig(DevConfig):
    RABBIT_PORT = os.getenv('RABBIT_PORT', '35672')
    SFTP_PORT = os.getenv('SFTP_PORT', '2222')
    TMP_TEST_DIRECTORY = Path(__file__).parent.joinpath('tmp_test_files')
    PARTIAL_FILES_DIRECTORY = TMP_TEST_DIRECTORY.joinpath('partial_files/')
    ENCRYPTED_FILES_DIRECTORY = TMP_TEST_DIRECTORY.joinpath('encrypted_files/')
    QUARANTINED_FILES_DIRECTORY = TMP_TEST_DIRECTORY.joinpath('quarantined_files/')
    EXCEPTION_MANAGER_URL = 'http://test'


# Use dev or test defaults depending on environment
if Config.ENVIRONMENT == 'DEV':
    Config = DevConfig
elif Config.ENVIRONMENT == 'TEST':
    Config = TestConfig
