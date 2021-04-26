import functools
import json

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

from behave import step


@step('a message is put on the inbound queue')
def send_message_to_rabbit(context):
    message = {
        'addressLine1': '666 Long Lane',
        'postcode': 'SW1 1ST'
    }
    with RabbitContext(exchange=Config.RABBITMQ_INBOUND_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=json.dumps(message),
            content_type='application/json',
            routing_key=Config.RABBITMQ_INBOUND_ROUTING_KEY)


@step('a message is put on the outbound queue')
def listen_for_messages(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_QUEUE,
                                    functools.partial(store_all_messages,
                                                      context=context))
    message = context.messages_received[0]
    context.id = message['id']
    context.address_line_1 = message['addressLine1']
    context.postcode = message['postcode']

    test_helper.assertIsNotNone(context.id)
    test_helper.assertIsNotNone(context.address_line_1)
    test_helper.assertIsNotNone(context.postcode)


def store_all_messages(ch, method, _properties, body, context):
    parsed_body = json.loads(body)
    context.messages_received.append(parsed_body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()
