# Copyright (C) 2020-2023 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from flask import redirect,url_for,request
from flask_login import current_user, login_user


class RenertAdminPermissionMixin(object):
    needed_permission = "database_admin"

    def is_accessible(self):
        return current_user and \
               current_user.is_authenticated and \
               current_user.has_permission_name(self.needed_permission)

    def inaccessible_callback(self, name, **kwargs):
        if current_user and current_user.is_authenticated:
            # User already authenticated, but doesn't have
            # the needed role/permissions
            return "Your account (%s) is not authorized to access this page (%s)" \
                % ( current_user.email, self.needed_permission)
        else:
            # redirect to login page if user doesn't have access
            return redirect(url_for('login', next=request.url))
