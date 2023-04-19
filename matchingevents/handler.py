import boto3
import json
import os

import math
from datetime import datetime


client = boto3.client("dynamodb")

def handler(event, context):

    message = None

    if "Records" in event and len(event["Records"]) > 0:
        record = event["Record"][0]

        if "Sns" in record and "Message" in record["Sns"]:
            print('message from gamelift:', record["Sns"]["Message"])

            message = json.loads(record["Sns"]["Message"])
    
    if message is None:
        print("message is None")
        return

    if message["detail-type"] != "GameLift Matchmaking Event":
        print("message is not gamelift matchmaking event")
        return

TICKET_UPDATE_TARGET = [
    "MatchmakingSucceeded",
    "MatchmakingTimeOut",
    "MatchmakingCancelled",
    "MatchmakingFailed",
]

TICKET_TABLE_NAME = os.getenv("TICKET_TABLE_NAME")

def updateTickets(detail):

    updateTickets = []

    if detail["type"] in TICKET_UPDATE_TARGET:

        for ticket in detail["tickets"]:
            ticketItem = {
                "Id": { "S": ticket["ticketId"]},
                "Type": {"S": detail["type"]},
                "TTL": {"N": str(math.floor(datetime.now().timestamp() / 1000) + 3600)}
            }

            if detail["type"] == "MatchmakingSucceed":

                ticketItem["Players"] = {"L": []}

                for player in ticket["players"]:
                    item = {
                        "M": {
                            "PlayerId": {"S": player["playerId"]},
                        }
                    }
                    if "playerSessionId" in player:
                        item["M"]["playerSessionId"] = {"S": player["playerSessionId"]}
                    
                    ticketItem["Players"]["L"].append(item)
                
                ticketItem["GameSessionInfo"] = {
                    "M": {
                        "IpAddress": {"S": detail["gameSessionInfo"]["ipAddress"]},
                        "Port": {"N": str(detail["gameSessionInfo"]["port"])},
                    }
                }
            
            updateTickets.append(ticketItem)
    
    try:
        resp = client.batch_write_item(
            RequestItems={
                "${TICKET_TABLE_NAME}": [ {"PutRequest": { "Item": d }} for d in updateTickets ]
            }
        )
    except client.exceptions.ProvisionedThroughputExceededException as e:
        print("provisioned throughput exceeded")
    except client.exceptions.ResourceNotFoundException as e:
        print("table %s is not found" % TICKET_TABLE_NAME)
    except client.exceptions.ItemCollectionSizeLimitExxceededException as e:
        print("item collection size exceeded")
    except client.exceptions.RequestLimitExceeded as e:
        print("request limit exceeded")
    except Exception as e:
        print("internal server error:", e)
    
