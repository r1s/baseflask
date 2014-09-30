from flask import Blueprint

example = Blueprint('example', __name__, template_folder='templates', url_prefix='/')