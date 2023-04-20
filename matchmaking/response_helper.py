import json


def create_response(status, body):
    return {
        "statusCode": status,
        "body": json.dumps(body)
    }
