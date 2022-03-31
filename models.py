from ast import For
from enum import unique
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app=app
    db.init_app(app)

class User(db.Model):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String, nullable=False)

    @classmethod
    def register(cls, username, password, first_name, last_name):
        """Register user with hased password & return user"""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into a normal (unicode utf8) string
        hashed_utf8 = hashed.decode('utf8')
        # return user with username and hashed password
        return cls(username=username, first_name=first_name, last_name=last_name, password=hashed_utf8)
    
    @classmethod
    def autenticate(cls, username, password):
        """Validate user and password. Return user if valid; else return False"""

        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

class DinnerMenu(db.Model):
    __tablename__="dinner_menus"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), primary_key=True)
    appetizer = db.Column(db.Integer, ForeignKey('recipes.id'))
    main_course = db.Column(db.Integer, ForeignKey('recipes.id'), nullable=False)
    side_dish = db.Column(db.Integer, ForeignKey('recipes.id'))
    dessert = db.Column(db.Integer, ForeignKey('recipes.id'))

    users = db.relationship('User', backref='dinners', foreign_keys=[user_id])

    appetizer_recipe = db.relationship('Recipe', backref='app_dinners', foreign_keys=[appetizer])
    main_course_recipe = db.relationship('Recipe', backref='mc_inners', foreign_keys=[main_course])
    side_dish_recipe = db.relationship('Recipe', backref='sd_dinners', foreign_keys=[side_dish])
    dessert_recipe = db.relationship('Recipe', backref='d_dinners', foreign_keys=[dessert])

class Recipe(db.Model):
    __tablename__="recipes"
    id = db.Column(db.Integer, primary_key=True, unique=True)   
    title = db.Column(db.Text, nullable=False)

class FavoriteDinnerMenu(db.Model):
    __tablename__="favorite_dinner_menus"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dinner_id = db.Column(db.Integer, ForeignKey('dinner_menus.id'))
    user_id = db.Column(db.Integer, ForeignKey('users.id'))

    favorite_dinners = db.relationship('DinnerMenu', backref="favorites")
    users = db.relationship('User', backref="favorites")
    