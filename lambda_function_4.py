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
    #Post the content 
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
        #Publicize the image to the channel using slack SDK
        result = client.files_sharedPublicURL(
            token=os.environ.get('UserToken'),
            file=file_id,
        )
        # Log the result
        LOGGER.info(f"Result public image: {result}")

    except SlackApiError as e:
        LOGGER.info(f"Error public file: {e}")

def post_slack(channel,url=None,message=None):
    #Ignore the ssl authentication
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    #Output the full url
    LOGGER.info(f"Full url: {url}")
    
    #Get the content of the image from the given url
    with urllib.request.urlopen(url,context=ctx) as web_file, open('/tmp/test.jpg', 'wb') as local_file:
        local_file.write(web_file.read())
    
        
    try:
        #Upload the image to the channel using slack SDK
        result = client.files_upload(
           channels=channel,
           initial_comment=message,
           file="/tmp/test.jpg",
           filetype="jpg",
        )
        
        #Output the success log
        LOGGER.info(f"Result post slack: {result}")
    except SlackApiError as e:
        #Output the false log
        LOGGER.info(f"Error uploading file: {e}")
        
def make_image_url(team_id,file_id,file_name,pre_url):
    #Shape the url
    ind = pre_url.rfind('-')
    pub_secret = pre_url[ind+1:]
    url = f"https://files.slack.com/files-pri/{team_id}-{file_id}/{file_name}?pub_secret={pub_secret}"
    return url
    
def lambda_handler(event, context):
    #Output received the event
    LOGGER.info(f"Received event: {json.dumps(event)}")
    
    body = {}
    #Verify the challeng authentication
    if event.get('challenge'):
        return event.get('challenge')
        
    #Get the body of the event
    if event.get('body'):
        body = json.loads(event['body'])
        
    #Check slack signature
    if event.get('headers', {}).get('X-Slack-Signature'):
        LOGGER.info(f"Passed X-Slack-Signature!: {json.dumps(event)}")
        channel = body['event']['channel']
        
        #Output your channel ID
        LOGGER.info(f"channel!: {channel}")
        #If get
        try:
            #image_url
            team_id = body['team_id']
            file_id = body['event']['files'][0]['id']
            file_name =  body['event']['files'][0]['name']
            pre_url = body['event']['files'][0]['permalink_public']

            #Upload from IOSsmartphone
            if "iOS" in file_name:
                file_name = os.environ.get('IphoneName')
                
            #Make the image URL
            url = make_image_url(team_id,file_id,file_name,pre_url)
            
            #Publicize the url of the image
            public_image(file_id)
            
            #Make the comment of the image if success
            message = "Post Same Image from AWS!!"
            

            
            LOGGER.info(f"team_id: {team_id} file_id: {file_id} file_name: {file_name}")
        except KeyError as e:
            #This url is used by posting error messages
            url = os.environ.get('BadURL')
            #Make the comment of the image  if false
            message = "You can post only the image file!!"
        #Post the image to the channel
        post_slack(channel,url,message)
        
    return respond(body)
