import bcrypt
from flask import request, render_template, flash, session, redirect, url_for
from flask.ext.login import login_required, login_user, current_user, logout_user
from flask.ext.bcrypt import Bcrypt
from ..models import User
from .forms import LoginForm
from . import main
from .. import login_manager, db


@main.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@main.route('/')
@login_required
def index():
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        approved = user.is_approved()
        if user and approved:
            bcrypt = Bcrypt()
            if bcrypt.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('.index'))
            else:
                error = "Your password is incorrect. Please try again."
        else:
            error = "Sorry. " + form.username.data + " is not a valid username, or it has not yet been granted access."
    return render_template("login.html", form=form, error=error)


@main.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('.login'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

