import boto3
import json
import os
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
jobs_table = dynamodb.Table(os.environ['DYNAMO_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        filename = body.get('filename')
        job_description = body.get('jobDescription')
        
        if not filename or not job_description:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'filename and jobDescription are required'})
            }
        
        # Ensure the S3 key ends with .pdf
        name, ext = os.path.splitext(filename)
        if ext.lower() != '.pdf':
            ext = '.pdf'
        job_id = f"{name}-{int(datetime.now().timestamp())}{ext}"
        
        # Create pre-signed URL for S3 upload (no job description in metadata)
        bucket_name = os.environ.get('S3_BUCKET_NAME', 'resume-boost-uploads-sainitesh-123')
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': job_id,
                'ContentType': 'application/pdf',
                # Optionally, you can add a short placeholder in metadata:
                'Metadata': {
                    'job-description': 'provided'
                }
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        # Store initial job status and full job description in DynamoDB
        jobs_table.put_item(Item={
            'jobId': job_id,
            'status': 'PROCESSING',
            'createdAt': datetime.now().isoformat(),
            'filename': filename,
            'jobDescription': job_description
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'jobId': job_id,
                'uploadUrl': presigned_url,
                'status': 'PROCESSING'
            })
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

def invoke_bedrock_model(prompt):
    model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31", "max_tokens": 4096,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id, accept='application/json', contentType='application/json')
    response_body = json.loads(response.get('body').read())
    ai_response_text = response_body['content'][0]['text']
    # Defensive: check if response is empty or not valid JSON
    try:
        return json.loads(ai_response_text)
    except Exception as e:
        print(f"Bedrock model did not return valid JSON. Response: {ai_response_text}")
        raise e 