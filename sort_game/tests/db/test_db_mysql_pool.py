from unittest.mock import patch

import pytest

from app.db import mysql_pool


def test_get_conn_pool_creation_failure(app_ctx):
    original_pool = mysql_pool._pool
    original_pool_settings = mysql_pool._pool_settings
    mysql_pool._pool = None
    mysql_pool._pool_settings = None

    try:
        with patch("app.db.mysql_pool.pooling.MySQLConnectionPool") as mock_pool:
            mock_pool.side_effect = mysql_pool.mysql.connector.Error("pool create failed")

            with pytest.raises(RuntimeError) as exc_info:
                mysql_pool.get_conn()

            assert "MySQL connection failed after retries" in str(exc_info.value)
    finally:
        mysql_pool._pool = original_pool
        mysql_pool._pool_settings = original_pool_settings


def test_get_conn_connection_failure(app_ctx):
    class DummyPool:
        def get_connection(self):
            raise mysql_pool.mysql.connector.Error("connection failed")

    original_pool = mysql_pool._pool
    original_pool_settings = mysql_pool._pool_settings
    mysql_pool._pool = DummyPool()
    mysql_pool._pool_settings = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "test_user",
        "password": "test_password",
        "database": "sort_portfolio_test",
    }

    try:
        with pytest.raises(RuntimeError) as exc_info:
            mysql_pool.get_conn()

        assert "Failed to get MySQL connection from pool" in str(exc_info.value)
    finally:
        mysql_pool._pool = original_pool
        mysql_pool._pool_settings = original_pool_settings