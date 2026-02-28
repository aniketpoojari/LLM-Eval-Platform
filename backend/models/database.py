import os
import sqlite3

from backend.logger.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(base_dir, "database", "eval_platform.db")

        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql"
        )
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            conn = self._get_connection()
            try:
                conn.executescript(schema_sql)
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
            finally:
                conn.close()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def execute(self, query, params=None):
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params or [])
            conn.commit()
            return cursor
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params or [])
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params or [])
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def insert(self, table, data):
        columns = []
        placeholders = []
        values = []
        for k, v in data.items():
            columns.append(k)
            if v == "datetime('now')":
                placeholders.append("datetime('now')")
            else:
                placeholders.append("?")
                values.append(v)

        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        self.execute(query, values)

    def update(self, table, data, where_clause, where_params=None):
        set_parts = []
        values = []
        for k, v in data.items():
            if v == "datetime('now')":
                set_parts.append(f"{k} = datetime('now')")
            else:
                set_parts.append(f"{k} = ?")
                values.append(v)

        set_clause = ", ".join(set_parts)
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = values + (where_params or [])
        self.execute(query, params)

    def delete(self, table, where_clause, where_params=None):
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self.execute(query, where_params or [])
