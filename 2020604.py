import urllib.request
import ssl

def is_file_content(img_file_path):
    #Ignore ssl certification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    #AWS /tmps/

    with urllib.request.urlopen(url2,context=ctx) as web_file, open(img_file_path, 'wb') as local_file:
        local_file.write(web_file.read())
        LOGGER.info(f"IsFileContent?: {web_file.read()}")
        
        
    files = {'file': open(img_file_path, 'rb')}

    return files


def use_slack_authtoken(path,OAuthToken,PostToken,channel):
    headers = {
        "Content-Type": "multipart/form-data",
        "Authorization": f"Bearer {os.environ.get('OAuthToken')}"
    }
    
    payload = {
        'token': os.environ.get('PostToken'),
        'channels': channel
    }
    #Insert files_upload api url
    url = SLACK_API_URL

    res = requests.post(url=url,data={"json": json.dumps(payload).encode("utf-8")},files=files,headers=headers)
 

  
