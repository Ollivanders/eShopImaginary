from sqlalchemy import Column

from app import db


class Commissions(db.Model):
    __tablename__ = 'commissions'

    id = Column(db.Integer, primary_key=True)
    date = Column(db.String)
    vendor_id = Column(db.Integer)
    rate = Column(db.REAL)
