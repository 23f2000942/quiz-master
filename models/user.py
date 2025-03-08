
from datetime import date
from . import db
from flask_login import UserMixin
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    qualification = db.Column(db.String(150))
    dob = db.Column(db.Date)
    role=db.Column(db.String(150),nullable=False,default="user")
    scores = db.relationship('Score', backref='user', cascade="all, delete-orphan", lazy=True)
