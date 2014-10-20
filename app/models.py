from hashlib import md5
from app import db, app


ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(20), index = True, unique = True)
    name = db.Column(db.String(120), index = True)
    added_on = db.Column(db.DateTime)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    email = db.Column(db.String(60), unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    jewels = db.relationship('Jewel', backref='author', lazy='dynamic')

    @staticmethod
    def make_unique_login(login):
        if User.query.filter_by(login = login).first() == None:
            return login
        version = 2
        while True:
            new_login = login + str(version)
            if User.query.filter_by(login = new_login) == None:
                break
            version += 1
        return new_login

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/{}?d=mm&s={}'.format(
                md5(self.email).hexdigest(), str(size))

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.login)


class Jewel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), index = True)
    name_en = db.Column(db.String(120), index = True, unique = True, nullable=False)
    added_on = db.Column(db.DateTime)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    prices = db.relationship('Price', backref='prices', lazy='dynamic')
    image = db.Column(db.String(255))

    def __repr__(self):
        return '<Item {}>'.format(self.name)

    def get_main_image_url(self):
        return '/{}/{}'.format(app.config['ITEM_IMAGE_FOLDER'], self.image)

    def get_small_image_url(self):
        return '/{}/{}'.format(app.config['ITEM_IMAGE_FOLDER'], self.image.split('.')[0] + '_180x200.' + self.image.split('.')[1])    
    
  
    # def get_small_image_url(self):
    #     return '/{}/{}'.format(app.config['ITEM_IMAGE_FOLDER'], '_180x240.'.join(self.image.split('.'))



class Image(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), index = True)
    

class Price(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    added_on = db.Column(db.DateTime)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    jewel_id = db.Column(db.Integer, db.ForeignKey('jewel.id'))
    price = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return '<Price {}>'.format(self.price)

