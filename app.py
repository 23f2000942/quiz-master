from flask import Flask, render_template, request, redirect, url_for
from models import db
from models.user import User
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from datetime import datetime

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizmaster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@admin.com").first():
        admin = User(
            email="admin@admin.com",
            password="admin",
            fullname="admin",
            role="admin",
            qualification="admin",
        )
        db.session.add(admin)
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        if username.lower() == "admin" or username.lower() == "admin@admin.com":
            return render_template(
                "register.html",
                message="Invalid username. Choose a different username.",
            )
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        qualification = request.form.get("qualification")

        dob = request.form.get("dob")
        if dob is None or dob == "":
            return "Date of birth is required", 400
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        print(type(dob_date))

        user = User(
            email=username,
            password=password,
            fullname=fullname,
            qualification=qualification,
            dob=dob_date,
            role="user",
        )
        try:
            db.session.add(user)
            db.session.commit()
            print(f"username:{username},password:{password} added succesffuly")

        except Exception as e:
            return render_template(
                "register.html", message="User already exists! Pls login."
            )

        return render_template(
            "userdashboard.html", username=username, password=password
        )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        check = User.query.filter_by(email=username).first()
        if check is None:  # email id doesnt exist
            return render_template(
                "register.html",
                message="Oh no! Looks like you aren't registered with us. Pls register first.",
            )
        else:
            if check.password != password:
                return render_template("login.html", message="Incorrect Password.")
            else:
                print(f"username:{username},password:{password}")
                if username.lower() == "admin@admin.com":
                    return redirect(url_for("path", role="admin"))
                else:
                    return redirect(url_for("path", role="user"))


@app.route("/addsubject", methods=["GET", "POST"])
def addsubject():
    if request.method == "GET":
        return render_template("addsubject.html")
    elif request.method == "POST":
        subjectname = request.form.get("subjectname")
        description = request.form.get("description")
        subject = Subject(name=subjectname, description=description)
        db.session.add(subject)
        db.session.commit()
        print(f"subject:{subjectname} added successfully")
        return render_template("addsubject.html", message="Subject added successfully")


@app.route("/deletesubject/<int:id>", methods=["GET", "POST"])
def deletesubject(id):
    subject = Subject.query.filter_by(id=id).first()
    if subject is None:
        print("Subject not found")
        return redirect(url_for("path", role="admin"))
    else:
        db.session.delete(subject)
        db.session.commit()
        print(f"subject:{subject.name} deleted successfully")
        return redirect(url_for("path", role="admin"))


@app.route("/editsubject/<int:id>", methods=["GET", "POST"])
def editsubject(id):
    if request.method == "GET":
        return render_template("editsubject.html")
    else:

        subject = Subject.query.filter_by(id=id).first()
        if subject is None:
            print("Subject not found")
            return redirect(url_for("path", role="admin"))
        subject.name = request.form.get("subjectname")
        subject.description = request.form.get("description")
        db.session.commit()
        print(f"subject:{subject.name} edited successfully")
        return redirect(url_for("path", role="admin"))


@app.route("/addchapter/<int:subjectid>", methods=["GET", "POST"])
def addchapter(subjectid):
    if request.method == "GET":
        return render_template("addchapter.html",subject=Subject.query.filter_by(id=subjectid).first().name)
    elif request.method == "POST":
        chaptername = request.form.get("chaptername")
        description = request.form.get("description")
        subject=Subject.query.filter_by(id=subjectid).first()
        if subject is None:
            return redirect(url_for("path", role="admin"))
        chapter = Chapter(name=chaptername, description=description,subject_id=subjectid)
        try:
            db.session.add(chapter)
            db.session.commit()
            print(f"chapter:{chaptername} added successfully")
            return render_template("addchapter.html", message="chapter added successfully",subject=Subject.query.filter_by(id=subjectid).first().name)
        except:
            return render_template("addchapter.html", message="repeated chapter",subject=Subject.query.filter_by(id=subjectid).first().name)

        


@app.route("/deletechapter/<int:id>", methods=["GET", "POST"])
def deletechapter(id):
    chapter = Chapter.query.filter_by(id=id).first()
    if chapter is None:
        print("chapter not found")
        return redirect(url_for("path", role="admin"))
    else:
        db.session.delete(chapter)
        db.session.commit()
        print(f"chapter:{chapter.name} deleted successfully")
        return redirect(url_for("path", role="admin"))


@app.route("/editchapter/<int:id>", methods=["GET", "POST"])
def editchapter(id):
    if request.method == "GET":
        return render_template("editchapter.html")
    else:

        chapter = Chapter.query.filter_by(id=id).first()
        if chapter is None:
            print("chapter not found")
            return redirect(url_for("path", role="admin"))
        chapter.name = request.form.get("chaptername")
        chapter.description = request.form.get("description")
        db.session.commit()
        print(f"chapter:{chapter.name} edited successfully")
        return redirect(url_for("path", role="admin"))
    
@app.route("/addquiz", methods=["GET", "POST"])
def addquiz():
    if request.method == "GET":
        return render_template("addquiz.html")
    else:

        chapter_id=request.form.get("chapterid")
        quizname=request.form.get("quizname")
        quizdate=request.form.get("quizdate")
        quizdate_format = datetime.strptime(quizdate, "%Y-%m-%d").date()
        quizduration=request.form.get("quizduration")
        quizduration_format=datetime.strptime(quizduration,"%H:%M").time()
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if chapter is None:
            print("chapter not found")
            return redirect(url_for('quizmanagement'))
        quiz = Quiz(chapter_id=chapter_id,quizdate=quizdate_format,quizduration=quizduration_format,quizname=quizname)
        db.session.add(quiz)
        db.session.commit()
        print(f"quiz:{quiz.quizname} added successfully")
        return redirect(url_for("quizmanagement"))
@app.route("/editquiz/<int:id>", methods=["GET", "POST"])
def editquiz(id):
    if request.method == "GET":
        return render_template("editquiz.html")
    else:

        quiz = Quiz.query.filter_by(id=id).first()
        if quiz is None:
            print("quiz not found")
            return redirect(url_for("path", role="admin"))
        chapter_id=request.form.get("chapterid")
        quizname=request.form.get("quizname")
        quizdate=request.form.get("quizdate")
        quizdate_format = datetime.strptime(quizdate, "%Y-%m-%d").date()
        quizduration=request.form.get("quizduration")
        quizduration_format=datetime.strptime(quizduration,"%H:%M").time()
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if chapter is None:
            print("chapter not found")
            return redirect(url_for('quizmanagement'))
        quiz.chapter_id=chapter_id
        quiz.quizdate=quizdate_format
        quiz.quizname=quizname
        quiz.quizduration=quizduration_format
        
        db.session.commit()
        print(f"quiz:{quiz.quizname} edited successfully")
        return redirect(url_for("quizmanagement"))

@app.route("/deletequiz/<int:id>", methods=["GET", "POST"])
def deletequiz(id):
    quiz = Quiz.query.filter_by(id=id).first()
    if quiz is None:
        print("quiz not found")
        return redirect(url_for('quizmanagement'))
    else:
        db.session.delete(quiz)
        db.session.commit()
        print(f"quiz:{quiz.quizname} deleted successfully")
        return redirect(url_for('quizmanagement'))

@app.route("/addquestion/<int:quizid>", methods=["GET", "POST"])
def addquestion(quizid):
    if request.method == "GET":
        return render_template("addquestion.html")
    else:
        chapterid=request.form.get("chapterid") #whats the point of this
        questiontitle=request.form.get("questiontitle")
        questionstatement=request.form.get("questionstatement")
        option1=request.form.get("option1")
        option2=request.form.get("option2") 
        option3=request.form.get("option3")
        option4=request.form.get("option4")
        correctoption=request.form.get("correctoption")
        
        quiz = Quiz.query.filter_by(id=quizid).first()
        if quiz is None:
            print("quiz not found")
            return redirect(url_for('quizmanagement'))
      
        question = Question(quizid=quizid,questiontitle=questiontitle,questionstatement=questionstatement,option1=option1,option2=option2,option3=option3,option4=option4,correctoption=correctoption)
        db.session.add(question)
        db.session.commit()
        print(f"question:{question.questiontitle} added successfully")
        return redirect(url_for("quizmanagement"))


@app.route("/editquestion/<int:id>", methods=["GET", "POST"])
def editquestion(id):
    if request.method == "GET":
        return render_template("editquestion.html")
    else:

        chapterid=request.form.get("chapterid") #whats the point of this
        questiontitle=request.form.get("questiontitle")
        questionstatement=request.form.get("questionstatement")
        option1=request.form.get("option1")
        option2=request.form.get("option2") 
        option3=request.form.get("option3")
        option4=request.form.get("option4")
        correctoption=request.form.get("correctoption")
        question = Question.query.filter_by(id=id).first()
        if question is None:
            print("question not found")
            return redirect(url_for('quizmanagement'))
        question.questiontitle=questiontitle
        question.questionstatement=questionstatement
        question.option1=option1
        question.option2=option2
        question.option3=option3
        question.option4=option4
        question.correctoption=correctoption
        db.session.commit()
        print(f"question:{question.questiontitle} edited successfully")
        return redirect(url_for("quizmanagement"))
        
        
@app.route("/deletequestion/<int:id>", methods=["GET", "POST"])
def deletequestion(id):
    question = Question.query.filter_by(id=id).first()
    if question is None:
        print("question not found")
        return redirect(url_for('quizmanagement'))
    else:
        db.session.delete(question)
        db.session.commit()
        print(f"question:{question.questiontitle} deleted successfully")
        return redirect(url_for('quizmanagement'))



@app.route("/dashboard/<string:role>")
def path(role):
    if role == "user":
        return render_template("userdashboard.html")
    elif role == "admin":
        return render_template(
            "admindashboard.html", users=User.query.all(), subjects=Subject.query.all())
    
@app.route('/dashboard/admin/quizmanagement')
def quizmanagement():
    return render_template('quizmanagement.html',quizzes=Quiz.query.all())

if __name__ == "__main__":
    app.run(debug=True)
