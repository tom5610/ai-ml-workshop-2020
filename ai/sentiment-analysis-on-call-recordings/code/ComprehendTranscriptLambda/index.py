import boto3
import json

s3_client = boto3.client('s3')
comprehend_client = boto3.client('comprehend')


def lambda_handler(event, context):
    try:
        s3_object = event["Records"][0]["s3"]
        key = s3_object["object"]["key"]
        bucket_name = s3_object["bucket"]["name"]
        comprehend_key_name = get_comprehend_key_name(key)

        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        transcript_result = json.loads(obj['Body'].read())
        transcriptions = transcript_result["results"]["transcripts"]
        text_list = []
        for t in transcriptions:
            text_list.append(t["transcript"])
        payload = build_initial_payload(key)
        payload["text"] = text_list

        sentiment_response = batch_detect_sentiment(text_list)
        entities_response = batch_detect_entities(text_list)
        key_phrases_response = batch_detect_key_phrases(text_list)
        dominant_language_response = batch_detect_dominant_language(text_list)

        payload["Sentiment"] = sentiment_response["ResultList"]
        payload["Entities"] = entities_response["ResultList"]
        payload["KeyPhrases"] = key_phrases_response["ResultList"]
        payload["DominantLanguage"] = dominant_language_response["ResultList"]


        with open('/tmp/' + comprehend_key_name, 'w') as outfile:
            json.dump(payload, outfile)
        s3_client.upload_file('/tmp/' + comprehend_key_name, bucket_name, "comprehend/" + comprehend_key_name)
        return payload
    except Exception as e:
        raise e


def get_comprehend_key_name(key):
    key_name_without_the_file_type = key.split('.')[0]
    key_name_without_folder = key_name_without_the_file_type.split('/')
    return key_name_without_folder[len(key_name_without_folder) - 1] + "-comprehend.json"


def build_initial_payload(key):
    payload = {}
    split_with_dot = key.split(".")
    split_with_dash = split_with_dot[0].split("-")
    payload["talker"] = split_with_dash[len(split_with_dash) - 1]
    payload["key"] = remove_slash(split_with_dot[0])

    contact_id = ""
    counter = 0
    split_length = len(split_with_dash)

    for item in split_with_dash:
        if counter == split_length - 1:
            contact_id = contact_id
        elif counter == split_length - 2:
            contact_id = contact_id + item
        else:
            contact_id = contact_id + item + "-"

        counter += 1

    payload["contactId"] = remove_slash(contact_id)
    return payload


def remove_slash(str):
    split_with_slashes = str.split("/")
    return split_with_slashes[len(split_with_slashes) - 1]

def batch_detect_sentiment(text_list):
    return comprehend_client.batch_detect_sentiment(
            TextList=text_list,
            LanguageCode='en'
    )

def batch_detect_key_phrases(text_list):
    return comprehend_client.batch_detect_key_phrases(
        TextList=text_list,
        LanguageCode='en'
    )

def batch_detect_entities(text_list):
    return comprehend_client.batch_detect_entities(
        TextList=text_list,
        LanguageCode='en'
    )

def batch_detect_dominant_language(text_list):
    return comprehend_client.batch_detect_dominant_language(
        TextList=text_list
    )
