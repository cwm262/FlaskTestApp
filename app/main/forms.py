from flask.ext.wtf import Form
from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(Form):
    username = StringField('Username: ', validators=[DataRequired('Please enter your username.')])
    password = PasswordField('Password: ', validators=[DataRequired('Please enter your password.')])
    submit = SubmitField('Login')