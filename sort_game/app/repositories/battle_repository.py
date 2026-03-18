from app.db import get_conn

# DBが起動を前提
# テーブル名・カラム名・型がSQL定義と一致しているか確認する.aaaaaaaaaaaaa
# SQL定義を変更した場合は、repository側のSQLも必ず見直す
ALGORITHM_NAME_TO_ID_SQL = """
SELECT id, name
FROM algorithms
WHERE is_active = TRUE
"""


def fetch_algorithm_id_map(conn):
    with conn.cursor(dictionary=True) as cur:
        cur.execute(ALGORITHM_NAME_TO_ID_SQL)
        rows = cur.fetchall()

    return {row["name"]: row["id"] for row in rows}


def insert_battle(conn, user_id, array_size, benchmark_size):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO battles
                (user_id, array_size, benchmark_size, status)
            VALUES
                (%s, %s, %s, %s)
            """,
            (user_id, array_size, benchmark_size, "COMPLETED"),
        )
        return cur.lastrowid


def insert_results(conn, battle_id, results):
    algorithm_id_map = fetch_algorithm_id_map(conn)

    rows = []
    missing_algorithms = []

    for row in results:
        algorithm = row["algorithm"]

        if algorithm not in algorithm_id_map:
            missing_algorithms.append(algorithm)
            continue

        rows.append(
            (
                battle_id,
                algorithm_id_map[algorithm],
                float(row["duration_ms"]),
                int(row["rank"]),
            )
        )

    if missing_algorithms:
        joined = ", ".join(sorted(set(missing_algorithms)))
        raise ValueError(f"unknown algorithm: {joined}")

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO battle_results
                (battle_id, algorithm_id, duration_ms, rank_position)
            VALUES
                (%s, %s, %s, %s)
            """,
            rows,
        )


def save_battle(user_id, array_size, benchmark_size, results):
    conn = get_conn()

    try:
        conn.start_transaction()

        battle_id = insert_battle(conn, user_id, array_size, benchmark_size)
        insert_results(conn, battle_id, results)

        conn.commit()
        return battle_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def fetch_recent_battles(user_id, limit):
    conn = get_conn()

    try:
        with conn.cursor(dictionary=True, buffered=True) as cur:
            cur.execute(
                """
                SELECT
                    b.id AS battle_id,
                    b.user_id,
                    b.array_size,
                    b.benchmark_size,
                    b.status,
                    b.created_at AS created_at,
                    a.name AS algorithm,
                    br.duration_ms,
                    br.rank_position AS `rank`
                FROM battle_results br
                JOIN battles b
                    ON b.id = br.battle_id
                JOIN algorithms a
                    ON a.id = br.algorithm_id
                JOIN (
                    SELECT id
                    FROM battles
                    WHERE user_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s
                ) latest
                    ON latest.id = b.id
                WHERE b.user_id = %s
                ORDER BY b.created_at DESC, b.id DESC, br.rank_position ASC
                """,
                (int(user_id), int(limit), int(user_id)),
            )

            rows = cur.fetchall()

            for row in rows:
                created_at = row.get("created_at")
                if created_at is not None:
                    row["created_at"] = created_at.strftime("%Y-%m-%d %H:%M:%S")

            return rows

    finally:
        conn.close()


def fetch_statistics(user_id, limit):
    conn = get_conn()

    try:
        with conn.cursor(dictionary=True, buffered=True) as cur:
            cur.execute(
                """
                SELECT
                    a.name AS algorithm,
                    AVG(br.duration_ms) AS avg_duration_ms,
                    SUM(CASE WHEN br.rank_position = 1 THEN 1 ELSE 0 END) AS rank_1,
                    SUM(CASE WHEN br.rank_position = 2 THEN 1 ELSE 0 END) AS rank_2,
                    SUM(CASE WHEN br.rank_position = 3 THEN 1 ELSE 0 END) AS rank_3,
                    SUM(CASE WHEN br.rank_position = 1 THEN 1 ELSE 0 END) AS wins,
                    COUNT(*) AS plays
                FROM battle_results br
                JOIN algorithms a
                    ON a.id = br.algorithm_id
                JOIN (
                    SELECT id
                    FROM battles
                    WHERE user_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s
                ) latest
                    ON latest.id = br.battle_id
                JOIN battles b
                    ON b.id = br.battle_id
                WHERE b.user_id = %s
                GROUP BY a.id, a.name
                ORDER BY
                    CASE a.name
                        WHEN 'quick' THEN 1
                        WHEN 'merge' THEN 2
                        WHEN 'heap' THEN 3
                        WHEN 'insertion' THEN 4
                        WHEN 'selection' THEN 5
                        WHEN 'bubble' THEN 6
                        ELSE 999
                    END
                """,
                (int(user_id), int(limit), int(user_id)),
            )
            return cur.fetchall()
    finally:
        conn.close()