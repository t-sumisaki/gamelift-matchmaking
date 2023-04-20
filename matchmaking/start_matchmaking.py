import boto3

import json

from response_helper import create_response
from get_player_data import get_player_data


gamelift = boto3.client("gamelift")


def handler(event, context):

    latency_map = None

    body = json.loads(event["body"])

    if "latencyMap" in body:
        latency_map = body["latencyMap"]

    
    if latency_map is None:
        msg = "incoming request did not have a latency map"
        print(msg)
        return create_response(400, {
            "message": msg
        })


    ok, player_data = get_player_data(event, context)

    if not ok:
        return create_response(200, {
            "ok": False,
            "message": "get_player_data failed"
        })

    player_id = player_data["Id"]["S"]
    group_id = int(player_data["groupId"]["N"])

    print("get player data: player_id=%s, group_id=%s" % (player_id, group_id))


    try:
        resp = gamelift.start_matchmaking(
            Players=[{
                "PlayerId": player_id,
                "PlayerAttributes": {
                    "groupid": {"N": group_id}
                },
                "LatencyInMs": latency_map,
            }]
        )

        ticket_id = resp["MatchmakingTicket"]["TicketId"]

        print("start matchmaking: %s" % ticket_id)

        return create_response(200, {
            "ticketId": ticket_id,
        })

    except Exception as e:
        print("gamelift.start_matchmaking failed:", e)
        return create_response(400, {
            "message": "start_matchmaking failed",
        })
    pass