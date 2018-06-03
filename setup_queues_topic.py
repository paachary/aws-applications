# Application for testing the fanout scenario using sns and sqs
import config
import boto3


def get_current_region():
    return boto3.session.Session().region_name


def get_account_name():
    return boto3.client("sts").get_caller_identity()["Account"]


sqs_client        = boto3.client('sqs',get_current_region())
sns_client        = boto3.client('sns',get_current_region())
s3_client         = boto3.client('s3',get_current_region())
sns_boto_resource = boto3.resource('sns',get_current_region())
dynamodb_client   = boto3.client('dynamodb',get_current_region())
sqs_resource      = boto3.resource('sqs',get_current_region())


def get_topic_arn(topic_name):
    return "arn:aws:sns:"+get_current_region()+":"+get_account_name()+":"+topic_name


def create_sns_topic(topic_name):
    response = sns_client.create_topic(Name=topic_name)
    print("Successfully created topic {0}".format(topic_name))


def create_queues(queues):
    for queue in queues:
        request = sqs_client.create_queue(QueueName=queue)
        print('Created queue : {0} successfully'.format(queue))


def get_queue_url(queue):
    response = sqs_client.get_queue_url(QueueName=queue)
    return response["QueueUrl"]


def subscribe_to_topic(topic_arn, queues):
    topic = sns_boto_resource.Topic(topic_arn)
    for queue in queues:
        subscription = topic.subscribe(
                             Protocol="sqs",
                             Endpoint="arn:aws:sqs:"+get_current_region()+":"+get_account_name()+":"+queue
                            )
        print("Successfully subscribed queue: {0} to topic: {1}".format(queue, topic))
        print(subscription)



"""
if __name__ == "__main__":
    queue1 = config.QUEUE1
    queue2 = config.QUEUE2
#    topic_name = config.TOPIC
#
#    queues = [queue1, queue2]
#    create_sns_topic(topic_name)
#    create_queues(queues)
#    topic_arn = get_topic_arn(topic_name)
#    subscribe_to_topic(topic_arn, queues)

#    print(get_queue_url(queue1))
#    print(get_queue_url(queue2))
"""
