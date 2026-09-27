"""DuckDB database connection manager for BusiAI.

Provides high-performance in-memory analytical querying.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import duckdb
from app.core.config import settings


class DatabaseManager:
    """Manages DuckDB analytical database instances."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        """Get or initialize the DuckDB connection."""
        if self._conn is None:
            if self.db_path:
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
                self._conn = duckdb.connect(self.db_path)
            else:
                self._conn = duckdb.connect(":memory:")
        return self._conn

    def execute_query(
        self, query: str, params: Optional[list[Any] | dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SQL query safely and return results as list of dictionaries."""
        cursor = self.connection.cursor()
        if params:
            result = cursor.execute(query, params)
        else:
            result = cursor.execute(query)

        columns = [desc[0] for desc in result.description] if result.description else []
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def execute_scalar(
        self, query: str, params: Optional[list[Any]] = None
    ) -> Any:
        """Execute query returning a single scalar value."""
        rows = self.execute_query(query, params)
        if rows and len(rows) > 0:
            first_row = rows[0]
            return next(iter(first_row.values()))
        return None

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the current connection."""
        res = self.connection.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name = ?",
            [table_name],
        ).fetchone()
        return bool(res and res[0] > 0)

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Return columns and types of a table."""
        return self.execute_query(f'DESCRIBE "{table_name}"')

    def close(self):
        """Close connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None


db_manager = DatabaseManager()
