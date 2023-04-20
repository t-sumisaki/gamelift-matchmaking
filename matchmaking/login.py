import boto3
import json
import os
import sys

from response_helper import create_response



client = boto3.client("coginito-idp")


def lambda_handler(event, context):

    req = event.body

    if 'username' not in req or 'password' not in req:
        return create_response(400, {
            "status": "fail",
            "msg": "Username and password are required"
        })
    

    
    resp, msg = initiate_auth(req['username'], req['password'])

    if resp is None:
        return create_response(400, {
            "status": "fail",
            "msg": msg
        })

    return create_response(200, {
        "status": "success",
        "tokens": resp['AuthenticationResult']
    })


def initiate_auth(username, password):

    try:

        resp = client.initiate_auth(
            ClientId=os.getenv("USER_POOL_APP_CLIENT_ID"),
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters= {
                'USERNAME': username,
                'PASSWORD': password,
            })
        

    except client.exceptions.InvalidParameterException as e:
        return None, "Username and password must not be empty"
    except (client.exceptions.NotAuthorizedException, client.exceptions.UserNotFoundException) as e:
        return None, "Username or password is incorrect"
    except Exception as e :
        print("Uncaught exception:", e, file=sys.stderr)
        return None, "Unknown error"

    return resp, None