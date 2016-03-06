import bcrypt
from flask import request, render_template, flash, session, redirect, url_for, abort
from flask.ext.login import login_required, login_user, current_user, logout_user
from flask.ext.bcrypt import Bcrypt
from ..models import User, Student
from .forms import LoginForm
from . import main
from .. import login_manager, db
import datetime


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


@main.route('/students/<pawprint>')
def student(pawprint):
    student = Student.query.filter_by(pawprint=pawprint).first()
    if student is None:
        abort(404)
    now = datetime.datetime.today()
    return render_template('student.html', student=student, time=now)


@main.route('/profile/<username>')
def profile(username):
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    if username != current_user.username:
        return redirect(url_for('.index'))
    user = User.query.get(username)
    return render_template('profile.html', user=user)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

