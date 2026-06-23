"""Add independent translation keys without linking existing translations."""

from uuid import uuid4

from sqlalchemy import inspect, text


TABLES = ("news", "guide_categories", "guide_articles")
UNIQUE_TRANSLATION_KEY_TABLES = ("guide_categories", "guide_articles")


def upgrade(engine):
    """Apply the translation-key migration safely and idempotently."""
    inspector = inspect(engine)
    existing_columns = {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in TABLES
    }
    has_unique_key = {
        table: any(
            constraint.get("column_names") == ["translation_key"]
            for constraint in inspector.get_unique_constraints(table)
        ) or any(
            index.get("unique") and index.get("column_names") == ["translation_key"]
            for index in inspector.get_indexes(table)
        )
        for table in TABLES
    }

    with engine.begin() as connection:
        for table in TABLES:
            if "translation_key" not in existing_columns[table]:
                connection.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN translation_key VARCHAR(36)")
                )

            record_ids = connection.execute(
                text(f"SELECT id FROM {table} WHERE translation_key IS NULL")
            ).scalars().all()
            if record_ids:
                connection.execute(
                    text(f"UPDATE {table} SET translation_key = :translation_key WHERE id = :id"),
                    [
                        {"id": record_id, "translation_key": str(uuid4())}
                        for record_id in record_ids
                    ]
                )
            connection.execute(
                text(f"ALTER TABLE {table} ALTER COLUMN translation_key SET NOT NULL")
            )
            if table in UNIQUE_TRANSLATION_KEY_TABLES and not has_unique_key[table]:
                connection.execute(
                    text(
                        f"CREATE UNIQUE INDEX IF NOT EXISTS "
                        f"uq_{table}_translation_key ON {table} (translation_key)"
                    )
                )
