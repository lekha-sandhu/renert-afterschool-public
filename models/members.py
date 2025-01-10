# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from flask_login import UserMixin
from sqlalchemy import Index
from pprint import pprint

from root import db
import global_settings

from hgsc_utils.sqla.dictable import Dictable
from models.login_users import LoginUser

class Member(UserMixin, db.Model, Dictable):
    ## HACK ALERT:
    ## THis is not the complete "Member" class from other projects,
    ## it is a minimal one just to keep GoogleAuth/LoginUser working
    ## in the Library project.
    __tablename__ = 'members'

    member_internal_id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, nullable=False, unique=True)
    last_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String,nullable=False)
    nickname = db.Column(db.String)

    grade = db.Column(db.Enum('1',
                              '2',
                              '3',
                              '4',
                              '5',
                              '6',
                              '7',
                              '8',
                              '9',
                              '10',
                              '11',
                              '12',
                              'K',
                              'Staff',
                              'JK',
                              'Volunteers',
                              name='member_grade'),
                      nullable=False)

    online = db.Column(db.Boolean,nullable=False,default=False)

    login_user_id = db.Column(db.Integer,
                                  db.ForeignKey("login_users.login_user_id"))

    active = db.Column(db.Boolean,nullable=False,default=True)

    # Global/Alberta Student ID ?
    school_udid = db.Column(db.Integer, unique=True)

    pronoun = db.Column(db.Enum('M',
                              'F',
                              'T',
                              name='pronouns'),
                        nullable=True)

    def __init__(self):
        pass

    @property
    def id(self):
        return self.member_internal_id

    def get_id(self):
        return self.member_internal_id

    @property
    def division(self):
        g = self.grade
        if g == 'K':
            return 'K'
        elif g in ['1','2','3']:
            return '1'
        elif g in ['4','5','6']:
            return '2'
        elif g in ['7','8','9']:
            return '3'
        elif g in ['10','11','12']:
            return '4'
        else:
            raise RuntimeError("should not happen")

    @property
    def is_student(self):
        # NOTE: "JK" is not considered part of the school (yet)
        return self.grade in ['K','1','2','3','4','5','6','7','8','9','10','11','12']

    @property
    def is_active_student(self):
        return self.active and self.is_student

    @property
    def is_staff(self):
        return self.grade == "Staff"

    @property
    def is_volunteer(self):
        return self.grade == "Volunteers"

    @property
    def display_name(self):
        s = self.first_name
        if self.nickname:
            s += " (" + self.nickname + ")"
        s += " " + self.last_name
        return s

    @property
    def common_name(self):
        if self.nickname:
            return self.nickname
        return self.first_name

    @property
    def reverse_display_name(self):
        s = self.last_name + ", " + self.first_name
        if self.nickname:
            s += " (" + self.nickname + ")"
        return s


    @property
    def abbr_name(self):
        return self.first_name + " " + \
               self.last_name[0] + "."

    @property
    def display_name_grade(self):
        s = self.last_name + ", " + self.first_name + " "
        if self.nickname:
            s += "(" + self.nickname + ") "
        if self.is_staff:
            s += "(Staff)"
        elif self.is_volunteer:
            s += "(Volunteer)"
        else:
            s += "(Gr. " + self.grade + ")"
        return s

    def __str__(self):
        return self.display_name_grade

    def __repr__(self):
        return "Member(internal-id: %d  school-id: %d  name: %s %s)" % \
            (self.member_internal_id,self.school_id,self.first_name,self.last_name)
