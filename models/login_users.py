# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from pprint import pprint
from datetime import datetime
from flask import g
from flask_login import UserMixin

from models.permissions import Permission

from root import db

class LoginUser(UserMixin, db.Model):
    __tablename__ = 'login_users'

    login_user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String,nullable=False,unique=True)
    name = db.Column(db.String)
    given_name = db.Column(db.String)
    family_name = db.Column(db.String)
    hd = db.Column(db.String)
    picture_url = db.Column(db.String)
    unique_id = db.Column(db.String)
    last_login_time = db.Column(db.DateTime,default=datetime.utcnow)

    ## ORM many-to-many connection using a secondary table.
    roles = db.relationship(
        "Role",
        secondary="login_users_to_roles")

    def __init__(self, email):
        self.email = email

    def update_from_google_auth_json(self,resp_json):
        """
        Whenever we get a valid login from google, it's possible the user
        changed his/her details - so update them.
        """
        self.name = resp_json["name"]
        self.family_name = resp_json["family_name"]
        self.given_name = resp_json["given_name"]
        self.picture_url = resp_json["picture"]
        self.unique_id = resp_json["sub"]
        self.hd = resp_json["hd"]
        self.last_login_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


    @property
    def id(self):
        return self.login_user_id

    def get_id(self):
        return self.login_user_id

    @property
    def first_name(self):
        return self.given_name

    @property
    def last_name(self):
        return self.family_name

    def get_permissions(self):
        # Load current permissions in session's global variable.
        if 'current_user_permissions' in g:
            return g.current_user_permissions

        sql="""select
                  distinct p.name
               from
                  permissions P,
                  roles_to_permissions RP,
                  login_users_to_roles UR
               where
                  P.permission_id = RP.permission_id
                 AND
                  RP.role_id = UR.role_id
                 AND
                  UR.login_user_id = :user"""

        x = db.session.execute( db.text(sql), { "user": self.id })
        x = set([x[0] for x in x])
        # Store current permissions in session's global variable.
        g.current_user_permissions = x
        return x

    def has_permission_name(self,permission_name):
        x = self.get_permissions()
        return permission_name in x

    @property
    def perm_internal_editor(self):
        return self.has_permission_name("reportcards_editor")

    @property
    def perm_external_editor(self):
        return self.has_permission_name("reportcards_external_review")

    @property
    def perm_impersonate(self):
        return self.has_permission_name("impersonate")

    @property
    def perm_debug(self):
        return self.has_permission_name("debug")

    @property
    def perm_db_admin(self):
        return self.has_permission_name("database_admin")


    def __str__(self):
        return "%s (Login-User-ID: %s)" % (self.email, self.login_user_id)
