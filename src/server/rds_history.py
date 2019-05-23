import json
import sys
import os
import logging
import datetime
import pymysql


rds_host  = os.environ['RDS_HOST']
name = os.environ['RDS_USER']
password = os.environ['RDS_PASSWORD']
db_name = os.environ['RDS_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


def get_history(event):
    num, offset = 5, 0
    with conn.cursor() as cur:
        cur.execute(f'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT {num} OFFSET {offset}')
        history = [[row[0].strftime('%Y-%m-%d %H:%M:%S'), row[1]] for row in cur]
    conn.commit()
    return history


def lambda_handler(event, context):
    history = get_history(event)

    return {
        'statusCode': '200',
        'body': json.dumps({'history': history}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }
