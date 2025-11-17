"""
Simple integration test to validate the DB bootstrap mechanism.
We expect:
 - The 'example_items' table exists (created from SQL migrations)
 - There is at least one row seeded with name='ping'
"""
from sqlalchemy import text


def test_example_items_table_exists_and_seeded(db_engine):
    # Check table exists via information_schema
    with db_engine.connect() as conn:
        exists = conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = 'example_items'
                )
                """
            )
        ).scalar()
        assert exists is True

        # Check seed data
        row = conn.execute(
            text("SELECT COUNT(*) FROM example_items WHERE name = 'ping'")
        ).scalar()
        assert row == 1

