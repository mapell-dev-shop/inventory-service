from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from inventory.db import Base


class Product(Base):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    price_cents: Mapped[int]
    stock: Mapped[int]


class Reservation(Base):
    """Stock held for one line of an order."""

    __tablename__ = "reservations"

    order_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), primary_key=True)
    quantity: Mapped[int]


class ProcessedEvent(Base):
    """Ids of events already handled, so a redelivered event changes nothing."""

    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
