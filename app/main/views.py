import collections
from flask import render_template, flash, redirect, url_for, abort, json
from flask.ext.login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import User, Student, Point, Warn, InfractionType, PointsRemovedHistory
from .forms import LoginForm, PointsForm, PasswordChangeForm, AddStudentForm, RemoveStudentForm, SearchPointsForm, RewardForm
from . import main
from .. import login_manager, db, mail
from config import RESULTS_PER_PAGE
from config import DevelopmentConfig
import datetime
from sqlalchemy import or_
from itsdangerous import URLSafeSerializer
from flask_mail import Message


@main.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@main.route('/acknowledge/<token>')
def confirm_punish(token):
    try:
        point = confirm_token(token)
        if point:
            point.acknowledged = True
            db.session.commit()
            flash("Thank you for acknowledging your points.", "success")
    except:
        flash("The acknowledgement link is invalid or has expired.", "danger")
    return render_template("ack.html")


@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        if user:
            approved = user.approved
            if not approved:
                error = "You do not have access to this application."
                return render_template("login.html", form=form, error=error)
            pwhash = user.password
            password = form.password.data
            if check_password_hash(pwhash, password):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('.index'))
            else:
                error = "Your password is incorrect. Please try again."
        else:
            error = "Sorry. " + form.username.data + " is not a valid username."
    return render_template("login.html", form=form, error=error)


@main.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('.login'))


@main.route('/students')
def studentlist():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    students = Student.query.filter_by(active=True).order_by(Student.lname)
    return render_template("studentlist.html", students=students)


@main.route('/students/<pawprint>', methods=['GET', 'POST'])
def student(pawprint):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    student = Student.query.filter_by(pawprint=pawprint, active=True).first()
    if student is None:
        abort(404)
    now = datetime.datetime.today()
    return render_template('student.html', student=student, time=now)


@main.route('/students/<pawprint>/give-points', methods=['GET', 'POST'])
def givepointspage(pawprint):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    student = Student.query.filter_by(pawprint=pawprint, active=True).first()
    if student is None:
        abort(404)
    form = PointsForm()
    infractiontypes = InfractionType.query.all()
    infraction_names = []
    for infraction in infractiontypes:
        infraction_names.append(infraction.description)
    infraction_choices = list(enumerate(infraction_names, 1))
    form.pointsField.choices = infraction_choices
    if form.validate_on_submit():
        try:
            do_punish(form, pawprint, student)
            return redirect(url_for('.student', pawprint=pawprint))
        except Exception as e:
            abort(500)
    now = datetime.datetime.today()
    return render_template('doPunish.html', student=student, time=now, form=form)


@main.route('/students/<pawprint>/remove-points', methods=['GET', 'POST'])
def rewardpage(pawprint):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    student = Student.query.filter_by(pawprint=pawprint, active=True).first()
    if student is None:
        abort(404)
    form = RewardForm()
    if form.validate_on_submit():
        try:
            point_total = student.pointTotal
            points_to_remove = float(form.removePointsField.data)
            new_point_total = point_total - points_to_remove
            if new_point_total < 0:
                flash("You can not lower a student's point total into the negatives.", "warning")
            else:
                now = datetime.datetime.today()
                new_point_removal_log_entry = PointsRemovedHistory(points_to_remove, form.whyField.data,
                                                                   now, current_user.username, pawprint)
                db.session.add(new_point_removal_log_entry)
                student.pointTotal = new_point_total
                db.session.commit()
                flash("Points removed.", 'success')
            return redirect(url_for('.student', pawprint=pawprint))
        except Exception as e:
            abort(500)
    return render_template('doReward.html', student=student, form=form)


@main.route('/profile/<username>')
def profile(username):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    if username != current_user.username:
        return redirect(url_for('.index'))
    user = User.query.get(username)
    return render_template('profile.html', user=user)


@main.route('/profile/<username>/password-change', methods=['GET', 'POST'])
def change_password(username):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    if username != current_user.username:
        return redirect(url_for('.index'))
    user = User.query.get(username)
    form = PasswordChangeForm()
    if form.validate_on_submit():
        try:
            if check_password_hash(user.password, form.currentPassword.data):
                newPassword = generate_password_hash(form.confirm.data)
                user.password = newPassword
                db.session.commit()
            return redirect(url_for('.logout'))
        except Exception as e:
            abort(500)
    flash("You will be asked to login again if your password change is successful", 'danger')
    return render_template('passChange.html', user=user, form=form)


@main.route('/profile/<username>/add-student', methods=['GET', 'POST'])
def add_student(username):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    if username != current_user.username:
        return redirect(url_for('.index'))
    form = AddStudentForm()
    if form.validate_on_submit():
        try:
            pawprint = form.pawprintField.data
            student_to_be_added = Student.query.get(pawprint)
            if student_to_be_added:
                if student_to_be_added.active is False:
                    student_to_be_added.active = True
                    points = Point.query.filter_by(student_id=pawprint).all()
                    for point in points:
                        point.active = True
                    warns = Warn.query.filter_by(student_id=pawprint).all()
                    for warn in warns:
                        warn.active = True
                    db.session.commit()
                    flash("We found a student with that pawprint already in the system, but marked as inactive. We have reactivated this student.")
                else:
                    flash("Student is already in system and active. No action taken.")
            else:
                first_name = form.firstNameField.data
                last_name = form.lastNameField.data
                newStudent = Student(pawprint, first_name, last_name)
                db.session.add(newStudent)
                db.session.commit()
                flash("Student added successfully.", 'success')
            return redirect(url_for(".profile", username=current_user.username))
        except Exception as e:
            abort(500)
    return render_template('addStudent.html', form=form)


@main.route('/profile/<username>/remove-student', methods=['GET', 'POST'])
def remove_student(username):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    if username != current_user.username:
        return redirect(url_for('.index'))
    form = RemoveStudentForm()
    pawprints = db.session.query(Student.pawprint).all()
    p = []
    for pawprint in pawprints:
        p.append(pawprint.pawprint)
    p = json.dumps(p)
    if form.validate_on_submit():
        try:
            pawprint = form.pawprintField.data
            toDelete = Student.query.get(pawprint)
            if toDelete:
                points = Point.query.filter_by(student_id=pawprint).all()
                for point in points:
                    point.active = False
                warns = Warn.query.filter_by(student_id=pawprint).all()
                for warn in warns:
                    warn.active = False
                toDelete.active = False
                db.session.commit()
                flash("Student removed successfully.", 'success')
            else:
                flash("Could not find student. Please verify that pawprint is correct.", "warning")
            return redirect(url_for(".profile", username=current_user.username))
        except Exception as e:
            abort(500)
    return render_template('removeStudent.html', form=form, student_pawprints=p)


@main.route('/points', methods=['GET', 'POST'])
@main.route('/points/<int:page>', methods=['GET', 'POST'])
def points(page=1):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    points = Point.query.filter_by(active=True).order_by(Point.when.desc()).paginate(page, RESULTS_PER_PAGE, False)
    students = Student.query.filter_by(active=True).order_by(Student.lname)
    form = SearchPointsForm()
    if form.validate_on_submit():
        query = form.pointsSearchField.data
        results = Point.query.filter(or_(Point.why.ilike('%'+query+'%'), Point.type.ilike('%'+query+'%'),
                                         Point.student_id.ilike('%'+query+'%'), Point.issuer_id.ilike('%'+query+'%'),
                                         Point.supervisor.ilike('%'+query+'%')), Point.active is True)
        return render_template("points.html", query=query, results=results, students=students, form=form)
    return render_template("points.html", points=points, students=students, form=form)


@main.route('/warnings', methods=['GET', 'POST'])
@main.route('/warnings/<int:page>', methods=['GET', 'POST'])
def warnings(page=1):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    warns = Warn.query.order_by(Warn.when.desc()).paginate(page, RESULTS_PER_PAGE, False)
    students = Student.query.filter_by(active=True).order_by(Student.lname)
    form = SearchPointsForm()
    if form.validate_on_submit():
        query = form.pointsSearchField.data
        results = Warn.query.filter(or_(Warn.why.ilike('%' + query + '%'), Warn.type.ilike('%' + query + '%'),
                                        Warn.student_id.ilike('%' + query + '%'),
                                        Warn.issuer_id.ilike('%' + query + '%'),
                                        Warn.supervisor.ilike('%' + query + '%')))
        return render_template("points.html", query=query, results=results, students=students, form=form)
    return render_template("warnings.html", warns=warns, students=students, form=form)


@main.route('/analytics')
def analytics(chartID='chart_ID', chart_type='line', chart_height=500):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    results = db.session.query(Point.when).add_column(Point.amount).all()
    timeArray = []
    amountArray = []
    d = {}
    for result in results:
        time = result.when
        if time in d:
            amount = d[time] + result.amount
            d[time] = amount
        else:
            d[time] = result.amount
    od = collections.OrderedDict(sorted(d.items()))
    for key, value in od.items():
        t = json.dumps(key.isoformat())
        timeArray.append(t)
        amountArray.append(value)
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    title = {"text": 'Points Assigned By Day'}
    xAxis = {"categories": timeArray}
    yAxis = {"title": {"text": 'Points'}, 'plotlines': [{'value': 0, 'width': 1, 'color': '#808080'}]}
    series = [{"name": 'Amount', "data": amountArray}]
    return render_template('analytics.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def do_punish(form, pawprint, student):
    if form.warning.data is True:
        try:
            give_warnings(form, pawprint)
        except Exception as e:
            raise e
    else:
        try:
            give_points(form, pawprint, student)
        except Exception as e:
            raise e


def give_points(form, pawprint, student):
    try:
        infraction = InfractionType.query.get(form.pointsField.data)
        typeOf = infraction.description
        if form.customAmountField.data != '':
            amount = form.customAmountField.data
        else:
            amount = infraction.value
        newpts = Point(amount, typeOf, form.whyField.data, form.whenField.data,
                       form.supervisorField.data, current_user.username, pawprint)
        student.pointTotal += float(amount)
        #token = generate_confirmation_token(newpts)
        #confirm_url = url_for('confirm_punish', token=token, _external=True)
        #html = render_template('email.html', confirm_url=confirm_url, type=newpts.typeOf, amount=newpts.amount)
        #subject = "You have been given points. Please acknowledge."
        #send_email(pawprint+"@mail.missouri.edu", subject, html)
        db.session.add(newpts)
        db.session.commit()
        flash("Points issued.", 'success')
    except Exception as e:
        raise Exception('Something went wrong: ' + str(e))


def give_warnings(form, pawprint):
    try:
        infraction = InfractionType.query.get(form.pointsField.data)
        warnType = infraction.description
        newWarning = Warn(warnType, form.whyField.data, form.whenField.data,
                          form.supervisorField.data, current_user.username, pawprint)
        db.session.add(newWarning)
        db.session.commit()
        flash("Warning issued.", 'success')
    except Exception as e:
        raise Exception('Something went wrong: ' + str(e))


def generate_confirmation_token(id):
    serializer = URLSafeSerializer(DevelopmentConfig.SECRET_KEY)
    return serializer.dumps(id, salt=DevelopmentConfig.SECURITY_PASSWORD_SALT)


def confirm_token(token):
    serializer = URLSafeSerializer(DevelopmentConfig.SECRET_KEY)
    try:
        point = serializer.loads(token, salt=DevelopmentConfig.SECURITY_PASSWORD_SALT)
    except:
        return False
    return point


def send_email(to, subject, template):
    msg = Message(subject, recipients=[to], html=template, sender=DevelopmentConfig.MAIL_DEFAULT_SENDER)
    mail.send(msg)
