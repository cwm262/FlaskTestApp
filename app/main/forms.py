from flask.ext.wtf import Form
from wtforms.fields import PasswordField, StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, DataRequired, optional, Length, EqualTo


class LoginForm(Form):
    username = StringField('Username: ', validators=[DataRequired('Please enter your username.')])
    password = PasswordField('Password: ', validators=[DataRequired('Please enter your password.')])
    submit = SubmitField('Login')


class PointsForm(Form):
    noCallNoShow = BooleanField('No Call, No Show [3 points]', validators=[optional()])
    leaveEarly = BooleanField('Left Early w/o Permission [2 points]', validators=[optional()])
    callInNoNote = BooleanField('Called-In w/o Doc Note [2 points]', validators=[optional()])
    drawerOff = BooleanField('Drawer Off by 1% or $5 [2 points]', validators=[optional()])
    notDoing = BooleanField('Not Doing as Instructed [1.5 points]', validators=[optional()])
    lateNoCall = BooleanField('Late w/ No Call [1 point]', validators=[optional()])
    eatBehind = BooleanField('Eating Behind Counter [1 point]', validators=[optional()])
    extendedBreak = BooleanField('Taking Extended Breaks [1 point]', validators=[optional()])
    outOfUniform = BooleanField('Out of Uniform [1 point', validators=[optional()])
    cellPhone = BooleanField('Cell Phone Use [1 point]', validators=[optional()])
    headPhone = BooleanField('Headphone Use [1 point]', validators=[optional()])
    callInWNotice = BooleanField('Called-In w/ Prior Notice [.5 point]', validators=[optional()])
    missedMeeting = BooleanField('Missed Employee Meeting [.5 point]', validators=[optional()])
    other = SelectField('Other', choices=[('', ''), ('.25', '.25 points'), ('.5', '.5 points'), ('.75', '.75 points'),
                                          ('1', '1 point'), ('1.5', '1.5 points'), ('2', '2 points'),
                                          ('2.5', '2.5 points'), ('3', '3 points')], validators=[optional()])
    warning = BooleanField('<strong>Is this a warning? [No points will be given if you check this box!]</strong>')
    whyField = StringField('Briefly (in < 140 characters) describe why you are giving points: ',
                           validators=[Length(min=3, max=140)])
    supervisorField = StringField("Are you giving points on behalf of a supervisor? If so, enter their pawprint: \
                                  (Otherwise, this will say your username)", validators=[Length(max=20), optional()])
    submit = SubmitField('Submit')


class PasswordChangeForm(Form):
    currentPassword = PasswordField('Current Password: ', validators=[DataRequired('You must enter your password.')])
    newPassword = PasswordField('New Password: ', validators=[InputRequired(), EqualTo('confirm',
                                                                                       message="Passwords must match")])
    confirm = PasswordField('Repeat Password: ')