# Copyright (C) 2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from sqlalchemy import text
from root import db
from hgsc_utils.sqla.timestamp_mixin import TimestampMixin

class AfterschoolSignin(db.Model, TimestampMixin):
    __tablename__ = "afterschool_signins"

    afterschool_signin_id = db.Column(db.Integer, primary_key=True)
    
    afterschool_class_id = db.Column(db.Integer,db.ForeignKey('afterschool_classes'),nullable=False)
    afterschool_class = db.Relationship('AfterschoolClass')

    student_id = db.Column(db.Integer, db.ForeignKey('library_students.id'), nullable=False)
    student = db.Relationship('Student')

    sign_in_time = db.Column(db.TIMESTAMP(timezone=True),nullable=False)
    sign_out_time = db.Column(db.TIMESTAMP(timezone=True),nullable=True)

    __table_args__ = (
        db.CheckConstraint(text("""
         (sign_out_time is NULL)
         or
         (sign_in_time < sign_out_time)
        """), name="afterschool_sign_out_time_check"),
    )


    def __repr__(self):
        return f"Afterschool-Signin<id: {self.afterschool_signin_id}>"

    
