from flask import Blueprint, request, jsonify
from ..services.order_service import (get_all_orders, create_order,get_order_by_id, update_order_status)
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

order_bp = Blueprint('order_bp', __name__)

PRODUCT_SERVICE_URL = 'http://product_service:5000'
USER_SERVICE_URL = 'http://user_service:5002'

@order_bp.route('/orders', methods=['GET'])
def list_orders():
    orders = get_all_orders()
    return jsonify({'message': 'Orders retrieved',
                    'orders': [{'id': o.id, 'product_id': o.product_id,
                                'quantity': o.quantity} for o in orders]}), 200

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    #Call product service to get product details
    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{order.product_id}")
    if product_response.status_code != 200:
        return jsonify({'error': 'Product not found'}), 404

    product_data = product_response.json()
    return jsonify({'id': order.id, 'product_id': order.product_id,
                    'quantity': order.quantity, 'product_name': product_data.get('name'),
                    'total_price': product_data.get('price') * order.quantity}), 200

@order_bp.route('/orders', methods=['POST'])
@jwt_required()
def add_order():
    data = request.get_json()
    user_id = get_jwt_identity()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if product_id is None or quantity is None:
        return jsonify({'error': 'Product ID and quantity are required'}), 400
    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({'error': 'Quantity must be an integer'}), 400

    logging.info(f"[ORDER] user_id: {user_id}, product_id: {product_id}, quantity: {quantity}")

    #Call product service
    try:
        product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}",
                                        timeout=3)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to product service: {e}")
        return jsonify({'error': 'Product service unavailable'}), 503

    if product_response.status_code != 200:
        return jsonify({'error': 'Product not found'}), 404



    product_data = product_response.json()
    if not product_data.get('name') or not product_data.get('price'):
        return jsonify({'error': 'Invalid product data received'}), 500

    try:
        reserved_stock = requests.post(f"{PRODUCT_SERVICE_URL}/products/{product_id}/reserved_stock",
                                     json={'quantity': quantity},
                                      timeout=3)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to product service for stock check: {e}")
        return jsonify({'error': 'Stock service unavailable'}), 503

    if reserved_stock.status_code != 200:
        return jsonify({'error': 'Not enough stock'}), 400


    product_name = product_data.get('name')
    total_price = product_data.get('price') * quantity

    new_order = create_order(user_id,product_id, product_name, quantity, total_price)
    return jsonify({'message': 'Order created',
                    'order': {'id': new_order.id, 'product_id': new_order.product_id,
                               'quantity': new_order.quantity}}), 201

@order_bp.route('/orders/<int:order_id>/confirm', methods=['POST'])
def confirm_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if order.status != 'pending':
        return jsonify({'error': 'Orders cannot be confirmed'}), 400

    requests.post(
        f"{PRODUCT_SERVICE_URL}/products/{order.product_id}/confirm_stock",
        json={'quantity': order.quantity}
    )

    order.status = 'confirmed'
    update_order_status(order_id, 'confirmed')
    return jsonify({'message': 'Order confirmed',
                    'order':{
                        'id':order.id,
                        'user_id':order.user_id,
                        'product_id':order.product_id,
                        'product_name':order.product_name,
                        'quantity':order.quantity,
                        'total_price':order.total_price,
                        'status':order.status
                    }}), 200

@order_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if order.status == 'confirmed':
        return jsonify({
            'message':'Cannot cancel confirm order'
        }),400

    requests.post(f"{PRODUCT_SERVICE_URL}/products/{order.product_id}/release_stock",
                  json={'quantity': order.quantity})
    order.status = 'cancelled'
    update_order_status(order_id, 'cancelled')
    return jsonify({
        'message': 'Order cancelled',
        'order':{
            'id':order.id,
            'user_id':order.user_id,
            'product_id':order.product_id,
            'product_name':order.product_name,
            'quantity':order.quantity,
            'total_price':order.total_price,
            'status':order.status
        }}), 200


@order_bp.route('/orders_detail/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{order.product_id}")
    if product_response.status_code != 200:
        return jsonify({'error': 'Product not found'}), 404

    user_response = requests.get(f"{USER_SERVICE_URL}/users/{order.user_id}")
    if user_response.status_code != 200:
        return jsonify({'error': 'User not found'}), 404

    user_data = user_response.json()
    product_data = product_response.json()
    return jsonify({
        'order':{
            'id': order_id,
            'user':{'id': user_data.get('id'), 'name': user_data.get('name')},
            'product':{'id': product_data.get('id'), 'name': product_data.get('name')},
            'quantity': order.quantity,
            'total_price': order.total_price,
            'status': order.status
        }
    })


