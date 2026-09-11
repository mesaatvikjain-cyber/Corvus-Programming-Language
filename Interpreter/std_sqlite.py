import sqlite3

# Corvus Embedded SQLite Database Engine (v4.6 - Security Hardened)

class SQLiteEngine:
    @staticmethod
    def connect(db_path=":memory:"):
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def execute(conn, query, params=()):
        cursor = conn.cursor()
        if isinstance(params, (list, tuple)):
            clean_params = params
        elif isinstance(params, dict):
            clean_params = params if len(params) > 0 else ()
        elif params is None or params == ():
            clean_params = ()
        else:
            clean_params = (params,)
        cursor.execute(str(query), clean_params)
        conn.commit()
        return cursor.rowcount

    @staticmethod
    def fetch_all(conn, query, params=()):
        cursor = conn.cursor()
        if isinstance(params, (list, tuple)):
            clean_params = params
        elif isinstance(params, dict):
            clean_params = params if len(params) > 0 else ()
        elif params is None or params == ():
            clean_params = ()
        else:
            clean_params = (params,)
        cursor.execute(str(query), clean_params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def close(conn):
        try:
            conn.close()
        except Exception:
            pass

_global_sqlite_engine = SQLiteEngine()
