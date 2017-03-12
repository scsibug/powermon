import boto3
import os
import json
import subprocess
import time
import sys

# Inspired by code at https://billyoverton.com/2016/06/19/smart-meter-collecting-the-data.html

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='powermon_scm')
sender_name = os.environ['POWERMON_SENDER']
f = open('realtime.scm.csv', 'r')
for line in iter(f):
    print line
    cols = line.split(",")
    send_data = {'MeterID': cols[3], 'Consumption': cols[7], 'Time': cols[0], 'MeterType': cols[4], 'Sender': sender_name}
    print cols
    print send_data
    queue.send_message(MessageBody=json.dumps(send_data))
f.close()

