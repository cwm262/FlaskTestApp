# import os
from app import create_app, db, models
from flask.ext.bcrypt import Bcrypt

app = create_app('default')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        bcrypt = Bcrypt()
        username = "bob"
        password = "password123"
        if not models.User.query.filter_by(username=username).first():
            user = models.User(username=username, password=bcrypt.generate_password_hash(password), approved=True)
            db.session.add(user)
            db.session.commit()
        if not models.Student.query.filter_by(pawprint='rvts6').first():
            student = models.Student('rvts6', 'Reid', 'Vardell')
            db.session.add(student)
            db.session.commit()
        if not models.Student.query.filter_by(pawprint='ted4').first():
            student = models.Student('ted4', 'Ted', 'Thomas')
            db.session.add(student)
            db.session.commit()
        if not models.Point.query.filter_by(id='1').first():
            point = models.Point(3, 'No call no show', 'bob', 'bob', 'rvts6')
            db.session.add(point)
            s = models.Student.query.filter_by(pawprint='rvts6').first()
            s.pointTotal += 3
            db.session.commit()
    app.run()