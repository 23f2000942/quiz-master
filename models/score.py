from . import db
from datetime import datetime

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quizid = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestampofattempt = db.Column(db.DateTime, default=datetime)
    totalscored = db.Column(db.Float)
   