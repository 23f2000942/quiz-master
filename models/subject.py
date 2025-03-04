from . import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False,unique=True)
    description = db.Column(db.Text)
    
    chapters = db.relationship('Chapter', backref='subject', lazy=True)
