# -*- coding: utf-8 -*-

import os


class BaseConfig(object):
    DEBUG = False
    SITE_NAME = 'BaseFlask'
    SECRET_KEY = "MY_VERY_SECRET_KEY"
    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    DB_NAME = '.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////{0}'.format(os.path.join(ROOT_PATH, DB_NAME))
    CSRF_ENABLED = True

    BABEL_LANGUAGES = ['en', ]
    BABEL_DEFAULT_LOCALE = 'en'

    BLUEPRINTS = ['example.example', ]

    EXTENSIONS = ['ext.db',
                  'ext.toolbar',
                  'ext.babel'
                  ]

    CONTEXT_PROCESSORS = []
    LOGGER_NAME = 'baseflask'

    DEBUG_LOG_FORMAT = '[%(asctime)s] %(levelname)s %(pathname)s:%(lineno)s %(message)s'

    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SITE_URL = 'http://localhost:5000'
    MAIL_SENDER = 'test@test.ru'
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
