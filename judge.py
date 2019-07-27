import base64
import json
import os
import uuid

import _judger
from flask import Blueprint, request

import config
import utils
from db import db

judge = Blueprint('judge', __name__, url_prefix='/judge')


class Submissions(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer)
    uuid = db.Column(db.String(32), default="")
    result = db.Column(db.Text)
    code = db.Column(db.Text)
    lang = db.Column(db.String(32))

    def __init__(self, problem_id: int, lang: str, code: str):
        self.code = code
        self.problem_id = problem_id
        self.lang = lang
        self.uuid = uuid.uuid4().hex
        work_dir = os.path.join(config.JUDGE_BASEDIR, self.uuid)
        os.mkdir(work_dir)
        self.compile(work_dir)
        result = self.judge(work_dir)
        self.result = json.dumps(result)

    def compile(self, workdir):
        return {}

    def judge(self, workdir):
        return {'test': True}

    @staticmethod
    def compare_output(got_output, output):
        output = output.strip(' \n')
        got_output = got_output.strip(' \n')
        result = None
        if output != got_output:
            if output.replace('\n', '').replace(' ', '') \
                    == got_output.replace('\n', '').replace(' ', ''):
                result = -2  # Presentation Error
            else:
                result = _judger.RESULT_WRONG_ANSWER
        return result


@judge.route('/', methods=['POST'])
@utils.api_call
def submit():
    whitelist = ['problem_id', 'code', 'lang']
    r = request.json
    for i in r.keys():
        if i not in whitelist:
            return 403, 'invalid parameters', None
    if type(r['problem_id']) != int:
        return 403, 'invalid parameters', None
    submission = Submissions(
        r['problem_id'],
        r['lang'],
        r['code'],
    )
    db.session.add(submission)
    db.session.commit()
    return 200, 'success', json.loads(submission.result)


RESULT_PRESENTATION_ERROR = -2
RESULT_COMPILE_ERROR = 6
result_msg = {
    _judger.RESULT_SUCCESS: 'Accepted',
    _judger.RESULT_RUNTIME_ERROR: 'Runtime Error',
    _judger.RESULT_WRONG_ANSWER: 'Wrong Answer',
    _judger.RESULT_CPU_TIME_LIMIT_EXCEEDED: 'Time Limit Exceeded',
    _judger.RESULT_REAL_TIME_LIMIT_EXCEEDED: 'Time Limit Exceeded',
    _judger.RESULT_SYSTEM_ERROR: 'System Error',
    _judger.RESULT_MEMORY_LIMIT_EXCEEDED: 'Memory Limit Exceeded',
    RESULT_PRESENTATION_ERROR: 'Presentation Error',
    RESULT_COMPILE_ERROR: 'Compile Error'
}
