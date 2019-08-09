import json
import logging
import os

from flask import Blueprint, request

import config
import utils
from db import db

problem = Blueprint('problem', __name__, url_prefix='/problem')
log = logging.getLogger('problem')


class Problems(db.Model):
    __tablename__ = "problems"
    id = db.Column(db.Integer, primary_key=True)
    limits = db.Column(db.Text)
    case_cnt = db.Column(db.Integer)
    cases = db.Column(db.Text)

    def __init__(self, limits: dict, cases: list):
        self.limits = json.dumps(limits)
        self.case_cnt = 0
        self.cases = "[]"
        self.add_cases(cases)

    def add_cases(self, cases):
        data_dir = config.JUDGE_DATADIR
        cases_temp = []
        for i in range(len(cases)):
            cases_temp.append({
                'input': os.path.join(data_dir, cases[i]['input']),
                'output': os.path.join(data_dir, cases[i]['output'])
            })
        self.cases = json.dumps(json.loads(self.cases) + cases_temp)
        self.case_cnt += len(cases)


def check_limits_fmt(l):
    for i in ['max_cpu_time', 'max_memory', 'max_output_size',
              'max_real_time', 'max_stack', 'max_process_number']:
        if i not in l.keys():
            raise ValueError()


def check_cases_fmt(c):
    for i in c:
        if type(i['input']) != str or type(i['output']) != str:
            raise ValueError()


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
        db.session.add(prob)
        db.session.commit()
        log.info(f'added problem {prob.id} to database...')
    except Exception as e:
        log.error('failed adding problem')
        return 501, 'SQL execution error', str(e)

    return 200, 'success', {
        'problem_id': prob.id,
        'problem_cases': prob.case_cnt,
    }


@problem.route('/update/<column>/<int:prob_id>', methods=['POST'])
@utils.api_call
def update(column, prob_id: int):
    prob = Problems.query.filter_by(id=prob_id).first()
    if not prob:
        return 404, 'no such problem', None
    try:
        r = request.json
        if column == 'limits':
            check_limits_fmt(r)
            update_limits(r, prob)
        elif column == 'cases':
            check_cases_fmt(r)
            update_cases(r, prob)
        else:
            raise ValueError()
    except ValueError:
        log.error(f'wrong updating parameters({column})')
        log.error(request.data)
        return 403, 'wrong parameters', None
    except Exception as e:
        log.error(f'Unknown error when updating {column}')
        log.error(str(e) + str(type(e)))
        return 500, 'Internal Error', None
    return 200, 'success', None


def update_limits(r, prob):
    prob.limits = json.dumps(r)
    db.session.add(prob)
    db.session.commit()


def update_cases(r, prob):
    prob.add_cases(r)
    db.session.add(prob)
    db.session.commit()


@problem.route('/info/<int:prob_id>')
@utils.api_call
def problem_info(prob_id: int):
    prob = Problems.query.filter_by(id=prob_id).first()
    data = {
        'id': prob_id,
        'exists': prob is not None,
    }
    if data['exists']:
        data.update({'case_cnt': prob.case_cnt})
    return 200, 'success', data
