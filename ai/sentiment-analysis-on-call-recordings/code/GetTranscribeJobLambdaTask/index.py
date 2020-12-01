import boto3
import json
import datetime

client = boto3.client('transcribe')


def lambda_handler(event, context):
    try:
        response = client.get_transcription_job(
            TranscriptionJobName=event["TranscriptionJobName"]
        )
        # BELOW IS THE CODE TO FIX SERIALIZATION ON DATETIME OBJECTS
        if "CreationTime" in response["TranscriptionJob"]:
            response["TranscriptionJob"]["CreationTime"] = str(response["TranscriptionJob"]["CreationTime"])
        if "CompletionTime" in response["TranscriptionJob"]:
            response["TranscriptionJob"]["CompletionTime"] = str(response["TranscriptionJob"]["CompletionTime"])
        if "StartTime" in response["TranscriptionJob"]:
            response["TranscriptionJob"]["StartTime"] = str(response["TranscriptionJob"]["StartTime"])
        return response["TranscriptionJob"]
    except Exception as e:
        raise e


def my_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()