import os
import sys
import json
import uuid
import boto3
import ctypes
import base64
import pymysql
import logging
import datetime

from io import BytesIO

for d, dirs, files in os.walk(os.path.join(os.getcwd(), 'local', 'lib')):
    for f in files:
        if f.endswith('.a'):
            continue
        ctypes.cdll.LoadLibrary(os.path.join(d, f))

import numpy as np
from PIL import Image
import onnx
import onnx_caffe2.backend as backend


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# INIT S3 CONNECTION AND MODEL
bucket_name = os.environ['BUCKET']
s3_model_path = os.environ['MODEL_PATH']
local_model_path = '/tmp/model.proto'

s3 = boto3.client('s3')

if os.path.isfile(local_model_path) != True:
    s3.download_file(bucket_name, s3_model_path, local_model_path)

graph = onnx.load(local_model_path)
model = backend.prepare(graph, device="CPU")
logger.info("SUCCESS: Model loaded properly.")

# INIT RDS CONNECTION 
name = os.environ['RDS_USER']
password = os.environ['RDS_PASSWORD']
rds_host  = os.environ['RDS_HOST']
db_name = os.environ['RDS_NAME']

try:
    rds_conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


def load_image(event):
    body = event['body'].decode('utf-8')
    body = json.loads(body)
    data_url = body['image']
    zoom = int(body['zoom'])
    assert zoom in [2, 3, 4]
    offset = int(data_url.index(','))+1
    img_bytes = base64.b64decode(data_url[offset:])
    img = Image.open(BytesIO(img_bytes))
    img = np.array(img).astype(np.uint8)
    return img, zoom


def save_image(img, prefix):
    name = uuid.uuid4().hex
    img = Image.fromarray(img)
    out_img = BytesIO()
    img.save(out_img, format='png')
    out_img.seek(0) 
    s3_img_path = '{}/{}.jpg'.format(prefix, name)
    response = s3.upload_fileobj(out_img, bucket_name, s3_img_path)
    s3_url = 'http://{}.s3.amazonaws.com/{}'.format(bucket_name, s3_img_path)
    return s3_url


def rescale(img, zoom):
    if zoom == 4:
        return img
    h, w, _ = img.shape
    new_h, new_w = int(h * zoom/4.0), int(w * zoom/4.0)
    img = Image.fromarray(img)
    img = img.resize(size=(new_w, new_h), resample=Image.BICUBIC)
    return np.array(img)


def run(img, zoom):
    model_input = img.astype(np.float32).transpose(2,0,1) / 255.
    model_input = np.expand_dims(model_input, axis=0)
    output = model.run(model_input)
    img_hr = output[0][0]
    img_hr = img_hr.transpose(1,2,0)
    img_hr = img_hr * 255
    img_hr[img_hr<0] = 0
    img_hr[img_hr>255.] = 255.
    img_hr = img_hr.astype(np.uint8)
    img_hr = rescale(img_hr, zoom)
    return img_hr


def write_to_rds(original_url, enlarged_url):
    date = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    create_sql = 'CREATE TABLE IF NOT EXISTS image_history ( \
                    dat DATETIME NOT NULL, \
                    original VARCHAR(255) NOT NULL, \
                    enlarged VARCHAR(255) NOT NULL \
                  )'
    insert_sql = 'INSERT INTO image_history (dat, original, enlarged) VALUES ("{}", "{}", "{}")'.format(date, original_url, enlarged_url)
    with rds_conn.cursor() as cur:
        cur.execute(create_sql)  
        rds_conn.commit()
        cur.execute(insert_sql)
    rds_conn.commit()


def lambda_handler(event, context):
    img_lr, zoom = load_image(event)
    img_hr = run(img_lr, zoom)
    url_lr = save_image(img_lr, 'original')
    url_hr = save_image(img_hr, 'enlarged')
    write_to_rds(url_lr, url_hr)

    return {
        'statusCode': '200',
        'body': json.dumps({'img_url': url_hr}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }