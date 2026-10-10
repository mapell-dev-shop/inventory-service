"""What inventory-service does when an event arrives from another service."""

from typing import Any

from shop_contracts.events import new_envelope
from shop_contracts.messaging import EventPublisher
from sqlalchemy import select
from sqlalchemy.orm import Session

from inventory.models import CancelledOrder, ProcessedEvent, Product, Reservation


def handle_order_placed(
    session: Session, envelope: dict[str, Any], publisher: EventPublisher
) -> None:
    """Reserve every line of the order, or none of them."""
    if session.get(ProcessedEvent, envelope["event_id"]) is not None:
        return
    order_id = envelope["data"]["order_id"]
    if session.get(CancelledOrder, order_id) is not None:
        session.add(ProcessedEvent(event_id=envelope["event_id"]))
        session.commit()
        return
    lines = envelope["data"]["lines"]
    skus = [line["sku"] for line in lines]
    products = {p.sku: p for p in session.scalars(select(Product).where(Product.sku.in_(skus)))}

    for line in lines:
        product = products.get(line["sku"])
        if product is None or product.stock < line["quantity"]:
            reason = "unknown sku" if product is None else "insufficient stock"
            session.add(ProcessedEvent(event_id=envelope["event_id"]))
            session.commit()
            publisher.publish(
                new_envelope(
                    "StockRejected", {"order_id": order_id, "sku": line["sku"], "reason": reason}
                ),
                key=order_id,
            )
            return

    for line in lines:
        products[line["sku"]].stock -= line["quantity"]
        session.add(Reservation(order_id=order_id, sku=line["sku"], quantity=line["quantity"]))
    session.add(ProcessedEvent(event_id=envelope["event_id"]))
    session.commit()
    publisher.publish(
        new_envelope(
            "StockReserved", {"order_id": order_id, "total_cents": envelope["data"]["total_cents"]}
        ),
        key=order_id,
    )


def release_reservations(session: Session, order_id: str) -> None:
    """Give back the stock held for the order and drop its reservations. Does not commit."""
    held = list(session.scalars(select(Reservation).where(Reservation.order_id == order_id)))
    for reservation in held:
        product = session.get(Product, reservation.sku)
        if product is not None:
            product.stock += reservation.quantity
        session.delete(reservation)


def handle_payment_failed(session: Session, envelope: dict[str, Any]) -> None:
    """Give back the stock reserved for an order whose payment failed."""
    if session.get(ProcessedEvent, envelope["event_id"]) is not None:
        return
    release_reservations(session, envelope["data"]["order_id"])
    session.add(ProcessedEvent(event_id=envelope["event_id"]))
    session.commit()


def handle_order_cancelled(session: Session, envelope: dict[str, Any]) -> None:
    """Give back the stock of a cancelled order, and remember it so it is never reserved."""
    if session.get(ProcessedEvent, envelope["event_id"]) is not None:
        return
    order_id = envelope["data"]["order_id"]
    release_reservations(session, order_id)
    if session.get(CancelledOrder, order_id) is None:
        session.add(CancelledOrder(order_id=order_id))
    session.add(ProcessedEvent(event_id=envelope["event_id"]))
    session.commit()
