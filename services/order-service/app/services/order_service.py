from flask import request

from ..extensions import db
from ..models.order import Order
from datetime import datetime, timedelta
import requests


PRODUCT_SERVICE_URL = "http://localhost:5000/products"

def get_all_orders():
    return Order.query.all()

def get_order_by_id(order_id):
    return Order.query.get(order_id)

def create_order(user_id,product_id, product_name, quantity, total_price):
    new_order = Order(
        user_id=user_id,
        product_id=product_id,
        product_name=product_name,
        quantity=quantity,
        total_price=total_price
    )
    db.session.add(new_order)
    db.session.commit()
    return new_order
def update_order_status(order_id, status):
    order = get_order_by_id(order_id)
    if not order:
        return None
    order.status = status
    db.session.commit()
    return order

def expire_orders():
    expired_time = datetime.utcnow() - timedelta(minutes=10)
    expired_orders = Order.query.filter(Order.status == 'pending', Order.created_at < expired_time).all()
    for order in expired_orders:
        requests.post(f"{PRODUCT_SERVICE_URL}/{order.product_id}/add_stock",
                      json={'quantity': order.quantity})
        order.status = 'cancelled'
    db.session.commit()