"""Deterministic Analytical Engine for BusiAI.

Executes exact, verifiable SQL calculations in DuckDB.
"""
import time
from typing import Any, Dict, List, Optional
from app.analysis.models import (
    ContributionItem,
    ContributionResult,
    PeriodComparisonRequest,
    PeriodComparisonResult,
    PeriodComparisonRow,
    SQLQueryResult,
)
from app.analysis.sql_validator import SQLSecurityValidator
from app.core.database import db_manager
from app.ingestion.service import ingestion_service


class AnalysisEngine:
    """Core deterministic analytical engine."""

    def execute_custom_sql(self, dataset_id: str, query: str) -> SQLQueryResult:
        """Validate and execute a custom SQL query against the dataset."""
        dataset = ingestion_service.get_dataset(dataset_id)
        if not dataset:
            return SQLQueryResult(success=False, error=f"Dataset {dataset_id} not found.")

        start_time = time.perf_counter()
        try:
            safe_query = SQLSecurityValidator.validate_and_sanitize(query)
            rows = db_manager.execute_query(safe_query)
            elapsed = (time.perf_counter() - start_time) * 1000.0

            columns = list(rows[0].keys()) if rows else []
            return SQLQueryResult(
                success=True,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=round(elapsed, 2),
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return SQLQueryResult(
                success=False,
                error=str(e),
                execution_time_ms=round(elapsed, 2),
            )

    def compare_periods(self, req: PeriodComparisonRequest) -> PeriodComparisonResult:
        """Compute exact period-over-period changes for a metric."""
        dataset = ingestion_service.get_dataset(req.dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {req.dataset_id} not found.")

        table = dataset.table_name
        date_col = req.date_column
        metric_col = req.metric_column

        # Choose date formatting based on period_type
        if req.period_type == "quarter":
            fmt = "strftime(\"{date_col}\"::DATE, '%Y-Q') || QUARTER(\"{date_col}\"::DATE)"
        elif req.period_type == "year":
            fmt = "strftime(\"{date_col}\"::DATE, '%Y')"
        elif req.period_type == "day":
            fmt = "strftime(\"{date_col}\"::DATE, '%Y-%m-%d')"
        else:  # default month
            fmt = "strftime(\"{date_col}\"::DATE, '%Y-%m')"

        period_expr = fmt.replace("{date_col}", date_col)

        query = f"""
            WITH aggregated AS (
                SELECT 
                    {period_expr} AS period,
                    SUM("{metric_col}") AS total_val
                FROM "{table}"
                WHERE "{date_col}" IS NOT NULL AND "{metric_col}" IS NOT NULL
                GROUP BY period
                ORDER BY period ASC
            ),
            with_lag AS (
                SELECT 
                    period,
                    total_val,
                    LAG(total_val) OVER (ORDER BY period) AS prev_val,
                    (total_val - LAG(total_val) OVER (ORDER BY period)) AS abs_diff,
                    ROUND(((total_val - LAG(total_val) OVER (ORDER BY period)) / NULLIF(LAG(total_val) OVER (ORDER BY period), 0)) * 100.0, 2) AS pct_diff
                FROM aggregated
            )
            SELECT period, total_val, prev_val, abs_diff, pct_diff
            FROM with_lag
        """

        rows = db_manager.execute_query(query)
        period_rows: List[PeriodComparisonRow] = []
        highest_growth_p = None
        highest_growth_val = float("-inf")
        largest_drop_p = None
        largest_drop_val = float("inf")

        for r in rows:
            pct = float(r["pct_diff"]) if r["pct_diff"] is not None else None
            period_name = str(r["period"])
            period_rows.append(
                PeriodComparisonRow(
                    period=period_name,
                    current_value=float(r["total_val"]),
                    previous_value=float(r["prev_val"]) if r["prev_val"] is not None else None,
                    absolute_change=float(r["abs_diff"]) if r["abs_diff"] is not None else None,
                    percentage_change=pct,
                )
            )
            if pct is not None:
                if pct > highest_growth_val:
                    highest_growth_val = pct
                    highest_growth_p = period_name
                if pct < largest_drop_val:
                    largest_drop_val = pct
                    largest_drop_p = period_name

        overall_change = None
        if len(period_rows) >= 2 and period_rows[0].current_value > 0:
            overall_change = round(
                ((period_rows[-1].current_value - period_rows[0].current_value) / period_rows[0].current_value) * 100.0,
                2,
            )

        return PeriodComparisonResult(
            metric=metric_col,
            date_column=date_col,
            periods=period_rows,
            overall_change_pct=overall_change,
            highest_growth_period=highest_growth_p,
            largest_drop_period=largest_drop_p,
        )

    def analyze_contribution(
        self, dataset_id: str, metric: str, dimension: str
    ) -> ContributionResult:
        """Compute segment contribution shares and concentration."""
        dataset = ingestion_service.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        table = dataset.table_name
        total_sum = float(db_manager.execute_scalar(f'SELECT SUM("{metric}") FROM "{table}"') or 0.0)
        if total_sum <= 0:
            return ContributionResult(
                metric=metric,
                dimension=dimension,
                total_value=0.0,
                items=[],
                top_3_concentration_pct=0.0,
            )

        query = f"""
            SELECT 
                "{dimension}"::VARCHAR AS segment,
                SUM("{metric}") AS seg_val,
                ROUND((SUM("{metric}") / {total_sum}) * 100.0, 2) AS share_pct
            FROM "{table}"
            WHERE "{dimension}" IS NOT NULL AND "{metric}" IS NOT NULL
            GROUP BY "{dimension}"
            ORDER BY seg_val DESC
        """
        rows = db_manager.execute_query(query)
        items: List[ContributionItem] = []
        top_3_sum = 0.0

        for i, r in enumerate(rows, start=1):
            share = float(r["share_pct"] or 0.0)
            if i <= 3:
                top_3_sum += share
            items.append(
                ContributionItem(
                    segment=str(r["segment"]),
                    value=float(r["seg_val"]),
                    percentage_share=share,
                    rank=i,
                )
            )

        return ContributionResult(
            metric=metric,
            dimension=dimension,
            total_value=total_sum,
            items=items,
            top_3_concentration_pct=round(top_3_sum, 2),
        )


analysis_engine = AnalysisEngine()
