# demo-print-file-service

A light weight service for building and transferring print files

## Setup

This service is built in python using [pipenv](https://pypi.org/project/pipenv/) for dependency management.
A [Makefile](./Makefile) is provided for shortcuts and consistency in setting up, building and running tests.

To initialise or update the pipenv run

```shell
make install
```

The service is built to run in a docker container, build the docker image locally with

```shell
make docker_build
```

## Configuration

Configuration is read by [config.py](/config.py). If `ENVIRONMENT` is not set to `DEV` the production config class will
be used. This will check and fail start up if any configuration is missing.

To run locally against the [ssdc-rm-docker-dev](https://github.com/ONSdigital/ssdc-rm-docker-dev) services set
environment variable `ENVIRONMENT` to `DEV`. This will switch to development defaults which are configured to point to
the docker dev backing services.

### Supplier Configuration

The suppliers are configured dynamically with a JSON file that is read in at start up. It can contain one or many
suppliers.

It must be in this format:

```json
{
  "SUPPLIER_NAME": {
    "sftpDirectory": "example/remote/directory",
    "encryptionKeyFilename": "example-key-file.asc"
  },
  ...
}
```

Where:

- `SUPPLIER_NAME`: Each different supplier is a new top level key, where the key is the supplier name. This name is what
  the print file service expects to receive in the `supplier` field of the print row messages.
- `sftpDirectory`: The remote directory it will write files to for this supplier
- `encryptionKeyFilename`: The name of the public key for that supplier which will be used to PGP encrypt the print
  files sent to them. That key file must be located in the directory configured by `SUPPLIER_KEY_DIRECTORY`

To see a working example, look at the [dummy_supplier_config.json](dummy_supplier_config.json) which configures two
different "dummy" suppliers, `SUPPLIER_A` and `SUPPLIER_B`.

## Message Format

The print file ingests print row messages which include the formatted print file row and some batch metadata needed to
build and send the file. One critical note, the `supplier` must match a supplier name in the supplier config otherwise
the message will error and be rejected.

Example print row message:

```json
{
  "row": "example|formatted|print|file|row",
  "packCode": "EXAMPLE_PACK_CODE",
  "supplier": "SUPPLIER_NAME",
  "batchId": "895df013-06a1-4e87-9a8e-f16820df4342",
  "batchQuantity": 10
}
```

## Tests

The tests in this repo are split into unit and integration tests.

Run all the tests, linting and docker build with

```shell
make build_and_test
```

The unit tests are written for pytest and can easily be debugged in any good python IDE, or can be run from the command
line with a coverage report with.

```shell
make unit_tests
```

Note: Pycharm defaults to unittest as it's test runner,
follow [this help page](https://www.jetbrains.com/help/pycharm/pytest.html) to set Pycharm to use Pytest.

The integration tests are also written in pytest but require the service to be running with backing services in the
provided docker compose. The make targets handle this automatically, run them own their own from the command line with

```shell
make integration_tests
```

Note this target does not automatically build the latest code, if you have made changes you need to build the image
first with `make docker_build`

If you want to run the integration tests from an IDE, first start up the service and backing services in docker compose
with

```shell
make up
```

Then once the print file service container has successfully started you should be able to run the test locally. Note
that the service code is still running within the docker container so debugging can only be done on the test code
itself, this is an area we would like to improve.

Once you are finished you can stop the docker compose services with

```shell
make down
```

## Dummy keys

This repo contains dummy keys for SSH and encryption in testing/dev. These keys *must not* be used outside development
environments.

### Dummy Key Passphrases

| Dummy Key        | Passphrase   |
| ---------------- | ------------ |
| Dummy SSDC RM    | test         |
| Dummy supplier A | test         |
| Dummy supplier B | test         |
| Dummy RSA        | dummy_secret |
