from __future__ import print_function
import boto3
import os
import json
import subprocess
import time
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Inspired by code at https://billyoverton.com/2016/06/19/smart-meter-collecting-the-data.html

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='powermon_scm')
rtlamr_path = os.environ['RTLAMR_PATH']
sender_name = os.environ['POWERMON_SENDER']
proc = proc = subprocess.Popen([rtlamr_path, '-format=json'],stdout=subprocess.PIPE)
f = open('scm.backup.json', 'w')
# TODO: If there is any content in the backup file, we should send it to SQS
while True:
  line = proc.stdout.readline()
  if not line:
    break
  data=json.loads(line)
  send_data = {'MeterID': data['Message']['ID'], 'Consumption': data['Message']['Consumption'], 'Time': data['Time'], 'MeterType': data['Message']['Type'], 'Sender': sender_name}
  try:
    queue.send_message(MessageBody=json.dumps(send_data))
  except:
    eprint("Failed to send message to SQS", sys.exc_info()[0])
    f.write(send_data)
  # If connection is down; the script crashes.
  # Write to a local file, and upon restart, send all of those messages first (sqlite?)
