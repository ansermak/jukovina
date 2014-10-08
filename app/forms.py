# -*-coding:utf-8 -*-

from flask.ext.wtf import  Form
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import Required

class ProductForm(Form):
    name = StringField(u'Назва брошки', validators=[Required()])
    description = TextAreaField(u'Опис')

class LoginForm(Form):
    openid = StringField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
