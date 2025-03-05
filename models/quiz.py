from sqlalchemy.ext.hybrid import hybrid_property
from . import db


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    quizdate = db.Column(db.Date)
    quizduration = db.Column(db.Time)
    
    quizname=db.Column(db.String(150), nullable=False,unique=True)
    
    questions = db.relationship('Question', backref='quiz', lazy=True)
    
    
    @hybrid_property
    def noofquestions(self):
        return len(self.questions)
