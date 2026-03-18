from ..extensions import db, text
from ..models.product import Product


def get_all_products():
    return Product.query.all()

def create_product(name, price, stock=0):
    new_product = Product(name=name, price=price, stock=stock)
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

def update_product(product_id, name=None, price=None, stock=None):
    product = get_product_by_id(product_id)
    if not product:
        return None
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
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