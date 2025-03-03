from . import db

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date)
    time_duration = db.Column(db.Time)
    remarks = db.Column(db.Text)
    
    #questions = db.relationship('Question', backref='quiz', lazy=True)
    #scores = db.relationship('Score', backref='quiz', lazy=True)
