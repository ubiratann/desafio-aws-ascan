import boto3
import json
import os

DEFAULT_TABLE = os.environ['TABLE']

def handler(event, context):

    operation = event['requestContext']['http']['method']
    dynamo  = boto3.resource('dynamodb').Table(DEFAULT_TABLE)

    OPERATIONS = {
        'post': lambda x: dynamo.put_item(**x),
        'get': lambda x: dynamo.get_item(**x),
        'put': lambda x: dynamo.update_item(**x),
        'delete': lambda x: dynamo.delete_item(**x),
    }

    if operation in OPERATIONS:
        return OPERATIONS[operation](event.get('payload'))
    else:
        raise ValueError(f'Invalid operation {operation}')
    