# std_orm.py
# Corvus Active-Record SQLite ORM
# Zero-dependency declarative object-relational mapping for SQLite databases.

import sqlite3
import os
from typing import Any, Dict, List, Optional, Union

_db_connections: Dict[str, sqlite3.Connection] = {}

def get_connection(db_path: str = "app.db") -> sqlite3.Connection:
    if db_path not in _db_connections:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _db_connections[db_path] = conn
    return _db_connections[db_path]

class QueryBuilder:
    def __init__(self, table_name: str, db_path: str = "app.db"):
        self.table_name = table_name
        self.db_path = db_path
        self._where_clause = ""
        self._where_params = []
        self._order_by_clause = ""
        self._limit_val = None

    def where(self, condition: str, params: Optional[List[Any]] = None):
        self._where_clause = condition
        self._where_params = params or []
        return self

    def order_by(self, column: str, direction: str = "ASC"):
        col_clean = column.strip()
        if " " in col_clean:
            parts = col_clean.split()
            col = parts[0]
            direction = parts[1]
        else:
            col = col_clean
        self._order_by_clause = f"ORDER BY {col} {direction.upper()}"
        return self

    def limit(self, n: int):
        self._limit_val = int(n)
        return self

    def all(self) -> List[Any]:
        conn = get_connection(self.db_path)
        cur = conn.cursor()

        sql = f"SELECT * FROM {self.table_name}"
        if self._where_clause:
            sql += f" WHERE {self._where_clause}"
        if self._order_by_clause:
            sql += f" {self._order_by_clause}"
        if self._limit_val is not None:
            sql += f" LIMIT {self._limit_val}"

        cur.execute(sql, self._where_params)
        rows = [Model(dict(r)) for r in cur.fetchall()]
        return rows

    def to_list(self) -> List[Any]:
        return self.all()

    def to_dicts(self) -> List[Dict[str, Any]]:
        return [r._data for r in self.all()]

    def first(self) -> Optional[Any]:
        self._limit_val = 1
        res = self.all()
        return res[0] if res else None


class Model:
    """Base class for Corvus Active-Record ORM models."""
    _table_name = "models"
    _db_path = "app.db"

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs):
        self._data = dict(data or {})
        self._data.update(kwargs)
        for k, v in self._data.items():
            setattr(self, k, v)

    @classmethod
    def set_db_path(cls, path: str):
        cls._db_path = path

    @classmethod
    def get_table_name(cls) -> str:
        return getattr(cls, "_table_name", cls.__name__.lower() + "s")

    @classmethod
    def migrate(cls, schema: Optional[Dict[str, str]] = None):
        """Create SQLite table if it does not already exist."""
        table = cls.get_table_name()
        conn = get_connection(cls._db_path)
        cur = conn.cursor()

        if schema:
            cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
            for col, col_type in schema.items():
                cols.append(f"{col} {col_type}")
            col_def = ", ".join(cols)
        else:
            col_def = "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, email TEXT, active INTEGER, payload TEXT"

        cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_def})")
        conn.commit()
        return True

    @classmethod
    def create(cls, fields: Dict[str, Any]):
        cls.migrate()
        table = cls.get_table_name()
        conn = get_connection(cls._db_path)
        cur = conn.cursor()

        keys = list(fields.keys())
        placeholders = ", ".join(["?" for _ in keys])
        cols = ", ".join(keys)
        values = [fields[k] for k in keys]

        cur.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", values)
        new_id = cur.lastrowid
        conn.commit()

        record = dict(fields)
        record["id"] = new_id
        return cls(record)

    @classmethod
    def find(cls, record_id: int):
        table = cls.get_table_name()
        conn = get_connection(cls._db_path)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
        row = cur.fetchone()
        if row:
            return cls(dict(row))
        return None

    @classmethod
    def where(cls, condition: str, params: Optional[List[Any]] = None) -> QueryBuilder:
        table = cls.get_table_name()
        qb = QueryBuilder(table, cls._db_path)
        return qb.where(condition, params)

    @classmethod
    def all(cls) -> List[Any]:
        return cls.where("1=1").all()

    def update(self, changes: Dict[str, Any]):
        if "id" not in self._data:
            return False
        table = self.get_table_name()
        conn = get_connection(self._db_path)
        cur = conn.cursor()

        set_clauses = [f"{k} = ?" for k in changes.keys()]
        vals = list(changes.values()) + [self._data["id"]]
        cur.execute(f"UPDATE {table} SET {', '.join(set_clauses)} WHERE id = ?", vals)
        conn.commit()

        self._data.update(changes)
        for k, v in changes.items():
            setattr(self, k, v)
        return True

    def delete(self):
        if "id" not in self._data:
            return False
        table = self.get_table_name()
        conn = get_connection(self._db_path)
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id = ?", (self._data["id"],))
        conn.commit()
        return True

    def __getitem__(self, item):
        return self._data.get(item)

    def __repr__(self):
        return f"<{self.get_table_name().capitalize()} {self._data}>"


def create_model_class(name: str, schema: Optional[Dict[str, str]] = None, db_path: str = "app.db") -> type:
    table_name = name.lower() + "s" if not name.endswith("s") else name.lower()
    new_cls = type(name, (Model,), {
        "_table_name": table_name,
        "_db_path": db_path
    })
    new_cls.migrate(schema)
    return new_cls

def connect_db(db_path: str = "app.db") -> sqlite3.Connection:
    return sqlite3.connect(db_path)
