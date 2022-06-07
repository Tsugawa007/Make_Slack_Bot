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
ssl_context = ssl.create_default_context(cafile=certifi.where())
client = WebClient(token=os.environ.get('OAuthToken'), ssl=ssl_context)

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


def public_image(file_id):
    try:
        result = client.files_sharedPublicURL(
            token=os.environ.get('UserToken'),
            file=file_id,
        )
        # Log the result
        LOGGER.info(f"Result public image: {result}")

    except SlackApiError as e:
        LOGGER.info(f"Error public file: {e}")

def post_slack(channel,url=None):
    #url="https://ferret.akamaized.net/uploads/article/6845/eyecatch/default-95e77d8922603c5a64085258c0cc3f96.png"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    LOGGER.info(f"Full url: {url}")
    with urllib.request.urlopen(url,context=ctx) as web_file, open('/tmp/NASA3.jpg', 'wb') as local_file:
        local_file.write(web_file.read())
    

    #ssl_context = ssl.create_default_context(cafile=certifi.where())
    #client = WebClient(token=os.environ.get('OAuthToken'), ssl=ssl_context)
        
    try:
        result = client.files_upload(
           channels=channel,
           initial_comment=f"Post Same Image from AWS!!",
           file="/tmp/NASA3.jpg",
           filetype="jpg",
        )
        LOGGER.info(f"Result post slack: {result}")
    except SlackApiError as e:
        LOGGER.info(f"Error uploading file: {e}")
        
def make_image_url(team_id,file_id,file_name,pre_url):
    ind = pre_url.rfind('-')
    pub_secret = pre_url[ind+1:]
    #ind_1 = pre_url.rfind('/')
    #pre_pub_secret = pre_url[:ind_1]
    #ind_2 = pre_pub_secret.rfind('-')
    #pub_secret = pre_pub_secret[ind_2+1:]
    url = f"https://files.slack.com/files-pri/{team_id}-{file_id}/{file_name}?pub_secret={pub_secret}"
    return url
    
def lambda_handler(event, context):
    LOGGER.info(f"Received event: {json.dumps(event)}")
    body = {}
    if event.get('challenge'):
        return event.get('challenge')
    if event.get('body'):
        body = json.loads(event['body'])
    if event.get('headers', {}).get('X-Slack-Signature'):
        LOGGER.info(f"Passed X-Slack-Signature!: {json.dumps(event)}")
        channel = body['event']['channel']
        LOGGER.info(f"channel!: {channel}")
        if body['event']['files']:
            #image_url
            #LOGGER.info(f"Got file!: {json.dumps(body['event']['files'][0]['thumb_360'])}")
            team_id = body['team_id']
            file_id = body['event']['files'][0]['id']
            file_name =  body['event']['files'][0]['name']
            pre_url = body['event']['files'][0]['permalink_public']
            url = make_image_url(team_id,file_id,file_name,pre_url)
            public_image(file_id)
            LOGGER.info(f"team_id: {team_id} file_id: {file_id} file_name: {file_name}")
        else:
            #text
            text_args = body['event']['text'].split(' ')
            ans = ' '.join(text_args[1:])
        post_slack(channel,url)
    return respond(body)
