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
import global_settings
from datetime import datetime


@app.route('/')
def index():
    students = Student.query.filter(Student.grade.in_(["1", "2", "3"])).all()  # Filter students in grades 1-3

    return render_template("index.html", students=students)

@app.route('/new')
def new_afterschool_class():
    s = Student.query.filter_by(grade='Staff').all()
    return render_template("new.html", instructors = s)

@app.route('/list-classes')
def list_all_classes():
    a = AfterschoolClass.query.all()
    return render_template("list-classes.html", all_classes=a)


@app.route('/process_new_afterschool_class', methods=["POST"])
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

    if not all([name, days, activity, grade, room, instructor, start_time, end_time]):
        return "error: cannot leave blank"
    
    valid_grades = set(str(i) for i in range(1, 13)) | {'K'}
    grades = grade.split(',')
    if not all(g.strip() in valid_grades for g in grades):
        return "error: grades must be 'K' or a number between 1 and 12, separated by commas"

    from datetime import datetime
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
def manage_class(afterschool_class_id):
    c = AfterschoolClass.query.get(afterschool_class_id)
    students = AfterschoolSignin.query.filter_by(afterschool_class_id=afterschool_class_id).all()
    grades = c.grades.split(',')
    
    students_grade = []
    for grade in grades:
        students_grade += Student.query.filter_by(grade=grade).all()
    
    return render_template("manage_class.html", afterschool_class=c, students=students, students_grade=students_grade)
    