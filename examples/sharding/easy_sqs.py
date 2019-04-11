import boto3
import json

class EasySqs():

    def __init__(self, config):
        self.sqs_client = boto3.client('sqs', 
            aws_access_key_id=config["aws_access_key_id"], 
            aws_secret_access_key=config["aws_secret_access_key"], 
            region_name=config["region_name"])

    def send_message(self, queue_url, message):
        # Send message to SQS queue
        response = self.sqs_client.send_message(
            QueueUrl=queue_url,
            DelaySeconds=10,
            MessageBody=(
                message
            )
        )
        return response

    def receive_message(self, queue_url):
        response = self.sqs_client.receive_message(
            QueueUrl=queue_url,
            MessageAttributeNames=[
                'string',
            ],
            MaxNumberOfMessages=1,
            VisibilityTimeout=10,
            WaitTimeSeconds=10
        )
        messages = response["Messages"]
        message = messages[0]
        return message

    def delete_message(self, queue_url, receipt_handle):
        response = self.sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        return response
