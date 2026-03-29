from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import CartItem, Product, create_tables, get_db
from fastapi.middleware.cors import CORSMiddleware

class ProductCreate(BaseModel):
    name: str
    price: int
    description: str | None = None
    stock: int

class ProductUpdate(BaseModel):
    price: int
    description: str | None = None
    stock: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None
    stock: int
    
    class Config:
        from_attributes = True


class CartAddRequest(BaseModel):
    product_id: int


class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Template"}


@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.name == product.name))
    existing_product = result.first()

    if existing_product:
        raise HTTPException(status_code=400, detail="Product name already registered")

    new_product = Product(name=product.name, price=product.price, stock=product.stock)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@app.get("/products/", response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

@app.get("/cart/", response_model=List[CartItemResponse])
async def get_cart(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem, Product).join(Product, CartItem.product_id == Product.id)
    )
    items = []
    for cart_item, product in result.all():
        items.append(
            CartItemResponse(
                product_id=product.id,
                name=product.name,
                price=product.price,
                quantity=cart_item.quantity,
            )
        )
    return items


@app.post("/cart/add", response_model=CartItemResponse)
async def add_to_cart(payload: CartAddRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == payload.product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock <= 0:
        raise HTTPException(status_code=400, detail="Not enough stock")

    product_id = product.id
    product_name = product.name
    product_price = product.price

    result = await db.execute(select(CartItem).filter(CartItem.product_id == product_id))
    cart_item = result.scalars().first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(product_id=product_id, quantity=1)
        db.add(cart_item)

    product.stock -= 1

    await db.commit()
    await db.refresh(cart_item)

    return CartItemResponse(
        product_id=product_id,
        name=product_name,
        price=product_price,
        quantity=cart_item.quantity,
    )


@app.post("/cart/remove", response_model=CartItemResponse)
async def remove_from_cart(payload: CartAddRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).filter(CartItem.product_id == payload.product_id))
    cart_item = result.scalars().first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    result = await db.execute(select(Product).filter(Product.id == payload.product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_id = product.id
    product_name = product.name
    product_price = product.price

    if cart_item.quantity <= 1:
        await db.delete(cart_item)
        quantity = 0
    else:
        cart_item.quantity -= 1
        quantity = cart_item.quantity

    product.stock += 1

    await db.commit()

    return CartItemResponse(
        product_id=product_id,
        name=product_name,
        price=product_price,
        quantity=quantity,
    )

@app.put("/products/{id}", response_model=ProductResponse)
async def update_product(id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == id))
    existing_product = result.scalars().first()

    if not existing_product:
        raise HTTPException(status_code=404, detail=f"Product with id {id} does not exists!")

    existing_product.price = product.price
    existing_product.stock = product.stock

    await db.commit()
    await db.refresh(existing_product)
    return existing_product

@app.delete("/products/{id}")
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == id))
    existing_product = result.scalars().first()

    if not existing_product:
        raise HTTPException(status_code=404, detail=f"Product with id {id} does not exists!")
    
    await db.delete(existing_product)
    await db.commit()
    return {"message": f"The product with id {id} was deleted succesfully!" }
    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)






