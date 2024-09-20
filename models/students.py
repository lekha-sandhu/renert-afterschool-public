# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from root import db
from hgsc_utils.sqla.dictable import Dictable
from datetime import datetime as dt, timedelta
from hgsc_utils.sqla.timestamp_mixin import TimestampMixin

class Student(db.Model, Dictable, TimestampMixin):
    """
    NOTE: These are not just students, but ALL school members (incl. staff)
    """
    __tablename__ = "library_students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    homeroom = db.Column(db.String)
    teacher_email = db.Column(db.String)
    student_email = db.Column(db.String)
    parent_email_1 = db.Column(db.String)
    parent_email_2 = db.Column(db.String)
    grade = db.Column(db.String)

    school_cafe_id = db.Column(db.Integer)
    photo_filename = db.Column(db.String)
    teacher_name = db.Column(db.String)

    def __str__(self):
        return f"{self.name} (Grade {self.grade})"
