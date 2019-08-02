import json
import os
import uuid
import logging
log = logging.getLogger('judge')

from flask import Blueprint, request

import config, utils
from constants import *
from db import db
from worker import Worker, CompileErrorException

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
        log.info('Judging Submission '+self.uuid)
        work_dir = os.path.join(config.JUDGE_BASEDIR, self.uuid)
        os.mkdir(work_dir)

        self.worker = Worker(work_dir, code, lang, problem_id)
        comp = self.compile()
        if not comp['result']:
            log.error('Compile Error for Submission '+self.uuid)
            result = {
                'result': RESULT_COMPILE_ERROR,
                'message': 'Compile Error',
                'details': {
                    'error': comp['message']
                }
            }
        else:
            result = self.judge()
        self.result = json.dumps(result)
        log.info(f'Final Result for Submission {self.uuid}:\n{self.result}')
        self.worker.destroy()

    def compile(self):
        log.info('Compiling: ')
        result = True
        message = ''
        source_path, output_path = '', ''
        try:
            source_path, output_path = self.worker.compile()
        except CompileErrorException as e:
            result = False
            message = e.message
        return {
            'result': result,
            'message': message,
            'source': source_path,
            'output': output_path,
        }

    def judge(self):
        r, c = self.worker.execute()
        return self.build_result(r, c)

    @staticmethod
    def build_result(result, case_cnt):
        if len(result) >= case_cnt:  # bigger than?
            return {
                'result': RESULT_SUCCESS,
                'message': 'Accepted'
            }
        else:
            return {
                'result': result[-1]['result'],
                'message': result_msg[result[-1]['result']] + ' on case ' + str(len(result))
            }


@judge.route('', methods=['POST'])
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
