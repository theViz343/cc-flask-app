import boto3

req_queue_url = 'https://sqs.us-east-1.amazonaws.com/266091126189/1225554005-req-queue'

def get_queue_length(queue_url):
    sqs = boto3.client('sqs', region_name='us-east-1')
    response = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    return int(response['Attributes']['ApproximateNumberOfMessages'])

def count_instances_with_tag(tag_key, tag_value):
    ec2 = boto3.client('ec2', region_name='us-east-1')
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:' + tag_key, 'Values': [tag_value]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    count = sum(len(reservations['Instances']) for reservations in response['Reservations'])
    return count

def scale_up(number):
    ec2 = boto3.client('ec2', region_name='us-east-1')
    user_data_script = 'user_data_script.sh'
    with open(user_data_script, 'r') as file:
        user_data = file.read()
    response = ec2.run_instances(
        ImageId='ami-099e7b73e6931c1a0',
        InstanceType='t2.micro',
        UserData=user_data,
        MinCount=number,
        MaxCount=number,
        IamInstanceProfile={
            'Arn': "arn:aws:iam::266091126189:instance-profile/sqs-and-s3-full-access"
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'app-tier-instance'
                    },
                ]
            }
        ]

    )

def scale_down(number):
    ec2 = boto3.client('ec2', region_name='us-east-1')
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['app-tier-instance']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    instance_ids = [instance['InstanceId'] for reservation in response['Reservations'] for instance in reservation['Instances']]
    count = min(count, len(instance_ids))
    if count > 0:
        ec2.terminate_instances(InstanceIds=instance_ids[:count])

while True:
    number_of_messages = get_queue_length(req_queue_url)
    no_of_instances_needed = min(int((number_of_messages/50)*19), 20)
    current_number = count_instances_with_tag('Name', 'app-tier-instance')
    print("Number of messages", number_of_messages)
    print("Number of instances needed", no_of_instances_needed)
    print("Current number of instances", current_number)
    if current_number>no_of_instances_needed:
        scale_down(current_number-no_of_instances_needed)
    elif current_number<no_of_instances_needed:
        scale_up(no_of_instances_needed-current_number)