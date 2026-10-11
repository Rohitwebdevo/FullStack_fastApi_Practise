from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

try:
    from .database import SessionLocal, engine
    from . import database_models
    from .database_models import Product as DBProduct
    from .models import Product
except ImportError:
    from database import SessionLocal, engine
    import database_models
    from database_models import Product as DBProduct
    from models import Product

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

database_models.Base.metadata.create_all(bind=engine)

products = [
    Product(id=1, name="Mobile", description="This is a mobile phone", price=500.0, quantity=10),
    Product(id=2, name="Lappy", description="This is a laptop", price=1000.0, quantity=5),
    Product(id=3, name="Tablet", description="This is a tablet", price=300.0, quantity=15)
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = SessionLocal()
    count = db.query(DBProduct).count()
    try:
        if db.query(DBProduct).count() == 0:
            for product in products:
                product_data = product.model_dump() if hasattr(product, "model_dump") else product.dict()
                db.add(database_models.Product(**product_data))
            db.commit()
    finally:
        db.close()

init_db()

@app.get("/")
def greet():
    return "Hello, welcome to the program!"

@app.get("/products")
def get_all_products(db: SessionLocal = Depends(get_db)):
    db_products = db.query(DBProduct).all()
    return db_products

@app.get("/products/{product_id}")
def get_product(product_id: int, db: SessionLocal = Depends(get_db)):
    try:
        db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
        if db_product:
            return db_product
        return {"error": "Product not found"}
    finally:
        db.close()

@app.post("/products", status_code=201)
def add_product(product: Product, db: SessionLocal = Depends(get_db)):
    try:
        payload = product.model_dump(exclude_none=True)

        if product.id is not None and db.query(DBProduct).filter(DBProduct.id == product.id).first():
            return JSONResponse(status_code=409, content={"detail": f"Product with id {product.id} already exists"})

        payload.pop("id", None)
        db_product = DBProduct(**payload)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError:
        db.rollback()
        return JSONResponse(status_code=409, content={"detail": "Product already exists or database constraint failed"})


@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product, db: SessionLocal = Depends(get_db)):
    db = SessionLocal()
    try:
        product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
        if not product:
            return {"error": "Product not found"}

        product.name = updated_product.name
        product.description = updated_product.description
        product.price = updated_product.price
        product.quantity = updated_product.quantity
        db.commit()
        return product
    finally:
        db.close()


@app.delete("/products")
def delete_products(product_id: int, db: SessionLocal = Depends(get_db)):
    try:
        product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
        if not product:
            return {"error": "Product not found"}
        db.delete(product)
        db.commit()
        return product
    finally:
        db.close()