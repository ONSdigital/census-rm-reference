import json
import uuid

from app.rabbit_context import RabbitContext
from config import TestConfig


def build_messages_with_uac(supplier, quantity, pack_code, batch_id):
    messages = []
    for i in range(quantity):
        messages.append({'printSupplier': supplier,
                         'batchQuantity': quantity,
                         'packCode': pack_code,
                         'batchId': batch_id,
                         'row': f'UAC{str(i)}|row_{i}|test|data'})
    return messages, batch_id


def build_messages_no_uac(supplier, quantity, pack_code, batch_id):
    messages = []
    for i in range(quantity):
        messages.append({'printSupplier': supplier,
                         'batchQuantity': quantity,
                         'packCode': pack_code,
                         'batchId': batch_id,
                         'row': f'row_{i}|test|data'})
    return messages, batch_id


def build_test_messages(quantity, supplier, pack_code, uac=True):
    batch_id = str(uuid.uuid4())
    return build_messages_with_uac(supplier, quantity, pack_code, batch_id) if uac \
        else build_messages_no_uac(supplier, quantity, pack_code, batch_id)


def send_test_messages(message_dicts):
    with RabbitContext() as rabbit:
        for message_dict in message_dicts:
            rabbit.channel.basic_publish(exchange='', routing_key=TestConfig.RABBIT_QUEUE,
                                         body=json.dumps(message_dict))
