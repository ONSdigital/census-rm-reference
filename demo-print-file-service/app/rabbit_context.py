import pika

from config import Config


class RabbitContext:

    def __init__(self, **kwargs):
        self._host = kwargs.get('host') or Config.RABBIT_HOST
        self._port = kwargs.get('port') or Config.RABBIT_PORT
        self._vhost = kwargs.get('vhost') or Config.RABBIT_VIRTUALHOST
        self._user = kwargs.get('user') or Config.RABBIT_USERNAME
        self._password = kwargs.get('password') or Config.RABBIT_PASSWORD
        self.queue_name = kwargs.get('queue_name') or Config.RABBIT_QUEUE

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, *_):
        self.close_connection()

    @property
    def channel(self):
        return self._channel

    def open_connection(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._host,
                                      self._port,
                                      self._vhost,
                                      pika.PlainCredentials(self._user, self._password)))

        self._channel = self._connection.channel()

        return self._connection

    def close_connection(self):
        self._connection.close()
        del self._channel
        del self._connection
