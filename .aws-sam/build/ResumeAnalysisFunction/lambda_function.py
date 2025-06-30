import boto3, json, fitz, urllib.parse, os

s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
jobs_table = dynamodb.Table(os.environ['DYNAMO_TABLE_NAME'])

def invoke_bedrock_model(prompt):
    model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31", "max_tokens": 4096,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id, accept='application/json', contentType='application/json')
    response_body = json.loads(response.get('body').read())
    ai_response_text = response_body['content'][0]['text']
    try:
        return json.loads(ai_response_text)
    except Exception as e:
        print(f"Bedrock model did not return valid JSON. Response: {ai_response_text}")
        raise e

def get_prompt(template_name, resume_text, job_description_text):
    prompts = {
        "achievement": (
            "You are an expert career coach and resume writer specializing in ATS optimization. "
            "Your task is to analyze the provided resume text and job description. For each responsibility or bullet point in the resume, suggest a rewrite that:\n"
            "1. Uses action verbs and quantifiable results\n"
            "2. Mirrors the language and keywords from the job description\n"
            "3. Demonstrates measurable impact\n"
            "4. Uses industry-relevant terminology\n"
            "5. Maximizes the chance of passing an ATS scan for this job\n"
            "\n"
            f"Job Description:\n{job_description_text}\n"
            f"Resume Text:\n{resume_text}\n"
            "\n"
            "Provide the output as a single valid JSON object with one key: 'achievement_suggestions'. Each suggestion should have 'original' and 'rewrite' fields. Limit to 5-7 suggestions."
        ),
        "culture": (
            "You are a strategic HR business partner and resume expert. Analyze the job description to identify company values, culture traits, and priorities. "
            "Then, suggest specific edits to the resume that would resonate with this company's culture and echo their values and language.\n"
            f"Job Description:\n{job_description_text}\n"
            f"Resume Text:\n{resume_text}\n"
            "\n"
            "Provide the output as a single valid JSON object with two keys: 'identified_values' (array of values) and 'alignment_suggestions' (array of suggestions with 'original' and 'rewrite' fields). Limit to 3-5 values and 3-5 suggestions."
        )
    }
    return prompts[template_name]

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    job_id = s3_key
    print(f"Starting analysis for jobId: {job_id}")
    try:
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        pdf_content = s3_object['Body'].read()
        # Get job description from DynamoDB
        job_item = jobs_table.get_item(Key={'jobId': job_id})
        job_description_text = job_item.get('Item', {}).get('jobDescription', 'No job description provided.')

        doc = fitz.open(stream=pdf_content, filetype="pdf")
        resume_text = "".join(page.get_text() for page in doc)
        doc.close()

        achievement_prompt = get_prompt("achievement", resume_text, job_description_text)
        culture_prompt = get_prompt("culture", resume_text, job_description_text)

        achievement_result = invoke_bedrock_model(achievement_prompt)
        culture_result = invoke_bedrock_model(culture_prompt)

        final_feedback = {**achievement_result, **culture_result}

        jobs_table.put_item(Item={'jobId': job_id, 'status': 'COMPLETED', 'feedback': json.dumps(final_feedback)})
        print("Process completed successfully.")
        return {'statusCode': 200, 'body': 'Analysis complete.'}
    except Exception as e:
        print(f"Error for jobId: {job_id}. Error: {str(e)}")
        jobs_table.put_item(Item={'jobId': job_id, 'status': 'FAILED', 'error': str(e)})
        raise e 