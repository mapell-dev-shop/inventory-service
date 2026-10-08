from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from shop_contracts.events import new_envelope, validate_event
from shop_contracts.messaging import InMemoryEventPublisher
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from inventory.api import app
from inventory.db import Base, get_session
from inventory.seed import seed


def event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """An envelope that passes the contract, as another service would publish it."""
    envelope = new_envelope(event_type, data)
    validate_event(envelope)
    return envelope


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with sessionmaker(engine)() as session:
        seed(session)
        yield session


@pytest.fixture
def publisher() -> InMemoryEventPublisher:
    return InMemoryEventPublisher()


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()
