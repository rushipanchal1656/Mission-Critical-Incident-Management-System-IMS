import boto3
import os
import json

sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION"))

QUEUE_URL = os.getenv("SQS_QUEUE_URL")

def enqueue(payload):
    print(f"📤 Sending to SQS: {payload}")

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(payload)
    )