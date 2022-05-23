import boto3
import json
import os

DEFAULT_TABLE = os.environ['TODO_LIST_TABLE']

def handler(event, context):

    operation = event['operation']
    dynamo  = boto3.resource('dynamodb').Table(DEFAULT_TABLE)

    OPERATIONS = {
        'create': lambda x: dynamo.put_item(**x),
        'read': lambda x: dynamo.get_item(**x),
        'update': lambda x: dynamo.update_item(**x),
        'delete': lambda x: dynamo.delete_item(**x),
        'list': lambda x: dynamo.scan(**x),
        'echo': lambda x: x,
        'ping': lambda x: 'pong'
    }

    if operation in OPERATIONS:
        return OPERATIONS[operation](event.get('payload'))
    else:
        raise ValueError(f'Invalid operation {operation}')
    