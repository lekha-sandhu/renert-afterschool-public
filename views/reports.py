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
import pytz

@app.route("/pick_report")
def pick_report():
    all_students = Student.query.filter(Student.grade != 'Staff').all()
    activities = AfterschoolClass.query.all()
    
    return render_template("pick_report.html", student = all_students, activity = activities)


@app.route("/report/student/<int:student_id>")
def report_by_student(student_id):
    # Call your report() logic, but only for this student
    return report_with_params(student_id=student_id, activity_id=None)

@app.route("/report/activity/<int:activity_id>")
def report_by_activity(activity_id):
    # Call your report() logic, but only for this activity
    return report_with_params(student_id=None, activity_id=activity_id)

def report_with_params(student_id=None, activity_id=None):

    startdate = request.form.get("startdate")
    enddate = request.form.get("enddate")
    singlemonthcheck = request.form.get("singledatecheck")
    student = None
    activity = None
           
    if startdate == "":
        startdate = None

    if enddate == "":
        enddate = None

    if (startdate is not None):
            
        if(singlemonthcheck == "on"):
            date_list = startdate.split("-")
            month = int(date_list[1])
            year = int(date_list[0])
            last_days = [31, (29 if year % 4 == 0 else 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            day = last_days[month-1]

            start_date = datetime(year, month, 1, 0,0,0)
            end_date = datetime(year, month, day, 23,59,59)
        elif (enddate is None):
            start_date_list = startdate.split("-")
            start_month = int(start_date_list[1])
            start_year = int(start_date_list[0])

            end_month = datetime.today().month
            end_year = datetime.today().year
            end_day = datetime.today().day
            
            start_date = datetime(start_year, start_month, 1, 0,0,0)
            end_date = datetime(end_year, end_month, end_day, 23,59,59)
        else:
            start_date_list = startdate.split("-")
            start_month = int(start_date_list[1])
            start_year = int(start_date_list[0])

            end_date_list = enddate.split("-")
            end_month = int(end_date_list[1])
            end_year = int(end_date_list[0])
            end_last_days = [31, (29 if end_year % 4 == 0 else 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            end_day = end_last_days[end_month-1]
            
            start_date = datetime(start_year, start_month, 1, 0,0,0)
            end_date = datetime(end_year, end_month, end_day, 23,59,59)
    
    def filters():
        
        conditions = []
        student = None
        activity = None
    
        if student_id is not None:
            conditions.append(AfterschoolSignin.student_id == student_id)
            student = Student.query.filter(Student.id == student_id).all()
            student = student[0]
        
        if startdate is not None:
            conditions.append(AfterschoolSignin.sign_in_time >= start_date)
            conditions.append(AfterschoolSignin.sign_in_time <= end_date)
        
        if activity_id is not None:
            conditions.append(AfterschoolSignin.afterschool_class_id == activity_id)
            activity = AfterschoolClass.query.filter(AfterschoolClass.afterschool_class_id == activity_id).all()
            activity = activity[0]
            
        return conditions, student, activity
    
    things_to_filter_by, student, activity = filters()
    
    signins = AfterschoolSignin.query.filter(*things_to_filter_by).order_by(AfterschoolSignin.sign_in_time.asc()).all()

    for signin in signins:
        if signin.sign_in_time:
            signin.sign_in_time = signin.sign_in_time.astimezone(pytz.timezone('America/Edmonton'))
        if signin.sign_out_time:
            signin.sign_out_time = signin.sign_out_time.astimezone(pytz.timezone('America/Edmonton'))
    
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

    # First, get all class info we need for display
    class_info = {c.afterschool_class_id: c.activity for c in AfterschoolClass.query.all()}

    # Combine class_counter and time_spent into a single dict
    combined_data = {}

    # Add sign-in counts
    for class_id, count in class_counter:
        combined_data[class_id] = {
            "count": count,
            "time": 0  # default to 0 in case no time recorded
        }

    # Add time data
    for row in time_spent:
        if len(row) == 3:
            _, class_id, total_time = row
        elif len(row) == 2:
            class_id, total_time = row
        else:
            continue

        if class_id not in combined_data:
            combined_data[class_id] = {"count": 0, "time": total_time}
        else:
            combined_data[class_id]["time"] = total_time

    # Add activity names
    for class_id in combined_data:
        combined_data[class_id]["name"] = class_info.get(class_id, "Unknown")

    return render_template(
        "report.html",
        student=student,
        startdate=startdate,
        enddate=enddate,
        activity=activity,
        signins=signins,
        combined_data=combined_data
    )
    pass

@app.route("/report", methods = ["POST"])
def report():
    student_id = request.form.get("student")
    startdate = request.form.get("startdate")
    enddate = request.form.get("enddate")
    singlemonthcheck = request.form.get("singledatecheck")
    activity_id = request.form.get("activity")
    student = None
    activity = None
        
    if student_id == "":
        student_id = None
        
    if activity_id == "":
        activity_id = None
           
    if startdate == "":
        startdate = None

    if enddate == "":
        enddate = None

    if (startdate is not None):
            
        if(singlemonthcheck == "on"):
            date_list = startdate.split("-")
            month = int(date_list[1])
            year = int(date_list[0])
            last_days = [31, (29 if year % 4 == 0 else 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            day = last_days[month-1]

            start_date = datetime(year, month, 1, 0,0,0)
            end_date = datetime(year, month, day, 23,59,59)
        elif (enddate is None):
            start_date_list = startdate.split("-")
            start_month = int(start_date_list[1])
            start_year = int(start_date_list[0])

            end_month = datetime.today().month
            end_year = datetime.today().year
            end_day = datetime.today().day
            
            start_date = datetime(start_year, start_month, 1, 0,0,0)
            end_date = datetime(end_year, end_month, end_day, 23,59,59)
        else:
            start_date_list = startdate.split("-")
            start_month = int(start_date_list[1])
            start_year = int(start_date_list[0])

            end_date_list = enddate.split("-")
            end_month = int(end_date_list[1])
            end_year = int(end_date_list[0])
            end_last_days = [31, (29 if end_year % 4 == 0 else 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            end_day = end_last_days[end_month-1]
            
            start_date = datetime(start_year, start_month, 1, 0,0,0)
            end_date = datetime(end_year, end_month, end_day, 23,59,59)
    
    def filters():
        
        conditions = []
        student = None
        activity = None
    
        if student_id is not None:
            conditions.append(AfterschoolSignin.student_id == student_id)
            student = Student.query.filter(Student.id == student_id).all()
            student = student[0]
        
        if startdate is not None:
            conditions.append(AfterschoolSignin.sign_in_time >= start_date)
            conditions.append(AfterschoolSignin.sign_in_time <= end_date)
        
        if activity_id is not None:
            conditions.append(AfterschoolSignin.afterschool_class_id == activity_id)
            activity = AfterschoolClass.query.filter(AfterschoolClass.afterschool_class_id == activity_id).all()
            activity = activity[0]
            
        return conditions, student, activity
    
    things_to_filter_by, student, activity = filters()
    
    signins = AfterschoolSignin.query.filter(*things_to_filter_by).order_by(AfterschoolSignin.sign_in_time.asc()).all()

    for signin in signins:
        if signin.sign_in_time:
            signin.sign_in_time = signin.sign_in_time.astimezone(pytz.timezone('America/Edmonton'))
        if signin.sign_out_time:
            signin.sign_out_time = signin.sign_out_time.astimezone(pytz.timezone('America/Edmonton'))
    
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

    # First, get all class info we need for display
    class_info = {c.afterschool_class_id: c.activity for c in AfterschoolClass.query.all()}

    # Combine class_counter and time_spent into a single dict
    combined_data = {}

    # Add sign-in counts
    for class_id, count in class_counter:
        combined_data[class_id] = {
            "count": count,
            "time": 0  # default to 0 in case no time recorded
        }

    # Add time data
    for row in time_spent:
        if len(row) == 3:
            _, class_id, total_time = row
        elif len(row) == 2:
            class_id, total_time = row
        else:
            continue

        if class_id not in combined_data:
            combined_data[class_id] = {"count": 0, "time": total_time}
        else:
            combined_data[class_id]["time"] = total_time

    # Add activity names
    for class_id in combined_data:
        combined_data[class_id]["name"] = class_info.get(class_id, "Unknown")

    return render_template(
        "report.html",
        student=student,
        startdate=startdate,
        enddate=enddate,
        activity=activity,
        signins=signins,
        combined_data=combined_data,
        singlemonthcheck = singlemonthcheck
    )