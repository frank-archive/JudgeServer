import os

JUDGE_BASEDIR = os.getenv('JUDGE_BASEDIR') or '/Users/frankli/Projects/AlterProjects/judge'
JUDGE_RUNDIR = JUDGE_BASEDIR + '/run'
JUDGE_DATADIR = os.getenv('JUDGE_DATADIR')
JUDGE_LOG = JUDGE_BASEDIR + '/judge.log'
token = os.getenv('JUDGE_TOKEN') or 'set_token'
DATABASE_URL = os.getenv('DATABASE_URL') or 'mysql+pymysql://username:password@localhost/judge?charset=utf8mb4'
