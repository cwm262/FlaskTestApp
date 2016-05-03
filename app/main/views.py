import collections
from flask import request, render_template, flash, session, redirect, url_for, abort, json, jsonify
from flask.ext.login import login_required, login_user, current_user, logout_user
from flask.ext.bcrypt import Bcrypt
from werkzeug.security import check_password_hash
from ..models import User, Student, Point, Warn, InfractionType, OldPoint
from .forms import LoginForm, PointsForm, PasswordChangeForm, AddStudentForm, RemoveStudentForm, SearchPointsForm
from . import main
from .. import login_manager, db
from config import RESULTS_PER_PAGE
import datetime
import dateutil.parser as dateparser
from sqlalchemy import or_

@main.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


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
                error = "You have not been granted access yet."
                return render_template("login.html", form=form, error=error)
            #bcrypt = Bcrypt()
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
    students = Student.query.order_by(Student.lname).all()
    return render_template("studentlist.html", students=students)


@main.route('/students/<pawprint>', methods=['GET', 'POST'])
def student(pawprint):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    student = Student.query.filter_by(pawprint=pawprint).first()
    if student is None:
        abort(404)
    now = datetime.datetime.today()
    return render_template('student.html', student=student, time=now)


@main.route('/students/<pawprint>/give-points', methods=['GET', 'POST'])
def givepointspage(pawprint):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    student = Student.query.filter_by(pawprint=pawprint).first()
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
            bcrypt = Bcrypt()
            if bcrypt.check_password_hash(user.password, form.currentPassword.data):
                newPassword = bcrypt.generate_password_hash(form.confirm.data)
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
            if not Student.query.get(pawprint):
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
                    oldPoint = OldPoint(point.amount, point.type, point.why, point.when, point.supervisor,
                                        point.issuer_id, point.student_id)
                    db.session.add(oldPoint)
                db.session.delete(toDelete)
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
    points = Point.query.order_by(Point.when.desc()).paginate(page, RESULTS_PER_PAGE, False)
    students = Student.query.order_by(Student.lname).all()
    form = SearchPointsForm()
    if form.validate_on_submit():
        query = form.pointsSearchField.data
        results = Point.query.filter(or_(Point.why.ilike('%'+query+'%'), Point.type.ilike('%'+query+'%'),
                                         Point.student_id.ilike('%'+query+'%'), Point.issuer_id.ilike('%'+query+'%'),
                                         Point.supervisor.ilike('%'+query+'%')))
        if not results:
            results = Point.query.filter(Point.when == query)
        return render_template("points.html", query=query, results=results, students=students, form=form)
    return render_template("points.html", points=points, students=students, form=form)


@main.route('/warnings')
def warnings():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    warns = Warn.query.order_by(Warn.when.desc()).all()
    students = Student.query.order_by(Student.lname).all()
    return render_template("warnings.html", warns=warns, students=students)


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
        db.session.add(newpts)
        db.session.commit()
        flash("Points issued.", 'success')
    except Exception as e:
        raise Exception('Something went wrong: ' + e)


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
        raise Exception('Something went wrong: ' + e)
