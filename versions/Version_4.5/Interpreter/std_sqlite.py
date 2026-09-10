import sqlite3

# Corvus Embedded SQLite Database Engine (v4.2)

class SQLiteEngine:
    @staticmethod
    def connect(db_path=":memory:"):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def execute(conn, query, params=()):
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount

    @staticmethod
    def fetch_all(conn, query, params=()):
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def close(conn):
        conn.close()

_global_sqlite_engine = SQLiteEngine()
