import boto3
import json
import os
from http import HTTPStatus
DEFAULT_TABLE_NAME = os.environ['TABLE']

TODO        = 1
IN_PROGRESS = 2
COMPLETE    = 3

ID_INDEX       = -1
FUNCTION_INDEX = -2

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
        response = {}
        try:
            table.put_item(**item)
            response["status"] = HTTPStatus.CREATED
            response["body"]   = "Item created with sucess"
        except Exception as err:
            print(err)
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = "Something went wrong"
        return response

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
        response = {}
        try:
            table.update_item(
            
            Key                       = {"id": id},
            UpdateExpression          = "set info.description=:d",
            ExpressionAttributeValues = {':d': item["description"] },
            ReturnValues              = "UPDATED_NEW"
            )
            response["status"] = HTTPStatus.OK
            response["body"]   = "Item description updated with sucess"
        except Exception as err:
            print(err)
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = "Something went wrong!"
        return response

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
        response = {}
        try:
            table.update_item(
            Key                       = {"id": id},
            UpdateExpression          = "set info.status=:s",
            ExpressionAttributeValues = {':s': status},
            ReturnValues              = "UPDATED_NEW"
            )
            response["status"] = HTTPStatus.OK
            response["body"]   = "Status updated with sucess!"
        except Exception as err:
            print(err)
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = "Something went wrong!"
        return response
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
        response = {}
        try:
            table.delete_item(Key = {"id":id})
            response["status"] = HTTPStatus.OK
            response["body"]   = "Status updated with sucess!"
        except Exception as err:
            print(err)
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = "Something went wrong!"
        return response
    
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
        response = {}
        try:
            response["status"] = HTTPStatus.OK
            if id != "":
                response["body"] = table.get_item(Key = {"id":id})
            else:
                response = get_all_tasks(dynamo)
        except Exception as err:
            print(err)
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = "Something went wrong!"
        return response

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
        response = {}
        try:
            response["status"] = HTTPStatus.OK
            response["body"]   = table.query(KeyConditionExpression = Key("status").eq(status))
        except Exception as err:
            print(err)
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = "Something went wrong!"
        return response

    def get_all_tasks(table):
        """
            Get all tasks
            Parameters
            ----------
            table : object
                Reference to the default database table
        """
        response = {}
        try:
            response["status"] = HTTPStatus.OK
            response["body"]   = table.scan()
        except Exception as err:
            print(err)
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = "Something went wrong!"
        return response

    #dynamo reference
    dynamo = boto3.resource("dynamodb").Table(DEFAULT_TABLE_NAME)
    
    #values from request context
    method       = event["requestContext"]["http"]["method"]
    splited_path = event["rawPath"].split("/")
    print(event)

    #parsed values from context
    body   = event["body"] if "body" in event  else {}
    params = event["pathParameters"] if "pathParameters" in event else {}
    
    #default route params
    id   = params["id"] if "id" in params else ""
    code = params["code"] if "code" in params else ""
    
    METHODS = ["GET","DELETE","POST","PUT"]

    GET_FUNCTIONS = {
        "get": {
            "function": get_task,
            "values": (id, dynamo)
        },
        "status":{
            "function": get_tasks_by_status,
            "values": (code, dynamo)
        }
    }

    PUT_FUNCTIONS = {
        "start": {
            "function": update_task_status,
            "values": (id, IN_PROGRESS, dynamo)
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
    }

    if method in METHODS:
        response = None 
        if method == "DELETE":
            response = delete_task(params["id"], dynamo)

        if method == "GET":
            func = splited_path[FUNCTION_INDEX]
            if  func in GET_FUNCTIONS:
                response = GET_FUNCTIONS[func]["function"](GET_FUNCTIONS[func]["values"])
            else:
                response = GET_FUNCTIONS["get"]["function"](GET_FUNCTIONS["get"]["values"])

        if method == "POST":
            response = create_task(body, dynamo)

        if method == "PUT":
            func     = splited_path[FUNCTION_INDEX]
            response = PUT_FUNCTIONS[func]["function"](PUT_FUNCTIONS[func]["values"])

        return {
            "status": response["status"],
            "body": json.dumps(response["body"]),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"body":"Bad request!"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }