# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from flask import abort, current_app
from flask_login import current_user
from functools import wraps

from root import db

class Permission(db.Model):
    __tablename__ = 'permissions'

    permission_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    description = db.Column(db.String)

    def __str__(self):
        return self.name + " (id: " + str(self.permission_id) + ")"

    def __repr__(self):
        return "Permission(id: %d  name: %s)" % \
            (self.permission_id,self.name)



class Role(db.Model):
    __tablename__ = 'roles'

    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    description = db.Column(db.String)

    ## ORM many-to-many connection using a secondary table.
    permissions = db.relationship(
        "Permission",
        secondary="roles_to_permissions")

    def __str__(self):
        return self.name + " (id: " + str(self.role_id) + ")"

    def __repr__(self):
        return "Role(id: %d  name: %s)" % \
            (self.role_id,self.name)



class RoleToPermission(db.Model):
    """
    Many-to-many connection table roles<->permissions
    """
    __tablename__ = 'roles_to_permissions'

    id = db.Column(db.Integer, primary_key=True)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.permission_id"), nullable=False)

    ## ORM Relations
    #role = db.relationship("Role")
    #permission = db.relationship("Permission")

    def __repr__(self):
        return "RoletoPermission(id: %d  role-id: %d permission-id: %d)" % \
            (self.id,self.role_id, self.permission_id)



class LoginUserToRole(db.Model):
    """
    Many-to-many connection table users <-> roles
    """
    __tablename__ = 'login_users_to_roles'

    id = db.Column(db.Integer, primary_key=True)

    login_user_id = db.Column(db.Integer, db.ForeignKey("login_users.login_user_id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)

    ## ORM Relations
    #login_user = db.relationship("LoginUser")
    #role = db.relationship("Role")

    def __repr__(self):
        return "UserToRole(id: %d  login-user-id: %d role-id: %d)" % \
            (self.id,self.login_user_id, self.role_id)





def permission_required(permission_name):
    """
    A decorator that accepts an argument.
    see: https://stackoverflow.com/a/10176276

    Use it like so:

        from models.permissions import permission_required

        @app.route('/')
        @login_required
        @permission_required("my_permission_name")
        def protected_content():
            pass

    """
    def permission_required_decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # Assume the user is already logged in (with @login_required ).
            # so don't repeat the checks.
            perms = current_user.get_permissions()
            if not (permission_name in perms):
                current_app.logger.debug("user %s (id %d) does not have permission '%s'" % \
                                         (current_user.email, current_user.id, permission_name))
                abort(403)

            return func(*args, **kwargs)
        return decorated_view
    return permission_required_decorator
