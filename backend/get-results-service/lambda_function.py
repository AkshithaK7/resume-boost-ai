import boto3, json, os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMO_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        job_id = event['pathParameters']['jobId']
    except KeyError:
        return {
            'statusCode': 400, 
            'headers': {
                'Content-Type': 'application/json', 
                'Access-Control-Allow-Origin': '*'
            }, 
            'body': json.dumps({'error': 'jobId not found in path.'})
        }

    try:
        response = table.get_item(Key={'jobId': job_id})
        
        if 'Item' in response:
            item = response['Item']
            
            # Parse feedback JSON if it exists and is a string
            if item.get('status') == 'COMPLETED' and isinstance(item.get('feedback'), str):
                try:
                    item['feedback'] = json.loads(item['feedback'])
                except json.JSONDecodeError:
                    # If feedback is not valid JSON, keep it as is
                    pass
                    
            return {
                'statusCode': 200, 
                'headers': {
                    'Content-Type': 'application/json', 
                    'Access-Control-Allow-Origin': '*'
                }, 
                'body': json.dumps(item)
            }
        else:
            # Job not found, return processing status
            return {
                'statusCode': 404, 
                'headers': {
                    'Content-Type': 'application/json', 
                    'Access-Control-Allow-Origin': '*'
                }, 
                'body': json.dumps({'status': 'PROCESSING'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500, 
            'headers': {
                'Content-Type': 'application/json', 
                'Access-Control-Allow-Origin': '*'
            }, 
            'body': json.dumps({'error': str(e)})
        } 