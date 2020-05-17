from sqlalchemy import Column

from app import db


class ProductPromotions(db.Model):
    __tablename__ = 'product_promotions'

    id = Column(db.Integer, primary_key=True)
    date = Column(db.String)
    product_id = Column(db.Integer)
    promotion_id = Column(db.Integer)
