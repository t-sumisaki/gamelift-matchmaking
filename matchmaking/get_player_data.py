import boto3

import os

from response_helper import create_response

cognito = boto3.client("cognito-idp")
dynamodb = boto3.client("dynamodb")


PLAYERS_TABLE_NAME = os.getenv("PLAYERS_TABLE_NAME")

def lambda_handler(event, context):

    ok, data = get_player_data(event, context)

    if not ok:
        return create_response(400, {
            "message": "get player data failed"
        })
    
    return create_response(200, {
        "playerData": data
    })

def get_player_data(event, context):

    sub = None
    token = None

    if "headers" in event:
        if "Authorization" in event["headers"]:
            token = event["headers"]["Authorization"]

    try:
        res = cognito.get_user(
            AccessToken=token
        )

        for attr in res["UserAttributes"]:
            if attr["Name"] == "sub":
                sub = attr["Value"]
                break

    except Exception as e:
        print("cognito.get_user failed:", e)
        return False, None


    try:
        res = dynamodb.get_item(
            TableName=PLAYERS_TABLE_NAME,
            Key={
                "Id": {"S": sub}
            }
        )

        return True, res["Item"]

    
    except Exception as e:
        print("dynamodb.get_item failed:",e )
        return False, None



