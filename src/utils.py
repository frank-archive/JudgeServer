import functools
import json
import os
import re
import traceback

import requests
from flask import request

import config

ses = requests.session()
nonce_matcher = re.compile(r'<input type="hidden" name="nonce" value="(.*)">')


def startup():
    def trymkdir(d):
        try:
            os.mkdir(d)
        except FileExistsError:
            pass

    trymkdir(config.JUDGE_BASEDIR)
    trymkdir(config.JUDGE_DATADIR)
    trymkdir(config.JUDGE_RUNDIR)

    @ensure_logged_in
    def conn_test():
        assert (ses.get(f'http://{config.HOST_ADDR}:{config.HOST_PORT}/').status_code == 200)
        assert (ses.get(f'http://{config.HOST_ADDR}:{config.HOST_PORT}/admin/statistics',
                        allow_redirects=False).status_code == 200)

    conn_test()


def api_call(func):
    @functools.wraps(func)
    def _api_response(*args, **kwargs):
        result = {}
        try:
            if 'X-Judge-Server-Token' not in request.headers.keys() or \
                    request.headers['X-Judge-Server-Token'] != config.token:
                result = {
                    'status': 403,
                    'message': 'Unauthorized',
                    'content': None
                }
            result['status'], result['message'], result['content'] = func(
                *args, **kwargs)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            result = {
                'status': 500,
                'message': 'Uncaught Error',
                'content': str(type(e)) + str(e)
            }
        finally:
            return json.dumps(result), result['status'], {'Content-Type': 'application/json;'}

    return _api_response


def ensure_logged_in(func):  # to CTFd
    @functools.wraps(func)
    def _ensure_logged_in(*args, **kwargs):
        if ses.get(f'http://{config.HOST_ADDR}:{config.HOST_PORT}/user',
                   allow_redirects=False).status_code == 302:
            text = ses.get(f'http://{config.HOST_ADDR}:{config.HOST_PORT}/login').text
            nonce = nonce_matcher.findall(text)[0]
            ses.post(f'http://{config.HOST_ADDR}:{config.HOST_PORT}/login', data={
                'name': config.HOST_USER,
                'password': config.HOST_PASS,
                'nonce': nonce
            }, headers={'Referer': 'http://localhost:8000/login'})
        func(*args, **kwargs)

    return _ensure_logged_in


@ensure_logged_in
def download_file(route: str, folder, filename):
    if not os.path.isdir(folder):
        raise NotADirectoryError
    path = os.path.join(folder, filename)
    content = ses.get(f'http://{config.HOST_ADDR}:{config.HOST_PORT}/{route.lstrip("/")}', stream=True)
    with open(path, 'wb') as f:
        for chunk in content.iter_content(1024):
            f.write(chunk)
