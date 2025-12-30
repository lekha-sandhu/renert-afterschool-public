from sqlalchemy import text,Computed,func
from sqlalchemy.dialects.postgresql import ExcludeConstraint


from hgsc_utils.sqla.timestamp_mixin import TimestampMixin
from root import db


class AfterschoolEnrollment(db.Model, TimestampMixin):
    __tablename__ = "afterschool_enrollments"

    afterschool_enrollment_id = db.Column(db.Integer, primary_key=True)

    afterschool_class_id = db.Column(db.Integer,db.ForeignKey('afterschool_classes.afterschool_class_id'),nullable=False)
    afterschool_class = db.Relationship('AfterschoolClass')

    student_id = db.Column(db.Integer, db.ForeignKey('library_students.id'), nullable=False)
    student = db.Relationship('Student')

    start_date = db.Column(db.DATE,nullable=False)
    end_date = db.Column(db.DATE,nullable=True)


    __table_args__ = (
        ## This beauty is an EXCLUDE constraint that prevents the same student_id,
        ## afterschool_class_id, in overlapping dates.
        ##
        ## The equilvanent SQL command is:
        ##
        ##    ALTER TABLE afterschool_enrollments
        ##       ADD CONSTRAINT no_overlapping_enrollments
        ##       EXCLUDE USING gist (
        ##          student_id WITH =,
        ##          afterschool_class_id WITH =,
        ##          daterange(start_date, COALESCE(end_date, 'infinity'::date), '[]') WITH &&
        ##       );
        ##
        ## Don't forget to enable gist/btree first (just once):
        ##
        ##     CREATE EXTENSION IF NOT EXISTS btree_gist;
        ExcludeConstraint(
            (student_id, '='),
            (afterschool_class_id, '='),
            (func.daterange(start_date, func.coalesce(end_date, 'infinity'), '[]'), '&&'),
            name='no_overlapping_enrollments',
            using='gist'
        ),
    )

    def __repr__(self):
        return f"Afterschool-Enrollment<id: {self.afterschool_enrollment_id}>"
