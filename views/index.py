# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from pprint import pprint,pformat
from sqlalchemy import text
import sqlalchemy.exc
import json
from  sqlalchemy.sql.expression import func
from sqlalchemy.sql import extract

from flask import request, render_template, redirect, url_for, abort, session
from flask import flash, current_app

from root import app,db

from models.students import Student
from models.afterschool_classes import AfterschoolClass
from models.afterschool_signins import AfterschoolSignin
import global_settings

from datetime import datetime, timedelta  


@app.route('/')
def index():
    # Get name of a random staff member
    # s = Student.query.filter_by(grade='12').order_by(func.random()).first()
    
    s = Student.query.filter_by(grade='2').all()
    class_activity = "math"
    grades = "2,3"
    return render_template("index.html",
                           students=s, class_activity = class_activity, grades = grades)


@app.route('/afterschool/<activity_name>')
def afterschool_page(activity_name):
    grades = 2,3
    s = Student.query.filter_by(grade='2').all()
    
    return render_template("afterschool.html", activity_name = activity_name, students = s)

@app.route('/add_student')
def add_student():
    
    return render_template("add_student.html")

@app.route('/new-afterschool-class')
def new_afterschool_class():
    
    s = Student.query.filter_by(grade='Staff').all()
    
    return render_template("new_afterschool_class.html", instructors = s)


@app.route("/process-new-afterschool-class", methods = ["POST"])
def process_new_afterschool_class():
    activity_name = request.form.get("activity_name")
    room = request.form.get("room")
    grades = request.form.get("grades")
    mon = request.form.get("1")
    tue = request.form.get("2")
    wed = request.form.get("3")
    thu = request.form.get("4")
    fri = request.form.get("5")
    sat = request.form.get("6")
    sun = request.form.get("7")
    teacher_id = request.form.get("teacher_name")
    starttime_str = request.form.get("starttime")
    endtime_str = request.form.get("endtime")
    
    start_time = datetime.strptime(starttime_str, "%H:%M")
    end_time = datetime.strptime(endtime_str, "%H:%M")
    
    #print("******** Teacher = ", teacherme)
    
    ins = Student.query.get(int(teacher_id))
    
    x = AfterschoolClass()
    x.room = room
    x.activity = activity_name
    x.instructor = ins
    x.start_time = starttime_str
    x.end_time = endtime_str
    x.weekdays = "Wed,Fri"
    x.grades = grades
    
    db.session.add(x)
    db.session.commit()

    return(f"Activity name = {activity_name} <br> Grades = {grades} <br> Room = {room} <br>\
        Monday = {mon} <br> Tueday = {tue} <br> Wednesday = {wed} <br> Thursday = {thu} <br> Friday = {fri} \
        <br> Saturday = {sat} <br> Sunday = {sun} <br> Teacher name = {teacher_id} <br> Start time = {starttime_str} \
        <br> End time = {endtime_str}")
    
@app.route("/list_classes")
def list_classes():
    a = AfterschoolClass.query.all()
    return render_template("list_classes.html", all_classes = a)

@app.route("/pick_student_report")
def pick_student_report():
    all_students = Student.query.filter(Student.grade != 'Staff').all()
    
    return render_template("pick_student_report.html", students = all_students)

@app.route("/studentreport", methods = ["POST"])
def student_report():
    student_id = request.form.get("student")
    signins = AfterschoolSignin.query.filter_by(student_id = student_id).all()
    return render_template("student_report.html", sid = student_id, signins = signins)

@app.route("/pick_monthly_report")
def pick_monthly_report():    
    return render_template("pick_monthly_report.html")

@app.route("/monthreport", methods = ["POST"])
def monthreport():
    month = request.form.get("date")    
    return render_template("monthly_report.html", month = month)

@app.route("/filtered_reports")
def filtered_reports():
    all_students = Student.query.filter(Student.grade != 'Staff').all()
    activities = AfterschoolClass.query.all()
    
    return render_template("filtered_reports.html", student = all_students, activity = activities)

@app.route("/report", methods = ["POST"])
def report():
    student_id = request.form.get("student")
    date = request.form.get("date")
    activity_id = request.form.get("activity")
    student = None
    activity = None
        
    if student_id == "":
        student_id = None
        
    if activity_id == "":
        activity_id = None
           
    if date == "":
        date = None
    
    if(date is not None):
        date_list = date.split("-")
        month = int(date_list[1])
        year = int(date_list[0])
        last_days = [31, (29 if year % 4 == 0 else 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        day = last_days[month-1]

        start_date = datetime(year, month, 1, 0,0,0)
        
        end_date = datetime(year, month, day, 23,59,59)
    
    def filters():
        
        conditions = []
        student = None
        activity = None
    
        if student_id is not None:
            conditions.append(AfterschoolSignin.student_id == student_id)
            student = Student.query.filter(Student.id == student_id).all()
            student = student[0]
        
        if date is not None:
            conditions.append(AfterschoolSignin.sign_in_time >= start_date)
            conditions.append(AfterschoolSignin.sign_in_time <= end_date)
        
        if activity_id is not None:
            conditions.append(AfterschoolSignin.afterschool_class_id == activity_id)
            activity = AfterschoolClass.query.filter(AfterschoolClass.afterschool_class_id == activity_id).all()
            activity = activity[0]
            
        return conditions, student, activity
    
    things_to_filter_by, student, activity = filters()
    
    signins = AfterschoolSignin.query.filter(*things_to_filter_by).all()
    
    def count_by_classes_for_student():
        num_times_that_student_joined_certain_class = db.session.query(          #starts a new SQLAlchemy query on the database session
            AfterschoolClass.afterschool_class_id,                               #This specifies that we want to retrieve the afterschool_class_id field from the AfterschoolClass table
            db.func.count(AfterschoolSignin.afterschool_class_id).label('class_count')  # Count the sign-ins
        ).join(
            AfterschoolSignin, AfterschoolSignin.afterschool_class_id == AfterschoolClass.afterschool_class_id
        ).filter(
            AfterschoolSignin.student_id == student_id  # Filter by the selected student
        ).group_by(
            AfterschoolClass.afterschool_class_id  # Group by the class ID
        ).filter(*things_to_filter_by).all()

        # Print the results
        for class_id, count in num_times_that_student_joined_certain_class:
            print(f"Class ID: {class_id}, Sign-in Count: {count}")
            
        return num_times_that_student_joined_certain_class
    
    def time_spent_for_student(student_id):
        time_spent = db.session.query(
                AfterschoolSignin.student_id,  # Student ID
                AfterschoolClass.afterschool_class_id,  # Class ID
                func.sum(
                    func.extract('epoch', 
                                func.coalesce(AfterschoolSignin.sign_out_time, AfterschoolSignin.sign_in_time + timedelta(minutes=60)) - AfterschoolSignin.sign_in_time)
                ).label('total_time')  # Sum the durations (in seconds)
                ).join(
                    AfterschoolClass, AfterschoolSignin.afterschool_class_id == AfterschoolClass.afterschool_class_id
                ).filter(
                    AfterschoolSignin.student_id == student_id  # Filter by selected student
                ).group_by(
                    AfterschoolSignin.student_id,  # Group by student
                    AfterschoolClass.afterschool_class_id  # Group by class ID
                ).filter(*things_to_filter_by).all()

        return time_spent
    
    def count_by_class():
        num_times_that_anyone_joined_certain_class = db.session.query(          #starts a new SQLAlchemy query on the database session
            AfterschoolClass.afterschool_class_id,                               #This specifies that we want to retrieve the afterschool_class_id field from the AfterschoolClass table
            db.func.count(AfterschoolSignin.afterschool_class_id).label('class_count')  # Count the sign-ins
        ).join(
            AfterschoolSignin, AfterschoolSignin.afterschool_class_id == AfterschoolClass.afterschool_class_id
        ).group_by(
            AfterschoolClass.afterschool_class_id  # Group by the class ID
        ).filter(*things_to_filter_by).all()

        # Print the results
        for class_id, count in num_times_that_anyone_joined_certain_class:
            print(f"Class ID: {class_id}, Sign-in Count: {count}")
            
        return num_times_that_anyone_joined_certain_class
    
    def time_spent_for_all():
        time_spent = db.session.query(
                AfterschoolClass.afterschool_class_id,  # Class ID
                func.sum(
                    func.extract('epoch', 
                                func.coalesce(AfterschoolSignin.sign_out_time, AfterschoolSignin.sign_in_time + timedelta(minutes=60)) - AfterschoolSignin.sign_in_time)
                ).label('total_time')  # Sum the durations (in seconds)
                ).join(
                    AfterschoolClass, AfterschoolSignin.afterschool_class_id == AfterschoolClass.afterschool_class_id
                ).group_by(
                    
                    AfterschoolClass.afterschool_class_id  # Group by class ID
                ).filter(*things_to_filter_by).all()
                
        return time_spent
    
    if student_id is not None:
        class_counter = count_by_classes_for_student()
    else:
        class_counter = count_by_class()
    
    if student_id is not None:
         time_spent = time_spent_for_student(student_id)
    else:
        time_spent = time_spent_for_all()
    
    return render_template("report.html", student = student, date = date, activity = activity, signins = signins, class_counter = class_counter, time_spent = time_spent)