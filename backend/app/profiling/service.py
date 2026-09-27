"""Profiling service using high-performance DuckDB analytical queries."""
import re
from typing import Dict, List, Optional
from app.core.database import db_manager
from app.ingestion.models import DatasetInfo
from app.profiling.models import (
    CategoricalStats,
    ColumnProfile,
    ColumnType,
    DatasetProfile,
    NumericStats,
    TemporalStats,
)


class ProfilingService:
    """Computes automated statistical summaries and profiles for datasets via DuckDB."""

    def __init__(self):
        self._profiles: Dict[str, DatasetProfile] = {}

    def profile_dataset(self, dataset: DatasetInfo) -> DatasetProfile:
        """Run comprehensive statistical profiling on dataset using DuckDB queries."""
        if dataset.id in self._profiles:
            return self._profiles[dataset.id]

        table = dataset.table_name
        total_rows = dataset.row_count
        total_cols = dataset.column_count

        column_profiles: List[ColumnProfile] = []
        issues: List[str] = []
        date_candidates: List[str] = []
        metric_candidates: List[str] = []
        dimension_candidates: List[str] = []

        total_null_cells = 0
        total_cells = total_rows * total_cols if total_rows > 0 and total_cols > 0 else 1

        for col_meta in dataset.columns:
            col_name = col_meta.name
            dtype = col_meta.data_type.upper()

            # Null count and distinct count
            stats_query = f"""
                SELECT 
                    COUNT(*) - COUNT("{col_name}") AS null_cnt,
                    COUNT(DISTINCT "{col_name}") AS distinct_cnt
                FROM "{table}"
            """
            base_stats = db_manager.execute_query(stats_query)[0]
            null_count = int(base_stats["null_cnt"] or 0)
            distinct_count = int(base_stats["distinct_cnt"] or 0)
            total_null_cells += null_count

            null_pct = (null_count / total_rows * 100.0) if total_rows > 0 else 0.0
            if null_pct > 30.0:
                issues.append(f"Column '{col_meta.original_name}' has high null rate ({null_pct:.1f}%)")

            # Determine column type
            inferred_type = self._infer_column_type(col_name, dtype, distinct_count, total_rows)
            is_pk = bool(null_count == 0 and distinct_count == total_rows and total_rows > 1)

            num_stats = None
            cat_stats = None
            temp_stats = None

            if inferred_type == ColumnType.NUMERIC:
                metric_candidates.append(col_name)
                # Compute numeric stats via DuckDB
                num_q = f"""
                    SELECT 
                        MIN("{col_name}") AS min_v,
                        MAX("{col_name}") AS max_v,
                        AVG("{col_name}") AS mean_v,
                        MEDIAN("{col_name}") AS median_v,
                        STDDEV("{col_name}") AS std_v,
                        QUANTILE_CONT("{col_name}", 0.25) AS q25_v,
                        QUANTILE_CONT("{col_name}", 0.75) AS q75_v,
                        SUM(CASE WHEN "{col_name}" = 0 THEN 1 ELSE 0 END) AS zero_cnt
                    FROM "{table}"
                    WHERE "{col_name}" IS NOT NULL
                """
                num_res = db_manager.execute_query(num_q)
                if num_res and num_res[0]["min_v"] is not None:
                    row = num_res[0]
                    q25 = float(row["q25_v"] or 0.0)
                    q75 = float(row["q75_v"] or 0.0)
                    iqr = q75 - q25
                    lower_bound = q25 - 1.5 * iqr
                    upper_bound = q75 + 1.5 * iqr

                    outlier_q = f"""
                        SELECT COUNT(*) AS out_cnt FROM "{table}"
                        WHERE "{col_name}" < {lower_bound} OR "{col_name}" > {upper_bound}
                    """
                    out_cnt = int(db_manager.execute_scalar(outlier_q) or 0)

                    num_stats = NumericStats(
                        min=float(row["min_v"]),
                        max=float(row["max_v"]),
                        mean=round(float(row["mean_v"] or 0.0), 2),
                        median=float(row["median_v"] or 0.0),
                        std=round(float(row["std_v"] or 0.0), 2),
                        q25=round(q25, 2),
                        q75=round(q75, 2),
                        outlier_count=out_cnt,
                        zero_count=int(row["zero_cnt"] or 0),
                    )

            elif inferred_type == ColumnType.DATETIME:
                date_candidates.append(col_name)
                temp_q = f"""
                    SELECT 
                        MIN("{col_name}")::VARCHAR AS min_d,
                        MAX("{col_name}")::VARCHAR AS max_d
                    FROM "{table}"
                    WHERE "{col_name}" IS NOT NULL
                """
                temp_res = db_manager.execute_query(temp_q)
                if temp_res and temp_res[0]["min_d"] is not None:
                    min_str = str(temp_res[0]["min_d"])
                    max_str = str(temp_res[0]["max_d"])
                    temp_stats = TemporalStats(
                        min_date=min_str,
                        max_date=max_str,
                    )

            elif inferred_type in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN, ColumnType.IDENTIFIER]:
                if inferred_type == ColumnType.CATEGORICAL:
                    dimension_candidates.append(col_name)

                top_q = f"""
                    SELECT "{col_name}"::VARCHAR AS val, COUNT(*) AS cnt
                    FROM "{table}"
                    WHERE "{col_name}" IS NOT NULL
                    GROUP BY "{col_name}"
                    ORDER BY cnt DESC
                    LIMIT 5
                """
                top_rows = db_manager.execute_query(top_q)
                top_list = [{"value": str(r["val"]), "count": int(r["cnt"])} for r in top_rows]

                cat_stats = CategoricalStats(
                    unique_count=distinct_count,
                    cardinality_ratio=round(float(distinct_count / total_rows), 4) if total_rows > 0 else 0.0,
                    top_values=top_list,
                )

            column_profiles.append(
                ColumnProfile(
                    name=col_name,
                    original_name=col_meta.original_name,
                    inferred_type=inferred_type,
                    data_type=col_meta.data_type,
                    total_count=total_rows,
                    null_count=null_count,
                    null_percentage=round(null_pct, 2),
                    is_primary_key_candidate=is_pk,
                    numeric_stats=num_stats,
                    categorical_stats=cat_stats,
                    temporal_stats=temp_stats,
                )
            )

        completeness = max(0.0, 100.0 - (total_null_cells / total_cells * 100.0))
        quality_score = round(completeness, 1)
        primary_date = date_candidates[0] if date_candidates else None

        profile = DatasetProfile(
            dataset_id=dataset.id,
            total_rows=total_rows,
            total_columns=total_cols,
            quality_score=quality_score,
            columns=column_profiles,
            primary_date_column=primary_date,
            key_metrics=metric_candidates,
            key_dimensions=dimension_candidates,
            issues_detected=issues,
        )

        self._profiles[dataset.id] = profile
        return profile

    def _infer_column_type(
        self, col_name: str, dtype: str, distinct_cnt: int, total_rows: int
    ) -> ColumnType:
        """Infer column business semantic type from DuckDB schema and column properties."""
        lower_name = col_name.lower()
        
        # ID detection
        if any(w in lower_name for w in ["id", "uuid", "key", "code", "sku"]) and distinct_cnt > 0.8 * total_rows:
            return ColumnType.IDENTIFIER

        # Date / Datetime
        if any(w in dtype for w in ["DATE", "TIME", "TIMESTAMP"]) or any(w in lower_name for w in ["date", "timestamp", "month", "created_at"]):
            return ColumnType.DATETIME

        # Boolean
        if "BOOL" in dtype or (distinct_cnt <= 2 and any(w in lower_name for w in ["is_", "has_", "flag", "status"])):
            return ColumnType.BOOLEAN

        # Numeric
        if any(w in dtype for w in ["INT", "DOUBLE", "FLOAT", "DECIMAL", "NUMERIC", "BIGINT", "HUGEINT", "TINYINT", "SMALLINT"]):
            return ColumnType.NUMERIC

        # Categorical vs Text
        if distinct_cnt <= 50 or (total_rows > 0 and (distinct_cnt / total_rows) < 0.25):
            return ColumnType.CATEGORICAL

        return ColumnType.TEXT


profiling_service = ProfilingService()
