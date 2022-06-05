import json
import logging
import os
import urllib.request
import ssl
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def respond(res="Hello"):
    ret = {
        'statusCode': '200',
        'body': json.dumps(res, ensure_ascii=False),
        'headers': {
            #'Content-Type': 'application/json',
        },
    }
    LOGGER.info(f"Return: {ret}")
    return ret


def post_slack(channel, message):
    url2="https://ferret.akamaized.net/uploads/article/6845/eyecatch/default-95e77d8922603c5a64085258c0cc3f96.png"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(url2,context=ctx) as web_file, open('/tmp/NASA2.png', 'wb') as local_file:
        local_file.write(web_file.read())
    

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    client = WebClient(token=os.environ.get('OAuthToken'), ssl=ssl_context)
        
    try:
        result = client.files_upload(
           channels=channel,
           initial_comment="Post Same Image!",
           file="/tmp/NASA2.png",
        )
        LOGGER.info(f"Result: {result}")
    except SlackApiError as e:
        LOGGER.info(f"Error uploading file: {e}")
    
def lambda_handler(event, context):
    LOGGER.info(f"Received event: {json.dumps(event)}")
    body = {}
    if event.get('body'):
        body = json.loads(event['body'])
    if event.get('headers', {}).get('X-Slack-Signature'):
        LOGGER.info(f"Passed X-Slack-Signature!: {json.dumps(event)}")
        channel = body['event']['channel']
        LOGGER.info(f"channel!: {channel}")
        if body['event']['files']:
            #image_url
            #LOGGER.info(f"Got file!: {json.dumps(body['event']['files'][0]['thumb_360'])}")
            ans = body['event']['files'][0]['thumb_360']
            LOGGER.info(f"ans content!: {ans}")
        else:
            #text
            text_args = body['event']['text'].split(' ')
            ans = ' '.join(text_args[1:])
        post_slack(channel, ans)
    return respond(body)
