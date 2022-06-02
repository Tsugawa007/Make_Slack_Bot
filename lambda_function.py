import json
import logging
import os

import requests

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def respond(res="Hello"):
    ret = {
        'statusCode': '200',
        'body': json.dumps(res, ensure_ascii=False),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    LOGGER.info(f"Return: {ret}")
    return ret


def post_slack(channel, message):
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        "Authorization": f"Bearer {os.environ.get('OAuthToken')}",
    }
    url = "https://slack.com/api/chat.postMessage"
    payload = {
        'text': message,
        "token": os.environ.get('PostToken'),
        "channel": channel,
    }
    LOGGER.info(f"Header: {headers} Payload: {payload}")
    res = requests.post(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    LOGGER.info(f"status: {res.status_code} content: {res.content}")


def lambda_handler(event, context):
    LOGGER.info(f"Received event: {json.dumps(event)}")
    body = {}
    if event.get('body'):
        body = json.loads(event['body'])
    if event.get('headers', {}).get('X-Slack-Signature'):
        LOGGER.info(f"Passed X-Slack-Signature!: {json.dumps(event)}")
        channel = body['event']['channel']
        text_args = body['event']['text'].split(' ')
        message = ' '.join(text_args[1:])
        post_slack(channel, message)
    return respond(body)
