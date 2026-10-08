from sqlalchemy import func, select
from sqlalchemy.orm import Session

from inventory.models import Product
from inventory.seed import seed


def test_seeding_again_resets_the_products_without_duplicates(session: Session) -> None:
    product = session.get(Product, "BOOK-1")
    assert product is not None
    product.stock = 0
    session.commit()

    seed(session)

    assert session.scalar(select(func.count()).select_from(Product)) == 3
    assert product.stock == 10
