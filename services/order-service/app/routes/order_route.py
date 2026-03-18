from flask import Blueprint, request, jsonify
from ..services.order_service import (get_all_orders, create_order,get_order_by_id, update_order_status)
import requests

order_bp = Blueprint('order_bp', __name__)

PRODUCT_SERVICE_URL = 'http://localhost:5001/products'
USER_SERVICE_URL = 'http://localhost:5002/users'

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
    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{order.product_id}")
    if product_response.status_code != 200:
        return jsonify({'error': 'Product not found'}), 404

    product_data = product_response.json()
    return jsonify({'id': order.id, 'product_id': order.product_id,
                    'quantity': order.quantity, 'product_name': product_data.get('name'),
                    'total_price': product_data.get('price') * order.quantity}), 200

@order_bp.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    user_id = data.get('user_id')  # Simulate user authentication
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not user_id or not product_id or quantity is None:
        return jsonify({'error': 'Product ID and quantity are required'}), 400
    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({'error': 'Quantity must be an integer'}), 400

    user_response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}")  # Simulate user authentication
    if user_response.status_code != 200:
        return jsonify({'error': 'User not found'}), 404

    #Call product service
    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")
    if product_response.status_code != 200:
        return jsonify({'error': 'Product not found'}), 404

    product_data = product_response.json()
    if product_data['stock'] < quantity:
        return jsonify({'error': 'Not enough stock'}), 400

    reduce_stock=requests.post(f"{PRODUCT_SERVICE_URL}/{product_id}/reduce_stock",
                               json={'quantity': quantity})
    if reduce_stock.status_code != 200:
        return jsonify({'error': 'Failed to reduce stock'}), 500

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
    stock_reduce=requests.post(f"{PRODUCT_SERVICE_URL}/{order.product_id}/reduce_stock",
                               json={'quantity': order.quantity})
    if stock_reduce.status_code != 200:
        return jsonify({'error': 'Failed to reduce stock'}), 500

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

    if order.status == 'cancelled':
        return jsonify({'error': 'Order is already cancelled'}), 400

    requests.post(f"{PRODUCT_SERVICE_URL}/{order.product_id}/add_stock",
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

    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{order.product_id}")
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


