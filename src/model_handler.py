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


def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # use str instead of basestring if using Python 3.x
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    # use str instead of basestring if using Python 3.x
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            print('KURWA')
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


# @app.after_request
# def allow_cross_domain(response: Response):
#     """Hook to set up response headers."""
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Headers'] = 'Content-Type'



def load_image(r):
    jsn = r.data.decode('utf-8')
    data = json.loads(jsn)
    w, h, data_url = int(data['width']), int(data['height']), data['image']
    offset = data_url.index(',')+1
    img_bytes = base64.b64decode(data_url[offset:])
    img = Image.open(BytesIO(img_bytes))
    img = np.array(img)
    return img

@app.route('/test',  methods=['POST', 'OPTIONS'])
# @cross_origin(origin='*', headers=['Content-Type'])
@crossdomain(origin='*')
def hello_world():
    img = load_image(request)
    plt.imsave('../TEST.jpg', img)
    return 'OK'



app.run(host="localhost", port=5000, debug=True)