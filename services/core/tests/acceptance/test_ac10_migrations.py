"""AC 10 (service part): an Alembic migration exists and creates the tables on a fresh database."""

import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config

SERVICE = Path(__file__).resolve().parents[2]


def test_a_migration_revision_exists() -> None:
    revisions = [
        p for p in (SERVICE / "alembic" / "versions").glob("*.py") if p.name != "__init__.py"
    ]
    assert revisions, (
        "generate one: `uv run alembic revision --autogenerate -m 'create items and orders'`"
    )


def test_upgrade_head_creates_items_and_orders(tmp_path: Path) -> None:
    db_file = tmp_path / "core.db"
    config = Config(str(SERVICE / "alembic.ini"))
    config.set_main_option("script_location", str(SERVICE / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{db_file}")
    command.upgrade(config, "head")

    with sqlite3.connect(db_file) as conn:
        items = {row[1] for row in conn.execute("PRAGMA table_info(items)")}
        orders = {row[1] for row in conn.execute("PRAGMA table_info(orders)")}
    assert {"id", "name", "price", "stock"} <= items
    assert {"id", "user_id", "item_id", "quantity"} <= orders
