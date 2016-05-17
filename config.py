import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'oh my god Becky look at her butt'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'super super super cereal secret'
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    BCRYPT_LOG_ROUNDS = 13

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_DATABASE_URI = 'postgresql://pointsadmin:password123@localhost/scpt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}