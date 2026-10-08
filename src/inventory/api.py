from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from inventory.db import get_session
from inventory.models import Product

app = FastAPI(title="inventory-service")

SessionDep = Annotated[Session, Depends(get_session)]


class ProductOut(BaseModel):
    sku: str
    name: str
    price_cents: int
    stock: int


def to_out(product: Product) -> ProductOut:
    return ProductOut(
        sku=product.sku, name=product.name, price_cents=product.price_cents, stock=product.stock
    )


@app.get("/products")
def list_products(session: SessionDep) -> list[ProductOut]:
    return [to_out(product) for product in session.scalars(select(Product).order_by(Product.sku))]


@app.get("/products/{sku}")
def get_product(sku: str, session: SessionDep) -> ProductOut:
    product = session.get(Product, sku)
    if product is None:
        raise HTTPException(404, "product not found")
    return to_out(product)
