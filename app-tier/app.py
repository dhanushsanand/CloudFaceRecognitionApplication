from face_recognition import face_match
import boto3
import json
import os
import requests

sqs = boto3.client('sqs', region_name='us-east-1') 
s3 = boto3.client('s3', region_name='us-east-1')
output_bucket_name = '1233405812-out-bucket'
sqs_response_queue_url = 'https://sqs.us-east-1.amazonaws.com/565393060131/1233405812-resp-queue'

REQUEST_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/565393060131/1233405812-req-queue'
DOWNLOAD_DIR = '/home/ubuntu/app-tier/model/downloaded_images'

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def process_sqs_message():
    while True:
        try:
            response = sqs.receive_message(
            QueueUrl=REQUEST_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
            )
            messages = response.get('Messages', [])
            if not messages:
                print("No messages in queue...")
                return 
            for message in messages:
                print(f"Received message: {message['Body']}")
                s3_url = message['Body']
                print(s3_url)
                image_name = s3_url.split('/')[-1]
                print(image_name)
                response = requests.get(s3_url)
                if response.status_code == 200:
                    image_path = os.path.join(DOWNLOAD_DIR, image_name)
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    result=face_match(image_path,'data.pt')
                    key = image_name.split('.')[0]
                    s3.put_object(Bucket=output_bucket_name,Key=key,Body=result[0])
                    s3_url = f"https://{output_bucket_name}.s3.amazonaws.com/{key}"
                    sqs.send_message(QueueUrl=sqs_response_queue_url,MessageBody=s3_url)
                    print(f"Image {image_name} downloaded successfully at {image_path}")
                    os.remove(image_path)
                else:
                    print(f"Failed to download image {image_name}. HTTP Status Code: {response.status_code}")
                    return
                sqs.delete_message(
                    QueueUrl=REQUEST_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
                print(f"Message deleted from queue.")
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")

if __name__ == "__main__":
    process_sqs_message()
