#!/bin/sh
aws configure set region `curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region`
cd /home/ec2-user
python process_records_from_queue_to_dynamodb.py
