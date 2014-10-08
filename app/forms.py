# -*-coding:utf-8 -*-

from flask.ext.wtf import  Form
from wtforms import StringField, TextAreaField
from wtforms.validators import Required

class ProductForm(Form):
    name = StringField(u'Назва брошки', validators=[Required()])
    description = TextAreaField(u'Опис')
