from . import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quizid = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    questionstatement = db.Column(db.Text, nullable=False)
    questiontitle=db.Column(db.String(150), nullable=False)
    option1 = db.Column(db.String(200))
    option2 = db.Column(db.String(200))
    option3 = db.Column(db.String(200))
    option4 = db.Column(db.String(200))
    correctoption = db.Column(db.String(200))
