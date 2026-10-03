from fastapi import FastAPI
from models import Product
from database import session, engine
import database_models
app=FastAPI()

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return "Hello, welcome to the program!"

products=[
    Product(id=1, name="Mobile", description="This is a mobile phone", price=500.0, quantity=10),
    Product(id=2, name="Lappy", description="This is a laptop", price=1000.0, quantity=5),
    Product(id=3, name="Tablet", description="This is a tablet", price=300.0, quantity=15)
]

@app.get("/products")
def get_all_products():
    db = session()
    query = db.query(Product).all()
    return query

@app.get("/products/{product_id}")
def get_product(product_id:int):
    for product in products:
        if product.id == product_id:
            return product
    return {'error':  "Product not found"}

@app.post("/products")
def add_product(product: Product):
    products.append(product)
    return product

@app.put("/products")
def Update_product(product_id:int, Updated_Product:Product):
    for i in range(len(products)):
        if products[i].id == product_id:
            products[i] = Updated_Product
            return Updated_Product
    return {'error':  "Product not found"}

@app.delete("/products")
def delete_products(product_id:int):
    for i in range(len(products)):
        if products[i].id == product_id:
            deleted_product = products.pop(i)
            return deleted_product
    return {'error':  "Product not found"}