# Application for testing the fanout scenario using sns and sqs
import ast
import time
import botocore
import config
import json
import setup_queues_topic 
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def process_records(record):
    logging.info("Inside the process_records function")
    dynamodb = setup_queues_topic.dynamodb_client

    security_id=record["SECURITY_ID"]

    try:
        logging.debug("trying to insert into the dynamodb table")
        dynamodb.put_item(TableName=config.DYNAMODBTBL,
                           Item={"Id":{
                                    "S": security_id},
                                 "SECURITY_RECORD":{
                                    "M": {"LOAD_DT":{"S": record["LOAD_DATE"]},
                                         "PRICE" : {"N":record["PRICE"]},
                                         "TICKER_SYMB" : {"S": record["TICKER_SYMB"]}
                                         }
                                  }
                                },
                           ConditionExpression='attribute_not_exists(Id)')
        logging.debug("Inserted record {}, into dynamodb table successfully.".format(record))
    except botocore.exceptions.ClientError as e:
        # Ignore the ConditionalCheckFailedException, bubble up
        # other exceptions.
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            logging.error("Error occurred while inserting into the dynamodb table ${0}".format(e))
            raise


def process_mutliple_messages(sqs_queue_name):
    logging.info("Inside the process_mutliple_messages function")
    try:
        # Create SQS client
        sqs = setup_queues_topic.sqs_resource
        # Receive message from SQS queue
        queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
        logging.debug("Getting the message from the queue: ${}".format(queue))
        while True:
            messages_to_delete = []
            for message in queue.receive_messages(
                         MaxNumberOfMessages=10):
                body = json.loads(ast.literal_eval(json.loads(message.body)["Message"]))
                logging.debug("extracting the body from the queue: ${}".format(body))
                process_records(record=body)
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
    except ValueError:
        print("Error while processing the queue")
    """
    except:
        print("Error while processing the queue")
    """

if __name__ == '__main__':
    logging.info("Invoking the process to extract the queue : {}".format(config.QUEUE2))
    process_mutliple_messages(config.QUEUE2)
    
