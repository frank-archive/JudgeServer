import functools
import json
import os
import traceback

from flask import request

import config


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
