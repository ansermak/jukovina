#!../flask/bin/python

import os
from unittest import TestLoader, TestResult, TextTestRunner
from config import basedir
from app import app, db
from app.tests.base import prepare_enviroment, clean_enviroment, TestBaseCase, captured_templates

BASE_DIR = 'app/tests'

if __name__ == '__main__':
    prepare_enviroment()
    suite =TestLoader().discover(BASE_DIR, pattern='test_*.py')
    TextTestRunner(verbosity=2).run(suite)
    clean_enviroment()


