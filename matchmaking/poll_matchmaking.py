import boto3
import json
import os

from response_helper import create_response


TICKET_TABLE_NAME = os.getenv("TICKET_TABLE_NAME")

dynamodb = boto3.client("dynamodb")

def lambda_handler(event, context):

    ticket_id = None

    body = json.loads(event["body"])

    if "ticketId" in body:
        ticket_id = body["ticketId"]

    if ticket_id is None:
        msg = "incoming request did not have ticket id"
        print(msg)


    try:
        resp = dynamodb.get_item(
            TableName=TICKET_TABLE_NAME,
            Key={
                "Id": {"S": ticket_id}
            }
        )

        ticket = resp["Item"]

        print("get ticket_data success:", ticket)

        return create_response(200, {
            "ticket": ticket
        })

    except Exception as e:
        print("failed to get ticket data:", e)
        return create_response(400, {
            "message": "failed to poll matchmaking"
        })

