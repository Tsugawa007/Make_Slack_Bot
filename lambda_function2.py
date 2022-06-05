import json
import logging
import os
import requests
import io
import base64
import urllib.request
import ssl

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
    #response = requests.get(url2)
    #file_data = response.content

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(url2,context=ctx) as web_file, open('/tmp/NASA2.png', 'wb') as local_file:
        local_file.write(web_file.read())
        LOGGER.info(f"IsFileContent?: {web_file.read()}")
        
        
    files = {'file': open('/tmp/NASA2.png', 'rb')}

    #r = requests.get(message, stream=True)
    #img_bytes = base64.b64decode(r.content)
    file_name = "cat.jpg"
    
    headers = {
        #Content-Type': 'multipart/form-data',
        "Authorization": f"Bearer {os.environ.get('OAuthToken')}"
    }
    
    #url = "https://slack.com/api/chat.postMessage"
    url = "https://slack.com/api/files.upload"
  

    payload = {
        'token': os.environ.get('PostToken'),
        'channels': channel
    }

    #LOGGER.info(f"Header: {headers} Payload: {payload}")
    '''
    res = requests.post(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    '''
    res = requests.post(
        url=url,data={"json": json.dumps(payload).encode("utf-8")},files=files,headers=headers)
    LOGGER.info(f"json content: {res.json()}")


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
