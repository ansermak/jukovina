# -*-coding:utf-8-*-

from flask import render_template, request, redirect
from app import app, db
from app.models import Item
from forms import ProductForm
from datetime import datetime
from translit import transliterate

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', 
    	title ='Home')


HAS_RIGHTS = True

def item_uniq_name(name):
    """Creates uniq name_en for handicraft:
    transliterates name and if such name_en exists in database
    adds underline and first free number
    """
    name_en = transliterate(name)
    cnt = Item.query.filter(Item.name_en==name_en).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = Item.query.filter(Item.name_en=='{}_{}'.format(name_en, i)).count()
        rzlt = '{}_{}'.format(name_en, i)
    else:
        rzlt = name_en
    return rzlt

@app.route('/new_product', methods=['GET', 'POST'])
def new_product():
    if not HAS_RIGHTS:
        return render_template('parking_page.html',
                msg=u'Нажаль, у вас немає на це дозвілу')
    product = ProductForm()
    if product.validate_on_submit():
        _prod = Item(name=product.name.data,
                name_en=item_uniq_name(product.name.data),
                description=product.description.data,
                added_by=0,
                added_on=datetime.utcnow())
        db.session.add(_prod)
        db.session.commit()
        return redirect('/{}'.format(_prod.name_en))
    return render_template('product_edit.html',
            product=product)
    

@app.route('/edit/<product_en_name>', methods=['GET', 'POST'])
@app.route('/<product_en_name>', methods=['GET', 'POST'])
def product(product_en_name):
    products = Item.query.filter(Item.name_en==product_en_name)
    product_c = products.count()
    if product_c == 0:
        return render_template('parking_page.html', 
                msg=u'Немає такої прикраси =(')
    elif product_c > 1:
        pass
        ## log error - we have more than one item eith the same name_en
    product_obj = products[0]
    print request.url_rule.rule
    edit_url = request.url_rule.rule.split('/')[1]
    if edit_url == 'edit':
        if HAS_RIGHTS:
            product_form = ProductForm()
            if product_form.validate_on_submit():
                print 'validated'
                _prod = Item(name=product_form.name.data,
                        name_en=item_uniq_name(product_form.name.data),
                        description=product_form.description.data,
                        added_by=0,
                        added_on=datetime.utcnow())
                db.session.add(_prod)
                db.session.commit()
                return redirect('/{}'.format(_prod.name_en))
            page = 'product_edit.html'
            product_form = ProductForm(obj=product)
            product_obj = product_form
        else:
            return redirect('/{}'.format(product_en_name))
    else:
        page = 'product.html'

    return render_template(page,
            product = product_obj,
            is_admin = HAS_RIGHTS,
            link_edit="/edit/{}".format(product_en_name))



