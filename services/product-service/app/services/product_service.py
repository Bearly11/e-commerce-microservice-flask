
from ..extensions import db, text
from ..models.product import Product
from werkzeug.utils import secure_filename
import os
import uuid



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "static", "image", "product_image")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def save_product_image(file):

    if not file or file.filename == '':
        raise ValueError("No file provided")


    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed")


    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    if file_length > 5 * 1024 * 1024:
        raise ValueError("File size exceeds 5MB limit")

    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)
    return f"/static/image/product_image/{filename}"


def get_all_products():
    return Product.query.all()

def create_product(name, price, stock=0, image_url=None):
    new_product = Product(name=name, price=price, stock=stock,image_url=image_url)
    db.session.add(new_product)
    db.session.commit()
    return new_product

def get_product_by_id(product_id):
    return Product.query.get(product_id)

def get_product_by_name(name):
    search = f"%{name}%"
    sql = text("SELECT * FROM products WHERE name LIKE :search")
    result = db.session.execute(sql, {'search': search}).fetchall()
    return result

def update_product(product_id, name=None, price=None, stock=None, image_url=None):
    product = get_product_by_id(product_id)
    if not product:
        return None
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
    if image_url is not None:
        product.image_url = image_url
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return None
    return product

def delete_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return False
    db.session.delete(product)
    db.session.commit()
    return True
def reduce_product_stock(product_id, quantity):
    product = get_product_by_id(product_id)
    if not product or product.stock < quantity:
        return False
    product.stock -= quantity
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise False
    return product.stock

def add_product_stock(product_id, quantity):
    product = get_product_by_id(product_id)
    if not product:
        return False
    product.stock += quantity
    db.session.commit()
    return product.stock

def reserved_product_stock(product_id,quantity):
    product = get_product_by_id(product_id)
    if not product or product.stock < quantity:
        return False
    product.stock -= quantity
    product.reserved_stock += quantity

    try:
        db.session.commit()
    except:
        db.session.rollback()
        return False

    return product.reserved_stock

def release_product_stock(product_id,quantity):
    product =get_product_by_id(product_id)
    if not product:
        return False
    if product.reserved_stock < quantity:
        return False
    product.reserved_stock -= quantity
    product.stock += quantity

    try:
        db.session.commit()
    except:
        db.session.rollback()
        return False
    return True
def confirm_product_stock(product_id,quantity):
    product = get_product_by_id(product_id)
    if not product or product.reserved_stock < quantity:
        return False
    product.reserved_stock -= quantity
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return False
    return True
