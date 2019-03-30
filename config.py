# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SHMUBlog-secret-key'
    SHMUBLOG_ADMIN_EMAIL = os.environ.get('SHMUBLOG_ADMIN_EMAIL') or 'hellckt@126.com'
    SHMUBLOG_USER_PER_PAGE = 10
    SHMUBLOG_POST_PER_PAGE = 10
    SHMUBLOG_COMMENT_PER_PAGE = 10

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-CKEditor
    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_SERVE_LOCAL = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                          'app-dev.db')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
