from models import *

class LoginForm(FlaskForm):
    login = StringField('Username or Email', [DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember')