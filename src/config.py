import os

JUDGE_BASEDIR = os.getenv('JUDGE_BASEDIR') or '/Users/frankli/Projects/AlterProjects/judge'
JUDGE_RUNDIR = JUDGE_BASEDIR + '/run'
JUDGE_DATADIR = JUDGE_BASEDIR + '/data'
JUDGE_LOG = JUDGE_BASEDIR + '/judge.log'
token = os.getenv('JUDGE_TOKEN') or 'set_token'
DATABASE_URL = os.getenv('DATABASE_URL') or 'mysql+pymysql://username:password@localhost/judge?charset=utf8mb4'

HOST_ADDR = os.getenv('HOST_ADDR')
HOST_PORT = os.getenv('HOST_PORT')
HOST_USER = os.getenv('HOST_USER')
HOST_PASS = os.getenv('HOST_PASS')
