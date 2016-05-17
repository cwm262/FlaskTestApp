# import os
from app import db, models
from flask.ext.restless import APIManager
from faker import Faker
from nameparser import HumanName
import string
import random
import datetime
from werkzeug.security import generate_password_hash

from app import app


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    db.drop_all()
    db.session.commit()
    db.create_all()
    db.session.commit()
    mgr = APIManager(app, flask_sqlalchemy_db=db)
    mgr.create_api(models.Point, results_per_page=-1, include_columns=['id', 'amount', 'type', 'why', 'when', 'supervisor', 'student_id'],
                   methods=['GET', 'POST'])
    # mgr.create_api(models.Warn, include_columns=['type', 'why', 'when', 'supervisor', 'student_id'],
    #                methods=['GET'])
    # mgr.create_api(models.PointsRemovedHistory, include_columns=['amount', 'why', 'when', 'issuer_id',
    #                                                              'student_id'], methods=['GET'])
    mgr.create_api(models.Student, results_per_page=-1, methods=['GET', 'POST'])
    # username = 'bob'
    # password = 'password123'
    # pwhash = generate_password_hash(password)
    # if not models.User.query.filter_by(username=username).first():
    #     user = models.User(username=username, password=pwhash, approved=True)
    #     db.session.add(user)
    #     db.session.commit()
    # if not models.Student.query.filter_by(pawprint='rvts6').first():
    fake = Faker()
    for _ in range(0, 20):
        name = HumanName(fake.name())
        paw = id_generator()
        student = models.Student(paw, name.first, name.last)
        pt = random.randint(1, 3)
        point = models.Point(pt, "Other", "Random", datetime.datetime.now(), "bob", "bob", paw)
        db.session.add(student)
        db.session.add(point)
    db.session.commit()
    # if not models.InfractionType.query.get(1):
    #     infraction1 = models.InfractionType('No Call, No Show', 3)
    #     infraction2 = models.InfractionType('Left Early w/o Permission', 2)
    #     infraction3 = models.InfractionType('Called-In w/o Doc Note', 2)
    #     infraction4 = models.InfractionType('Drawer Off by 1% or $5', 2)
    #     infraction5 = models.InfractionType('Not Doing as Instructed', 3)
    #     infraction6 = models.InfractionType('Late w/ No Call', 1)
    #     infraction7 = models.InfractionType('Eating Behind Counter', 1)
    #     infraction8 = models.InfractionType('Taking Extended Breaks', 1)
    #     infraction9 = models.InfractionType('Out of Uniform', 1)
    #     infraction10 = models.InfractionType('Cell Phone Use', 1)
    #     infraction11 = models.InfractionType('Out of Uniform', 1)
    #     infraction12 = models.InfractionType('Missed Employee Meeting', .5)
    #     infraction13 = models.InfractionType('Other', 0)
    #     db.session.add(infraction1)
    #     db.session.add(infraction2)
    #     db.session.add(infraction3)
    #     db.session.add(infraction4)
    #     db.session.add(infraction5)
    #     db.session.add(infraction6)
    #     db.session.add(infraction7)
    #     db.session.add(infraction8)
    #     db.session.add(infraction9)
    #     db.session.add(infraction10)
    #     db.session.add(infraction11)
    #     db.session.add(infraction12)
    #     db.session.add(infraction13)
    #     db.session.commit()
    app.run()
