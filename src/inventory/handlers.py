"""What inventory-service does when an event arrives from another service."""

from typing import Any

from shop_contracts.events import new_envelope
from shop_contracts.messaging import EventPublisher
from sqlalchemy import select
from sqlalchemy.orm import Session

from inventory.models import ProcessedEvent, Product, Reservation


def handle_order_placed(
    session: Session, envelope: dict[str, Any], publisher: EventPublisher
) -> None:
    """Reserve every line of the order, or none of them."""
    if session.get(ProcessedEvent, envelope["event_id"]) is not None:
        return
    order_id = envelope["data"]["order_id"]
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


def handle_payment_failed(session: Session, envelope: dict[str, Any]) -> None:
    """Give back the stock reserved for an order whose payment failed.

    Deleting the reservations makes a redelivered event harmless: it finds none to release.
    """
    order_id = envelope["data"]["order_id"]
    held = list(session.scalars(select(Reservation).where(Reservation.order_id == order_id)))
    for reservation in held:
        product = session.get(Product, reservation.sku)
        if product is not None:
            product.stock += reservation.quantity
        session.delete(reservation)
    session.commit()
