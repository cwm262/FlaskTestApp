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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pawprint = db.Column(db.String(12), unique=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    pointTotal = db.Column(db.Float, default=0)
    currentEmployee = db.Column(db.Boolean, default=True)
    when_added = db.Column(db.DateTime)
    points = db.relationship('Point', backref='students', lazy='dynamic')
    warnings = db.relationship('Warn', backref='students', lazy='dynamic')

    def __init__(self, pawprint, fname, lname):
        self.pawprint = pawprint
        self.fname = fname
        self.lname = lname
        self.when_added = datetime.datetime.today()

    def __repr__(self):
        return 'Id: %d' % self.id + '\n' + 'First Name: %r' % self.fname + '\n' + 'Last Name: %r' % self.lname + '\n' \
            + 'Point Total: %f' % self.pointTotal

    def get_points(self):
        return self.points

    def get_warnings(self):
        return self.warnings

    def is_employee(self):
        if self.currentEmployee == 0:
            return True
        return False

    def get_point_total(self):
        return self.pointTotal


class Point(db.Model):
    __tablename__ = 'points'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=False, default=1)
    when = db.Column(db.DateTime)
    issuer_id = db.Column(db.String, db.ForeignKey('users.username'))
    issuer = db.relationship(User, uselist=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))


class Warn(db.Model):
    __tablename__ = 'warns'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer, nullable=False)
    why = db.String(db.String(140))
    when = db.Column(db.DateTime)
    issuer_id = db.Column(db.String, db.ForeignKey('users.username'))
    issuer = db.relationship(User, uselist=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))