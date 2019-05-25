import os
import sys
import json
import math
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
    body = event['body'].decode('utf-8')
    body = json.loads(body)
    img_per_site, page_num = int(body['linksPerPage']), int(body['pageNumber'])
    offset = (page_num - 1) * img_per_site
    with conn.cursor() as cur:
        cur.execute(f'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT {img_per_site} OFFSET {offset}')
        history = [[row[0].strftime('%Y-%m-%d %H:%M:%S'), row[1]] for row in cur]
        cur.execute('SELECT COUNT(*) FROM image_history')
        total_images = cur.fetchall()[0][0]
    sites_num = math.ceil(total_images / img_per_site)
    return history, sites_num


def lambda_handler(event, context):
    history, n_sites = get_history(event)

    return {
        'statusCode': '200',
        'body': json.dumps({
            'history': history,
            'sites': n_sites
            }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }
