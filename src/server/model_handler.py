# import torch
# from torch.autograd import Variable
import numpy as np
import sys
import base64
import json
from flask import Flask, request, Response, make_response, current_app
from flask_cors import CORS, cross_origin
from functools import update_wrapper
from datetime import timedelta
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
# sys.path.append('./pytorch-SRResNet/')



# model = torch.load('./pytorch-SRResNet/model/final.pth')

app = Flask(__name__)
# app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)


def handler(event, context):
    # Odebranie danych
    t = np.random.normal(size=(10, 15))
    s = base64.b64encode(t)
    r = base64.decodebytes(s)
    q = np.frombuffer(r)
    print(q.shape)
    # q = np.frombuffer(r, dtype=np.float64)

    # im_input = im_l.astype(np.float32).transpose(2,0,1)
    # im_input = np.expand_dims(im_input, axis=0)
    # im_input = torch.Tensor(torch.from_numpy(im_input).float())
    
    # out = model(im_input)
    # im_h = out.data[0].numpy().astype(np.float32)
    # im_h = im_h*255.
    # im_h[im_h<0] = 0
    # im_h[im_h>255.] = 255.            
    # im_h = im_h.transpose(1,2,0).astype(np.uint8)

    # return records

@app.after_request
def allow_cross_domain(response: Response):
    """Hook to set up response headers."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'



def load_image(r):
    jsn = r.data.decode('utf-8')
    data = json.loads(jsn)
    w, h, data_url = int(data['width']), int(data['height']), data['image']
    offset = data_url.index(',')+1
    img_bytes = base64.b64decode(data_url[offset:])
    img = Image.open(BytesIO(img_bytes))
    img = np.array(img)
    return img


@app.route('/test',  methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type'])
# @crossdomain(origin='*')
def hello_world():
    img = load_image(request)
    
    return 'OK'



app.run(host="localhost", port=5000, debug=True)