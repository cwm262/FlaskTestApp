from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from config import config
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(config['default'])

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
moment = Moment(app)
mail = Mail(app)

from app import views, models

