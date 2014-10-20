#!../flask/bin/python
#-*-coding:utf-8-*-
import os
import unittest

from config import basedir 
from app import app, db
from app.models import Jewel,User, ROLE_ADMIN, ROLE_USER
from app.tests.base import prepare_enviroment, clean_enviroment, TestBaseCase, captured_templates

class TestJewelCase(TestBaseCase):

    def test_new_jewel(self):
        
        # user - has no rights
        self.login_user()
        with captured_templates(app) as templates:
            rzlt = self.app.get('/new_jewel/')
            self.assertEqual(rzlt.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'parking_page.html')
            self.assertEqual(context['msg'], u'Нажаль, у вас немає на це дозвілу')

        # admin user - clean form
        self.login_admin()
        with captured_templates(app) as templates:
            rzlt = self.app.get('/new_jewel/')
            self.assertEqual(rzlt.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'jewel_edit.html')

        #saving with empty name - should return form
        with captured_templates(app) as templates:
            rzlt = self.app.post('/new_jewel/',data=dict(
                    name = '',
                    description=u'новий ювелірний вироб'
                ))
            self.assertEqual(rzlt.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'jewel_edit.html')
            self.assertGreater(len(context['jewel'].errors['name']), 0)
            self.assertEqual(context['jewel'].description.data, u'новий ювелірний вироб')

        #saving without image
        with captured_templates(app) as templates:
            rzlt = self.app.post('/new_jewel/',data=dict(
                    name=u'каблучка',
                    description=u'новий ювелірний вироб'
                ), follow_redirects=True)
            self.assertEqual(rzlt.status_code, 200)
            template, context = templates[0]
            self.assertEqual(len(templates), 1)
            new_jewel = Jewel.query.filter(Jewel.name==u'каблучка')[-1]
            self.assertEqual(new_jewel.name, u'каблучка')
            self.assertEqual(new_jewel.name_en, u'kabluchka')
            self.assertEqual(template.name, 'jewel.html')

        #print rzlt.data
        #print rzlt.status_code
        #print rzlt.status
        #print rzlt.headers
        #print rzlt. mimetype


if __name__ == '__main__':
    prepare_enviroment()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestJewelCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    clean_enviroment()

