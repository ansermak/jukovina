# -*-coding:utf-8-*-

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, ProductForm
from models import User, ROLE_USER, ROLE_ADMIN, Item
from datetime import datetime
from translit import transliterate
from werkzeug import secure_filename
import os

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def berfore_request():
    g.user = current_user

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
@login_required
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
        file_image = request.files['image']
        if file_image:
            file_name = secure_filename(file_image.filename)
            file_image.save(os.path.join(app.root_path, app.config['ITEM_IMAGE_FOLDER'], file_name))
            _prod.image = file_name
        db.session.add(_prod)
        db.session.commit()
        return redirect('/{}'.format(_prod.name_en))
    return render_template('product_edit.html',
            product=product)
    

@app.route('/edit/<product_en_name>', methods=['GET', 'POST'])
@app.route('/<product_en_name>', methods=['GET', 'POST'])
@login_required
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
    edit_url = request.url_rule.rule.split('/')[1]
    if edit_url == 'edit':
        if HAS_RIGHTS:
            product_form = ProductForm()
            if product_form.validate_on_submit():
                modified = False
                if product_obj.name != product_form.name.data:
                    product_obj.name=product_form.name.data
                    modified = True
                    product_obj.name_en=item_uniq_name(product_form.name.data)
                if product_obj.description != product_form.description.data:
                    product_obj.description = product_form.description.data
                    modified = True
                if product_obj.image != product_form.image.data:
                    if os.path.isfile(product_obj.image):
                        os.remove(os.path.join(
                            app.root_path, 
                            app.config['ITEM_IMAGE_FOLDER'], 
                            product_obj.image))
                    modified = True
                    file_image = request.files['image']
                    if file_image:
                        file_name = secure_filename(file_image.filename)
                        file_image.save(os.path.join(app.root_path, app.config['ITEM_IMAGE_FOLDER'], file_name))
                        product_obj.image = file_name
                #db.session.add(_prod)
                db.session.commit()
                return redirect('/{}'.format(product_obj.name_en))
            page = 'product_edit.html'
            product_form = ProductForm(obj=product_obj)
            product_obj = product_form
        else:
            return redirect('/{}'.format(product_en_name))
    else:
        page = 'product.html'

    return render_template(page,
            product = product_obj,
            is_admin = HAS_RIGHTS,
            link_edit="/edit/{}".format(product_en_name))


@app.route('/')
@app.route('/index')
#@login_required
def index():
    print '=============', app.root_path
    user = g.user
    product_list = Item.query.all()
    return render_template('index.html',
        title ='Home',
        user = user,
        product_list=product_list)


@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html',
        title = 'Sign In',
        form = form, 
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == '':
        flask('Invalid login. Please try again.')
        return redirect(url_for('login'))

    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        login = resp.nickname
        if login is None or login == '':
            login = resp.email.split('@')[0]
        login = User.make_unique_login(login)    
        user = User(login = login, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or ulr_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<login>')
@login_required
def user(login):
    user = User.query.filter_by(login = login).first()
    if user == None:
        flash('User {} not found'.format(login))
        return redirect(url_for('index'))
    items = [
        {'author': user, 'body': 'Super-mega thing'}, 
        {'author': user, 'body': 'Another one'}
    ]
    return render_template('user.html',
        user = user,
        items = items)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
