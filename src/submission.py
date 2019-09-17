
from flask import Blueprint
import utils
import judge

submission = Blueprint('submission', __name__, url_prefix='/submission')

@submission.route('')
@utils.api_call
def list_submissions():
    submissions = judge.Submissions.query.order_by(
        judge.Submissions.problem_id.asc()
    ).all()
    return 200, 'OK', [i.uuid for i in submissions]

@submission.route('<uuid>')
@utils.api_call
def submission_detail(uuid):
    submission = judge.Submissions.query.filter_by(uuid=uuid).first()
    if submission is None:
        return 404, '', {}
    return 200, 'OK', {
        'problem_id': submission.problem_id,
        'lang': submission.lang,
        'code': submission.code,
        'result': submission.result,
    }