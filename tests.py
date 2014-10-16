#!../flask/bin/python

import os
from unittest import TestLoader, TestResult, TextTestRunner

from config import basedir
from app import app, db

BASE_DIR = 'app/tests'

if __name__ == '__main__':

    app.config['TESTING'] = True
    app.config['CSRF'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
    db.create_all()

    loader = TestLoader()
    rzlt = TestResult()
    found_tests = loader.discover(BASE_DIR, pattern='test_*.py')
    TextTestRunner(verbosity=2).run(found_tests)
    db.session.remove()
    db.drop_all()
    os.remove(os.path.join(basedir, 'test.db'))

