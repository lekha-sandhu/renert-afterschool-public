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
from models.afterschool_enrollment import AfterschoolEnrollment
from flask_login import login_required
from models.permissions import permission_required

import global_settings
from datetime import datetime
from datetime import date
app.jinja_env.globals['now'] = datetime.now

import pytz




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
    students = Student.query.filter(Student.name.ilike(f"%{query}%")).order_by(Student.name).all()
    student_list = [{"id": s.id, "name": s.name, "grade": s.grade} for s in students]

    sql = """
    select
    *
    from
    library_students
    
    left join
    afterschool_signins
    on
    library_students.id = afterschool_signins.student_id
    and
    afterschool_signins.sign_in_date_cache = '2025-04-03'

    left join
    afterschool_classes
    on
    afterschool_signins.afterschool_class_id = afterschool_classes.afterschool_class_id

    where
    library_students.name ilike '%aman%'
    order by
    name ;
    """

    student_list2 = db.session.execute( text(sql) )
    student_list2 = [x._asdict() for x in student_list2]
    pprint(student_list2)
    
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
    active_classes = AfterschoolClass.query.filter_by(active=True).all()
    return render_template("list-classes.html", active_classes=active_classes)

@app.route("/manage_classes")
@login_required
@permission_required("afterschool")
def manage_classes():
    all_classes = AfterschoolClass.query.all()
    return render_template("manage_classes.html", all_classes=all_classes)


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

    filters_for_enrollment = []
    filters_for_enrollment.append(AfterschoolEnrollment.afterschool_class_id == afterschool_class_id)
    filters_for_enrollment.append(AfterschoolEnrollment.start_date <= today)
    filters_for_enrollment.append(AfterschoolEnrollment.end_date >= today)

    enrolled_students = AfterschoolEnrollment.query.filter(*filters_for_enrollment).all()

    students_grade = Student.query.filter(Student.grade.in_(grades)).order_by(Student.name).all()

    return render_template(
            "manage_class.html",
            afterschool_class=c,
            students=students_signed_in,
            students_grade=students_grade,
            enrolled_students=enrolled_students)

@app.route("/enable_class/<int:afterschool_class_id>")
@login_required
@permission_required("afterschool")
def enable_class(afterschool_class_id):
    c = AfterschoolClass.query.get(afterschool_class_id)
    c.active=True
    db.session.add(c)
    db.session.commit()
    return redirect("/manage_classes")

@app.route("/disable_class/<int:afterschool_class_id>")
@login_required
@permission_required("afterschool")
def disable_class(afterschool_class_id):
    c = AfterschoolClass.query.get(afterschool_class_id)
    c.active=False
    db.session.add(c)
    db.session.commit()
    return redirect("/manage_classes")

@app.route("/sign_in_student", methods=["POST"])
@login_required
@permission_required("afterschool")
def process_student_sign_in():
    student_id = request.form.get("student_id")
    class_id = request.form.get("class_id")
    sign_in_time = datetime.now().astimezone(tz=global_settings.tz)

    
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
    tz = pytz.timezone('America/Edmonton')
    sign_out_time = datetime.now(tz)
    
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
        student.sign_out_time = datetime.now().astimezone(tz=global_settings.tz)
        db.session.add(student)

    db.session.commit()
    return redirect("/manage_class/" + str(class_id))

@app.route("/manage_enrollments/<int:afterschool_class_id>")
@login_required
@permission_required("afterschool")
def manage_enrollments(afterschool_class_id):
    afterschool_activity = AfterschoolClass.query.get(afterschool_class_id)
    valid_grades = afterschool_activity.grades.split(',')
    valid_students_for_enrollment = []
    for grade in valid_grades:
        valid_students_for_enrollment += Student.query.filter_by(grade=grade).order_by(Student.name).all()
    
    enrollments = AfterschoolEnrollment.query.filter_by(afterschool_class_id = afterschool_class_id).all()

    return render_template("enrollments.html", afterschool_class=afterschool_activity, valid_students_for_enrollment = valid_students_for_enrollment, enrollments = enrollments)

@app.route("/enroll_student", methods=["POST"])
@login_required
@permission_required("afterschool")
def process_student_enrollment():
    student_id = request.form.get("student_id")
    class_id = request.form.get("class_id")
    startdate = request.form.get("startdate")
    enddate = request.form.get("enddate")

    print(f"Enrolling student {student_id} to class_id {class_id} with start date = {startdate} and end date = {enddate}")

    new_afterschool_enrollment =  AfterschoolEnrollment(
        student_id=student_id,
        afterschool_class_id=class_id,
        start_date = startdate,
        end_date = enddate
    )
    db.session.add(new_afterschool_enrollment)
    db.session.commit()

    return redirect("/manage_enrollments/"+str(class_id))

@app.route("/remove_student_enrollment", methods=["POST"])
@login_required
@permission_required("afterschool")
def process_remove_student_enrollment():
    class_id = request.form.get("class_id")
    afterschool_enrollment_id = request.form.get("afterschool_enrollment_id")

    record = db.session.query(AfterschoolEnrollment).get(afterschool_enrollment_id)

    if record:
        db.session.delete(record)  
        db.session.commit()    

    return redirect("/manage_enrollments/"+str(class_id))