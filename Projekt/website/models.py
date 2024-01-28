from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))




class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable = False)
    category = db.Column(db.String(30), default='rent', nullable = False)
    amount = db.Column(db.Float, nullable = False)
    date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, type, category, amount, user_id):
        self.type = type
        self.category = category
        self.amount = amount 
        self.user_id = user_id   






class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable = False)
    type = db.Column(db.String(30), nullable = False)
    icon = db.Column(db.String(50), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, type, icon, user_id):
        self.name = name
        self.type = type
        self.icon = icon      
        self.user_id = user_id




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    transactions = db.relationship('Transaction')
    categories = db.relationship('Category')
   

