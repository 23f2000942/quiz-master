from flask import Flask, render_template,request,redirect,url_for
from models import db
from models.user import User
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from datetime import datetime

app = Flask(__name__)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@admin.com').first():
        admin = User(email='admin@admin.com', password='admin', fullname='admin', role='admin', qualification='admin')
        db.session.add(admin)
        db.session.commit()



@app.route('/',methods=['GET','POST'])
def register():
    if(request.method=='GET'):
        return render_template('register.html')
    elif (request.method=='POST'):
        username=request.form.get('username')
        if(username.lower()=="admin"):
            return render_template('register.html',message="Invalid username. Choose a different username.")
        password=request.form.get('password')
        fullname=request.form.get('fullname')
        qualification=request.form.get('qualification')
       
        dob = request.form.get('dob')
        if dob is None or dob == "":
            return "Date of birth is required", 400
        dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        print(type(dob_date))

        
        user=User(email=username,password=password,fullname=fullname,qualification=qualification,dob=dob_date,role='user')
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            return render_template('register.html',message="User already exists! Pls login.")
        return render_template('userdashboard.html',username=username,password=password)
        

@app.route('/login',methods=['GET','POST'])
def login():
    if(request.method=='GET'):
        return render_template('login.html')
    elif (request.method=='POST'):
        username=request.form.get('username')
        password=request.form.get('password')
        check=User.query.filter_by(email=username).first()
        if check is None: #email id doesnt exist
            return render_template('register.html',message="Oh no! Looks like you aren't registered with us. Pls register first.")
        else:
            if check.password!=password:
                return render_template('login.html',message="Incorrect Password.")
            else:
                print(f"username:{username},password:{password}")
                if username.lower()=="admin":
                    return render_template('admindashboard.html',username=username,password=password)
                else:
                    return render_template('userdashboard.html',username=username,password=password)

            



if __name__ == '__main__':
    app.run(debug=True)
