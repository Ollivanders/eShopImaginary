from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app import db
from models.order import Order


class OrderLines(db.Model):
    __tablename__ = 'orders_lines'

    order_line_id = Column(db.Integer, primary_key=True)
    product_id = Column(db.Integer)
    # product_description = Column(db.String)
    product_price = Column(db.REAL)
    # product_vat_rate = Column(db.REAL)
    discount_rate = Column(db.REAL)
    quantity = Column(db.REAL)
    full_price_amount = Column(db.REAL)
    discounted_amount = Column(db.REAL)
    # vat_amount = Column(db.REAL)
    total_amount = Column(db.REAL)

    order_id = Column(Integer, ForeignKey('orders.id'))

    order = relationship(Order)
