import boto3

from response_helper import create_response

def lambda_handler(event, context):

    return create_response(200, {
        "status": "ok"
    })
