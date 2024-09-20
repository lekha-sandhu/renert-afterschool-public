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

import re
from jinja2.utils import markupsafe
from flask_admin.model.template import EndpointLinkRowAction, LinkRowAction

from root import app,db,csrf,admin
from hgsc_utils.flask_admin.flask_admin_menu_separator import DividerMenu
from hgsc_utils.flask_admin.flask_admin_permission_mixin import RenertAdminPermissionMixin

# Hack for changed API in Jinja2
Markup = markupsafe.Markup

