import json
import logging
import os
import urllib.request
import ssl
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import proto
import datetime
from google.cloud import vision
import time

# Instantiates a client
client_vision_api = vision.ImageAnnotatorClient()

#Setting Log 
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

#Setting SSL  authentication
ssl_context = ssl.create_default_context(cafile=certifi.where())
client = WebClient(token=os.environ.get('OAuthToken'), ssl=ssl_context)

def judge_back_symbol(symbol):
    flag = False
    flag_3 = 0
    if "class" in symbol:
        flag = True
        symbol = "class"
    if "def" in symbol:
        flag = True
        symbol = "def"
    if "for" in symbol:
        flag = True
        symbol = "for"
    if "while" in symbol:
        flag = True
        symbol = "while"
    if "if" in symbol:
        flag = True
        symbol = "if"
    if "elif" in symbol:
        flag = True
        symbol = "elif"
    if "else" in symbol:
        flag = True
        symbol = "else"
    if "#" in symbol and  "101" in symbol:
        flag = True
        flag_3 = 1
        symbol = "#101"  
    if "#" in symbol and  "102" in symbol:
        flag = True
        flag_3 = 2
        symbol = "#102"
    return flag,symbol,flag_3

def judge_front_symbol(symbol):
    flag = False
    if ':' in symbol:
        if "class" in symbol[:6]:flag=True
        if "def" in symbol[:6]:flag=True
        if "for" in symbol[:6]:flag=True
        if "while" in symbol[:6]:flag=True
        if "if" in symbol[:6]:flag=True
        if "elif" in symbol[:6]:flag=True
        if "else" in symbol[:6]:flag=True
    return flag


def judge_indent(symbol,symbols,symbol_nums):
    if len(symbols) >= 2:
        if symbol == "elif" and symbols[-2] == "if":
            return  symbol_nums[-1]
        if symbol == "else" and symbols[-2] == "if":
            return  symbol_nums[-1]
        if symbol == "else" and symbols[-2] == "elif":
            return  symbol_nums[-1]
        if symbol == "if" and symbols[-2] == "else":
            return symbol_nums[-1] -1
    if symbol == "def":
        if len(symbol_nums) > symbols.index("def"):
            return symbol_nums[symbols.index("def")]
    if symbol == "class":
        if len(symbol_nums) > symbols.index("class"):
            return symbol_nums[symbols.index("class")]
    return -1

def content_process(datalist):
    indent_cnt = 0
    symbols = []
    symbol_nums = []
    former_indent = 0
    former_is_symbol = False
    flag_3 = 0
    flag_4 = False
    former_flag_3 = False
    former_flag_3_cnt = 0
    new_content = ""
    fomer_row_ind = 0
    flag,symbol,flag_3 = judge_back_symbol(datalist[:5])
    if flag:
        symbols.append(symbol)
        symbol_nums.append(1)
        former_is_symbol = True

    for i in range(len(datalist)):
        new_content += datalist[i] 
        if datalist[i] == '\n':    
            front_symbol = datalist[fomer_row_ind:i]
            back_symbol = datalist[i+1:i+6]
            flag,symbol,flag_3 = judge_back_symbol(back_symbol)
            if flag :
                symbols.append(symbol)
                if len(symbol_nums) == 0:
                    indent_cnt = former_indent
                else:
                    if former_is_symbol:
                        if former_flag_3:
                            indent_cnt = former_indent
                        else:
                            indent_cnt += 1
                    else:
                        if flag_3 == 2:
                            indent_cnt = former_indent - 1
                            former_flag_3 = True
                            former_flag_3_cnt = 0
                        elif flag_3 == 1: 
                            indent_cnt = 0
                        else:
                            tmp_cnt= judge_indent(symbol,symbols,symbol_nums)
                            if tmp_cnt != -1:
                                indent_cnt = tmp_cnt
                            else:
                                indent_cnt = former_indent
                symbol_nums.append(indent_cnt)
                former_is_symbol = True
            else:
                if judge_front_symbol(front_symbol):
                    indent_cnt += 1
                else:
                    if former_flag_3:
                        former_flag_3_cnt += 1
                        if former_indent >= 1:
                            if former_flag_3_cnt != 1:
                                indent_cnt = former_indent - 1
                            else:
                                indent_cnt = former_indent
                        else:
                            indent_cnt = 0
                            former_flag_3 = False
                    else:
                        indent_cnt = former_indent
                former_is_symbol = False
            new_content += "    " * indent_cnt
            former_indent = indent_cnt
            fomer_row_ind = i
    return new_content

def load_content(content):
    image = vision.Image(content=content)
    # Performs label detection on the image file
    response =  client_vision_api.document_text_detection(
        image=image,
        image_context={'language_hints': ['ja','en']}
    )
    response_content = proto.Message.to_json(response)
    LOGGER.info(f"Vision_API:{response_content}")
    text_json = json.loads(response_content)
    datalist_before = text_json["textAnnotations"]
    LOGGER.info(f"datalist_before_length:{len(datalist_before)}")
    if len(datalist_before) <= 10:
        return "101.jpg"
    else:
        datalist = datalist_before[0]["description"]
        new_content = content_process(datalist)
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        # Format: YYYYMMDDhhmmss
        now_time = now.strftime('%Y%m%d%H%M%S')
        create_file_name = "test" + str(now_time) + ".py"
        f = open('/tmp/'+ create_file_name, 'w')
        f.writelines(new_content)
        f.close()
        return create_file_name

    


def respond(res="Hello"):
    #Post the content 
    ret = {
        'statusCode': '200',
        'body': json.dumps(res, ensure_ascii=False),
        'headers': {
            #'Content-Type': 'application/json',
        },
    }
    #LOGGER.info(f"Return: {ret}")
    return ret


def public_image(file_id):
    try:
        #Publicize the image to the channel using slack SDK
        result = client.files_sharedPublicURL(
            token=os.environ.get('UserToken'),
            file=file_id,
        )
        # Log the result
        #LOGGER.info(f"Result public image: {result}")

    except SlackApiError as e:
        LOGGER.info(f"Error public file: {e}")

def post_image_slack(channel,url=None,message=None,flag=False):
    #Ignore the ssl authentication
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    #Output the full url
    #LOGGER.info(f"Full url: {url}")
    
    #Get the content of the image from the given url
    with urllib.request.urlopen(url,context=ctx) as web_file, open('/tmp/test.jpg', 'wb') as local_file:
        local_file.write(web_file.read())
    
    if flag:
        # Loads the image into memory
        with open('/tmp/test.jpg', 'rb') as image_file:
            content = image_file.read()
            #LOGGER.info(f"The content using gcp api: {content}")
            file_path="/tmp/"+load_content(content)
            LOGGER.info(f"File Path: {file_path}")
            
            if file_path == "/tmp/101.jpg":
                file_type="jpg"
                file_path="/tmp/test.jpg"
                message = " You can post only a screenshot of a code!!"
            else:
                file_type="python"
            #LOGGER.info(f"Sceenshot file path: {file_path}")

    else:
        file_path="/tmp/test.jpg"
        file_type="jpg"
        LOGGER.info(f"Failed  path: {file_path}")
        
    try:
        #Upload the image to the channel using slack SDK
        result = client.files_upload(
           channels=channel,
           initial_comment=message,
           file=file_path,
           filetype=file_type,
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
    #Setting  variables
    flag = False
    body = {}
    channel=""

    #Output received the event
    #LOGGER.info(f"Received event: {json.dumps(event)}")

    #Verify the challenge authentication
    if event.get('challenge'):
        return event.get('challenge')
        
    #Get the body of the event
    if event.get('body'):
        body = json.loads(event['body'])
        
    #Check slack signature
    if event.get('headers', {}).get('X-Slack-Signature'):
        LOGGER.info(f"Passed X-Slack-Signature!: {json.dumps(event)}")
        try:
            channel = body['event']['channel']
            #LOGGER.info(f"channel!: {channel}")
            
            #Setting the variables about image_url
            team_id = body['team_id']
            file_id = body['event']['files'][0]['id']
            file_name =  body['event']['files'][0]['name']
            pre_url = body['event']['files'][0]['permalink_public']
                
            #Make the image URL
            url = make_image_url(team_id,file_id,file_name,pre_url)
            
            #Publicize the url of the image
            public_image(file_id)
            
            #Make the comment of the image if success
            message = "Make a code file sucessfully from AWS!!"
            
            LOGGER.info(f"team_id: {team_id} file_id: {file_id} file_name: {file_name}")
            flag=True
            post_image_slack(channel,url,message,flag)
            return respond(body)

        except KeyError as e:
            LOGGER.info("KeyError_Begin")
            message = " You can post only a screenshot of a code!!"
            url = os.environ.get('BadURL')
            post_image_slack(channel,url,message,flag)
            LOGGER.info("KeyError101")
            return respond(body)
    time.sleep(5)
