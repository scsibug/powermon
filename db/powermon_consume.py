import boto3
import sys
import os
import json
import subprocess
import time
import psycopg2
import dateutil.parser
from settings import *

# Initialize Database
conn = psycopg2.connect(pg_conn_str)
curs = conn.cursor() 

# Initialize AWS Queue
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='powermon_scm')

# SQL Queries
find_reader_id_SQL = "select name,id from readers"
find_meter_SQL = "select id, name, type from meters where name = %(name)s and type = %(type)s"
insert_reading_SQL = "insert into meter_readings (id, reading, tstamp, meter, reader) values (DEFAULT, %(reading)s, %(tstamp)s, %(meter_id)s, (SELECT id from readers WHERE name = %(reader_name)s))"
insert_meter_SQL = "insert into meters (id, name, type) values (DEFAULT, %(name)s, %(type)s) RETURNING id"

while True:
  for message in queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=30):
    msg = json.loads(message.body)
    print msg
    meter_name = str(msg["MeterID"])
    meter_type = msg["MeterType"]
    tstamp = dateutil.parser.parse(msg["Time"])
    # Find meter
    curs.execute(find_meter_SQL,{'name':meter_name, 'type':meter_type})
    # Results are either 1, or none
    found_meter = curs.fetchone()
    meter_id = None
    if (found_meter is None):
        # Do insert, save row id
        curs.execute(insert_meter_SQL, {'name':meter_name, 'type':meter_type,})
        meter_id = curs.fetchone()[0]
    else:
        meter_id = found_meter[0]
    curs.execute(insert_reading_SQL, {'reading':msg["Consumption"], 'tstamp':tstamp, 'meter_id':meter_id, 'reader_name':msg["Sender"]})
    conn.commit()
    # If message successfully processed, delete
    message.delete()
    
