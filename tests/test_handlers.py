from typing import Any

from shop_contracts.messaging import InMemoryEventPublisher
from sqlalchemy import select
from sqlalchemy.orm import Session

from inventory.handlers import handle_order_placed
from inventory.models import Product, Reservation
from tests.conftest import event


def order_placed(*lines: tuple[str, int]) -> dict[str, Any]:
    return event(
        "OrderPlaced",
        {
            "order_id": "o-1",
            "lines": [{"sku": sku, "quantity": qty, "unit_price_cents": 100} for sku, qty in lines],
            "total_cents": 100 * sum(qty for _, qty in lines),
        },
    )


def stock(session: Session, sku: str) -> int:
    product = session.get(Product, sku)
    assert product is not None
    return product.stock


def reservations(session: Session) -> list[tuple[str, int]]:
    return [
        (r.sku, r.quantity) for r in session.scalars(select(Reservation).order_by(Reservation.sku))
    ]


def test_an_order_in_stock_is_reserved_and_announced(
    session: Session, publisher: InMemoryEventPublisher
) -> None:
    handle_order_placed(session, order_placed(("BOOK-1", 2), ("PEN-1", 5)), publisher)

    assert stock(session, "BOOK-1") == 8
    assert stock(session, "PEN-1") == 95
    assert reservations(session) == [("BOOK-1", 2), ("PEN-1", 5)]
    [envelope] = publisher.published
    assert envelope["type"] == "StockReserved"
    assert envelope["data"] == {"order_id": "o-1", "total_cents": 700}


def test_the_last_items_in_stock_can_be_reserved(
    session: Session, publisher: InMemoryEventPublisher
) -> None:
    handle_order_placed(session, order_placed(("BOOK-1", 10)), publisher)

    assert stock(session, "BOOK-1") == 0
    assert publisher.published[0]["type"] == "StockReserved"


def test_one_short_line_rejects_the_whole_order(
    session: Session, publisher: InMemoryEventPublisher
) -> None:
    handle_order_placed(session, order_placed(("PEN-1", 5), ("BOOK-1", 11)), publisher)

    assert stock(session, "PEN-1") == 100
    assert stock(session, "BOOK-1") == 10
    assert reservations(session) == []
    [envelope] = publisher.published
    assert envelope["type"] == "StockRejected"
    assert envelope["data"] == {"order_id": "o-1", "sku": "BOOK-1", "reason": "insufficient stock"}


def test_an_unknown_sku_is_rejected(session: Session, publisher: InMemoryEventPublisher) -> None:
    handle_order_placed(session, order_placed(("NOPE-1", 1)), publisher)

    [envelope] = publisher.published
    assert envelope["data"]["reason"] == "unknown sku"


def test_a_redelivered_event_reserves_once(
    session: Session, publisher: InMemoryEventPublisher
) -> None:
    envelope = order_placed(("BOOK-1", 2))

    handle_order_placed(session, envelope, publisher)
    handle_order_placed(session, envelope, publisher)

    assert stock(session, "BOOK-1") == 8
    assert len(publisher.published) == 1
