from app import db
import datetime


class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.BOOLEAN, default=False)
    approved = db.Column(db.BOOLEAN, default=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class Student(db.Model):
    __tablename__ = 'students'
    pawprint = db.Column(db.String(12), primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    pointTotal = db.Column(db.Float, default=0)
    currentEmployee = db.Column(db.Boolean, default=True)
    when_added = db.Column(db.DateTime)
    points = db.relationship('Point', cascade="all, delete", backref='students', lazy='dynamic')
    warnings = db.relationship('Warn', cascade="all, delete", backref='students', lazy='dynamic')

    def __init__(self, pawprint, fname, lname):
        self.pawprint = pawprint
        self.fname = fname
        self.lname = lname
        self.when_added = datetime.datetime.today()


class Point(db.Model):
    __tablename__ = 'points'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=False, default=0)
    type = db.Column(db.String(80))
    why = db.Column(db.String(140))
    when = db.Column(db.Date)
    supervisor = db.Column(db.String(20))
    issuer_id = db.Column(db.String, db.ForeignKey('users.username'))
    issuer = db.relationship(User, uselist=False)
    student_id = db.Column(db.String, db.ForeignKey('students.pawprint'))

    def __init__(self, amount, type, why, when, supervisor, issuer_id, student_id):
        self.amount = amount
        self.type = type
        self.why = why
        self.when = when
        if supervisor == '':
            self.supervisor = issuer_id
        else:
            self.supervisor = supervisor
        self.issuer_id = issuer_id
        self.student_id = student_id


class OldPoint(db.Model):
    __tablename__ = 'old_points'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=False, default=0)
    type = db.Column(db.String(80))
    why = db.Column(db.String(140))
    when = db.Column(db.Date)
    supervisor = db.Column(db.String(20))
    issuer_id = db.Column(db.String)
    student_id = db.Column(db.String)

    def __init__(self, amount, type, why, when, supervisor, issuer_id, student_id):
        self.amount = amount
        self.type = type
        self.why = why
        self.when = when
        self.supervisor = supervisor
        self.issuer_id = issuer_id
        self.student_id = student_id


class Warn(db.Model):
    __tablename__ = 'warns'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(80))
    why = db.Column(db.String(140))
    when = db.Column(db.Date)
    supervisor = db.Column(db.String(20))
    issuer_id = db.Column(db.String, db.ForeignKey('users.username'))
    issuer = db.relationship(User, uselist=False)
    student_id = db.Column(db.String, db.ForeignKey('students.pawprint'))

    def __init__(self, type, why, when, supervisor, issuer_id, student_id):
        self.type = type
        self.why = why
        self.when = when
        if supervisor == '':
            self.supervisor = issuer_id
        else:
            self.supervisor = supervisor
        self.issuer_id = issuer_id
        self.student_id = student_id


class InfractionType(db.Model):
    __tablename__ = 'infractionTypes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, default=0)

    def __init__(self, description, value):
        self.description = description
        self.value = value