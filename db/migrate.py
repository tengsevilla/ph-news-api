"""
Safe, additive schema migration.

Run this on an existing Railway database after pulling new code that adds columns.
It only adds missing columns — never drops, renames, or alters existing ones.
Safe to run multiple times (idempotent).

Usage:
    python db/migrate.py
"""
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import inspect, text

from db.connection import get_engine
from db.models import Base


def _col_definition(col, dialect) -> str:
    """Build a PostgreSQL column definition string from a SQLAlchemy Column."""
    type_str = col.type.compile(dialect=dialect)
    nullable = "" if col.nullable else " NOT NULL"
    default = ""
    if col.default is not None and hasattr(col.default, "arg"):
        arg = col.default.arg
        if callable(arg):
            pass  # Python-side callable default — not representable as SQL DEFAULT
        elif isinstance(arg, str):
            default = f" DEFAULT '{arg}'"
        elif arg is not None:
            default = f" DEFAULT {arg}"
    return f'"{col.name}" {type_str}{nullable}{default}'


def migrate() -> None:
    engine = get_engine()
    inspector = inspect(engine)

    # Create any entirely new tables first
    Base.metadata.create_all(engine)
    print("[migrate] Ensured all tables exist.")

    added: list[str] = []

    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue  # just created above, no columns to add

            existing_cols = {c["name"] for c in inspector.get_columns(table.name)}

            for col in table.columns:
                if col.name in existing_cols:
                    continue

                col_def = _col_definition(col, engine.dialect)
                sql = f'ALTER TABLE "{table.name}" ADD COLUMN IF NOT EXISTS {col_def}'
                print(f"  [migrate] {table.name}: adding column {col.name!r}")
                conn.execute(text(sql))
                added.append(f"{table.name}.{col.name}")

    if added:
        print(f"\n[migrate] Added {len(added)} column(s): {', '.join(added)}")
    else:
        print("[migrate] Schema is already up to date — nothing to add.")


if __name__ == "__main__":
    migrate()
