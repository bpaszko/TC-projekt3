import pytest
import json


def test_get_history_event1():
    event = {
        'body': json.dumps(
            {
                'linksPerPage': 5,
                'pageNumber' : 1
            }
        )
    }
    body = event['body']
    body = json.loads(body)
    img_per_site, page_num = int(body['linksPerPage']), int(body['pageNumber'])
    assert img_per_site > 0 and page_num > 0
    offset = (page_num - 1) * img_per_site
    q = f'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT {img_per_site} OFFSET {offset}'
    assert q == 'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT 5 OFFSET 0'

def test_get_history_event2():
    event = {
        'body': json.dumps(
            {
                'linksPerPage': 5,
                'pageNumber' : 3
            }
        )
    }
    body = event['body']
    body = json.loads(body)
    img_per_site, page_num = int(body['linksPerPage']), int(body['pageNumber'])
    assert img_per_site > 0 and page_num > 0
    offset = (page_num - 1) * img_per_site
    q = f'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT {img_per_site} OFFSET {offset}'
    assert q == 'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT 5 OFFSET 10'

def test_get_history_event3():
    event = {
        'body': json.dumps(
            {
                'linksPerPage': 10,
                'pageNumber' : 1
            }
        )
    }
    body = event['body']
    body = json.loads(body)
    img_per_site, page_num = int(body['linksPerPage']), int(body['pageNumber'])
    assert img_per_site > 0 and page_num > 0
    offset = (page_num - 1) * img_per_site
    q = f'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT {img_per_site} OFFSET {offset}'
    assert q == 'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT 10 OFFSET 0'

def test_get_history_event4():
    event = {
        'body': json.dumps(
            {
                'linksPerPage': -5,
                'pageNumber' : 1
            }
        )
    }
    with pytest.raises(AssertionError):
        body = event['body']
        body = json.loads(body)
        img_per_site, page_num = int(body['linksPerPage']), int(body['pageNumber'])
        assert img_per_site > 0 and page_num > 0
        offset = (page_num - 1) * img_per_site
        q = f'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT {img_per_site} OFFSET {offset}'
        assert q == 'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT 10 OFFSET 0'

def test_get_history_event5():
    event = {
        'body': json.dumps(
            {
                'linksPerPage': 5,
                'pageNumber' : -5
            }
        )
    }
    with pytest.raises(AssertionError):
        body = event['body']
        body = json.loads(body)
        img_per_site, page_num = int(body['linksPerPage']), int(body['pageNumber'])
        assert img_per_site > 0 and page_num > 0
        offset = (page_num - 1) * img_per_site
        q = f'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT {img_per_site} OFFSET {offset}'
        assert q == 'SELECT dat, enlarged FROM image_history ORDER BY dat DESC LIMIT 10 OFFSET 0'