from flask import Blueprint, request, jsonify
from ..services.product_service import (get_all_products, create_product,
                                        get_product_by_id, update_product,
                                        delete_product, get_product_by_name,
                                        reduce_product_stock, add_product_stock)

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/products', methods=['GET'])
def list_products():
    products = get_all_products()
    return jsonify({'message': 'Products retrieved',
                    'products': [{'id': p.id, 'name': p.name,
                                  'price': p.price,'stock':p.stock} for p in products]}), 200

@product_bp.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock', 0)

    if not name or price is None:
        return jsonify({'error': 'Name and price are required'}), 400
    try:
        price = float(price)
    except ValueError:
        return jsonify({'error': 'Price must be a number'}), 400

    try:
        stock = int(stock)
    except ValueError:
        return jsonify({'error': 'Stock must be an integer'}), 400

    new_product = create_product(name, price, stock)
    return jsonify({'message': 'Product created',
                    'product': {'id': new_product.id, 'name': new_product.name,
                                'price': new_product.price,'stock':new_product.stock}}), 201

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'id': product.id, 'name': product.name,
                    'price': product.price,'stock':product.stock}), 200

@product_bp.route('/products/<string:name>', methods=['GET'])
def get_product_by_name_route(name):
    product = get_product_by_name(name)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'products':[{'id':p.id,
                                 'name':p.name,
                                 'price':p.price,
                                 'stock':p.stock} for p in product]}), 200

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product_route(product_id):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock')

    updated_product = update_product(product_id, name, price, stock)
    if not updated_product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'message': 'Product updated',
                    'product': {'id': updated_product.id, 'name': updated_product.name,
                                'price': updated_product.price}}), 200

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    success = delete_product(product_id)
    if not success:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'message': 'Product deleted'}), 200

@product_bp.route('/products/<int:product_id>/reduce_stock', methods=['POST'])
def reduce_stock(product_id):
    data = request.get_json()
    quantity = data.get('quantity')
    product=get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if quantity is None:
        return jsonify({'error': 'Quantity is required'}), 400
    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({'error': 'Quantity must be an integer'}), 400

    new_stock = reduce_product_stock(product_id, quantity)
    if new_stock is False:
        return jsonify({'error': 'Product not found or insufficient stock'}), 404
    return jsonify({'message': 'Stock reduced', 'new_stock': new_stock}), 200

@product_bp.route('/products/<int:product_id>/add_stock', methods=['POST'])
def add_stock(product_id):
    data = request.get_json()
    quantity = data.get('quantity')
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if quantity is None:
        return jsonify({'error': 'Quantity is required'}), 400
    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({'error': 'Quantity must be an integer'}), 400

    new_stock = add_product_stock(product_id, quantity)
    if new_stock is False:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'message': 'Stock added', 'new_stock': new_stock}), 200


