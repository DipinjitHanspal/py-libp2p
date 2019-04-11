from easy_sqs import EasySqs
import json

aws_config = json.loads(open("aws_config.json").read())

queue_url = "https://sqs.us-east-1.amazonaws.com/875814277611/test-queue"

def main():
    sqs = EasySqs(aws_config)

    # Send a message to the queue
    send_resp = sqs.send_message(queue_url, json.dumps({
            "type": "throughput_incr",
            "info": "topic1"
        }))
    print("Send response: \n" + str(send_resp))

    # Receive message
    receive_resp = sqs.receive_message(queue_url)
    message_body = receive_resp["Body"]
    print("Receive message body: \n" + str(message_body))

    # Delete message from the queue
    receipt_handle = receive_resp["ReceiptHandle"]
    delete_resp = sqs.delete_message(queue_url, receipt_handle)
    print("Delete response: \n" + str(delete_resp))




if __name__ == "__main__":
    main()