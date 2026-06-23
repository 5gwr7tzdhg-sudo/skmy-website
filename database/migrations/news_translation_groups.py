"""Allow translated news records to share one translation key."""

from sqlalchemy import inspect, text


def upgrade(engine):
    """Remove only the single-column unique constraint from news.translation_key."""
    inspector = inspect(engine)
    unique_constraints = [
        constraint for constraint in inspector.get_unique_constraints("news")
        if constraint.get("column_names") == ["translation_key"]
    ]
    unique_indexes = [
        index for index in inspector.get_indexes("news")
        if index.get("unique") and index.get("column_names") == ["translation_key"]
    ]

    with engine.begin() as connection:
        for constraint in unique_constraints:
            connection.execute(
                text(f'ALTER TABLE news DROP CONSTRAINT IF EXISTS "{constraint["name"]}"')
            )
        for index in unique_indexes:
            connection.execute(
                text(f'DROP INDEX IF EXISTS "{index["name"]}"')
            )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_news_translation_key "
                "ON news (translation_key)"
            )
        )
