import os

JUDGE_BASEDIR = os.getenv('JUDGE_BASEDIR')\
    or '/Users/frankli/Projects/AlterProjects/judge'
JUDGE_DATADIR = '/opt/data'
JUDGE_LOG = JUDGE_BASEDIR + '/judge.log'
token = os.getenv('JUDGE_TOKEN')\
    or 'set_token'
DATABASE_URL = os.getenv('DATABASE_URL')\
    or 'mysql+pymysql://username:password@localhost/judge?charset=utf8mb4'

try:
    os.mkdir(JUDGE_BASEDIR)
except FileExistsError:
    pass
