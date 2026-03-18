from app.db import get_conn


def test_db_connection(app_ctx):
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1")
            row = cur.fetchone()
        finally:
            cur.close()
    finally:
        conn.close()

    assert row is not None
    assert row[0] == 1