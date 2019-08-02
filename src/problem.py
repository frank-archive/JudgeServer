import json

from flask import Blueprint, request

import utils
from db import db

problem = Blueprint('problem', __name__, url_prefix='/problem')


class Problems(db.Model):
    __tablename__ = "problems"
    id = db.Column(db.Integer, primary_key=True)
    limits = db.Column(db.Text)
    case_cnt = db.Column(db.Integer)
    cases = db.Column(db.Text(16777216))

    def __init__(self, limits: dict, cases: list):
        self.limits = json.dumps(limits)
        self.case_cnt = len(cases)
        self.cases = json.dumps(cases)


@problem.route('/add', methods=['POST'])
@utils.api_call
def add_problem():
    try:
        r = request.json
        for i in ['cases', 'limits']:
            if i not in r.keys():
                raise Exception()
        if type(r['cases']) != list:
            raise Exception()
        for i in ['max_cpu_time', 'max_memory', 'max_output_size',
                  'max_real_time', 'max_stack', 'max_process_number']:
            if i not in r['limits'].keys():
                raise Exception()
        for i in r['cases']:
            if type(i['input']) != str or type(i['output']) != str:
                raise Exception()
    except Exception:
        return 403, 'wrong parameters', None

    try:
        prob = Problems(r['limits'], r['cases'])
        db.session.add(prob)
        db.session.commit()
    except Exception as e:
        return 501, 'SQL execution error', str(e)

    return 200, 'success', {
        'problem_id': prob.id
    }


@problem.route('/info/<int:prob_id>')
@utils.api_call
def problem_info(prob_id: int):
    prob = Problems.query.filter_by(id=prob_id).first()
    data = {
        'id': prob_id,
        'exists': prob is not None
    }
    if data['exists']:
        data.update({'case_cnt': prob.case_cnt})
    return 200, 'success', data
