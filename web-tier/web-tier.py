from flask import Flask, request, jsonify
import boto3
from werkzeug.utils import secure_filename
import requests
import  traceback
import time

app = Flask(__name__)
s3 = boto3.client('s3',region_name='us-east-1')
sqs = boto3.client('sqs',region_name='us-east-1')

sqs_request_queue_url = 'https://sqs.us-east-1.amazonaws.com/565393060131/1233405812-req-queue'
sqs_response_queue_url = 'https://sqs.us-east-1.amazonaws.com/565393060131/1233405812-resp-queue'

input_bucket_name = '1233405812-in-bucket'
output_bucket_name = '1233405812-out-bucket'

@app.route('/', methods=['POST'])
def upload_image():
    if 'inputFile' not in request.files:
        return 'No file part', 400
    file = request.files['inputFile']
    filename = secure_filename(file.filename)

    try:
        s3.upload_fileobj(file, input_bucket_name, filename)
        s3_url = f"https://{input_bucket_name}.s3.amazonaws.com/{filename}"
        sqs.send_message(QueueUrl=sqs_request_queue_url,MessageBody=s3_url)
        time.sleep(5)
        image_name, classification_result = poll_response_queue(filename)
        return jsonify({image_name:classification_result}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def poll_response_queue(filename):
    while True:
        response = sqs.receive_message(QueueUrl=sqs_response_queue_url,MaxNumberOfMessages=1,WaitTimeSeconds=10)
        
        messages = response.get('Messages', [])
        if not messages:
            print(f"Still waiting for response for {filename}")
            return
            
        for message in messages:
                sqs.delete_message(QueueUrl=sqs_response_queue_url,ReceiptHandle=message['ReceiptHandle'])
                print(f"Received message: {message['Body']}")
                s3_url = message['Body']
                print(s3_url)
                classification_result = None
                response = requests.get(s3_url)
                image_name = s3_url.split('/')[-1]
                print(image_name)
                if response.status_code == 200:
                    classification_result = response.content.decode('utf-8')
                else:
                    print(f"Failed to retrieve classification result. HTTP Status Code: {response.status_code}")
                    continue
                
                return image_name, classification_result
        else:
            print(f"Still waiting for response for {filename}")

        return None, None

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
