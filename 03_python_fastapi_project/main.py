from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import Product, create_tables, get_db
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

