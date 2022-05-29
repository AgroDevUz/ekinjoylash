from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
class MicroBlogModelView(ModelView):
    
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))