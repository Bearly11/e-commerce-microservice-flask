
from ..extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer,default=0)
    image_url = db.Column(db.String(255), nullable=True)
    reserved_stock = db.Column(db.Integer,default=0)

