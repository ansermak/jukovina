# -*-coding:utf-8 -*-

from flask.ext.wtf import  Form
from wtforms import StringField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired, NoneOf

class ProductForm(Form):
    name = StringField(u'Назва брошки', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empt', None)])
    description = TextAreaField(u'Опис')
    image = FileField(u'Основне зображення')

class LoginForm(Form):
    openid = StringField('openid', validators = [DataRequired()])
    remember_me = BooleanField('remember_me', default = False)
