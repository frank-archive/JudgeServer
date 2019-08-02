import json
import logging
log = logging.getLogger('problem')

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


def check_limits_fmt(l):
    for i in ['max_cpu_time', 'max_memory', 'max_output_size',
              'max_real_time', 'max_stack', 'max_process_number']:
        if i not in l.keys():
            raise Exception()


def check_cases_fmt(c):
    for i in c:
        if type(i['input']) != str or type(i['output']) != str:
            raise Exception()


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
        check_limits_fmt(r['limits'])
        check_cases_fmt(r['cases'])
    except Exception:
        return 403, 'wrong parameters', None

    try:
        prob = Problems(r['limits'], r['cases'])
        log.info(f'adding problem {prob.id} to database...')
        db.session.add(prob)
        db.session.commit()
    except Exception as e:
        log.error('failed adding problem')
        return 501, 'SQL execution error', str(e)

    return 200, 'success', {
        'problem_id': prob.id
    }


@problem.route('/update/<int:prob_id>/<column>', methods=['POST'])
@utils.api_call
def update(prob_id, column):
    if column not in ['cases', 'limits']:
        return 404, 'no such column', None
    r = request.json
    prob = Problems.query.filter_by(id=prob_id).first()
    if not prob:
        return 404, 'no such problem'
    if column == 'cases':
        try:
            check_cases_fmt(r)
        except Exception:
            log.error('wrong updating parameters(limits)')
            return 403, 'wrong parameters', None
        prob.cases = json.dumps(r)
        prob.case_cnt = len(r)
    else:
        try:
            check_limits_fmt(r)
        except Exception:
            log.error('wrong updating parameters(cases)')
            return 403, 'wrong parameters', None
        prob.limits = json.dumps(r)
    db.session.add(prob)
    db.session.commit()
    return 200, 'success', None


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
