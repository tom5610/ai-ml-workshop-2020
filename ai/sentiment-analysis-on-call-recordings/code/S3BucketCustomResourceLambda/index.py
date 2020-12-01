import util.cfnresponse
import boto3
import uuid

client = boto3.client('s3')

cfnresponse = util.cfnresponse

def lambda_handler(event, context):
    response_data = {}
    try:
        if event["RequestType"] == "Create":
            bucket_name = uuid.uuid4().hex+'-connect'
            # response = client.create_bucket(
            #     Bucket=bucket_name,
            # )
            response_data["BucketName"] = bucket_name
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)

        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
    except Exception as e:
        print(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
