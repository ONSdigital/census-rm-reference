import pytest

from config import ConfigError, DevConfig, TestConfig


def test_check_config_dev_config():
    # When
    DevConfig.check_config()

    # Then no config error is raised


def test_check_config_test_config():
    # When
    TestConfig.check_config()

    # Then no config error is raised


def test_check_config_fails_on_invalid_supplier_config_json():
    # Given
    # Subclass DevConfig to avoid interfering with original attributes
    class ConfigInvalidSupplier(DevConfig):
        SUPPLIERS_CONFIG = {
            'TEST_SUPPLIER': {
                'NOT_VALID': 'SUPPLIER_CONFIG'
            }
        }

    # When, then raises
    with pytest.raises(ConfigError) as e:
        ConfigInvalidSupplier.check_config()

    assert 'Invalid supplier config' in str(e)


def test_check_config_fails_on_empty_supplier_config_json():
    # Given
    # Subclass DevConfig to avoid interfering with original attributes
    class ConfigEmptySuppliers(DevConfig):
        SUPPLIERS_CONFIG = {}

    # When, then raises
    with pytest.raises(ConfigError) as e:
        ConfigEmptySuppliers.check_config()

    assert 'Supplier config is empty' in str(e)


def test_check_config_fails_on_missing_supplier_key():
    # Given
    # Subclass DevConfig to avoid interfering with original attributes
    class ConfigMissingKey(DevConfig):
        SUPPLIERS_CONFIG = {
            'VALID_SUPPLIER_MISSING_KEY': {
                'sftpDirectory': 'valid/remote/directory',
                'encryptionKeyFilename': 'missing-key-file.asc'
            }
        }

        # When, then raises
    with pytest.raises(ConfigError) as e:
        ConfigMissingKey.check_config()

    assert 'Supplier key not found' in str(e)
