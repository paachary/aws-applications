# Application for testing the fanout scenario using sns and sqs
import time
import config
import json
import setup_queues_topic


def process_mutliple_messages(sqs_queue_name):
    # Create SQS client
    sqs = setup_queues_topic.sqs_resource
    messages_to_process = []
   # Receive message from SQS queue
    queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
    while True:
        messages_to_delete = []
        for message in queue.receive_messages(
                     MaxNumberOfMessages=10):
            body = json.loads(message.body)
            print('Received message: %s' % body['Message'])

            # add message to delete
            messages_to_delete.append({
            'Id': message.message_id,
            'ReceiptHandle': message.receipt_handle
           })

        # if you don't receive any notifications the
        # messages_to_delete list will be empty
        if len(messages_to_delete) == 0:
                time.sleep(10)
         # delete messages to remove them from SQS queue
         # handle any errors
        else:
             delete_response = queue.delete_messages(
                     Entries=messages_to_delete)

if __name__ == '__main__':
    process_mutliple_messages(config.QUEUE1)

