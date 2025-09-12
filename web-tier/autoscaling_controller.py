import instance_manager as ec2_instances_util
import boto3
import time

sqs_client = boto3.client('sqs', region_name="us-east-1")

def get_sqs_url(client):
    sqs_queue = client.get_queue_url(QueueName="1233405812-req-queue")
    return sqs_queue["QueueUrl"] 

WEB_TIER = "i-0e1edb91db0ae26fd"
App_TIER = "i-063898088024c8a04"

def auto_scale_instances():
    while True:
        queue_length = int(sqs_client.get_queue_attributes(QueueUrl=get_sqs_url(sqs_client), AttributeNames=['ApproximateNumberOfMessages'])
            .get("Attributes").get("ApproximateNumberOfMessages"))

        print("Request queue length:", queue_length)

        running_instances = ec2_instances_util.get_running_instances()
        stopped_instances = ec2_instances_util.get_stopped_instances()
        running_instances.remove(WEB_TIER)
        running_instances.remove(App_TIER)

        if queue_length == 0:
            all_instances = ec2_instances_util.get_running_instances()
            all_instances.remove(WEB_TIER)
            all_instances.remove(App_TIER)
            print("Queue is empty, shutting down all instances except 1 (down scaling)")
            ec2_instances_util.stop_multiple_instances(all_instances)
            return

        elif 1 <= queue_length <= 10:
            if len(running_instances) == 0:
                if len(stopped_instances) >= 1:
                    ec2_instances_util.start_instance(stopped_instances[0])
                else:
                    ec2_instances_util.create_instance()

        elif 5 < queue_length <= 50:
            if len(running_instances) < 10:
                length_of_running_instances = len(running_instances)
                length_of_stopped_instances = len(stopped_instances)
                needed_instances = 10 - length_of_running_instances
                if length_of_stopped_instances >= needed_instances:
                    ec2_instances_util.start_multiple_instances(stopped_instances[:needed_instances])
                else:
                    ec2_instances_util.start_multiple_instances(stopped_instances)
                    for _ in range(needed_instances - length_of_stopped_instances):
                        ec2_instances_util.create_instance()

        time.sleep(10)
        print("Waiting for 10 seconds before checking again...\n")
        return

print("Starting Auto Scaling")
auto_scale_instances()
exit(0)
