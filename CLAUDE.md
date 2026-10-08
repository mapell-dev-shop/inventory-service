# inventory-service

Owns products, stock and reservations. The map of the whole shop is in ../CLAUDE.md.

* Check your work with `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` and `uv run mypy src`.
* Stock changes in `handlers.py`, and `seed.py` resets the demo products. A reservation is made in the same transaction that records the event id in `processed_events`.
* An order is reserved completely or not at all. A failed payment gives the reserved stock back.
* A schema change is a new Alembic migration in `migrations/versions/`. Never edit a migration that has been applied.
* An event change starts in ../contracts (see its VERSIONING.md), never here.
