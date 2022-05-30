from logging import Logger
from multiprocessing.connection import Client
from pydoc import doc
import boto3
import json
import os

DEFAULT_TABLE_NAME = os.environ['TABLE']

TODO        = 1
IN_PROGRESS = 2
COMPLETE    = 3

def handler(event, context):
    """
        This method will be called on the invok action of the AWS lambda function 
    """

    def create_task(item, table):
        """
            Create a task on default database table
            Parameters
            ----------
            item : dict
                Definition of the item to be created on database
            table : object
                Reference to the default database table
        """
        return table.put_item(item)
    
    def update_task_description(id, item, table):
        """
            Update the description of a task
            Parameters
            ----------
            id : int
                Id of the task to be updated
            item : object
                Object with the new description
            table : object
                Reference to the default database table
        """
        return table.update_item(
            
            Key                       = {"id": id},
            UpdateExpression          = "set info.description=:d",
            ExpressionAttributeValues = {':d': item["description"] },
            ReturnValues              = "UPDATED_NEW"
        )

    def update_task_status(id, status, table):
        """
            Update the status of a task
            Parameters
            ----------
            id : int
                Id of the task to be updated
            status : int
                The new status code
            table : object
                Reference to the default database table
        """
        return table.update_item(
            Key                       = {"id": id},
            UpdateExpression          = "set info.status=:s",
            ExpressionAttributeValues = {':s': status},
            ReturnValues              = "UPDATED_NEW"
        )

    def delete_task(id, table):
        """
            Delete a task
            Parameters
            ----------
            id : int
                Id of the task to be deleted
            table : object
                Reference to the default database table
        """
        return table.delete_item(Key = {"id":id})
    
    def get_task(id, table):
        """
            Get an especific task by id from database
            Parameters
            ----------
            id : int
                Id of the task to be updated
            table : object
                Reference to the default database table
        """
        return table.get_item(Key = {"id":id})
    
    def get_tasks_by_status(status, table):
        """
            Get all tasks that have an especific status
            Parameters
            ----------
            status : int
                Wanted status code of the tasks
            table : object
                Reference to the default database table
        """
        return table.query(KeyConditionExpression = Key("status").eq(status))

    def get_all_tasks(table):
        """
            Get all tasks
            Parameters
            ----------
            table : object
                Reference to the default database table
        """
        return table.scan()

    #dynamo reference
    dynamo = boto3.resource("dynamodb").Table(DEFAULT_TABLE_NAME)
    #values from request context
    method = event["requestContext"]["http"]["method"]
    path   = event["requestContext"]["path"].split("/")[-2]
    #parsed values from context
    body   = json.loads(event["body"] if "body" in event  else None)
    params = json.loads(event["queryStringParameters"] if "queryStringParameters" in event else None)
    

    METHODS = {
        "PUT": {
            "start": {
                "function": update_task_status,
                "values": (params["id"], IN_PROGRESS, dynamo)
            },
            "stop": {
                "function": update_task_status,
                "values": (params["id"], TODO, dynamo)
            },
            "finish": {
                "function": update_task_status,
                "values": (params["id"], COMPLETE, dynamo)
            },
            "update": {
                "function": update_task_description,
                "values": (params["id"], body, dynamo)
            }
        },
        "POST": {

        }
    }

  