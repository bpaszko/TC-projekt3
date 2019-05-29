import base64
import uuid
import datetime
import numpy as np
import json
import os
from io import BytesIO
from PIL import Image
import pytest



### helper code
def make_data_url():
    fn = 'tmp_img.png'
    img = Image.fromarray(image)
    img.save(fn)
    prefix = 'data:image/png;base64,'
    with open(fn, 'rb') as fin:
        contents = fin.read()
        data_url = prefix + base64.b64encode(contents)
    os.remove(fn)
    return data_url


class S3Mock:
    def upload_fileobj(self, a, b, c):
        return 'MOCK'


image = np.random.randint(low=0, high=256, size=(75, 75, 3), dtype=np.uint8) 
bucket_name = 'TEST_BUCKET'
s3 = S3Mock()

### tests
def test_load_image():
    daturi = make_data_url()
    event = {'body': '{{\"image\": \"{}\", \"zoom\": 2}}'.format(daturi).encode('utf-8')}
    img, zoom = load_image(event)
    assert np.array_equal(img, image)
    assert zoom == 2


def test_negative_zoom():
    daturi = make_data_url()
    event = {'body': '{{\"image\": \"{}\", \"zoom\": -1}}'.format(daturi).encode('utf-8')}
    with pytest.raises(AssertionError):
        load_image(event)


def test_too_large_zoom():
    daturi = make_data_url()
    event = {'body': '{{\"image\": \"{}\", \"zoom\": 5}}'.format(daturi).encode('utf-8')}
    with pytest.raises(AssertionError):
        load_image(event)


def test_rescale4():
    img = rescale(image, 4)
    h, w, d = image.shape[0], image.shape[1], image.shape[2]
    assert img.shape == (h, w, d)


def test_rescale3():
    img = rescale(image, 3)
    h, w, d = int(image.shape[0]*3/4.0), int(image.shape[1]*3/4.0), image.shape[2]
    assert img.shape == (h, w, d)


def test_save():
    url = save_image(image, 'enlarged')
    assert url.endswith('.jpg')
    assert url.startswith('http://TEST_BUCKET.s3.amazonaws.com/enlarged/')


### Original code
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
