from flask import Blueprint, request, jsonify
from ..services.product_service import (get_all_products, create_product,
                                        get_product_by_id, update_product,
                                        delete_product, get_product_by_name,
                                        reduce_product_stock, add_product_stock,
                                        save_product_image)

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/', methods=['GET'])
def list_products():
    products = get_all_products()
    return jsonify({'message': 'Products retrieved',
                    'products': [{'id': p.id, 'name': p.name,
                                  'price': p.price,'stock':p.stock,
                                   'image_url':p.image_url} for p in products]}), 200

@product_bp.route('/upload_image', methods=['POST'])
def upload_image():
    image_file = request.files.get('image_url')
    if not image_file:
        return jsonify({'error': 'No image file provided'}), 400

    print("File content type:", image_file.content_type)

    try:
        image_url = save_product_image(image_file)

    except Exception as e:
        return jsonify({'error':str(e)}), 500

    return jsonify({
        'message': 'Image uploaded successfully',
        'image_url': image_url
    })


@product_bp.route('/', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock', 0)
    image_url = data.get('image_url')

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


    new_product = create_product(name, price, stock, image_url)
    return jsonify({'message': 'Product created',
                    'product': {'id': new_product.id, 'name': new_product.name,
                                'price': new_product.price,'stock':new_product.stock,
                                 'image_url':new_product.image_url}}), 201

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'id': product.id, 'name': product.name,
                    'price': product.price,'stock':product.stock,
                     'image_url':product.image_url}), 200

@product_bp.route('/name/<string:name>', methods=['GET'])
def get_product_by_name_route(name):
    product = get_product_by_name(name)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'products':[{'id':p.id,
                                 'name':p.name,
                                 'price':p.price,
                                 'stock':p.stock,
                                  'image_url':p.image_url} for p in product]}), 200

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product_route(product_id):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock')
    image_url = data.get('image_url')

    updated_product = update_product(product_id, name, price, stock, image_url)
    if not updated_product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'message': 'Product updated',
                    'product': {'id': updated_product.id, 'name': updated_product.name,
                                'price': updated_product.price,
                                'image_url':updated_product.image_url}}), 200

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    success = delete_product(product_id)
    if not success:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'message': 'Product deleted'}), 200

@product_bp.route('/<int:product_id>/reduce_stock', methods=['POST'])
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

@product_bp.route('/<int:product_id>/add_stock', methods=['POST'])
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


@product_bp.route('/debug_upload_image', methods=['POST'])
def debug_upload_image():
    image = request.files.get('image_url')
    print("request.files:", request.files)
    print("content type:",image.content_type)


    return jsonify({
        'message': 'check console',
        'content_type': image.content_type

    })

