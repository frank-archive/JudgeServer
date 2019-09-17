import logging

from flask import Flask

import config
import utils
from db import db, create_database
from judge import judge
from problem import problem
from submission import submission

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.register_blueprint(problem)
app.register_blueprint(judge)
app.register_blueprint(submission)
logging.basicConfig(level=logging.INFO)
with app.app_context():
    db.init_app(app)


@app.route('/ping')
@utils.api_call
def ping():
    return 200, 'pong', None


@app.route('/init')
@utils.api_call
def init():
    try:
        with app.app_context():
            db.drop_all()
            app.config['SQLALCHEMY_DATABASE_URI'] = str(create_database())
            db.create_all()
    except Exception as e:
        return 500, 'Initialization Error', str(e)
    return 200, 'success', None


if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
