# DB接続が取得できることを前提とする
# usersテーブルのカラム名とSQLが一致しているか確認する
# email は UNIQUE を前提に1件取得する

from app.db.mysql_pool import get_connection


def find_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, username, email, password_hash, is_active
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()