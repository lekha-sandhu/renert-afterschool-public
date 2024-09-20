# Copyright (C) 2020-2023 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from flask_admin.menu import BaseMenu

"""
Add a line-separator in a Flask-Admin menu.

From: https://github.com/flask-admin/flask-admin/issues/1745#issuecomment-589110574

Typical Usage:
    admin.add_menu_item(DividerMenu(name='Divider'), target_category='CategoryName')

"""

class DividerMenu(BaseMenu):
    """
        Bootstrap Menu divider item
    """
    def __init__(self, name, class_name=None, icon_type=None, icon_value=None, target=None):
        super(DividerMenu, self).__init__(name, 'divider', icon_type, icon_value, target)

    def get_url(self):
        pass

    def is_visible(self):
        return True

