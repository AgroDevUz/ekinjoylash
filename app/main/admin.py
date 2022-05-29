from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
from flask_admin.contrib import geoa

class MicroBlogModelView(ModelView):
    column_exclude_list = ['password']
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))
class GeoModelView(geoa.ModelView):
    column_exclude_list = ['geometry']
    # form_widget_args = {'geometry': {'data-height': 400, 'data-width': 400}}
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))