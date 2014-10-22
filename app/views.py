# -*-coding:utf-8-*-
import os

from datetime import datetime
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from translit import transliterate

from app import app, db, lm, oid
from forms import LoginForm, JewelForm
from models import User, ROLE_USER, ROLE_ADMIN, Jewel

from basic_functions import get_small_image_name, image_dir,\
    image_resize, image_uniq_name, save_image

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def berfore_request():
    g.user = current_user

@app.route('/new_jewel/', methods=['GET', 'POST'])
@login_required
def new_jewel():
    if not g.user.is_admin():
        return render_template('parking_page.html',
                msg=u'Нажаль, у вас немає на це дозвілу')
    jewel_form = JewelForm()
    if jewel_form.validate_on_submit():
        _jewel = Jewel(name=jewel_form.name.data,
                name_en=jewel_uniq_name(jewel_form.name.data),
                description=jewel_form.description.data,
                added_by=0,
                added_on=datetime.utcnow())
        file_image = request.files.get('image', None)
        if file_image:
            _jewel.image = save_image(file_image)
        db.session.add(_jewel)
        db.session.commit()
        return redirect('/{}'.format(_jewel.name_en))
    return render_template('jewel_edit.html',
            jewel=jewel_form)
    

@app.route('/edit/<jewel_en_name>/', methods=['GET', 'POST'])
@app.route('/<jewel_en_name>/', methods=['GET', 'POST'])
@login_required
def jewel(jewel_en_name):
    #getting data by jewel name from url
    jewels = Jewel.query.filter(Jewel.name_en==jewel_en_name)
    jewel_c = jewels.count()
    
    if jewel_c == 0:
        return render_template('parking_page.html', 
                msg=u'Немає такої прикраси =(')
    elif jewel_c > 1:
        pass
        ## log error - we have more than one jewel eith the same name_en

    jewel_obj = jewels[0]
    edit_url = request.url_rule.rule.split('/')[1]
    
    if edit_url == 'edit':
        
        if g.user.is_admin():
            jewel_form = JewelForm()
            
            if jewel_form.validate_on_submit():
                modified = False
               
                if jewel_obj.name != jewel_form.name.data:
                    jewel_obj.name=jewel_form.name.data
                    modified = True
                    jewel_obj.name_en=jewel_uniq_name(jewel_form.name.data)
               
                if jewel_obj.description != jewel_form.description.data:
                    jewel_obj.description = jewel_form.description.data
                    modified = True
               
                if jewel_obj.image != jewel_form.image.data:
                    if jewel_obj.image is not None and os.path.isfile(
                        os.path.join(image_dir,jewel_obj.image)):
                            os.remove(os.path.join(image_dir, jewel_obj.image))
                            os.remove(os.path.join(image_dir, 
                                get_small_image_name(jewel_obj.image)))

                    modified = True
                    
                    file_image = request.files['image']

                    if file_image:
                        jewel_obj.image = save_image(file_image)

                if modified: 
                    db.session.commit()

                return redirect('/{}'.format(jewel_obj.name_en))

            page = 'jewel_edit.html'
            jewel_form = JewelForm(obj=jewel_obj)
            jewel_obj = jewel_form

        else:
            return redirect('/{}'.format(jewel_en_name))
    else:
        page = 'jewel.html'

    return render_template(page,
            jewel = jewel_obj,
            link_edit="/edit/{}".format(jewel_en_name))


@app.route('/')
@app.route('/index/')
@login_required
def index():
    user = g.user
    jewel_list = Jewel.query.all()
    return render_template('index.html',
        title ='Home',
        user = user,
        jewel_list=jewel_list)


@app.route('/login/', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = [
            'nickname',
            'email'])

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

        # if this is first user in the base (user table is empy)
        # we give him admin status
        status = ROLE_ADMIN if User.query.count() == 0 else ROLSE_USER
        user = User(login = login, email = resp.email, role = status)
        
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


# Functions

def jewel_uniq_name(name):
    """Creates uniq name_en for handicraft:
    transliterates name and if such name_en exists in database
    adds underline and first free number
    """
    name_en = transliterate(name)
    cnt = Jewel.query.filter(Jewel.name_en==name_en).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = Jewel.query.filter(Jewel.name_en=='{}_{}'.format(
                name_en, i)).count()
        rzlt = '{}_{}'.format(name_en, i)
    else:
        rzlt = name_en
    return rzlt 