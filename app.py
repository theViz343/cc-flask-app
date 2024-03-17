from flask import Flask, request
import csv
import boto3
import base64

app = Flask(__name__)
req_queue_url = 'https://sqs.us-east-1.amazonaws.com/266091126189/1225554005-req-queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/266091126189/1225554005-resp-queue'

def send_file_to_queue(f):
    sqs = boto3.client('sqs')
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

@app.route("/", methods=['POST'])
def process_file():
    f = request.files['inputFile']
    f_name = f.filename.split('.')[0]
    result = "File not found."
    send_file_to_queue(f)

    with open('lookup.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == f_name:
                result = f"{f_name}:{row[1]}"
    return result