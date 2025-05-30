# Copyright (C) 2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from sqlalchemy import text,Computed
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

    # "Computed" is postgres' "GENERATED ALWAYS AS" - an auto-generated column,
    # truncating the sign-in timestamp to date (for quicker indexing and querying)
    sign_in_date_cache = db.Column(db.Date,Computed(text("sign_in_time")),nullable=False,index=True)

    preenrolled = db.Column(db.Boolean, nullable = False, default = False)
    
    __table_args__ = (
        ## Sign-out time must be AFTER sign-in time
        db.CheckConstraint(text("""
         (sign_out_time is NULL)
         or
         (sign_in_time < sign_out_time)
        """), name="afterschool_sign_out_time_check"),

        ## Sign-in time and Sign-out time must be on the SAME DATE
        db.CheckConstraint(text("""
         (sign_out_time is NULL)
         or
         (date(sign_in_time) = date(sign_out_time))
        """), name="afterschool_sign_in_out_same_date"),

        # This is Postgres' "PARTIAL INDEX" (an INDEX with a WHERE-clause).
        # Because the index is UNIQUE, it will prevent creating duplicated records
        # of the same (student-id + class-id + date) if the "sign-out-time" is NULL -
        # Effectively preventing a student from being signed-in to the same class multiple times
        # without being signed-out first.
        #
        # NOTE: this does not prevent a student from being signed-in to DIFFERENT classes at the same time.
        #
        # create unique index
        #     idx_single_signin_per_class
        #     on afterschool_signins(student_id, afterschool_class_id, sign_in_date_cache)
        #     where sign_out_time is null ;
        db.Index('idx_single_signin_per_class', student_id, afterschool_class_id, sign_in_date_cache,
                 unique=True,
                 postgresql_where=text("sign_out_time is NULL")),
    )


    def __repr__(self):
        return f"Afterschool-Signin<id: {self.afterschool_signin_id}>"
