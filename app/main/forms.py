from flask.ext.wtf import Form
from wtforms.fields import PasswordField, StringField
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    username = StringField('email', validators=[DataRequired('Please enter your username.')])

    password = PasswordField('password', validators=[DataRequired('Please enter your password.')])