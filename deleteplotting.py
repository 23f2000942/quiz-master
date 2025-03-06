from models import db
from models.user import User
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from datetime import datetime, date
from matplotlib import pyplot as plt
from sqlalchemy import or_
import pandas as pd 

scores = Score.query.all()

df=pd.DataFrame(scores)
print(df)

