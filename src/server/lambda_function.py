import json
import boto3
import ctypes
import os
import base64
from io import BytesIO

for d, dirs, files in os.walk(os.path.join(os.getcwd(), 'local', 'lib')):
    for f in files:
        if f.endswith('.a'):
            continue
        ctypes.cdll.LoadLibrary(os.path.join(d, f))

import numpy as np
import json
from PIL import Image
import onnx
import onnx_caffe2.backend as backend

bucket_name = 'mini-tc-2019'
s3_model_path = 'static/model.proto'
local_model_path = '/tmp/model.proto'


s3 = boto3.client('s3')

if os.path.isfile(local_model_path) != True:
    s3.download_file(bucket_name, s3_model_path, local_model_path)

graph = onnx.load(local_model_path)
model = backend.prepare(graph, device="CPU")


def load_image(event):
    body = event['body'].decode('utf-8')
    body = json.loads(body)
    data_url = body['image']
    offset = int(data_url.index(','))+1
    img_bytes = base64.b64decode(data_url[offset:])
    img = Image.open(BytesIO(img_bytes))
    img = np.array(img).astype(np.uint8)
    return img


def save_image1(img):
    img = Image.fromarray(img)
    out_img = BytesIO()
    img.save(out_img, format='png')
    out_img.seek(0) 
    # try:
    response = s3.upload_fileobj(out_img, bucket_name, 'original/12.jpg')
    # except ClientError as e:
    #     logging.error(e)
    #     return False
    return True


def save_image2(img):
    img = Image.fromarray(img)
    out_img = BytesIO()
    img.save(out_img, format='png')
    out_img.seek(0) 
    # try:
    response = s3.upload_fileobj(out_img, bucket_name, 'enlarged/12.jpg')
    # except ClientError as e:
    #     logging.error(e)
    #     return False
    return True


def run(img):
    model_input = img.astype(np.float32).transpose(2,0,1) / 255.
    model_input = np.expand_dims(model_input, axis=0)
    output = model.run(model_input)
    img_hr = output[0][0]
    img_hr = img_hr.transpose(1,2,0)
    img_hr = img_hr * 255
    img_hr[img_hr<0] = 0
    img_hr[img_hr>255.] = 255.            
    return img_hr.astype(np.uint8)


def lambda_handler(event, context):
    img_lr = load_image(event)
    img_hr = run(img_lr)
    save_image1(img_lr)
    save_image2(img_hr)
    
    return {
        'statusCode': '200',
        'body': json.dumps('hello'),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }