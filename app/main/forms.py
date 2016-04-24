from flask.ext.wtf import Form
from wtforms.fields import PasswordField, StringField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, DataRequired, optional, Length, EqualTo


class LoginForm(Form):
    username = StringField('Username: ', validators=[DataRequired('Please enter your username.')])
    password = PasswordField('Password: ', validators=[DataRequired('Please enter your password.')])
    submit = SubmitField('Login')


class PointsForm(Form):
    pointsField = SelectField('Misbehavior', validators=[DataRequired()], coerce=int)
    customAmountField = SelectField('Customize the amount of points: If you leave this blank, the default amount will\
                                    be given', choices=[('', ''), ('.25', '.25 points'), ('.5', '.5 points'),
                                                        ('.75', '.75 points'), ('1', '1 point'),
                                                        ('1.5', '1.5 points'), ('2', '2 points'), ('2.5', '2.5 points'),
                                                        ('3', '3 points')], validators=[optional()])
    whenField = DateField('When did this occur?', format='%Y-%m-%d', validators=[DataRequired()])
    warning = BooleanField('<strong>Is this a warning? [No points will be given if you check this box!]</strong>')
    whyField = StringField('Briefly (in < 140 characters) describe why you are giving points: ',
                           validators=[Length(min=3, max=140)])
    supervisorField = StringField("Are you giving points on behalf of a supervisor? If so, enter their pawprint: \
                                  (Otherwise, this will say your username)", validators=[Length(max=20), optional()])
    submit = SubmitField('Submit')


class PasswordChangeForm(Form):
    currentPassword = PasswordField('Current Password: ', validators=[DataRequired('You must enter your password.')])
    newPassword = PasswordField('New Password: ', validators=[InputRequired(), Length(min=8, max=40),
                                                              EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Repeat Password: ')
    submit = SubmitField('Submit')


class AddStudentForm(Form):
    pawprintField = StringField('Student Pawprint: ', validators=[DataRequired('Please enter their pawprint.')])
    firstNameField = StringField('Student First Name: ', validators=[DataRequired('Please enter their first name.')])
    lastNameField = StringField('Student Last Name: ', validators=[DataRequired('Please enter their last name.')])
    submit = SubmitField('Submit')
