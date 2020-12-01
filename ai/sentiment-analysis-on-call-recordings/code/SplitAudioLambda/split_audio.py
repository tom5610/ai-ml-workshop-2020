import boto3
import glob
import logging
import os
import uuid
import urllib
import datetime

# 
# Lambda requirements:
#   Access to read and write for S3, and log
#   S3 Create (all) as a trigger with a wav suffix
#   Environment variables:
#       destination_bucket
#       left_key_prefix
#       right_key_prefix
# 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.resource('s3')
s3client = boto3.client('s3')
destination_bucket_name = os.environ['destination_bucket']
left_key_prefix = os.environ['left_key_prefix']
right_key_prefix = os.environ['right_key_prefix']
destination_folder = os.environ['destination_folder']

logger.info('Initialized with destination {}, right_key_prefix {}, left_key_prefix {}'.format(destination_bucket_name, left_key_prefix, right_key_prefix))

os.environ['PATH'] = os.environ['PATH'] + ':' + os.environ['LAMBDA_TASK_ROOT'] 
logger.info('PATH: {}'.format(os.environ['PATH']))

def split_new_recording(event, context):
    for record in event['Records']:
        clean_temp_folder()

        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote(record['s3']['object']['key'])
        response = s3client.head_object(Bucket=bucket, Key=key)
        contactId = response['Metadata']['contact-id']
        
        dt = datetime.date.today()
        year = '{:%Y}'.format(dt)
        month = '{:%m}'.format(dt)
        logger.info('the month is: {} and the year is: {}'.format(month, year))
        logger.info('Object ContactID: {}'.format(contactId))

        logger.info('Invoked for bucket {} key {}'.format(bucket, key))
        temp_file = fetch_source(bucket, key)
        left_result_key = destination_folder + left_key_prefix + '/' + year + '/' + month + '/' + contactId + '-' + left_key_prefix + '.wav'
        right_result_key = destination_folder + right_key_prefix + '/' + year + '/' + month + '/' + contactId + '-' + right_key_prefix + '.wav'
        put_result(split_channel(temp_file, 1), destination_bucket_name, left_result_key)
        put_result(split_channel(temp_file, 2), destination_bucket_name, right_result_key)

    return "ok"

def split_channel(temp_file, channel_num):
    result_temp_file = '/tmp/{}.wav'.format(uuid.uuid4())
    command = 'sox {} {} remix {}'.format(temp_file, result_temp_file, channel_num)
    logger.info('Executing {}'.format(command))
    os.system(command)
    return result_temp_file

def fetch_source(bucket_name, key):
    temp_file = '{}/{}.wav'.format(temp_folder(), uuid.uuid4())
    source_bucket = s3.Bucket(bucket_name)
    source_bucket.download_file(key, temp_file)
    return temp_file

def put_result(local_file, destination_bucket_name, destination_key):
    logger.info('putting file {} in to bucket: {} with file name {}'.format(local_file, destination_bucket_name, destination_key))
    destination_bucket = s3.Bucket(destination_bucket_name)
    destination_bucket.upload_file(local_file, destination_key)

def temp_folder():
    return '/tmp'

def clean_temp_folder():
    for file in glob.glob(temp_folder() + '/*.wav'):
        os.remove(file)