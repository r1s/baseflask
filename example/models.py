from ext import db, Base
from helpers.models import CRUDMixin


class Example(CRUDMixin, Base):
    __tablename__ = 'example'
    query = db.session.query_property()

    title = db.Column(db.String(32))
    description = db.Column(db.String(512))
    is_active = db.Column(db.Boolean, default=True, nullable=False, unique=False)