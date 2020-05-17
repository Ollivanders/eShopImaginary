from sqlalchemy import Column
from sqlalchemy.orm import relationship

from app import db


class Order(db.Model):
    __tablename__ = 'orders'

    # id = Column(db.Integer, primary_key=True)
    id = Column(db.Integer, primary_key=True)
    date = Column(db.String)
    vendor_id = Column(db.Integer)
    customer_id = Column(db.Integer)

    order_lines = relationship("OrderLines")
