from flask import Flask, request
import csv
import boto3
import base64

app = Flask(__name__)
req_queue_url = 'https://sqs.us-east-1.amazonaws.com/266091126189/1225554005-req-queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/266091126189/1225554005-resp-queue'
import threading

lock = threading.Lock()

def send_file_to_queue(f):
    sqs = boto3.client('sqs', region_name='us-east-1')
    file_content_binary = f.read()
    file_content_base64 = base64.b64encode(file_content_binary).decode('utf-8')
    f_name = f.filename.split('.')[0]
 
    sqs.send_message(
    QueueUrl=req_queue_url,
    MessageAttributes={
        'Filename': {
            'DataType': 'String',
            'StringValue': f_name,
        },
    },
    MessageBody=(file_content_base64)
)

def get_response_from_queue(fname):
    sqs = boto3.client('sqs', region_name='us-east-1')
    response = sqs.receive_message(
        QueueUrl=response_queue_url,
        MaxNumberOfMessages=10,
        MessageAttributeNames=[
            'All',
        ],
        WaitTImeSeconds=60,

    )
    if 'Messages' in response:
        print("Got message from queue...")
        for message in response['Messages']:
            content = message['Body']
            file_name = content.split(':')[0]
            if file_name==fname:
                return content
    else:
        return None

@app.route("/", methods=['POST'])
def process_file():
    f = request.files['inputFile']
    f_name = f.filename.split('.')[0]
    result = None
    print("sending file to queue")
    with lock:
        send_file_to_queue(f)
    print("sent file to queue")
    while result is None:
        with lock:
            result = get_response_from_queue(f_name)
    return result