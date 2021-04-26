import os


class Config:
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    PROTOCOL = os.getenv('PROTOCOL', 'http')

    RABBITMQ_HOST = os.getenv('RABBITMQ_SERVICE_HOST', 'localhost')
    RABBITMQ_PORT = os.getenv('RABBITMQ_SERVICE_PORT', '6672')
    RABBITMQ_HTTP_PORT = os.getenv('RABBITMQ_HTTP_PORT', '16672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_INBOUND_QUEUE = os.getenv('RABBITMQ_INBOUND_QUEUE', 'case.sample.inbound')
    RABBITMQ_OUTBOUND_QUEUE = os.getenv('RABBITMQ_OUTBOUND_QUEUE', 'case.sample.outbound')
    RABBITMQ_INBOUND_EXCHANGE = os.getenv('RABBITMQ_INBOUND_EXCHANGE', 'inbound-exchange')
    RABBITMQ_INBOUND_ROUTING_KEY = os.getenv('RABBITMQ_INBOUND_ROUTING_KEY',
                                             'case.sample.inbound')
    RABBITMQ_OUTBOUND_ROUTING_KEY = os.getenv('RABBITMQ_OUTBOUND_ROUTING_KEY',
                                              'case.sample.outbound')

    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')

    DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST_ACTION = os.getenv('DB_HOST_ACTION', 'localhost')
    DB_HOST_CASE = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '6432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_ACTION_CERTIFICATES = os.getenv('DB_ACTION_CERTIFICATES', '')
    DB_CASE_CERTIFICATES = os.getenv('DB_CASE_CERTIFICATES', '')
