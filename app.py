from flask import Flask, render_template, request, redirect, url_for,session,jsonify
from models import db
from models.user import User
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from datetime import datetime, date
from matplotlib import pyplot as plt
from sqlalchemy import or_, func
import os
import numpy as np
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = 'aditi'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizmaster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG'] = True

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@admin.com").first():
        admin = User(
            email="admin@admin.com",
            password=generate_password_hash("admin"),
            fullname="admin",
            role="admin",
            qualification="admin",
        )
        db.session.add(admin)
        db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route("/register", methods=["GET", "POST"])
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
        password = generate_password_hash(request.form.get("password"))
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
        print(f"username:{username},password:{password},userid={user.id}")

        return redirect(url_for("path", role="user", id=user.id))



@app.route("/login", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
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
            if not check_password_hash(check.password, password):
                return render_template("login.html", message="Incorrect Password.")
            else:
                login_user(check)
                print(f"username:{username},password:{password}")
                if username.lower() == "admin@admin.com":
                    return redirect(url_for("path", role="admin", id=1))
                else:
                    print(
                        f"user id is \n\n{check.id}\n\n"
                    )
                    return redirect(
                        url_for(
                            "path",
                            role="user",
                            id=check.id
                        )
                    )
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


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
        return redirect(url_for("path", role="admin", id=1))
    else:
        db.session.delete(subject)
        db.session.commit()
        print(f"subject:{subject.name} deleted successfully")
        return redirect(url_for("path", role="admin", id=1))


@app.route("/editsubject/<int:id>", methods=["GET", "POST"])
def editsubject(id):
    subject = Subject.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("editsubject.html",subject=subject)
    else:

        if subject is None:
            print("Subject not found")
            return redirect(url_for("path", role="admin", id=1))
        subjectname = request.form.get("subjectname")
        subjectdescription = request.form.get("description")

        if not subjectname:
            subjectname=subject.name
        if not subjectdescription:
            subjectdescription=subject.description

        subject.name=subjectname
        subject.description=subjectdescription
        
        db.session.commit()
        print(f"subject:{subject.name} descirption:{subject.description} edited successfully")
        return redirect(url_for("path", role="admin", id=1))


@app.route("/addchapter/<int:subjectid>", methods=["GET", "POST"])
def addchapter(subjectid):
    if request.method == "GET":
        return render_template(
            "addchapter.html",
            subject=Subject.query.filter_by(id=subjectid).first().name,
        )
    elif request.method == "POST":
        chaptername = request.form.get("chaptername")
        description = request.form.get("description")
        subject = Subject.query.filter_by(id=subjectid).first()
        if subject is None:
            return redirect(url_for("path", role="admin", id=1))
        chapter = Chapter(
            name=chaptername, description=description, subject_id=subjectid
        )
        try:
            db.session.add(chapter)
            db.session.commit()
            print(f"chapter:{chaptername} added successfully")
            return render_template(
                "addchapter.html",
                message="chapter added successfully",
                subject=Subject.query.filter_by(id=subjectid).first().name,
            )
        except:
            return render_template(
                "addchapter.html",
                message="repeated chapter",
                subject=Subject.query.filter_by(id=subjectid).first().name,
            )


@app.route("/deletechapter/<int:id>", methods=["GET", "POST"])
def deletechapter(id):
    chapter = Chapter.query.filter_by(id=id).first()
    if chapter is None:
        print("chapter not found")
        return redirect(url_for("path", role="admin", id=1))
    else:
        db.session.delete(chapter)
        db.session.commit()
        print(f"chapter:{chapter.name} deleted successfully")
        return redirect(url_for("path", role="admin", id=1))


@app.route("/editchapter/<int:id>", methods=["GET", "POST"])
def editchapter(id):
    chapter = Chapter.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("editchapter.html",chapter=chapter)
    else:

        
        if chapter is None:
            print("chapter not found")
            return redirect(url_for("path", role="admin", id=1))
        chaptername = request.form.get("chaptername")
        chapterdescription = request.form.get("description")

        if not chaptername:
            chaptername=chapter.name
        if not chapterdescription:
            chapterdescription=chapter.description

        chapter.name=chaptername
        chapter.description=chapterdescription
        
       
        db.session.commit()
        print(f"chapter:{chapter.name} edited successfully")
        return redirect(url_for("path", role="admin", id=1))


@app.route("/addquiz", methods=["GET", "POST"])
def addquiz():
    if request.method == "GET":
        return render_template("addquiz.html")
    else:

        chapter_id = request.form.get("chapterid")
        quizname = request.form.get("quizname")
        quizdate = request.form.get("quizdate") or "2026-01-01"
        quizdate_format = datetime.strptime(quizdate, "%Y-%m-%d").date()
        quizduration = request.form.get("quizduration") or "00:10"
        quizduration_format = datetime.strptime(quizduration, "%H:%M").time()
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if chapter is None:
            print("chapter not found")
            return redirect(url_for("quizmanagement"))
        quiz = Quiz(
            chapter_id=chapter_id,
            quizdate=quizdate_format,
            quizduration=quizduration_format,
            quizname=quizname,
        )
        db.session.add(quiz)
        db.session.commit()
        print(f"quiz:{quiz.quizname} added successfully")
        return redirect(url_for("quizmanagement"))


@app.route("/editquiz/<int:id>", methods=["GET", "POST"])
def editquiz(id):
    quiz = Quiz.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("editquiz.html",quiz=quiz)
    else:

        
        if quiz is None:
            print("quiz not found")
            return redirect(url_for("path", role="admin", id=1))
        


        chapter_id = request.form.get("chapterid") or quiz.chapter_id
        quizname = request.form.get("quizname") or quiz.quizname
        quizdate = request.form.get("quizdate") 
        if quizdate:
            quizdate_format = datetime.strptime(quizdate, "%Y-%m-%d").date() 
        else: 
            quizdate_format = quiz.quizdate
        quizduration = request.form.get("quizduration") 
        if quizduration:
    
            quizduration_format = datetime.strptime(quizduration, "%H:%M").time() 
        else:
            quizduration_format =quiz.quizduration

        #validate if new chapter_id is correct
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if chapter is None:
            print("chapter not found")
            return redirect(url_for("quizmanagement"))
        quiz.chapter_id = chapter_id
        quiz.quizdate = quizdate_format
        quiz.quizname = quizname
        quiz.quizduration = quizduration_format

        db.session.commit()
        print(f"quiz:{quiz.quizname} edited successfully")
        return redirect(url_for("quizmanagement"))


@app.route("/deletequiz/<int:id>", methods=["GET", "POST"])
def deletequiz(id):
    quiz = Quiz.query.filter_by(id=id).first()
    if quiz is None:
        print("quiz not found")
        return redirect(url_for("quizmanagement"))
    else:
        db.session.delete(quiz)
        db.session.commit()
        print(f"quiz:{quiz.quizname} deleted successfully")
        return redirect(url_for("quizmanagement"))


@app.route("/addquestion/<int:quizid>", methods=["GET", "POST"])

def addquestion(quizid):
    chapterid=Quiz.query.filter_by(id=quizid).first().chapter_id
    chapter=Chapter.query.filter_by(id=chapterid).first()
    if request.method == "GET":
        return render_template("addquestion.html",chapter=chapter)
    else:
        
        questiontitle = request.form.get("questiontitle")
        questionstatement = request.form.get("questionstatement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correctoption = request.form.get("correctoption")

        quiz = Quiz.query.filter_by(id=quizid).first()
        if quiz is None:
            print("quiz not found")
            return redirect(url_for("quizmanagement"))

        question = Question(
            quizid=quizid,
            questiontitle=questiontitle,
            questionstatement=questionstatement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correctoption=correctoption,
        )
        db.session.add(question)
        db.session.commit()
        print(f"question:{question.questiontitle} added successfully")
        return redirect(url_for("quizmanagement"))


@app.route("/editquestion/<int:id>", methods=["GET", "POST"])
def editquestion(id):
    question = Question.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("editquestion.html",question=question)
    else:

        
        questiontitle = request.form.get("questiontitle") or question.questiontitle
        questionstatement = request.form.get("questionstatement") or question.questionstatement
        option1 = request.form.get("option1") or question.option1
        option2 = request.form.get("option2") or question.option2
        option3 = request.form.get("option3") or question.option3
        option4 = request.form.get("option4") or question.option4
        correctoption = request.form.get("correctoption") or question.correctoption
        correctoption = request.form.get("correctoption")
        
        if question is None:
            print("question not found")
            return redirect(url_for("quizmanagement"))
        question.questiontitle = questiontitle
        question.questionstatement = questionstatement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correctoption = correctoption
        db.session.commit()
        print(f"question:{question.questiontitle} edited successfully")
        return redirect(url_for("quizmanagement"))


@app.route("/deletequestion/<int:id>", methods=["GET", "POST"])
def deletequestion(id):
    question = Question.query.filter_by(id=id).first()
    if question is None:
        print("question not found")
        return redirect(url_for("quizmanagement"))
    else:
        db.session.delete(question)
        db.session.commit()
        print(f"question:{question.questiontitle} deleted successfully")
        return redirect(url_for("quizmanagement"))


@app.route("/dashboard/user/<int:id>", methods=["GET", "POST"])
def userdashboard(id):
    user=User.query.filter_by(id=id).first()
    name=user.fullname
    return render_template(
        "userdashboard.html",
        quizzes=Quiz.query.filter(Quiz.quizdate >= date.today()).all(),
        user=user,
        id=id,name=name
    )


@app.route("/dashboard/user/<int:id>/userscores", methods=["GET", "POST"])
def userscores(id):
    user=User.query.filter_by(id=id).first()
    scores = db.session.query(
        Score.quizid,
        Quiz.quizname,
        Chapter.name,
        Score.timestampofattempt,
        Score.totalscored
    ).join(
        Quiz, Score.quizid == Quiz.id
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).filter(
        Score.userid == id
    ).all()
    print(user.fullname)
    return render_template("userscores.html",user=user,scores=scores )


@app.route("/dashboard/user/<int:id>/usersummary", methods=["GET", "POST"])
def usersummary(id):
    user=User.query.filter_by(id=id).first()
    attempts_per_subject = db.session.query(
    Subject.name,
    func.count(Score.id).label('attempt_count')
).join(
    Chapter, Subject.id == Chapter.subject_id
).join(
    Quiz, Chapter.id == Quiz.chapter_id
).join(
    Score, Quiz.id == Score.quizid
).filter(
    Score.userid == id
).group_by(
    Subject.name
).all()
    print(attempts_per_subject)
    x,y=[],[]
    for tu in attempts_per_subject:
        x.append(tu[0])
        y.append(tu[1])
    plt.figure()
    plt.bar(x,y)
    plt.xlabel("Subject")
    plt.ylabel("No. of Quizzes attempted")
    userchartpath1 = os.path.join('static', f'userchart1{id}.png')
    plt.savefig(userchartpath1)
    plt.close()
    day_wise_attempts = db.session.query(
    func.date(Score.timestampofattempt).label('attempt_date'),
    func.count(Score.id).label('attempt_count')
).filter(
    Score.userid == id
).group_by(
    func.date(Score.timestampofattempt)
).order_by(
    func.date(Score.timestampofattempt)
).all()
    print(day_wise_attempts)
    days,data=[],[]
    for tu in day_wise_attempts:
        days.append(tu[0])
        data.append(tu[1])
    plt.figure()
    plt.pie(data,labels=days)
    userchartpath2 = os.path.join('static', f'userchart2{id}.png')
    plt.savefig(userchartpath2)
    plt.close()

    
    

    return render_template("usersummary.html",user=user,chartname1=f'userchart1{id}.png',chartname2=f'userchart2{id}.png')
@app.route("/dashboard/admin/adminsummary", methods=["GET", "POST"])
def adminsummary():
    subject_top_scores = db.session.query(
    Subject.name.label('subject_name'),
    func.max(Score.totalscored).label('top_score')
).join(
    Chapter, Subject.id == Chapter.subject_id
).join(
    Quiz, Chapter.id == Quiz.chapter_id
).join(
    Score, Quiz.id == Score.quizid
).group_by(
    Subject.name
).all()
    print(subject_top_scores)
    subjects=[subject_top_score[0] for subject_top_score in subject_top_scores]
    topscores=[subject_top_score[1] for subject_top_score in subject_top_scores]
    plt.bar(subjects,topscores)
    plt.xlabel("Subject")
    plt.ylabel("Topscores")
    adminchartpath1 = os.path.join('static', 'adminchart1.png')
    plt.savefig(adminchartpath1)
    plt.close()
    print(adminchartpath1)
    subject_wise_attempts = db.session.query(
    Subject.name.label('subject_name'),
    func.count(Score.id).label('total_attempts')
).join(
    Chapter, Subject.id == Chapter.subject_id
).join(
    Quiz, Chapter.id == Quiz.chapter_id
).join(
    Score, Quiz.id == Score.quizid
).group_by(
    Subject.name
).all()
    print(subject_wise_attempts)
    subjects=[subject_wise_attempt[0] for subject_wise_attempt in subject_wise_attempts]
    noofattempts=[subject_wise_attempt[1] for subject_wise_attempt in subject_wise_attempts]
   #for radar plot
    num_vars = len(subjects)


    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

   
    noofattempts += noofattempts[:1]
    angles += angles[:1]

    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

  
    ax.plot(angles, noofattempts, color='blue', linewidth=2)
    ax.fill(angles, noofattempts, color='blue', alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(subjects)

    if(not noofattempts):
        return redirect(url_for('path',role='admin',id=1))
    ax.set_ylim(0, max(noofattempts))

   
    plt.title('Subjects vs Number of Attempts', y=1.1)
    adminchartpath2 = os.path.join('static', 'adminchart2.png')
    plt.show()
    plt.savefig(adminchartpath2)
    plt.close()

    



    return render_template("adminsummary.html",chartname1="adminchart1.png",chartname2="adminchart2.png")

    






@app.route("/dashboard/user/<int:id>/<int:quizid>/viewquiz", methods=["GET", "POST"])
def userviewquiz(id, quizid):
    user=User.query.filter_by(id=id).first()
    quiz = Quiz.query.filter_by(id=quizid).first()
    chapter = Chapter.query.filter_by(id=quiz.chapter_id).first()
    subject = Subject.query.filter_by(id=chapter.subject_id).first()
    print(quiz, chapter, subject)
    return render_template(
        "userviewquiz.html",
        
        quiz=quiz,
        chapter=chapter.name,
        subject=subject.name,
        user=user
    )





@app.route("/dashboard/user/<int:id>/<int:quizid>/startquiz", methods=["GET", "POST"])
def userstartquiz(id, quizid):
    
    count,displaycount = 0,0
    session["scores"]={}

    if request.method == "GET":
        quiz = Quiz.query.filter_by(id=quizid).first()
        total = quiz.noofquestions
        questions = sorted(quiz.questions, key=lambda question: question.id)
        print(questions)

        if (quiz is None) or (total==0) or (quiz.questions[0] is None):

            return redirect(url_for("path", role="user", id=id))
        print(quiz.questions)
        question = quiz.questions[0]
        questionid = question.id
        return redirect(
            url_for(
                "displayquestion",
                id=id,
                quizid=quizid,
                questionid=questionid,
                count=displaycount,
                total=total,
            )
        )


@app.route(
    "/dashboard/user/<int:id>/<int:quizid>/<int:questionid>/<int:count>/<int:total>",
    methods=["GET", "POST"],
)

def displayquestion(id, quizid, questionid, count, total):
    displaycount=count+1
    if request.method == "GET":  # display the question
        question = Question.query.filter_by(id=questionid).first()
        
        return render_template(
            "usershowquestion.html", question=question, count=displaycount, total=total
        )

    else:  # process the answer (POST)
        scores = session.get('scores', {})
        action = request.form.get("action")
        selectedoption = request.form.get("selectedoption")
        question = Question.query.filter_by(id=questionid).first()
        correctoption = question.correctoption

        if selectedoption == correctoption:
            print(f"Correct answer for question {question}")
            scores[str(questionid)] = 1
        else:
            print(f"Wrong answer for question {question}")
            scores[str(questionid)] = 0
        session["scores"] = scores

        if action == "next" and count + 1 < total:
            quiz = Quiz.query.filter_by(id=quizid).first()
            questions = sorted(quiz.questions, key=lambda question: question.id)
            count += 1
            
            questionid = questions[count].id

            return redirect(
                url_for(
                    "displayquestion",
                    id=id,
                    quizid=quizid,
                    questionid=questionid,
                    count=displaycount,
                    total=total,
                )
            )

        if action == "submit" or count + 1 >= total:
            if selectedoption == correctoption:
                print(f"correct answer for question {question}")
                scores[str(questionid)] = 1
            else:
                print(f"wrong answer for question {question}")
                scores[str(questionid)] = 0
            session["scores"] = scores
            timeofattempt = datetime.now()
            totalscored = sum(scores.values()) if scores else 0

            score_object = Score(
                quizid=quizid,
                userid=id,
                totalscored=totalscored,
                timestampofattempt=timeofattempt,
            )
            db.session.add(score_object)
            db.session.commit()
            scoreid = score_object.id
            print(dict(session))

            return redirect(url_for("userresults", quizid=quizid, scoreid=scoreid))
@app.route(
    "/dashboard/user/<int:quizid>/<int:scoreid>/results",
    methods=["GET", "POST"],
)
def userresults(quizid, scoreid):

    quiz = Quiz.query.filter_by(id=quizid).first()
    userscore = Score.query.filter_by(id=scoreid).first()
    userid = userscore.userid
    user=User.query.filter_by(id=userid).first()

    if not quiz or not userscore: 
        return "Invalid quiz or score", 404

    yourscore = userscore.totalscored
    noofquestions = quiz.noofquestions
    scores = session.get('scores', {})

    data = []
    question_ids = [int(qid) for qid in scores.keys()]
    questions = Question.query.filter(Question.id.in_(question_ids)).all()
    question_map = {q.id: q for q in questions}

    for question_id in question_ids:
        question = question_map.get(question_id)
        if question:
            data.append({
                'id': question.id,
                'statement': question.questionstatement,
                'score': scores[str(question_id)]
            })

    

    return render_template(
        "userquizover.html",
        quiz=quiz,
        data=sorted(data, key=lambda x: x['id']),
        yourscore=yourscore,
        noofquestions=noofquestions,
        user=user
    )
@app.route("/dashboard/<string:role>/<int:id>")
def path(role, id):
    if role == "user":
        name = User.query.filter_by(id=id).fullname
        return redirect(url_for("userdashboard", id=id, name=name))
    elif role == "admin":
        return render_template(
            "admindashboard.html", users=User.query.all(), subjects=Subject.query.all()
        )


@app.route("/dashboard/admin")
def reroute_to_admin():
    return redirect(url_for("path", role="admin", id=1))


@app.route("/dashboard/admin/quizmanagement")
def quizmanagement():
    return render_template("quizmanagement.html", quizzes=Quiz.query.all())

@app.route("/dashboard/admin/search",methods=["GET","POST"])
def adminsearch():
    if request.method=="GET":
        return render_template("adminsearch.html")
    else:
        whattosearch=request.form.get("whattosearch")
        query=request.form.get("query")
        if whattosearch == 'user':
            results = User.query.filter(
                or_(
                    User.fullname.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.qualification.ilike(f"%{query}%"),
                    User.role.ilike(f"%{query}%"),
                    User.dob.ilike(f"%{query}%"),
                )
            ).all()
        elif whattosearch == 'quiz':
            results = Quiz.query.filter(or_
            (Quiz.quizname.ilike(f"%{query}%"), 
             Quiz.quizdate.ilike(f"%{query}%"),
             Quiz.quizduration.ilike(f"%{query}%"))).all()
        elif whattosearch == 'subject':
            results = Subject.query.filter(
                or_(
                    Subject.name.ilike(f"%{query}%"),
                    Subject.description.ilike(f"%{query}%")
                )
            ).all()
        
        elif whattosearch == 'question':
                results = Question.query.filter(
                or_(
                    Question.questionstatementstatement.ilike(f"%{query}%"),
                    Question.questionstatementtitle.ilike(f"%{query}%"),
                    Question.option1.ilike(f"%{query}%"),
                    Question.option2.ilike(f"%{query}%"),
                    Question.option3.ilike(f"%{query}%"),
                    Question.option4.ilike(f"%{query}%")
                )
            ).all()
        else:
            results = []
        return render_template('adminsearchresults.html', results=results, whattosearch=whattosearch,query=query)

@app.route("/dashboard/user/<int:id>/search",methods=["GET","POST"],endpoint="usersearch")
def usersearch(id):
    user=User.query.filter_by(id=id).first()
    if request.method=="GET":
        return render_template("usersearch.html",user=user)
    else:
        whattosearch=request.form.get("whattosearch")
        query=request.form.get("query")
        
        if whattosearch == 'quiz':
            results = Quiz.query.filter(or_
            (Quiz.quizname.ilike(f"%{query}%"), 
             Quiz.quizdate.ilike(f"%{query}%"),
             Quiz.quizduration.ilike(f"%{query}%"))).all()
        elif whattosearch == 'subject':
            results = Subject.query.filter(
                or_(
                    Subject.name.ilike(f"%{query}%"),
                    Subject.description.ilike(f"%{query}%")
                )
            ).all()
        
        
        else:
            results = []
        
        
        print(user.fullname)
        return render_template('usersearchresults.html', results=results, whattosearch=whattosearch,query=query,user=user)

#API routes
@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    chapters = Chapter.query.all()
    data=[]
    for chapter in chapters:
        data.append({'id': chapter.id, 'name': chapter.name,'description':chapter.description, 'subject_id': chapter.subject_id})

    return jsonify(data)


@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    data=[]
    for quiz in quizzes:
        data.append({'id': quiz.id, 'name': quiz.quizname,'date':str(quiz.quizdate), 'quizduration': str(quiz.quizduration), 'no.ofquestions': quiz.noofquestions, 'chapter_id': quiz.chapter_id})
    return jsonify(data)


@app.route('/api/scores', methods=['GET'])
def get_scores():
    scores = Score.query.all()
    data=[]
    for score in scores:
        data.append({'id': score.id, 'quizid': score.quizid,'userid':score.userid, 'totalscored': score.totalscored, 'timestampofattempt': str(score.timestampofattempt)})
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
