#!../flask/bin/python
#-*-coding:utf-8-*-

import os
import unittest

from config import basedir 
from app import app, db
from app.models import User, ROLE_ADMIN, ROLE_USER

from flask import template_rendered
from contextlib import contextmanager

@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestBaseCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.user = User.query.filter(User.role == ROLE_USER).first()
        self.admin = User.query.filter(User.role == ROLE_ADMIN).first()
    
    def login_user(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True 

    def login_admin(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.admin.id
            sess['_fresh'] = True 

    def tearDown(self):
        pass


    def test_login(self):
        
        # redirecting to login page

        rzlt = self.app.get('/')
        self.assertIn('<a href="/login?next=', rzlt.data)
        self.assertEqual(302, rzlt.status_code)
        
        # login user
        
        self.login_user()
        #checking redirect to hello_page

        rzlt = self.app.get('/', follow_redirects=True)
        self.assertIn('Привет, {}'.format(self.user.login), rzlt.data)
        self.assertEqual(200, rzlt.status_code)

        #print rzlt.data
        #print rzlt.status_code
        #print rzlt.status
        #print rzlt.headers
        #print rzlt. mimetype

def prepare_enviroment():
    app.config['TESTING'] = True
    app.config['CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
    db.create_all()
    db.session.add(User(login='simple user',email='simpple@mail.com', role=ROLE_USER))
    db.session.add(User(login='admin user', role=ROLE_ADMIN))
    db.session.commit()


def clean_enviroment():
    db.session.remove()
    db.drop_all()
    os.remove(os.path.join(basedir, 'test.db'))


if __name__ == '__main__':
    prepare_enviroment()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBaseCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    clean_enviroment()

