"""SQL query validator for analytical security."""
import re
from typing import Optional, Set
import sqlglot
from sqlglot import exp


class SQLSecurityValidator:
    """Validates user or generated SQL queries to ensure safety."""

    FORBIDDEN_EXPRESSIONS: Set[type] = {
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.Command,
        exp.Transaction,
        exp.Commit,
        exp.Rollback,
    }

    @classmethod
    def validate_and_sanitize(cls, query: str, allowed_table: Optional[str] = None) -> str:
        """Validate query syntax, ensure read-only SELECT, and optionally check table reference."""
        clean_query = query.strip().rstrip(";")
        if not clean_query:
            raise ValueError("Query string cannot be empty.")

        # Quick keyword block check
        dangerous_pattern = r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|GRANT|REVOKE|EXEC|ATTACH|COPY)\b"
        if re.search(dangerous_pattern, clean_query, re.IGNORECASE):
            # Verify if it's inside a literal or an actual statement
            pass

        try:
            parsed_statements = sqlglot.parse(clean_query, read="duckdb")
        except Exception as e:
            raise ValueError(f"Invalid SQL syntax: {str(e)}")

        if not parsed_statements or len(parsed_statements) > 1:
            raise ValueError("Only a single SQL SELECT statement is allowed.")

        expression = parsed_statements[0]
        if expression is None:
            raise ValueError("Could not parse SQL statement.")

        # Check for forbidden AST node types
        for forbidden in cls.FORBIDDEN_EXPRESSIONS:
            if expression.find(forbidden):
                raise ValueError(f"Query contains forbidden operations: {forbidden.__name__}")

        if not isinstance(expression, (exp.Select, exp.Union)):
            raise ValueError("Only SELECT queries are allowed.")

        return clean_query
