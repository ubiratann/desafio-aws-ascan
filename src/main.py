import boto3
import os
import json
import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Attr, And, Key
from botocore.exceptions import ClientError
from http import HTTPStatus
from decimal import Decimal


DEFAULT_TABLE_NAME = os.environ['TABLE']

TODO        = 1
IN_PROGRESS = 2
DONE        = 3

ID_INDEX       = -1
FUNCTION_INDEX = -2

CONDITIONAL_EXCEPTION = "ConditionalCheckFailedException"

def now():
    return datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

def parse_body(body):
    """
        This method is a turn-around to fix the problem with Decimal not serializable elements thats becomes from dynamodb
        Parameter
        ---------
        body: dict
            object with the body of response
    """
    if isinstance(body, list):
        for list_item in body:
            list_item = parse_body(list_item)
    else:
        for item in body:
            # recursively parsing nested dicts
            if isinstance(body[item], dict):
                body[item] = parse_body(body[item])
            #parsing Decimal objects to int
            if isinstance(body[item], Decimal):
                body[item] = int(body[item])  
    return body

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
    item["id"]         = uuid.uuid4().int & (1<<64)-1
    item["status_code"]     = TODO
    item["created_at"] = now()
    response = {}
    try:
        table.put_item(
            TableName           = DEFAULT_TABLE_NAME,
            Item                = {**item},
            ConditionExpression = Attr("id").not_exists(),
        )
        response["status"] = HTTPStatus.CREATED
        response["body"] =  {
                               "message": "Task created with success!",
                               "item": item
                            }
    except ClientError as err:
        if err.response["Error"]["Code"] == CONDITIONAL_EXCEPTION:
            response["status"] = HTTPStatus.FORBIDDEN
            response["body"]   = {"message" : f"The id={item['id']} is allready in use !"}
    except:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = {"message" : "Something went wrong :'("}
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
        aux = table.update_item(
            TableName                 = DEFAULT_TABLE_NAME,
            Key                       = {"id": id},
            ConditionExpression       = And(Attr("id").exists(), Attr("id").eq(id)),
            UpdateExpression          = "SET description =:description, updated_at =:updated_at",
            ExpressionAttributeValues = { 
                                            ":description" : item["description"],
                                            ":updated_at"  : now() },
            ReturnValues              = "UPDATED_NEW"
        )
        response["status"] = HTTPStatus.OK
        response["body"]   = {
                                "message" : "Task description updated with sucess !",
                                "item"    :  aux["Attributes"]
                             }
    except ClientError as err:
        if err.response["Error"]["Code"] == CONDITIONAL_EXCEPTION:
            response["status"] = HTTPStatus.NOT_FOUND
            response["body"]   = {"message" : f"Invalid id={item['id']}, check it and try again!"}       
    except:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = {"message" : "Something went wrong :'("}
    return response

def update_task_status(id, status_code, table):
    """
        Update the status of a task
        Parameters
        ----------
        id : int
            Id of the task to be updated
        status_code : int
            The new status code
        table : object
            Reference to the default database table
    """
    response = {}
    messages = {
        IN_PROGRESS : "Now the task is in in progress!",
        TODO        : "Now the task is stoped!",
        DONE        : "Now the task is done!"
    }
    try:
        item = table.update_item(
            TableName                 = DEFAULT_TABLE_NAME,
            Key                       = {"id": id},
            UpdateExpression          = "SET status_code=:status_code, updated_at =:updated_at",
            ExpressionAttributeValues = {
                                           ":status_code": status_code,
                                           ":updated_at" : now()
                                        },
            ConditionExpression       = And(Attr("id").exists(), Attr("id").eq(id)),
            ReturnValues              = "ALL_NEW"
        )
        response["body"] = {
                              "message" : messages[status_code],
                              "item"    : item["Attributes"]
                           }
        response["status"] = HTTPStatus.OK
    except ClientError as err:
        if err.response["Error"]["Code"] == CONDITIONAL_EXCEPTION:
            response["status"] = HTTPStatus.NOT_FOUND
            response["body"]   = {"message" : f"Invalid id={id}, check it and try again !"}
    except:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = {"message" : "Something went wrong :'("}
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
        table.delete_item(
            Key                 = {"id":id},
            ConditionExpression = Attr("id").exists()
        )
        response["status"] = HTTPStatus.OK
        response["body"]   = {"message" : f"Item with id={id} deleted with sucess !"}
    except ClientError as err:
        if err.response["Error"]["Code"] == CONDITIONAL_EXCEPTION:
            response["status"] = HTTPStatus.NOT_FOUND
            response["body"]   = {"message" : f"Invalid id={id}, check it and try again !"}  
    except:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = {"message" : "Something went wrong :'("}
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
            aux = table.get_item(
                TableName = DEFAULT_TABLE_NAME,
                Key       = {"id":id},
            )
            response["status"] = HTTPStatus.OK
            response["body"]   = aux["Item"] 
        except KeyError as err:
            response["status"] = HTTPStatus.NOT_FOUND
            response["body"]   = { "message" : f"Theres no item with id={id}"}
        except ClientError as err:
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = { "message" : err.response['Error']['Message']}         
        except:
            response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            response["body"]   = {"message" : "Something went wrong :'("}
    else:
        response = get_all_tasks(table)
    return response

def get_tasks_by_status(status_code, table):
    """
        Get all tasks that have an especific status
        Parameters
        ----------
        status_code : int
            Wanted status code of the tasks
        table : object
            Reference to the default database table
    """
    response = {}
    try:
        aux = table.query(
            TableName              = DEFAULT_TABLE_NAME,
            IndexName              = "status_code_index",
            KeyConditionExpression = Key("status_code").eq(status_code)
        )
        response["status"] = HTTPStatus.OK
        response["body"]   = aux["Items"]
    except ClientError as err:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = { "message" : err.response['Error']['Message']}         
    except:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = {"message" : "Something went wrong :'("}
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
        aux                = table.scan(TableName = DEFAULT_TABLE_NAME,)
        response["status"] = HTTPStatus.OK
        response["body"]   = aux["Items"]   
    except ClientError as err:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = { "message" : err.response['Error']['Message']}      
    except:
        response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
        response["body"]   = {"message" : "Something went wrong :'("}
    return response

def handler(event, context):
    """
        This method will be called on the invok action of the AWS lambda function 
    """
    #dynamo reference
    dynamo = boto3.resource("dynamodb").Table(DEFAULT_TABLE_NAME)
    
    #values from request context
    method       = event["requestContext"]["http"]["method"]
    splited_path = event["rawPath"].split("/")

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
            "values": (id, DONE)
        },
        "update": {
            "function": update_task_description,
            "values": (code, body)
        }
    }

    if method in METHODS:
        response = {} 
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
        
        response["body"] = parse_body(response["body"])
        return {
            "statusCode": response["status"],
            "body": json.dumps(response["body"]),
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