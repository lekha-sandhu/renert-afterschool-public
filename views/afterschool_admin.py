# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from flask import request,redirect,url_for,abort,flash
from flask_login import current_user, login_user
from pprint import pprint,pformat
from flask_admin import form as flask_admin_form
from flask_admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.contrib.sqla import filters
from flask_admin.contrib.sqla.filters import BaseSQLAFilter, FilterEqual
from flask_admin import BaseView, expose
from sqlalchemy import and_, or_
from markupsafe import Markup

import re
from jinja2.utils import markupsafe
from flask_admin.model.template import EndpointLinkRowAction, LinkRowAction

from root import app,db,csrf,admin
from hgsc_utils.flask_admin.flask_admin_menu_separator import DividerMenu
from hgsc_utils.flask_admin.flask_admin_permission_mixin import RenertAdminPermissionMixin

from models.afterschool_classes import AfterschoolClass
from models.afterschool_signins import AfterschoolSignin
from models.afterschool_enrollment import AfterschoolEnrollment

def _format_datetime(dt):
    return dt.strftime("%Y-%m-%d if  %I:%M:%S %p").replace(" 0", " ") if dt else None

def _format_date(dt):
    return dt.strftime("%Y-%m-%d") if dt else None

def _format_time(dt):
    return dt.strftime("%I:%M:%S %p").lstrip("0") if dt else None

def _format_afterschool_class(ac):
    return Markup(f'<a href="/admin/afterschoolclass/?search={(ac.activity + " " + ac.room).replace(" ", "+")}">{ac.activity} ({ac.room})</a>')

class AfterschoolAdminPermissionMixin(RenertAdminPermissionMixin):
    needed_permission = "afterschool_admin"


class AfterschoolClassesView(AfterschoolAdminPermissionMixin,ModelView):
    can_create = True
    can_delete = False
    can_edit = True
    can_export = True

    column_sortable_list = [
        'activity',
        'room',
        'instructor.name',
        'grades',
        'weekdays',
        'start_time',
        'end_time',
        'active'
    ]
    column_list = [
        'activity',
        'room',
        'instructor.name',
        'grades',
        'weekdays',
        'start_time',
        'end_time',
        'active'
    ]

    column_searchable_list = [
        'activity',
        'room',
        'instructor.name',
        'grades',
        'weekdays',
        'start_time',
        'end_time',
    ]

    column_formatters = {
        'start_time': lambda v,c,m,n: _format_time(m.start_time),
        'end_time': lambda v,c,m,n: _format_time(m.end_time)
    }

    column_labels = {
    }

    column_filters = [
        'activity',
        'room',
        'instructor.name',
        'grades',
        'weekdays',
        'start_time',
        'end_time',
        'active'
    ]

    column_default_sort = [
        ("updated_at",True),
        ("created_at",True),
    ]



class AfterschoolSigninsView(AfterschoolAdminPermissionMixin,ModelView):
    can_create = False
    can_delete = False
    can_edit = True
    can_export = True

    column_searchable_list = [
        'student.name',
        'afterschool_class.activity',
    ]

    column_filters = [
        'afterschool_class',
        'student',
        'sign_in_time',
        'sign_out_time',
        'sign_in_date_cache'
    ]

    column_formatters = {
        'afterschool_class': lambda v,c,m,n: _format_afterschool_class(m.afterschool_class),
        'sign_in_time': lambda v,c,m,n: _format_datetime(m.sign_in_time),
        'sign_out_time': lambda v,c,m,n: _format_datetime(m.sign_out_time)
    }

    column_exclude_list = [
        "created_at",
        "updated_at",
        "sign_in_date_cache",
    ]

    column_default_sort = [
        ("updated_at",True),
        ("created_at",True),
    ]

class AfterschoolEnrollmentView(AfterschoolAdminPermissionMixin,ModelView):
    can_create = True
    can_delete = False
    can_edit = True
    can_export = True

    column_searchable_list = [
        'student.name',
        'afterschool_class.activity',
    ]

    column_filters = [
        'afterschool_class',
        'student',
        'start_date',
        'end_date'
    ]

    column_formatters = {
        'afterschool_class': lambda v,c,m,n: _format_afterschool_class(m.afterschool_class),
        'start_date': lambda v,c,m,n: _format_date(m.start_date),
        'end_date': lambda v,c,m,n: _format_date(m.end_date)
    }

    column_exclude_list = [
        "created_at",
        "updated_at",
    ]

    column_default_sort = [
        ("updated_at",True),
        ("created_at",True),
    ]

admin.add_view(AfterschoolClassesView(AfterschoolClass, db.session, name="AfterSchool Classes",category="Afterschool"))
admin.add_view(AfterschoolSigninsView(AfterschoolSignin, db.session, name="AfterSchool Sign-ins",category="Afterschool"))
admin.add_view(AfterschoolEnrollmentView(AfterschoolEnrollment, db.session, name="AfterSchool Enrollment",category="Afterschool"))