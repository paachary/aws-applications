# Application for testing the fanout scenario using sns and sqs
import time
import config
import json
import setup_queues_topic
import logging


logging.basicConfig(filename='fanout_process.log', 
                    format='%(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p', 
                    level=logging.INFO)

def process_mutliple_messages(sqs_queue_name):
    # Create SQS client
    logging.info("Inside the process_mutliple_messages function")
    sqs = setup_queues_topic.sqs_resource
    messages_to_process = []
   # Receive message from SQS queue
    queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
    while True:
        messages_to_delete = []
        for message in queue.receive_messages(
                     MaxNumberOfMessages=10):
            body = json.loads(message.body)
            logging.debug("extracting the body from the queue: ${}".format(body['Message']))

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
             logging.info("Deleting of queue completed")


if __name__ == '__main__':
    logging.info("Invoking the process to extract the queue : {}".format(config.QUEUE2))
    process_mutliple_messages(config.QUEUE1)

