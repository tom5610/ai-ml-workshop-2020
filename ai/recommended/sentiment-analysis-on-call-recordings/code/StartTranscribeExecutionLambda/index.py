
import boto3
import os
import json
client = boto3.client('stepfunctions')


def lambda_handler(event, context):
    try:
        s3_object = event["Records"][0]["s3"]
        key = s3_object["object"]["key"]
        bucket_name = s3_object["bucket"]["name"]
        print(key)
        print(os.environ['TRANSCRIBE_STATE_MACHINE_ARN'])
        region = os.environ['AWS_REGION']
        file_uri = form_key_uri(bucket_name, key, region)
        job_name = get_job_name(key)
        print(job_name)
        execution_input = {
          "jobName": job_name,
          "mediaFormat": os.environ["MEDIA_FORMAT"],
          "fileUri": file_uri,
          "languageCode": os.environ["LANGUAGE_CODE"],
          "transcriptDestination": os.environ["TRANSCRIPTS_DESTINATION"],
          "wait_time": os.environ["WAIT_TIME"]
        }

        response = client.start_execution(
            stateMachineArn=os.environ['TRANSCRIBE_STATE_MACHINE_ARN'],
            input=json.dumps(execution_input)
        )
        print(response)
        return "hello"
    except Exception as e:
        raise e


def get_job_name(key):
    key_name_without_the_file_type = key.split('.')[0]
    #REMOVING FOLDERS
    keys = key_name_without_the_file_type.split('/')
    keys = keys[len(keys)-1].split("%") #THIS IS TO CLEAN UP CHARACTERS NOT ALLOWED BY TRANSCRIBE JOB
    #GETTING THE FIRST ELEMENT
    return keys[0]


def form_key_uri(bucket_name,key,region):
    return "https://s3.amazonaws.com/"+bucket_name+"/"+key

