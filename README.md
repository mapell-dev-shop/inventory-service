# inventory-service

The inventory bounded context of the shop: products, their stock, and the stock reserved for orders.

## Run it

`./run-all.sh` in the shop workspace starts it with everything else. On its own:

    uv sync
    uv run alembic upgrade head
    uv run python -m inventory.seed
    uv run uvicorn inventory.api:app --port 8002
    uv run python -m inventory.worker

`inventory.seed` resets the three demo products, stock included.

## Test it

    uv run pytest
    uv run ruff check . && uv run ruff format --check .
    uv run mypy src

## Events

* Consumes `OrderPlaced`. It reserves every line or none of them, then publishes `StockReserved` or `StockRejected`.
* Consumes `PaymentFailed` and gives the order's reserved stock back.
* Consumes `OrderCancelled` and gives the order's reserved stock back. It also remembers the order, so a later `OrderPlaced` for it is refused without publishing anything.

## Known limitations

* The event is published after the database commit. If publishing fails or the process dies in between, the reservation exists and nobody hears about it. A failed publish stops the worker with an error.
* Run one worker at a time: two workers could both read the same stock level and oversell, and a late `OrderPlaced` is refused only because one worker handles it after the `OrderCancelled`.
