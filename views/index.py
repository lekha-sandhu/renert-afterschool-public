# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary
from pprint import pprint,pformat
from sqlalchemy import text
import sqlalchemy.exc
import json
from  sqlalchemy.sql.expression import func

from flask import request, render_template, redirect, url_for, abort, session
from flask import flash, current_app

from root import app,db

from models.students import Student
from models.afterschool_classes import AfterschoolClass
from models.afterschool_signins import AfterschoolSignin
from flask_login import login_required
from models.permissions import permission_required

import global_settings
from datetime import datetime
from datetime import date
app.jinja_env.globals['now'] = datetime.now




@app.route('/')
@login_required
@permission_required("afterschool")
def index():
    return render_template("index.html")

@app.route('/check_student')
@login_required
@permission_required("afterschool")
def do_check_student():
    query = request.args.get('q')
    students = Student.query.filter(Student.name.ilike(f"%{query}%")).all()
    student_list = [{"id": s.id, "name": s.name} for s in students]
    return json.dumps(student_list)


@app.route('/about')
@login_required
@permission_required("afterschool")
def about_page():
    return render_template("about.html")

@app.route('/new')
@login_required
@permission_required("afterschool")
def new_afterschool_class():
    s = Student.query.filter_by(grade='Staff').all()
    return render_template("new.html", instructors = s)

@app.route('/list-classes')
@login_required
@permission_required("afterschool")
def list_all_classes():
    a = AfterschoolClass.query.all()
    print(a)
    return render_template("list-classes.html", all_classes=a)


@app.route('/process_new_afterschool_class', methods=["POST"])
@login_required
@permission_required("afterschool")
def process_new_afterschool_class():
    pprint(request.form)

    # name = request.form.get("name")
    days = request.form.getlist("day")  
    print (days)
    days=",".join(days)
    print (days)
    activity = request.form.get("activity")
    grade = request.form.get("grade")
    room = request.form.get("room")
    instructor = request.form.get("instructor")
    print("**** INSTRUCTOR = ", instructor)
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    if not all([days, activity, grade, room, instructor, start_time, end_time]):
        return "error: cannot leave blank"
    
    valid_grades = set(str(i) for i in range(1, 13)) | {'K'}
    grades = grade.split(',')
    if not all(g.strip() in valid_grades for g in grades):
        return "error: grades must be 'K' or a number between 1 and 12, separated by commas"

    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")

    if start_time > end_time:
        return "error: start time cannot be greater than end time"
    n = AfterschoolClass()
    n.active=True
    n.school_year_id=12
    n.activity=activity
    n.room = room
    n.grades = grade
    n.weekdays = days
    n.start_time = start_time
    n.end_time = end_time


    #fix: use real instructor
    # ins=Student.query.filter_by(name='Lekha Sandhu').first()
    # n.instructor = ins

    ins=Student.query.get(int(instructor))
    n.instructor = ins

    db.session.add(n)
    db.session.commit()
    return f"You asked to add a new activity: {activity} in room {room} for grades {grade}"


@app.route("/manage_class/<int:afterschool_class_id>")
@login_required
@permission_required("afterschool")
def manage_class(afterschool_class_id):
    c = AfterschoolClass.query.get(afterschool_class_id)
    today = date.today()
    students_signed_in = AfterschoolSignin.query.filter_by(afterschool_class_id=afterschool_class_id).filter_by(sign_in_date_cache=today).all()
    grades = c.grades.split(',')
    
    signed_in_ids = {s.student_id for s in students_signed_in if not s.sign_out_time}


    all_students_in_grades = []
    for grade in grades:
        all_students_in_grades += Student.query.filter_by(grade=grade).order_by(Student.name).all()

    available_students = [s for s in all_students_in_grades if s.id not in signed_in_ids]

    return render_template("manage_class.html", afterschool_class=c, students=students_signed_in, students_grade=available_students)



@app.route("/sign_in_student", methods=["POST"])
@login_required
@permission_required("afterschool")
def process_student_sign_in():
    student_id = request.form.get("student_id")
    class_id = request.form.get("class_id")
    sign_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    print(f"Signing in student {student_id} to class_id {class_id} at {sign_in_time}")

    x =  AfterschoolSignin(
        student_id=student_id,
        afterschool_class_id=class_id,
        sign_in_time=sign_in_time
    )
    db.session.add(x)
    db.session.commit()

    return redirect("/manage_class/"+str(class_id))


@app.route("/sign_out_student", methods=["POST"])
@login_required
@permission_required("afterschool")
def process_student_sign_out():
    student_id = request.form.get("student_id")
    class_id = request.form.get("class_id")
    afterschool_signin_id = request.form.get("afterschool_signin_id")
    sign_out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    
    record = db.session.query(AfterschoolSignin).get(afterschool_signin_id)
        
    if record:
        record.sign_out_time = sign_out_time
        db.session.commit()
    
    return redirect("/manage_class/"+str(class_id))

@app.route("/sign_out_all_students", methods=["POST"])
@login_required
@permission_required("afterschool")
def sign_out_all_students():
    class_id = request.form.get("class_id")
    today = date.today()

    students_signed_in = AfterschoolSignin.query.filter_by(
        afterschool_class_id=class_id,
        sign_in_date_cache=today
    ).filter(AfterschoolSignin.sign_out_time.is_(None)).all()

    for student in students_signed_in:
        student.sign_out_time = datetime.now()  
        db.session.add(student)

    db.session.commit()
    return redirect("/manage_class/" + str(class_id))
