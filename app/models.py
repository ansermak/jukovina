from app import db

ROLE_USER = 0
ROLE_USER = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	login = db.Column(db.String(20), index = True, unique = True)
	name = db.Column(db.String(120), index = True)
	added_on = db.Column(db.DateTime)
	added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	email = db.Column(db.String(60), unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
        items = db.relationship('Item', backref='author', lazy='dynamic')


	def __repr__(self):
		return u'<User {}>'.format(self.login)

class Item(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(120), index = True)
        name_en = db.Column(db.String(120), index = True, unique = True, nullable=False)
	added_on = db.Column(db.DateTime)
	added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	description = db.Column(db.Text)
        prices = db.relationship('Price', backref='prices', lazy='dynamic')

	def __repr__(self):
		return u'<Item {}>'.format(self.name)


class Price(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	added_on = db.Column(db.DateTime)
	added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
	price = db.Column(db.Integer, default = 0)

	def __repr__(self):
		return u'<Price {}>'.format(self.price)
