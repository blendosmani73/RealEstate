from sqlalchemy import text

from database import engine


def apply_migrations() -> None:
    """Migrime të lehta për databaza ekzistuese (pa Alembic)."""
    statements = [
        """
        ALTER TABLE properties
        ADD COLUMN IF NOT EXISTS created_by_id INTEGER
        REFERENCES users(id) ON DELETE SET NULL;
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_properties_created_by_id
        ON properties USING btree (created_by_id);
        """,
        """
        ALTER TABLE properties
        ADD COLUMN IF NOT EXISTS neighborhood VARCHAR(255);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_properties_neighborhood
        ON properties USING btree (neighborhood);
        """,
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
