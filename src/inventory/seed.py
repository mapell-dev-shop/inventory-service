"""Resets the demo products: python -m inventory.seed (safe to run again)."""

from sqlalchemy.orm import Session

from inventory.db import SessionLocal
from inventory.models import Product

PRODUCTS = [
    {"sku": "BOOK-1", "name": "Clean Code", "price_cents": 2500, "stock": 10},
    {"sku": "PEN-1", "name": "Gel pen", "price_cents": 300, "stock": 100},
    {"sku": "LAPTOP-1", "name": "Laptop", "price_cents": 150000, "stock": 5},
]


def seed(session: Session) -> None:
    for product in PRODUCTS:
        session.merge(Product(**product))
    session.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed(session)
