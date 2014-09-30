# -*- coding: utf-8 -*-

from flask.ext.babel import Babel
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base


db = SQLAlchemy()
babel = Babel()
Base = declarative_base()

toolbar = lambda app: DebugToolbarExtension(app)  # has no init_app()
