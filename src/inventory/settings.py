import os

DATABASE_URL = os.environ.get("INVENTORY_DATABASE_URL", "sqlite:///inventory.db")
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
