# Copyright (C) 2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from sqlalchemy import text
from root import db
from hgsc_utils.sqla.timestamp_mixin import TimestampMixin

class AfterschoolClass(db.Model, TimestampMixin):
    __tablename__ = "afterschool_classes"

    afterschool_class_id = db.Column(db.Integer, primary_key=True)

    active = db.Column(db.Boolean, nullable=False, default=True, server_default=text('true'))

    # HACK ALERT: fix this ugliness. Since it is currently unused, set it to 99 so it won't
    # match any valid years in other database (don't you just love Y2K-style magic numbers?)
    school_year_id = db.Column(db.Integer, nullable=False, default=99, server_default=text('99'))

    activity = db.Column(db.String, nullable=False)

    room = db.Column(db.String,nullable=False)

    # TODO: normalize to classes-to-teachers table?
    instructor_id = db.Column(db.Integer, db.ForeignKey('library_students.id'), nullable=False)
    instructor = db.Relationship('Student')

    # Comma-separated list of grades (case-sensitive),
    # e.g. "K,4,5,9"
    grades = db.Column(db.String,nullable=False)

    # TODO: normalize to classes-to-day-and-times table?
    # Comma-separated list of abbreviated weekdays (case-sensitive),
    # e.g. "Mon,Wed,Thu"
    weekdays = db.Column(db.String,nullable=False)

    start_time = db.Column(db.Time,nullable=False)
    end_time = db.Column(db.Time,nullable=False)

    __table_args__ = (
        db.CheckConstraint(text("""
         (start_time < end_time)
        """), name="afterschool_class_time_check"),

        db.CheckConstraint(text("""
         grades ~ '^(K|Staff|1|2|3|4|5|6|7|8|9|10|11|12)(,(K|Staff|1|2|3|4|5|6|7|8|9|10|11|12))*$'
        """), name="afterschool_class_grades_check"),

        db.CheckConstraint(text("""
         weekdays ~ '^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)(,(Mon|Tue|Wed|Thu|Fri|Sat|Sun))*$'
        """), name="afterschool_class_weekdays_check"),
    )


    def __repr__(self):
        return f"Afterschool-Class<id: {self.afterschool_class_id}, activity: {self.activity}>"
