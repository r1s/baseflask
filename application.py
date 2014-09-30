# -*- coding: utf-8 -*-

from flask.ext.mail import Mail
from helpers.app import AppFactory
from settings import DevelopmentConfig

app = AppFactory(DevelopmentConfig).get_app(__name__)
mail = Mail(app)
