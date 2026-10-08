"""Kafka consumer process of inventory-service: python -m inventory.worker"""

from typing import Any

from shop_contracts.messaging import KafkaEventPublisher, run_consumer

from inventory import settings
from inventory.db import SessionLocal
from inventory.handlers import handle_order_placed, handle_payment_failed


def main() -> None:
    publisher = KafkaEventPublisher(settings.KAFKA_BOOTSTRAP_SERVERS)

    def on_order_placed(envelope: dict[str, Any]) -> None:
        with SessionLocal() as session:
            handle_order_placed(session, envelope, publisher)

    def on_payment_failed(envelope: dict[str, Any]) -> None:
        with SessionLocal() as session:
            handle_payment_failed(session, envelope)

    run_consumer(
        settings.KAFKA_BOOTSTRAP_SERVERS,
        "inventory-service",
        {"OrderPlaced": on_order_placed, "PaymentFailed": on_payment_failed},
    )


if __name__ == "__main__":
    main()
