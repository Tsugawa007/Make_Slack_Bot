import json

def lambda_handler(event, context):
    ret = {
        'statusCode': '200',
        'body': json.dumps(event.get('body'), ensure_ascii=False),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    return ret
