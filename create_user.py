#!/usr/bin/python

from getpass import getpass
from flask.ext.bcrypt import Bcrypt
from app import db
from app.models import User


def main():
        bcrypt = Bcrypt()
        db.metadata.create_all(db.engine)
        if User.query.all():
            create = input('A user already exists! Create another? (y/n): ')
            if create == 'n':
                return

            email = input('Enter email address: ')
            password = getpass()
            assert password == getpass('Password (again): ')

            user = User(email=email, password=bcrypt.generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            print('User added.')

main()