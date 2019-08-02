import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask

import config, utils
from judge import judge
from problem import problem

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.register_blueprint(problem)
app.register_blueprint(judge)
with app.app_context():
    from db import db

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
            from db import db, create_database
            db.drop_all()
            app.config['SQLALCHEMY_DATABASE_URI'] = str(create_database())
            db.create_all()
    except Exception as e:
        return 500, 'Initialization Error', str(e)
    return 200, 'success', None


if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
