
from sqlalchemy import text,Computed
from root import db
from hgsc_utils.sqla.timestamp_mixin import TimestampMixin

class AfterschoolEnrollment(db.Model, TimestampMixin):
    __tablename__ = "afterschool_enrollments"

    afterschool_enrollment_id = db.Column(db.Integer, primary_key=True)

    afterschool_class_id = db.Column(db.Integer,db.ForeignKey('afterschool_classes'),nullable=False)
    afterschool_class = db.Relationship('AfterschoolClass')

    student_id = db.Column(db.Integer, db.ForeignKey('library_students.id'), nullable=False)
    student = db.Relationship('Student')

    start_date = db.Column(db.DATE,nullable=False)
    end_date = db.Column(db.DATE,nullable=True)

    