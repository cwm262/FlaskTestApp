import bcrypt
from flask import request, render_template, flash, session, redirect, url_for, abort, jsonify
from flask.ext.login import login_required, login_user, current_user, logout_user
from flask.ext.bcrypt import Bcrypt
from ..models import User, Student, Point, Warn, InfractionType
from .forms import LoginForm, PointsForm
from . import main
from .. import login_manager, db
import datetime
import pygal


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
            bcrypt = Bcrypt()
            if bcrypt.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flash("You have successfully logged in.", 'success')
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
    points = Point.query.filter_by(student_id=pawprint).order_by(Point.when.desc()).all()
    warns = Warn.query.filter_by(student_id=pawprint).order_by(Warn.when.desc()).all()
    now = datetime.datetime.today()
    return render_template('student.html', student=student, time=now, points=points, warns=warns)


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


@main.route('/points')
def points():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    points = Point.query.order_by(Point.when.desc()).all()
    students = Student.query.order_by(Student.lname).all()
    return render_template("points.html", points=points, students=students)


@main.route('/warnings')
def warnings():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    warns = Warn.query.order_by(Warn.when.desc()).all()
    students = Student.query.order_by(Student.lname).all()
    return render_template("warnings.html", warns=warns, students=students)


@main.route('/analytics')
def analytics():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    results = db.session.query(Point.type).add_column(Point.amount).all()
    d = {}
    for result in results:
        if result.type in d:
            amount = d[result.type] + result.amount
            d[result.type] = amount
        else:
            d[result.type] = result.amount
    pyChart = pygal.Pie()
    for key, value in d.items():
        pyChart.add(key, value)
    pyChart.title = "Points Issued by Type (in %)"
    chart = pyChart.render_data_uri()
    return render_template("analytics.html", chart=chart)


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
        newpts = Point(amount, typeOf, form.whyField.data, form.whenField.data, form.supervisorField.data,
                       current_user.username, pawprint)
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