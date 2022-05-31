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
            table.put_item(
                TableName = DEFAULT_TABLE_NAME,
                Item      = {**item}
            )
            response["status"] = HTTPStatus.CREATED
            response["body"]   = "Item created with sucess"
        except:
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
                TableName                 = DEFAULT_TABLE_NAME,
                Key                       = {"id": id},
                UpdateExpression          = "set info.description=:d",
                ExpressionAttributeValues = {':d': item["description"] },
                ReturnValues              = "UPDATED_NEW"
            )
            response["status"] = HTTPStatus.OK
            response["body"]   = "Item description updated with sucess"
        except:
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
                TableName                 = DEFAULT_TABLE_NAME,
                Key                       = {"id": id},
                UpdateExpression          = "SET info.status_code=:s",
                ExpressionAttributeValues = {':s': status},
                ReturnValues              = "UPDATED_NEW"
            )
            response["status"] = HTTPStatus.OK
            response["body"]   = "Status updated with sucess!"
        except:
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
            response["body"]   = "Item deleted with sucess!"
        except:
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
        if id != "":
            try:
                response["status"] = HTTPStatus.OK
                aux = table.get_item(TableName=DEFAULT_TABLE_NAME, Key={"id":id})
                response["body"] = aux["Item"]
            except KeyError:
            ## Handling the case where not item was found so the "Item" key dont exists in the aux object 
                response["status"] = HTTPStatus.NOT_FOUND
                response["body"]   = "No items with the passed id were found."                 
            except:
                response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
                response["body"]   = "Something went wrong!" 
        else:
            response = get_all_tasks(dynamo)
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
            aux                = table.query(
                TableName              = DEFAULT_TABLE_NAME,
                KeyConditionExpression = Key("status").eq(status)
            )
            response["body"] = aux["Items"]
        except KeyError:
            ## Handling the case where not item was found so the "Item" key dont exists in the aux object 
                response["status"] = HTTPStatus.NOT_FOUND
                response["body"]   = "No items with the passed id were found."  
        except:
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
            aux                = table.scan(TableName = DEFAULT_TABLE_NAME,)
            response["body"]   = aux["Items"]   
        except:
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
    body   = json.loads(event["body"]) if "body" in event  else {}
    params = event["pathParameters"] if "pathParameters" in event else {}
    
    #default route params
    id   = int(params["id"]) if "id" in params else ""
    code = int(params["code"]) if "code" in params else ""
    
    METHODS = ["GET","DELETE","POST","PUT"]

    GET_FUNCTIONS = {
        "get": {
            "function": get_task,
            "values": id
        },
        "status":{
            "function": get_tasks_by_status,
            "values": code
        }
    }

    PUT_FUNCTIONS = {
        "start": {
            "function": update_task_status,
            "values": (id, IN_PROGRESS)
        },
        "stop": {
            "function": update_task_status,
            "values": (id, TODO)
        },
        "finish": {
            "function": update_task_status,
            "values": (id, COMPLETE)
        },
        "update": {
            "function": update_task_description,
            "values": (code, body)
        }
    }

    if method in METHODS:
        response = None 
        if method == "DELETE":
            response = delete_task(id, dynamo)

        if method == "GET":
            func = splited_path[FUNCTION_INDEX]
            if  func in GET_FUNCTIONS:
                response = GET_FUNCTIONS[func]["function"](GET_FUNCTIONS[func]["values"], dynamo)
            else:
                response = GET_FUNCTIONS["get"]["function"](GET_FUNCTIONS["get"]["values"], dynamo)

        if method == "POST":
            response = create_task(body, dynamo)

        if method == "PUT":
            func     = splited_path[FUNCTION_INDEX]
            response = PUT_FUNCTIONS[func]["function"](*PUT_FUNCTIONS[func]["values"], dynamo)

        return {
            "statusCode": response["status"],
            "body": response["body"],
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": {"message":"Bad request!"},
            "headers": {
                "Content-Type": "application/json"
            }
        }